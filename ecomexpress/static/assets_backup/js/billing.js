$(document).ready(function(){

    $(".date").datepicker({ changeMonth: true, changeYear: true, dateFormat: "yy-mm-dd" });
    $(".date").datepicker({ changeMonth: true, changeYear: true, dateFormat: "yy-mm-dd" });

    $("#id_provisional_billing").click(function(e){
        e.preventDefault();
        $(".content-row").addClass('hidden');
        $("#id_provisional_billing_div").removeClass('hidden');
    });

    $("#id_bill_generation").click(function(e){
        e.preventDefault();
        $(".content-row").addClass('hidden');
        $("#id_bill_generation_div").removeClass('hidden');
    });

    // Provisional billing section
    var submit_provisional_form = function(){
        var provisional_form = "#id_provisional_form";
        $.ajax({
            url: '/billing/provisional_billing/',
            type: 'POST',
            data: $(provisional_form).serialize(),
            success: function(resp){
                if(resp.success){
                    alert(resp.message);
                } else {
                    alert(resp.errors);
                }
            }
        });
    };

    var validate_provisional_form = function(){
        var date_from = $("#id_provisional_billing_from").val();
        var date_to = $("#id_provisional_billing_to").val();
        if (date_from && date_to) return true; else return false;
    };

    var validate_form = function(){
        var date_from = $("#id_billing_from").val();
        var date_to = $("#id_billing_to").val();
        if (date_from && date_to) return true; else return false;
    };

    var update_provisional_reports = function(){
        $.ajax({
            url: '/billing/update_provisional_reports/',
            type: 'GET',
            success: function(resp){
                $("#id_provisional_reports_div").html(resp.html);
            }
        });
    };

    $("#id_provisional_preview_button").click(function(e){
        e.preventDefault();
        if (validate_provisional_form()) submit_provisional_form();
        else alert('Please select date from and date to');
    });

    $("#id_provisional_reports").click(function(e){
        e.preventDefault();
        $(".content-row").addClass('hidden');
        $("#id_provisional_reports_div").removeClass('hidden');
        var is_report_div_empty =$("#id_provisional_reports_div").is(":empty");
        if(is_report_div_empty) update_provisional_reports();
    });

    $(document).on("click", '#id_provisional_reports_update', function(e){
        update_provisional_reports();
    });

    // Billing Section
    var submit_billing_form = function(form_hash, url){
        var form = form_hash;
        $.ajax({
            url: url,
            type: 'POST',
            data: $(form).serialize(),
            success: function(resp){
                if(resp.success){
                    alert(resp.message);
                } else {
                    alert(resp.errors);
                }
            }
        });
    };

    var update_billing_status = function(){
        $.ajax({
            url: '/billing/update_billing_status/',
            type: 'GET',
            success: function(resp){
                $("#id_bill_generation_status_div").html(resp.html);
            }
        });
    };

    var update_billing_reports = function(){
        $.ajax({
            url: '/billing/update_billing_reports/',
            type: 'GET',
            success: function(resp){
                $("#id_billing_reports_div").html(resp.html);
            }
        });
    };

    $("#id_bill_generation_button").click(function(e){
        e.preventDefault();
        if (validate_form()) submit_billing_form("#id_bill_generation_form", "/billing/generate/");
        else alert('Please select date from and date to');
    });

    $("#id_bill_generation_status").click(function(e){
        e.preventDefault();
        $(".content-row").addClass('hidden');
        $("#id_bill_generation_status_div").removeClass('hidden');
        var is_report_div_empty =$("#id_bill_generation_status_div").is(":empty");
        if(is_report_div_empty) update_billing_status();
    });

    $(document).on("click", '#id_bill_generation_status_update', function(e){
        update_billing_status();
    });

    $("#id_billing_reports").click(function(e){
        e.preventDefault();
        $(".content-row").addClass('hidden');
        $("#id_billing_reports_div").removeClass('hidden');
        var is_billing_report_div_empty =$("#id_billing_reports_div").is(":empty");
        if(is_billing_report_div_empty) update_billing_reports();
    });

    var add_report_row = function(){
        $(".billing_report_expand").parents('tr').remove();
        e.preventDefault();
        var $cur_row = $(this).closest('tr');
        var queue_id = $(this).attr('data-queue_id');

        var $new_row = $(".billing_report_expand").clone();
        $new_row.attr('data-queue_id', queue_id);
        $new_row.removeClass("hidden");
        var new_row_str = $new_row[0].outerHTML;

        var row_str = "<tr><td colspan='6'>" + new_row_str + "</td></tr>";
        var $row = $(row_str);
        $cur_row.after($row);
        $(".billing_report_expand").show();
    };

    $(document).on("click", '.get-billing-reports', function(e){
        var queue_id = $(this).attr('data-queue_id');
        $("#id_billqueue").val(queue_id);
    });

    var update_customer_reports = function(queue_id){
        console.log('update reports');
        $.ajax({
            url: '/billing/get_customer_reports/',
            type: 'GET',
            data: {'queue_id': queue_id},
            success: function(resp){
                console.log(resp);
                if(resp.success){
                    $("#id_billing_report_modal_body").html(resp.html);
                } else {
                    alert(resp);
                }
            }
        });

    };

    // update billing reports
    $(document).on("click", '.download-billing-reports', function(e){
        var queue_id = $(this).attr('data-queue_id');
        update_customer_reports(queue_id);
    });

});
