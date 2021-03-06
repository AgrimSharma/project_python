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
			"opacity": "0.8"
		});
		$("#backgroundPopup").fadeIn("slow");
		$("#popupContact").fadeIn("slow");
		popupStatus = 1;
	}
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

//centering popup
function centerPopupCust(){
	//request data for centering
    //centering
	$("#popupContact").css({
		"position": "absolute",
		"width":500,
	});
	//only need force for IE6
	
	var windowWidth = document.documentElement.clientWidth;
	var windowHeight = document.documentElement.clientHeight;
	var popupHeight = $("#popupContact").height();
	var popupWidth = $("#popupContact").width();
	//centering
	$("#popupContact").css({
		"position": "fixed",
		"top":  '80px',//windowHeight/2-popupHeight/2,
		"left": windowWidth/2-popupWidth/2,
		"height":'auto',
	});
	//only need force for IE6
	
	$("#backgroundPopup").css({
		"height": windowHeight
	});
	
	$("#backgroundPopup").css({
	});
	
    $("#popupContact").load("/location/add/") 
    
   
	
}




function centerPopupLocation(url){
	//request data for centering
    //centering
	
	$("#popupContact").css({
		"position": "absolute",
		"width":500,
	});
	//only need force for IE6
	
	var windowWidth = document.documentElement.clientWidth;
	var windowHeight = document.documentElement.clientHeight;
	var popupHeight = $("#popupContact").height();
	var popupWidth = $("#popupContact").width();
	//centering
	$("#popupContact").css({
		"position": "fixed",
		"top":  '80px',//windowHeight/2-popupHeight/2,
		"left": windowWidth/2-popupWidth/2,
		"height":'330px',
	});
	//only need force for IE6
	
	$("#backgroundPopup").css({
		"height": windowHeight
	});
	
	
	
	
	$("#backgroundPopup").css({
		});
$("#popupContact").load(url) 
}






//CONTROLLING EVENTS IN jQuery
$(document).ready(function(){

	//alert("hiiii");

	//LOADING POPUP
	$("#AddLocation").click(function(){
		//centering with css
		centerPopupCust();
		//load popup
		loadPopup();
	});
				
	//CLOSING POPUP
	$("#popupContactClose").click(function(){
		disablePopup();
	});

	
	$(".AddLocation2").click(function(){
	       var location = $(this).attr('location');
			centerPopupLocation(location);
			//load popup
			loadPopup();
		});
	
	$("#edit_customer").click(function(){
	       var customer_id = $(this).attr('cust_id');
			//centering with css
//	      alert("hi");
			centerPopupEditCustomer(customer_id);
			//load popup
			loadPopup();
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

});