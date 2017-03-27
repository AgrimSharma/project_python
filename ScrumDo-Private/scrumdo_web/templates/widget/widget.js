{% load projects_tags %}

function renderWidget() {
    document.write("<div id='scrumdo_burndown_{{widget.iteration.id}}'>");
    document.write("<img src='{{  widget.iteration|google_chart_url }}' />")
    document.write("</div>");
    
}




renderWidget()
