(function($) {
    // call this method for a table. This function will duplicate the last row
    // and remove data from all columns.
    $.fn.addRow = function ( options ) {

        // default options.
        var settings = $.extend({
            // These are the defaults.
            backgroundColor: "white"
        }, options );

        var $tr = this.find('tr:first');
        var $lasttr = this.find('tr:last');
        var $clone = $tr.clone();
        $clone.children('th').each(function(i, v){
            var id_val = $(this).attr('id');
            $(this).replaceWith('<td id='+id_val+'></td>');
        });
        $clone.css('height', 35);
        $clone.find('td').each(function(ind, val){
            var id_val = $(val).attr('id').split('-');
            if (id_val[1] == 'zone_org' || id_val[1] == 'zone_dest'|| id_val[1] == 'origin'|| id_val[1] == 'destination'){
                $(val).addClass('editable');
            }else{
                $(val).addClass('new-edit');
            }
            $(val).text('');
        });
        $lasttr.after($clone);
        return this;
    };

}( jQuery ));
