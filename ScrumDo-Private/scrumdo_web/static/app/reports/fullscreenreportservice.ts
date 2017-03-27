/// <reference path="../_all.ts" />

module scrumdo{

    export class FullScreenReportService{
        public static $inject:Array<string> = [
            "$uibModal",
            "urlRewriter",
            "$rootScope"
        ];

        constructor(private $modal: ng.ui.bootstrap.IModalService,
                    private urlRewriter: URLRewriter,
                    private $rootScope: ng.IScope){

        }

        public openGraph(reportType: string, 
                        reportData, 
                        title = "", 
                        legends = [], 
                        chartType: number = null,
                        project: Project = null){
            var m = this.$modal.open({
                templateUrl: this.urlRewriter.rewriteAppUrl("reports/fullscreenreport.html"),
                controller: "FullScreenReportsController",
                controllerAs: 'ctrl',
                size: "fullscreen",
                backdrop: "static",
                keyboard: true,
                backdropClass: 'fullscreen-modal',
                openedClass: 'fullscreen-modal',
                windowClass: 'fullscreen-modal',
                resolve: {
                    reportData: () => reportData,
                    reportType: () => reportType,
                    legends: () => legends,
                    title: () => title,
                    chartType: () => chartType,
                    project: () => project
                }
            });

            m.rendered.then(() => {
                this.$rootScope.$broadcast("renderFullScreenReport", null);
            })
        }
    }


    export class FullScreenReportsController{
        public static $inject:Array<string> = [
            "organizationSlug",
            "$scope",
            "reportManager",
            "reportData",
            "reportType",
            "legends",
            "title",
            "chartType",
            "project"
        ];

        private showReport: boolean;

        constructor(private organizationSlug: string,
                    private $scope: ng.IScope,
                    private reportManager: ReportManager,
                    private reportData,
                    private reportType: string,
                    private legends,
                    private title: string,
                    private chartType: number,
                    private project: Project){

            this.showReport = false;
            this.$scope.$on("renderFullScreenReport", this.renderGraph);
        }

        private renderGraph = () => {
            setTimeout(() => {
                this.showReport = true;
                this.$scope.$apply();
            },300);
        }
    }
}
