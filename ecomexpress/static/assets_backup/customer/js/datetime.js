(function ($, undefined) {
    $.fn.datetimepicker = function (options) {
        if(typeof options == typeof '') return this.datepicker.apply(this, arguments);
        options = $.extend({}, options);
        options.showTime = true;
        options.constrainInput = false;
        return this.datepicker(options);
    }

    $.datepicker._getTimeText = function (inst, h, m) {
        h = h || inst.selectedHour || 0;
        m = m || inst.selectedMinute || 0;

        if (this._get(inst, 'clockType') == 12) {
            return (h == 0 || h == 12 ? '12' : h >= 12 ? h - 12 : h)
            + ':' + (m < 10 ? '0' + m : m)
            + ' ' + (h < 12 ? 'AM' : 'PM');
        } else return h + ':' + (m < 10 ? '0' + m : m);
    }

    var formatDate = $.datepicker.formatDate;
    $.datepicker.formatDate = function (format, date, settings) {
        //console.log(this);
        var inst = $.datepicker._curInst;
        var showTime = inst ? this._get(inst, 'showTime') : false;
        if (showTime) {
            date.setHours(inst.selectedHour || 0);
            date.setMinutes(inst.selectedMinute || 0);
        }

        return formatDate.apply(this, arguments) + (showTime ? ' ' + this._getTimeText(inst) : '');
    }
    $.datepicker._defaults.clockType = 12;

    var _hideDatepicker = $.datepicker._hideDatepicker;
    $.datepicker._hideDatepicker = /*overrides*/function () {
        var inst = $.datepicker._curInst;
        inst.selectedHour = inst.currentHour = inst.selectedMinute = inst.currentMinute = undefined;
        _hideDatepicker.apply(this, arguments);
    }

    var _getDate = $.datepicker._getDate;
    $.datepicker._getDate = /*overrides*/function (inst) {
        var date = _getDate.apply(this, arguments);

        date.setHours(inst.selectedHour || inst.currentHour);
        date.setMinutes(inst.selectedMinute || inst.currentMinute);
        return date;
    }

    var parseDate = $.datepicker.parseDate;
    var rxTime = /\s+([0-9]+)(\:[0-9]+){0,1}(\:[0-9]+){0,1}(\s*[apm]+){0,1}/i;
    $.datepicker.parseDate = function (format, value, settings) {
        var h = 0, m = 0;

        var time = value.match(rxTime);
        if ($.isArray(time)) {
            h = parseFloat(time[1]);
            m = parseFloat((time[2] || '').replace(':', ''));
            if (isNaN(h)) h = 0;
            if (isNaN(m)) m = 0;

            if ((settings.clockType || $.datepicker._defaults.clockType) == 12) {
                if (h == 12) h = 0;
                if (time[0].toLowerCase().indexOf('p') > -1) h += 12;
            }

            value = value.replace(time[0], '');
        }

        var val = parseDate.apply(this, arguments);
        val.setHours(h);
        val.setMinutes(m);

        return val;
    }

    $.datepicker._setDateFromField = /*overrides*/function (inst, noDefault) {
        if (inst.input.val() == inst.lastVal) {
            return;
        }
        var dateFormat = this._get(inst, 'dateFormat');
        var dates = inst.lastVal = inst.input ? inst.input.val() : null;
        var date, defaultDate;
        date = defaultDate = this._getDefaultDate(inst);
        var settings = this._getFormatConfig(inst);
        try {
            date = this.parseDate(dateFormat, dates, settings) || defaultDate;
        } catch (event) {
            this.log(event);
            dates = (noDefault ? '' : dates);
        }
        inst.selectedDay = date.getDate();
        inst.drawMonth = inst.selectedMonth = date.getMonth();
        inst.drawYear = inst.selectedYear = date.getFullYear();
        inst.currentDay = (dates ? date.getDate() : 0);
        inst.currentMonth = (dates ? date.getMonth() : 0);
        inst.currentYear = (dates ? date.getFullYear() : 0);
        inst.currentHour = (dates ? date.getHours() : 0);
        inst.currentMinute = (dates ? date.getMinutes() : 0);
        this._adjustInstDate(inst);
    }

    var _updateDatepicker = $.datepicker._updateDatepicker;
    $.datepicker._updateDatepicker = /*overrides*/function (inst) {
        var showTime = this._get(inst, 'showTime');
        var buttons = this._get(inst, 'buttons');

        var self = this;

        if (buttons) inst.settings['showButtonPanel'] = true;

        _updateDatepicker.apply(this, arguments);

        inst.dpDiv.css({ zIndex: 1000 });
        if (buttons) {
            var panel = inst.dpDiv.find('.ui-datepicker-buttonpane:first').html('');

            for (var i in buttons) {
                var button = $('<button class="ui-datepicker-current ui-state-default ui-priority-secondary ui-corner-all"/>');

                (function (func) {
                    if (typeof func == 'object') {
                        if (func.attr)
                            button.attr(func.attr);
                        if (func.css)
                            button.css(func.css);
                        func = func.click || function () { };
                    }
                    button.text(i).click(function () { func.apply(self, ['#' + inst.id, inst]); }).appendTo(panel);
                })(buttons[i]);
            }
        }
       
        if (showTime) {
            var table = inst.dpDiv.find('table:last');
            var thead = table.find('thead>tr:first');
            var tbody = table.find('tbody>tr:first');
            var numRows = tbody.parent().children('tr').length;

            var lblTime = $('<th colspan="2" style="white-space:nowrap">12:00 AM</th>').appendTo(thead);
            lblTime.width(lblTime.width());
            var dpwidth = inst.dpDiv.width();
            inst.dpDiv.width(dpwidth + lblTime.width());
            var groups = inst.dpDiv.find('.ui-datepicker-group');
            groups.width(dpwidth/groups.length);
            groups.eq(groups.length-1).width(dpwidth/groups.length+lblTime.width());
            
            var height = table.height() - table.find('td:first').height() * 2;
            var tdHour = $('<td/>').css({ height: height, marginTop: 10, paddingLeft: 20 }).attr('rowspan', numRows).appendTo(tbody);
            var tdMin = $('<td/>').css({ height: height, marginTop: 10 }).attr('rowspan', numRows).appendTo(tbody);

            var divHour = $('<div/>').appendTo(tdHour);
            var divMin = $('<div/>').appendTo(tdMin);

            inst.selectedHour = inst.selectedHour || inst.currentHour;
            inst.selectedMinute = inst.selectedMinute || inst.currentMinute;
            lblTime.text($.datepicker._getTimeText(inst));

            divHour.slider({ min: 0, max: 23, value: inst.selectedHour, orientation: 'vertical', slide: function (e, ui) {
                inst.selectedHour = ui.value;
                if (inst.input)
                    inst.input.val($.datepicker._formatDate(inst));
                lblTime.text($.datepicker._getTimeText(inst));
            }
            });
            divMin.slider({ min: 0, max: 59, value: inst.selectedMinute, orientation: 'vertical', slide: function (e, ui) {
                inst.selectedMinute = ui.value;
                if (inst.input)
                    inst.input.val($.datepicker._formatDate(inst));
                lblTime.text($.datepicker._getTimeText(inst));
            }
            });
        }
    }
})(jQuery);


     


var options = { buttons: {
    'Cancel': { css: { 'float': 'right' }, click: function (sel, inst) {
        $.datepicker._hideDatepicker();
        if (inst.input)
            inst.input.val(inst.lastVal);
    }
               },
    'OK': { css: { 'float': 'right' }, click: function (sel, inst) {
        $.datepicker._hideDatepicker();
        
    }
           },
    'Clear': function (sel) {
        $.datepicker._clearDate(sel);
    }
}
};

$('#dp12').datetimepicker(options);
var _hidden = $('#hidden').datetimepicker($.extend({onClose:function(){ _hidden.next().text('Show! (' + _hidden.val() + ')'); }},options));
$('#multi').datetimepicker($.extend({numberOfMonths:2},options));
$('#dp24').datetimepicker($.extend({clockType:24},options));
$('#inline').datetimepicker();