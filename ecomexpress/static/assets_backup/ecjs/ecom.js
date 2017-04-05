$("#awb_scan").focus();

$("#shipment_count").submit(function(){
  //alert("test");
  return false;
});

$(".awb").change(function(){

    var awb=$("#awb_scan").val();
    var counter = $('.table > tbody').children('tr:last').attr('counter');
    if (!counter) {
       counter=0;
    }
    counter=parseInt(counter)+1;
    var datastring = "awb="+awb+"&comp="+0+"&counter="+counter;
    $.ajax({
        type:"POST",
        url: "/service-centre/field_pickup_operation/{{pid}}/",
        data: datastring,
        success: function(resp){
        if (resp==1) {
            alert("Already exists");
        }
        else if (resp==2) {
            alert("Incorrect Airwaybill Number");
        }
        
        else{
            $(".table > tbody").append(resp);
             if(resp.match(/Mismatch/g)){
                mis_count = parseInt($("#mismatch_count").val()) + 1;
                $("#mismatch_count").val(mis_count);
             }
             if(resp.match(/Verified/g)){
                verified_count = parseInt($("#verified_count").val()) + 1;
                $("#verified_count").val(verified_count);
             }
            }
        }
    });
   
    $("#awb_scan").val("");
    $("#awb_scan").focus();
    return false;

});

