function showDays() {
    var start = $('.date_from').datepicker('getDate');
    var end = $('.date_to').datepicker('getDate');
    if (!start || !end) return;
    var days = (end - start) / 1000 / 60 / 60 / 24;
    if(days >31){
    alert("Report cannot be generated for dates exceeding 31 days.");
    $(".date_from").val('');
    $(".date_to").val('');}
}
$(".date_to").datepicker({dateFormat: 'yy-mm-dd',onSelect: showDays,});
$(".date_from").datepicker({dateFormat: 'yy-mm-dd',onSelect: showDays,});
