(function(){

    var update_alert_background = function(success){
        if(success){
            $(".include_cbag_message").removeClass('alert alert-error');
            $(".include_cbag_message").addClass('alert alert-success');
        }else{
            $(".include_cbag_message").removeClass('alert alert-success');
            $(".include_cbag_message").addClass('alert alert-error');
        }
    };

    // consolidated bag creation ajax update function
    var submit_cbag_creation_form = function(){
        $.ajax({
            url: '/operations/cbag/create/',
            type: 'POST',
            data: $("#cbag-form").serialize(),
            success: function(resp){
                $("#cbag-form").html(resp.form);
                if(resp.success){
                    $("#cbag_table_body").prepend(resp.bag_row);
                }else{
                    alert(resp.message); 
                }
            }
        });
    };

    // consolidated bag creation
    $(document).on('click', "#create_cbag", function(){
        var bag_num = $("#id_bag_number").val();
        var destination = $("#id_destination").val();
        if(bag_num && destination){
            submit_cbag_creation_form();
        }else{
            alert('Please fill Bag number and Destination');
            return false;
        }
    });

    // include bag in consolidated bag popup
    var update_modal_body = function(cbag_num){
        var cbag_num = $("#hidden_cbag_number").val();
        $.ajax({
            url: '/operations/cbag/details/',
            type: 'GET',
            data: {'cbag_num': cbag_num},
            success: function(resp){
                $("#cbag_include_table_body").html(resp.html);
            }
        });
    };

    $(document).on('click', ".cbag_include", function(){
        var cbag_num = $(this).parents('tr').data('cbag');
        $("#hidden_cbag_number").val(cbag_num);
        $("#include_cbag_modal").modal('show');
        update_modal_body(cbag_num);
    });

    var include_bag_to_cbag = function(bag_num){
        var cbag_num = $("#hidden_cbag_number").val();
        $.ajax({
            url: '/operations/cbag/include_bag/',
            type: 'POST',
            data: {'cbag_num': cbag_num, 'bag_num': bag_num},
            success: function(resp){
                $(".cbag_bag_number").val('');
                if(resp.success){
                    $("#cbag_include_table_body").prepend(resp.html);
                }else{
                    update_alert_background(resp.success);
                    $(".include_cbag_message").text(resp.message);
                    $(".include_cbag_message").show();
                }
            }
        });
    };

    // include bag in consolidated bag
    $(".cbag_bag_number").on('change', function(){
        var bag_num = $(".cbag_bag_number").val();
        if(!bag_num){ return false};
        include_bag_to_cbag(bag_num);
    });

    var cbag_remove_bag = function(bag_num){
        var cbag_num = $("#hidden_cbag_number").val();
        $.ajax({
            url: '/operations/cbag/remove_bag/',
            type: 'POST',
            data: {'cbag_num': cbag_num, 'bag_num': bag_num},
            success: function(resp){
                if(resp.success){ 
                    $("tr#bag-" + bag_num).remove();
                }
                update_alert_background(resp.success);
                $(".include_cbag_message").text(resp.message);
                $(".include_cbag_message").show();
            }
        });

    };

    $(document).on('click', ".cbag-remove-bag", function(){
        var bag_num = $(this).parents('tr').data('bag');
        cbag_remove_bag(bag_num);
    });

    var cbag_close = function(cbag_num){
        $.ajax({
            url: '/operations/cbag/close/',
            type: 'POST',
            data: {'cbag_num': cbag_num},
            success: function(resp){
                $("tr#cbag-" + cbag_num).find('.cbag_include').attr('disabled', 'disabled');
                $("tr#cbag-" + cbag_num).find('.cbag_close').attr('disabled', 'disabled');
                alert(resp.message);
            }
        });
    };

    // consolidated bag manifest
    $(document).on('click', ".cbag_close", function(){
        var cbag_num = $(this).parents('tr').data('cbag');
        console.log('close ', cbag_num);
        if(!cbag_num){ return false};
        cbag_close(cbag_num);
    });

})();
