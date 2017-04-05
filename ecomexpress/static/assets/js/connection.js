$(function(){

$("#bag_scan").focus();

var include_bag_original = function(){
    var bag_number = $("input.bag_number").val();
    var actual_weight = $("input.actual_weight").val();
    var cid = $("#connection_id").val();
    $.ajax({
        type:"POST",
        url: "/service-centre/include_bags_connection/",
        data: {'cid': cid, 'bag_num': bag_number},
        success: function(resp){
            if(resp.success){
                $(".table-bag > tbody").prepend(resp.html);
                var shipment_count = parseInt($("#shipment_count").val()) + parseInt(resp.ship_count);
                $("#shipment_count").val(shipment_count);
            }else{ alert(resp.message) }
        }
    });
    $("#bag_scan").val("");
    $("#bag_scan").focus();
};

var include_bag = _.throttle(include_bag_original, 3000);

$("#bag_scan").die('keydown').live('keydown' ,function(e){
   if(e.keyCode == 13 || e.keyCode == 9){ include_bag(); }
});

var include_bag_popup_original = function(cid){
    $.ajax({
        type:"GET",
        url: "/service-centre/get_connection_bags/",
        data: {'cid': cid },
        success: function(resp){
            $("#connection_id").val(resp.cid);
            $("#connection_include_bag_modal_body").html(resp.html);
            $("#connection_include_bag_popup").modal('show');
        }
    });
};


var include_bag_popup = _.throttle(include_bag_popup_original, 3000);

$(".include_bags").live('click' ,function(e){
    console.log('include bags');
    var cid = $(this).attr('connection_id');
    include_bag_popup(cid);
});

});
