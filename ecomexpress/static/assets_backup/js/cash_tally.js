 $(document).ready(function() {
    $(".img_loader").hide();
    $(".img_loader_codd").hide();
    $(".cash_tally_date").datepicker({ changeMonth: true, changeYear: true, dateFormat: "yy-mm-dd" });
    $('.deposit_time').timepicker();

    var get_checked_awbs = function(){
        var awbs = [];
        $(".airwaybill_number_check").each(function(i,v){
            if($(v).is(":checked")){
              awbs.push($(v).val());
            }
        });
        return awbs;
    };

    var get_checked_amounts = function(){
        var amts = [];
        $(".airwaybill_number_check").each(function(i,v){
            // calculate_me class help to calculate sum of only selected outscan id in the dropdown list
            if($(v).is(":checked") && $(v).parents('tr').hasClass('calculate_me')){
                var amt = $(v).parents('tr').find('.shipment_amount_collected').eq(0).text();
                amts.push(parseFloat(amt));
            }
        });
        return amts;
    };

    var get_total_amount = function(){
        var amt_array = get_checked_amounts();
        console.log('amoutn array', amt_array);
        total_amount = amt_array.reduce(function(p1, p2){return p1 + p2 ; }, 0);
        console.log('checked amount is ', total_amount);
        return total_amount;
    };

    var update_total_amount = function(){
        var total_amount = get_total_amount();
        $("span#total_amount_id").text(total_amount);
    };

    $(".airwaybill_number_check").live('change', function(){
        var is_checked = $(this).is(':checked')
        console.log('clikced on awb check');
        if(is_checked){
            console.log('checked');
            console.log('checked..',$(this).parents('tr').find(".awbs-checked"));
            $(this).parents('tr').find(".awbs-checked").show();
            $(this).parents('tr').find(".awbs-unchecked").hide();
            $(this).attr('checked', 'checked');
        }else{
            console.log('unchecked');
            console.log('checked..',$(this).parents('tr').find(".awbs-unchecked"));
            $(this).parents('tr').find(".awbs-unchecked").show();
            $(this).parents('tr').find(".awbs-checked").hide();
            $(this).removeAttr('checked');
        }
        update_total_amount();
    });

    $("select.outscans-list").change(function(){
        $(".unclosed_ships").hide();
        $(".unclosed_ships").removeClass('calculate_me');
        var os_id = $(this).val();
        if (os_id == 'all'){
            $(".unclosed_ships").show();
            $(".unclosed_ships").addClass('calculate_me');
        }else{
            $(".outscan-"+os_id).show();
            $(".outscan-"+os_id).addClass('calculate_me');
        }
        update_total_amount();
    });

    $('.shipment_amount_collected').live('click', function(){
        $(this).editable('/delivery/cash_tally/update_shipment_collected_value/', {
            indicator : 'Saving...',
            width : '50px',
            tooltip   : 'Click to edit',
            callback: function(result, settings){
                var resp = eval("(" + result + ")");

                // update collected amount
                var last_collection = resp.last_collection;
                var ship_id = $(this).attr('id');
                $(".collected-"+ship_id).text(last_collection);

                if(resp.success == true){
                    // get pending collectable amount and pending amount
                    var pend = $(".pending-"+ship_id);
                    var pending_amount = $(pend).attr('data-val');
                    // update pending amount
                    var pend_amt =  parseFloat(pending_amount) - parseFloat(last_collection);
                    $(pend).text('Rs. '+pend_amt);
                    // update total amount
                    update_total_amount();
                    // update the outscan tally
                    $.ajax({
                        type: 'GET',
                        url: '/delivery/cash_tally/delivered_cash_tally/',
                        success: function (resp){
                            $("#outscanCollections > tbody").html("")
                            $("#outscanCollections > tbody").html(resp.html)
                        }
                    });
                }else{
                    alert(resp.message);
                }
           }
        });
    });

    $("#cashtallyAirwaybillNumber").live('change', function(){
        console.log('clikced on all awb check');
        var is_checked = $(this).is(':checked')
        if(is_checked){
            $(".awbs-checked").show();
            $(".awbs-unchecked").hide();
            $(".airwaybill_number_check:checkbox").attr('checked', 'checked');
        }else{
            $(".awbs-unchecked").show();
            $(".awbs-checked").hide();
            $(".airwaybill_number_check:checkbox").removeAttr('checked');
        }
        update_total_amount();
    });

    $("#updateCollectedAmount").live('click', function(){
        $(".img_loader").show();
        var awbs = get_checked_awbs();
        if(awbs.length == 0){
           $(".img_loader").hide();
           alert("Please select some Airwaybill numbers before click on submit");
           return false;
        }

        $.ajax({
            type: 'POST',
            url: '/delivery/cash_tally/delivered_cash_tally/',
            data: {'awbs':awbs},
            success: function (resp){
                $(".img_loader").hide();
                if (resp.success){
                    $(".update_message").show();
                    update_total_amount();
                    for(i = 0; i < resp.awbs.length; i++){
                         var awb_el = "awb-" + awbs[i];
                         $("#"+awb_el).find('input.airwaybill_number_check').remove();
                         var amt = $("#"+awb_el).parent('tr').find('span.shipment_amount_collected').eq(0).text();
                         $("#"+awb_el).parent('tr').find('span.shipment_amount_collected').remove();
                         $("#"+awb_el).parent('tr').find('td.collected_amount').text('Rs. '+amt);
                    }
                    $("#outscanCollections > tbody").html("")
                    $("#outscanCollections > tbody").html(resp.html)
                }else{
                    alert('some error occured');
                }
           }
        });

    });

    $("#CashTallyAddShipment").live('click', function(){
        var awb = $("input[name='ppd-airwaybill_number']").val();
        var coll_val = $("input[name='cash_tally-collectable_amount']").val();
        $.ajax({
            type: 'POST',
            url: '/delivery/cash_tally/add_shipment/',
            data: {'collectable_value': coll_val, 'awb':awb},
            success: function(resp){
                $(".add-ppd-shipment-success").hide();
                $(".add-ppd-shipment-error").hide();
                if (resp.success){
                    $(".add-ppd-shipment-success").show();
                    var row_str = "<tr><td>"+resp.airwaybill_number+"</td><td>"+resp.pieces+"</td><td>"+resp.collectable_value+"</td>";
                        row_str += "<td>"+resp.customer+"</td><td>"+resp.collected_amount+"</th><td>"+resp.pending_amount+"</td></tr>";
                    $("table.add-ppd-shipment-table tr:last").after(row_str);
                }else{
                    $(".add-ppd-shipment-error").show();
                    $(".add-ppd-shipment-error").html(resp.error_list);
                }
           }
        });
    });

    $(".add-coddbatch").live('click', function(){
        var fewSeconds = 3;
        var btn = $(this);
        btn.prop('disabled', true);
        var date=$("input.date").val();
        var table_data = $("#codtable > tbody").html();
        var datastring = "&date="+date;
        $.ajax({
            type:"GET",
            url: "/delivery/add_coddeposit/",
            data: datastring,
            success: function(resp){
                if(resp.success){
                    $("#codtable > tbody").html("")
                    $("#codtable > tbody").append(resp.html);
                    $("#codtable > tbody").append(table_data);
                    setTimeout(function(){
                        btn.prop('disabled', false);
                    }, fewSeconds*1000);
                }else{
                    alert(resp.msg);
                }
            }
        });
        return false;
    });

    $(".awb_update").live('click', function(){
        var amount = $("input.amt").val();
        var awb=$("input.awb").val();
        var cash_emp=$("input.cash_emp").val();
        var delivery_emp=$("input.delivery_emp").val();
        var datastring = "amt="+amount+"&awb="+awb+"&cash_emp="+cash_emp+"&delivery_emp="+delivery_emp+"&upd_type=upd";
        $.ajax({
            type:"POST",
            url: "/delivery/awb_tally/",
            data: datastring,
            success: function(resp){
                $(".tableawbsuc > tbody").append(resp);
            }
        });
        return false;
    });

    $(".denomination").change(function(){
        var type=$(this).attr("dtype");
        var quantity = $(this).val();
        var amt = type*quantity;
        $('#'+type+'').val(amt);
        $('#total').val("");
        var total = parseInt($("#1000").val())+parseInt($("#500").val())+parseInt($("#100").val())+parseInt($("#50").val())+parseInt($("#20").val())+parseInt($("#10").val())+parseInt($("#5").val())+parseInt($("#1").val());
        $('#total').val(total);
    });

    $("[id^=codd_close]").live("click",function(){
        var codd_id=$(this).attr("codd_id");
        var dis = $(this).attr('disabled');
        if (dis == 'disabled'){
            return False;
        }
        $(".img_loader_codd").hide();
        $("#img_loader_codd-"+codd_id).show();
        $.ajax({
            type:"POST",
            url: "/delivery/close_codd/",
            data: {'codd_id': codd_id},
            success: function(resp){
                console.log(resp);
                $("#img_loader_codd-"+resp.codd_id).hide();
                $("#success"+resp.codd_id+"").html("<span class='label label-success'>Closed</span>");
                $(".cash_deposits").attr("disabled", "disabled");
                $("#codd_close-"+resp.codd_id+"").attr("disabled", "disabled");
                $("#domestic").html(resp.daily_cash_tally_html);
                $(".img_loader_codd").hide();
            }
        });
        return false;
    });

    $(".reason_code").change(function(){
       var reason_code = $(this).val();
       var awb=$(this).attr("type");
       var datastring = "reason_code="+reason_code+"&awb="+awb+"&upd_type=rc";
       $.ajax({
          type:"POST",
          url: "/delivery/awb_tally/",
          data: datastring,
          success: function(resp){
              $("#reason"+awb+"").html(" ");
              $("#reason"+awb+"").html(resp);
          }
       });
       return false;
    });
});
