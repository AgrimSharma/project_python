/***************************/
//@Author: Adrian "yEnS" Mato Gondelle
//@website: www.yensdesign.com
//@email: yensamg@gmail.com
//@license: Feel free to use it, but keep this credits please!
/***************************/

//SETTING UP OUR POPUP
//0 means disabled; 1 means enabled;
var popupStatus = 0;

//loading popup with jQuery magic!
function loadPopup(){
	//loads popup only if it is disabled
	if(popupStatus==0){
		$("#backgroundPopup").css({
			"opacity": "0.7"
		});
		$("#backgroundPopup").fadeIn("slow");
		$("#popupContact").fadeIn("slow");
		popupStatus = 1;
	}
	$("#popdate").datepicker({
	      changeMonth: true, changeYear: true, dateFormat: "dd/mm/yy" });

	$("#popupform").hide();
}

//disabling popup with jQuery magic!
function disablePopup(){

	//disables popup only if it is enabled
	if(popupStatus==1){
		$("#backgroundPopup").fadeOut("slow");
		$("#popupContact").fadeOut("slow");
		popupStatus = 0;
	}
}

function centerOctroiDetails(octroi_id){
	//request data for centering
    //centering
	$("#popupContact").css({
		"position": "absolute",
		"top": 220,
		"left": 200,
		"width":900,
		"height":500,

	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/hub/octroi_summary_edit/"+octroi_id+"/")
}

//centering popup
function centerPopupEmployee(){
	//request data for centering
    //centering
	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 483,
		"width":225,
		"height":395,

	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/authentication/registration")
}


function centerPopupPickup(){
	//request data for centering
    //centering
	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 483,
		"width":411,
		"height":474,

	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/pickup/request_pickup/")

}




function centerPopupEditEmployee(employee_id){
	//request data for centering
    //centering
	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 483,
		"width":225,
		"height":395,

	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/authentication/edit_employee/"+employee_id+"/")
}


function centerPopupForgotPass(){
	$("#popupContact").css({
		"position": "absolute",
		"top": 284,
		"left": 483,
		"width":225,
		"height":159,

	});
	$("#backgroundPopup").css({
		});
$("#popupContact").load("/authentication/password/reset/")
}


function centerPopupFile(pickup_id){
	$("#popupContact").css({
		"position": "absolute",
		"top": 284,
		"left": 483,
		"width":225,
		"height":80,

	});
	$("#backgroundPopup").css({
		});

$("#popupContact").load("/service-centre/upload_file/"+pickup_id+"/")


}

function upload_auto_pickup_file(){

	$("#popupContact").css({
		"position": "absolute",
		"top": 284,
		"left": 483,
		"width":275,
		"height":110,

	});
	$("#backgroundPopup").css({
		});

$("#popupContact").load("/service-centre/auto_upload_file")


}


function add_rates(){

	$("#popupContact").css({
		"position": "absolute",
		"top": 284,
		"left": 483,
		"width":275,
		"height":110,

	});
	//$("#backgroundPopup").css({ });

//$("#popupContact").load("/service-centre/auto_upload_file")


}

function upload_rev_pickup_file(){

        $("#popupContact").css({
                "position": "absolute",
                "top": 284,
                "left": 483,
                "width":275,
                "height":110,

        });
        $("#backgroundPopup").css({
                });

$("#popupContact").load("/service-centre/upload_rev_file")


}


function centerPopupAddShipment(pickup_id){
	$("#popupContact").css({
		"position": "absolute",
		"top": 132,
		"left": 483,
		"width":347,
		"height":540,

	});
	$("#backgroundPopup").css({
		});

$("#popupContact").load("/shipment/add_shipment/"+pickup_id+"/")


}

function centerPopupAWB(){
	$("#popupContact").css({
		"position": "absolute",
		"top": 284,
		"left": 483,
		"width":281,
		"height":228,

	});
	$("#backgroundPopup").css({
		});

$("#popupContact").load("/airwaybill/airwaybill_generate/")
}


function centerPopupEditShipment(shipment_id, pickup_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 483,
		"width":343,
		"height":528,

	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/shipment/edit_shipment/"+shipment_id+"/"+pickup_id+"/")
}

function centerPopupIncludeShipment(bag_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({});
    $("#popupContact").load("/service-centre/include_shipment/"+bag_id+"/")
}

function centerPopupDelinkShipment(bag_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/service-centre/delink_shipment/"+bag_id+"/")
}

function centerPopupGenerateManifest(bag_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/service-centre/generate_manifest/"+bag_id+"/")
}

function centerPopupIncludeBags(connection_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/service-centre/include_bags/"+connection_id+"/")
}

function centerPopupDelinkBags(connection_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/service-centre/delink_bags/"+connection_id+"/")
}

function centerPopupGenerateChallan(connection_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/service-centre/generate_challan/"+connection_id+"/")
}

function centerPopupGenerateChallan(connection_id){

	$("#popupContact").css({

		"position": "absolute",
		"top": 122,
		"left": 288,
		"width":719,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/service-centre/generate_challan/"+connection_id+"/")
}
function centerPopupIncludeConnection(runcode_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/service-centre/include_connection/"+runcode_id+"/")
}

function centerPopupDelinkConnection(runcode_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/service-centre/delink_connection/"+runcode_id+"/")
}


function centerPopupIncludeShipmentOutscan(outscan_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/delivery/include_shipment/"+outscan_id+"/")
}

function centerPopupDelinkShipmentOutscan(outscan_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/delivery/delink_shipment/"+outscan_id+"/")
}

function centerPopupIncludeDelinkShipmentRevOutscan(outscan_id, upd_type){

        $("#popupContact").css({
                "position": "absolute",
                "top": 122,
                "left": 204,
                "width":904,
                "height":400,
                "padding":0,


        });
        //only need force for IE6

        $("#backgroundPopup").css({
                });
$("#popupContact").load("/pickup/include_delink_shipment/"+outscan_id+"/"+upd_type+"/")
}

function centerPopupIncludeShipmentSal(sal_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/delivery/include_shipment_sal/"+sal_id+"/")
}

function centerPopupDelinkShipmentSal(sal_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/delivery/delink_shipment_sal/"+sal_id+"/")
}

function centerPopupSubCustomerBilling(shipper_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/billing/subcust_previous/"+shipper_id+"/")
}

function centerPopupDeliverySheet(outscan_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,

		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/delivery/delivery_sheet/"+outscan_id+"/")
}

function centerPopupRevDeliverySheet(outscan_id){

        $("#popupContact").css({
                "position": "absolute",
                "top": 122,
                "left": 204,
                "width":904,
                "height":400,

                "padding":0,


        });
        //only need force for IE6

        $("#backgroundPopup").css({
                });
$("#popupContact").load("/pickup/reverse_pickup_sheet/"+outscan_id+"/")
}


function centerPopupDeliverySheetSAL(sal_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/delivery/delivery_sheet_sal/"+sal_id+"/")
}


function centerPopupRemoveShipmentCODD(codd_id, awb) {
    console.log('inside center popup ..coddeposit-shipments-table');
	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 427,
		"width":365,
		"height":320,
		"padding":0,
	});
	//only need force for IE6
	$("#backgroundPopup").css({ });
    console.log('sending ajax request..');
    $.ajax({
        url: "/delivery/remove_shipment_codd/"+codd_id+"/",
        type: "POST",
        data: {'awb': awb},
        success: function(resp){
            console.log('ajax request received..', resp);
            if (resp.success){
                // remove the awb row and reset the counter
                $("#"+awb).parents('tr').remove();
                //$(".coddeposit-shipments-table tr").each(function(i, v){
                    //$(v).first().val(i+1);
                //});
            }
        }
    });
}

function centerPopupIncludeShipmentCODD(codd_id){
	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 427,
		"width":365,
		"height":320,
		"padding":0,
	});
	//only need force for IE6
	$("#backgroundPopup").css({ });
    $("#popupContact").load("/delivery/include_shipment_codd/"+codd_id+"/")
}

function centerPopupCashdeposit(codd_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 299,
		"width":604,
		"height":510,
		"padding":0,
	});
	//only need force for IE6
	$("#backgroundPopup").css({ });
    $("#popupContact").load("/delivery/cash_denomination/"+codd_id+"/")
}

function centerPopupDelinkShipmentCODD(codd_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/delivery/delink_shipment_codd/"+codd_id+"/")
}

function centerPopupDepositSheetCODD(codd_id){

	$("#popupContact").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":904,
		"height":400,
		"padding":0,


	});
	//only need force for IE6

	$("#backgroundPopup").css({
		});
$("#popupContact").load("/delivery/deposit_sheet/"+codd_id+"/")
}

function centerPopupIncludeRTOShipment(bag_id){
	$("#popupRTOShipment").css({
		"position": "absolute",
		"top": 122,
		"left": 204,
		"width":600,
		"height":400,
		"padding":0,
	});
	//only need force for IE6
	$("#backgroundPopup").css({});
    $("#popupRTOShipment").show();
    $("#rtosubmitFormAwbList").val('');
    $("#popupRTOShipment").load("/delivery/rto_shipments/")
}


//CONTROLLING EVENTS IN jQuery
$(document).ready(function(){

	//LOADING POPUP
	//Click the button event!
	$("#add_employee").click(function(){
		centerPopupEmployee();
		loadPopup();
	});

	$("#forgotpass").click(function(){

		centerPopupForgotPass();
		loadPopup();
	});


	$(".edit_employee").click(function(){
	    var employee_id = $(this).attr('employee_id');
		//centering with css
//      alert("hi");
		centerPopupEditEmployee(employee_id);
		//load popup
		loadPopup();
	});

	$("#add_pickup").click(function(){
		centerPopupPickup();
		loadPopup();
	});

        $(".upload_rev_pickup_file").click(function(){
                // var pickup_id = $(this).attr('pickup_id');

                 upload_rev_pickup_file();
                        loadPopup();
        });


	$("#AddRates").click(function(){
		// var pickup_id = $(this).attr('pickup_id');

		 add_rates();
		 loadPopup();
	});


	$(".upload_auto_pickup_file").click(function(){
		// var pickup_id = $(this).attr('pickup_id');

		 upload_auto_pickup_file();
			loadPopup();
	});


	$(".upload_file").click(function(){
	    var pickup_id = $(this).attr('pickup_id');
        centerPopupFile(pickup_id);
		loadPopup();
	});

	$(".include_shipment").live("click",function(){
	    var bag_id = $(this).attr("bag_id");
		centerPopupIncludeShipment(bag_id);
		loadPopup();
	});

	$(".gen_mnfst").live("click",function(){
	    var bag_id = $(this).attr("bag_id");
		centerPopupGenerateManifest(bag_id);
		loadPopup();
	});


$(".delink_shipment").live("click",function(){
	    var bag_id = $(this).attr("bag_id");
		centerPopupDelinkShipment(bag_id);
		loadPopup();
	});


   $(".add_shipment").click(function(){
        var pickup_id = $(this).attr('pickup_id');
		centerPopupAddShipment(pickup_id);
		loadPopup();
	});

	$("#generate_awb").click(function(){
		centerPopupAWB();
		loadPopup();
	});

	$(".edit_shipment").click(function(){

	    var shipment_id = $(this).attr('shipment_id');
	    var pickup_id = $(this).attr('pickup_id');
        centerPopupEditShipment(shipment_id, pickup_id);
		loadPopup();
	});

	$(".include_bags").live("click",function(){
	    var connection_id = $(this).attr("connection_id");
		centerPopupIncludeBags(connection_id);
		loadPopup();
	});

	$(".gen_challan").live("click",function(){
	    var connection_id = $(this).attr("connection_id");
		centerPopupGenerateChallan(connection_id);
		loadPopup();
	});


$(".delink_bags").live("click",function(){
	    var connection_id = $(this).attr("connection_id");
		centerPopupDelinkBags(connection_id);
		loadPopup();
	});

	$(".include_connection").live("click",function(){
	    var runcode_id = $(this).attr("runcode_id");
		centerPopupIncludeConnection(runcode_id);
		loadPopup();
	});

$(".delink_connection").live("click",function(){
	    var runcode_id = $(this).attr("runcode_id");
		centerPopupDelinkConnection(runcode_id);
		loadPopup();
	});



	$(".include_shipment_outscan").live("click",function(){
	    var outscan_id = $(this).attr("outscan_id");
		centerPopupIncludeShipmentOutscan(outscan_id);
		loadPopup();
	});

        $(".include_shipment_revoutscan").live("click",function(){
            var outscan_id = $(this).attr("outscan_id");
                centerPopupIncludeDelinkShipmentRevOutscan(outscan_id, 0);
                loadPopup();
        });



	$(".gen_dlvry").click(function(){
	    var outscan_id = $(this).attr("bag_id");
		centerPopupGenerateManifest(bag_id);
		loadPopup();
	});


$(".delink_shipment_revoutscan").live("click",function(){
	    var outscan_id = $(this).attr("outscan_id");
		centerPopupIncludeDelinkShipmentRevOutscan(outscan_id, 1);
		loadPopup();
	});

$(".delink_shipment_outscan").live("click",function(){
            var outscan_id = $(this).attr("outscan_id");
                centerPopupDelinkShipmentOutscan(outscan_id);
                loadPopup();
        });


$(".include_shipment_sal").live("click",function(){
	    var sal_id = $(this).attr("sal_id");
		centerPopupIncludeShipmentSal(sal_id);
		loadPopup();
	});

$(".delink_shipment_sal").live("click",function(){
	    var sal_id = $(this).attr("sal_id");
		centerPopupDelinkShipmentSal(sal_id);
		loadPopup();
	});

$(".subcust_billing").click(function(){
	    var shipper_id = $(this).attr("shipper_id");
		centerPopupSubCustomerBilling(shipper_id);
		loadPopup();
	});

	$(".del_sheet").live("click",function(){
	    var outscan_id = $(this).attr("outscan_id");
		$("#popupContact").html("");
		centerPopupDeliverySheet(outscan_id);
		loadPopup();
	});

        $(".revdel_sheet").live("click",function(){
            var outscan_id = $(this).attr("outscan_id");
                $("#popupContact").html("");
                centerPopupRevDeliverySheet(outscan_id);
                loadPopup();
        });

	$(".del_sheet_sal").live("click",function(){
	    var sal_id = $(this).attr("sal_id");
		centerPopupDeliverySheetSAL(sal_id);
		loadPopup();
	});

$(".include_shipment_codd").live("click",function(){
	    var codd_id = $(this).attr("codd_id");
		centerPopupIncludeShipmentCODD(codd_id);
		loadPopup();
});

$(".remove-shipment").live("click", function(){
	    var codd_id = $(this).attr("cod_id");
	    var awb = $(this).attr("id");
		centerPopupRemoveShipmentCODD(codd_id, awb);
		loadPopup();
});

$(".cash_deposits").live("click",function(){
	    var codd_id = $(this).attr("codd_id");
		centerPopupCashdeposit(codd_id);
		loadPopup();
	});

$(".delink_shipment_codd").live("click",function(){

	    var codd_id = $(this).attr("codd_id");
		centerPopupDelinkShipmentCODD(codd_id);
		loadPopup();
	});

$(".gen_deposit").live("click",function(){
	    var codd_id = $(this).attr("codd_id");
		centerPopupDepositSheetCODD(codd_id);
		loadPopup();
	});


	//CLOSING POPUP
	//Click the x event!
	$("#popupContactClose").click(function(){
		disablePopup();
	});

    $("#popupContactCl").click(function(){
		disablePopup();
	});


	//Click out event!
	$("#backgroundPopup").click(function(){
		disablePopup();
	});
	//Press Escape event!
	$(document).keypress(function(e){
		if(e.keyCode==27 && popupStatus==1){
			disablePopup();
		}
	});




        $(".edit_octroi").click(function(){
	    var employee_id = $(this).attr('octroi_id');
		//centering with css
//      alert("hi");
		centerOctroiDetails(employee_id);
		//load popup
		loadPopup();
	});

        $("#generate_bill").live("click",function(){
	      $("#popupContact").html($("#popupform").html());
	      $("#popupContact").css({
		"position": "absolute",
		"top": 172,
		"left": 483,
		"width":225,
		"height":285,

	      });
	      loadPopup();
	});

    $("input#awb_rto").click(function(e){
        if( $("#popupRTOShipment").children().length > 0){
            $("#popupRTOShipment").show();
        }else{
		    centerPopupIncludeRTOShipment();
		    loadPopup();
        }
    });

});


