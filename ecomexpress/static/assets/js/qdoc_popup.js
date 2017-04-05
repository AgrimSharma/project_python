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
function centerPopup(){

	//request data for centering
	//centering
	$("#popupContact").css({
		"position": "absolute",
		"top": 126,
		"left": 238,
		"width":483,
		"height":700,
	});
	//only need force for IE6
	
	$("#backgroundPopup").css({
		
	});
    $("#popupContact").load("add/") 	
}


function centerPopupedit(question_batchid){

	//request data for centering
	//centering
	$("#popupContact").css({
		"position": "absolute",
		"top": 126,
		"left": 238,
		"width":483,
		"height":646,
	});
	//only need force for IE6
	
	$("#backgroundPopup").css({
		
	});
    $("#popupContact").load("/customer/add/") 	
}


function centerPopupview(question_batchid){
  //request data for centering
	//centering
	$("#popupContact").css({
		"position": "absolute",
		"top": 126,
		"left": 238,
		"width":483,
		"height":646,
	});
	//only need force for IE6
	
	$("#backgroundPopup").css({
		"height":"100%",
	});
    $("#popupContact").load("/customer/add/") 	
}


function centerPopupupl(question_batchid){
    //request data for centering
	//centering
	$("#popupContact").css({
		"position": "absolute",
		"top": 193,
		"left": 408,
		"width":340,
		"height":85,
	});
	//only need force for IE6
	
	$("#backgroundPopup").css({
		
	});
	
	//alert(question_batchid)
    $("#popupContact").load("/qdoc_upload/"+question_batchid+"/file_upload_stage3") 	
}

function centerPopupiq(question_id){

	//request data for centering
	//centering
	$("#popupContact").css({
		"position": "absolute",
		"top": 193,
		"left": 408,
		"width":340,
		"height":85,
	});
	//only need force for IE6
	
	$("#backgroundPopup").css({
		
	});
	//alert(question_id)
    $("#popupContact").load("/qdoc_upload/"+question_id+"/improve_ques") 	
}



//CONTROLLING EVENTS IN jQuery
$(document).ready(function(){
	
	//LOADING POPUP
	//Click the button event!
	$("#add_doc").click(function(){
	    //alert("hi")
	    //centering with css
		centerPopup();
		//load popup
		loadPopup();
	});

$(".edit").click(function(){

    var question_batchid = $(this).attr('question_batchid');
	  //  alert("hi")
	    //centering with css
		centerPopupedit(question_batchid);
		//load popup
		loadPopup();
	});
	
$(".view").click(function(){
    var question_batchid = $(this).attr('question_batchid');
	  //  alert("hi")
	    //centering with css
		centerPopupview(question_batchid);
		//load popup
		loadPopup();
	});




$("#edit_stg5").click(function(){
    var question_batchid = $(this).attr('question_batchid');
	  //  alert("hi")
	    //centering with css
		centerPopupedit(question_batchid);
		//load popup
		loadPopup();
	});

$("#edit_stg6").click(function(){
    var question_batchid = $(this).attr('question_batchid');
	  //  alert("hi")
	    //centering with css
		centerPopupedit(question_batchid);
		//load popup
		loadPopup();
	});


    $("#upl_stg3").click(function(){
	    var question_batchid = $(this).attr('question_batchid');
       // alert(question_batchid)
	    
	    //centering with css
		centerPopupupl(question_batchid);
		//load popup
		loadPopup();
	});


    $(".upl_stg7").click(function(){
        var question_batchid = $(this).attr('question_batchid');
       // alert(question_batchid)
	    
	    //centering with css
		centerPopupupl(question_batchid);
		//load popup
		loadPopup();
	});
	

    $("#improve_ques").click(function(){
     //   alert("hi")    
	    var question_id = $(this).attr('question_id');
       // alert(question_id)
	    
	    //centering with css
		centerPopupiq(question_id);
		//load popup
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

});