/// <reference path="../_all.ts" />

module scrumdo{

    function shortIterationName(value:string, max:number){
        if (value.length <= max) return value;
        value = value.substr(0, max);
        return value + (' …');
    }

    class SentimentChart{

        public margin: { top: number, right: number, bottom: number, left: number };
        public svg;
        public scope;
        public attrs;
        public compile;
        public element: ng.IAugmentedJQuery;
        public root;
        public width: number;
        public height: number

        constructor(scope, element, attrs, compile){
            this.element = element;
            this.attrs = attrs;
            this.scope = scope;
            this.compile = compile;

            this.margin = { top: 20, right: 20, bottom: 90, left: 50 };
            this.svg = d3.select(this.element[0]).append("svg");
            this.svg.attr("class", "report").attr("width", "100%").attr("height", "100%");

            this.root = this.svg.append("g").attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")")
        }

        createLegend() {

        }

        renderNoData() {
            this.root.append("svg:text").text("No data").attr("class", "no-data").attr("x", this.width / 2).attr("y", this.height / 2);
        }

        render = () => {
            var chartType, data, ref;
            this.width = this.element.width() - this.margin.left - this.margin.right;
            this.height = Math.max(200, this.element.height() - this.margin.top - this.margin.bottom - 20);
            if (((ref = this.scope.reportData) != null ? ref.data : void 0) == null) {
                return;
            }
            data = this.scope.reportData.data;
            this.renderGraph(data);
        }

        renderGraph(data) {
            this.root.selectAll("*").remove();
            var x = d3.scale.ordinal().rangeRoundBands([0, this.width], .05),
                y = d3.scale.linear().range([this.height, 0]);

            var tickCount = Math.min(10, data.length);
            var xAxis = d3.svg.axis()
                .scale(x)
                .orient("bottom");

            var yAxis = d3.svg.axis()
                .scale(y)
                .orient("left")
                .ticks(tickCount)
                .tickFormat(d3.format("d"));
            
            x.domain(data.map((d:any) => { return d.iteration; }));
            y.domain([0, 1+d3.max(data, (d:any) => { return d.total; })]);

            var yGrid = d3.svg.axis()
                .scale(y)
                .innerTickSize(-this.width)
                .outerTickSize(0)
                .orient("left")
                .tickFormat("");

            var xGrid = d3.svg.axis()
                .scale(x)
                .innerTickSize(-this.height)
                .outerTickSize(0)
                .orient("bottom")
                .tickFormat("");

            this.root.append("g")
                .attr("class", "grid-line")
                .attr("pointer-events", "none")
                .call(yGrid);

            this.root.append("g")
                .attr("class", "grid-line")
                .attr("transform", "translate(0," + this.height + ")")
                .attr("pointer-events", "none")
                .call(xGrid);

            this.root.append("g")
                .attr("class", "y axis")
                .call(yAxis)
                .selectAll("text")
                .attr("dx", "-0.5em");

            this.root.append("text")
                .attr("text-anchor", "middle")
                .attr("x", this.width / 2)
                .attr("y", -5)
                .text("Iterations");

            this.root.append("text")
                .attr("text-anchor", "middle")
                .attr("y", -40)
                .attr("x", -this.height / 2)
                .attr("dy", ".75em")
                .attr("transform", "rotate(-90)")
                .text("Sentiments Avg.");

            this.root.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + this.height + ")")
                .call(xAxis)
                .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "-.8em")
                .attr("dy", "-.05em")
                .attr("transform", "rotate(-90)" )
                .call(this.wrap);

            this.root.selectAll("bar")
                .data(data)
                .enter().append("rect")
                .style("fill", "steelblue")
                .attr("x", (d) =>  x(d.iteration) )
                .attr("width", x.rangeBand())
                .attr("y", (d) => y(d.total) )
                .attr("height", (d) => this.height - y(d.total) );

        }

        wrap = (text) => {
            text.each(function() {
                var text = d3.select(this);
                var name = text.text();
                var tspan = text.text(null).append("tspan").attr("x", 0).attr("y", 0);
                tspan.text(shortIterationName(name, 15));
            });
        }
    }


    export var ReportSentiment = function($compile, storyEditor) {
        return {
            restrict: 'EA',
            scope: {
                project: "=",
                reportData: "="
            },
            link: function(scope, element, attrs) {
                var report;
                trace("ReportLead::link");
                scope.$on('reRenderReportGraph', () => {
                    angular.element(element).empty();
                    setTimeout(() => {
                        report = new SentimentChart(scope, element, attrs, $compile);
                        report.render();    
                    },50);
                })
                report = new SentimentChart(scope, element, attrs, $compile);
                report.render();
                return scope.$watchGroup(["reportData", "project"], report.render);
            }
        };
    };
}