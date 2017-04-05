

/** This will be our global, topmost level namespace */
var ECOMM = ECOMM || { };

ECOMM.ie = function(){ return navigator.userAgent.indexOf('MSIE') != -1; }

/** This is the skeleton for the module. Copy this to start with a new module */
ECOMM.skeletonModule = (function () {
    // define some config (Settings)
    var config = {
        autoInvokeInit: false, // whether the init function must be invoked automatically when page loads
        someconfig: 'a',
        somelist: ['apples', 'oranges', 'mangoes']
    };

    // define the init function (Implementation)
    var init = function () {
        alert('no!!');
    };

    // return an object
    return {
        config: config,
        init: init
    };

    /** This will make it possible to override config before calling implementation */
})();


/** Scripts for pickup module **/
ECOMM.pickup_dashboard = (function () {

    var config = {
        autoInvokeInit: false
    };

    var init = function (){
        var get_and_update_sc = function(address, element_id){
            $.ajax({
            url: "/generic/getpincode_info/",
            type: "GET",
            data: {'address': address},
            success: function(resp){
                $("#" + element_id + " option[value="+ resp.sc_id +"]").prop('selected', true);
            }
            });

        };

        $("#address_pincode").on("click", function(){
            var address = $("#shipment_address").val();
            get_and_update_sc(address, 'service_centre_rd')
        });

            $("#id_pickup_date").datepicker({dateFormat: 'yy-mm-dd'});

            // get corresponding service center for pincode
        var get_pincode_pickup_sc = function(pincode, element_id){
            $.ajax({
            url: "/services/get_pincode_pickup_sc/",
            type: "GET",
            data: {'pincode': pincode},
            success: function(resp){
                if(resp.success){
                    $("#" + element_id + " option[value="+ resp.pickup_sc +"]").prop('selected', true);
                }else{ alert("pincode not found!"); }
            }
            });
        };

        // call the pickup_sc update function when pincode is changed
        $("#id_pincode").on("change", function(){
            var pincode = $(this).val();
            if (pincode){
                get_pincode_pickup_sc(pincode, "id_delivery_service_centre");
            }
        });

        // autocomplete vendor name
        $("#id_vendor_name").autocomplete({
            source: "/services/get-vendors/",
            minLength: 3,
        });

        // auto fill the address once the vendor name is selected
        var get_vendor_address = function(name, element_id){
            $.ajax({
            url: "/services/get_vendor_address/",
            type: "GET",
            data: {'name': name},
            success: function(resp){
                $("#" + element_id).text(resp.address);
            }
            });
        };

        // id_vendor_name
        $("#id_vendor_name").focusout(function(){
            console.log('vendor anem changed');
            var name = $(this).val();
            if (name){
                console.log('call vendor anem changed');
                get_vendor_address(name, "id_address");
            }
        });

    };

    var status_update = function (){
        // update the pickup status
        var update_pickup_status = function(pickup_id, pickup_status){
            $.ajax({
                url: "/services/update_pickup_enroll_status/",
                type: "POST",
                data: {'pickup_id': pickup_id, "pickup_status": pickup_status},
                success: function(resp){
                    $("#pickup_status_" + resp.pickup_id).text(resp.status);
                }
            });
        };

        $(".pickup-status").on("click", function(){
            console.log('pickup stauts clicked');
            var pickup_id = $(this).parents('tr').data().val;
            var pickup_status = $(this).data().val;
            update_pickup_status(pickup_id, pickup_status)
        });

        $("#id_pickup_enroll_upload").on("click", function(){
            $("#id_pickup_enroll").modal("show");
        });
    };

    return {
        config: config,
        init: init,
        status_update: status_update
    }
})();

ECOMM.cod_panel = (function () {
    // define some config (Settings)
    var config = {
        autoInvokeInit: false, // whether the init function must be invoked automatically when page loads
        cod_panel_id: "id_cod_panel_dashboard",
        coddeposit_form: "id_codpanel_coddeposit_form"
    };

    // define the init function (Implementation)
    var init = function () {
        alert('no!!');
    };

    var update_coddeposits = function(){
        $("#id_search_loader").show();
        $.ajax({
            url: "/delivery/cod_panel/coddeposits_search/",
            type: "GET",
            data: $("#" + config.coddeposit_form).serialize(),
            success: function(resp){
                $("#id_search_loader").hide();
                $("#" + config.cod_panel_id).html(resp.html);
            }
        });
    };

    var init = function (){
        $("#id_cod_panel_cod_deposits").on('click', function(){
            update_coddeposits();
        });

        $(document).on("click", "#id_coddeposit_search_button", function(e){
            update_coddeposits();
        });
       
    }

    // return an object
    return {
        config: config,
        init: init
    };

    /** This will make it possible to override config before calling implementation */
})();


