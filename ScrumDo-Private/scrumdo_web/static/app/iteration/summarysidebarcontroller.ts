/// <reference path="../_all.ts" />

module scrumdo{

    interface thisScope extends ng.IScope{
        iteration: Iteration;
        project: Project;
    }

    export class IterationSummarySidebarController{

        public static $inject: Array<string> = [
            "$scope",
            "organizationSlug",
            "projectSlug",
            "iterationManager",
            "reportManager",
            "userService",
            "fullScreenReportService"
        ]

        private stats;
        private cfdData;
        private cfdDataCache;
        private sentimentTeam;
        private editingMission: boolean = false;
        private missionCopy: string;

        constructor(private $scope: thisScope,
                    private organizationSlug: string,
                    private projectSlug: string,
                    private iterationManager: IterationManager,
                    private reportManager: ReportManager,
                    private userService: UserService,
                    private fullScreenReportService: FullScreenReportService){

            this.loadStats();

            this.sentimentTeam ={slug:this.$scope.project.slug, 
                                name:this.$scope.project.name, 
                                icon: this.$scope.project['icon'], 
                                color: this.$scope.project['color']};
            setTimeout(() => {
                this.drawConnectingLines();
            }, 100);

        }

        loadStats = () =>{
            this.iterationManager.loadStatsForIteration(this.organizationSlug, 
                                                        this.$scope.project.slug, 
                                                        this.$scope.iteration.id).then((r) => {
               this.stats = r;
            });

            var reportOptions = {
                cfd_show_backlog: false,
                detail: false,
                enddate: moment().format("YYYY-MM-DD"),
                startdate: moment().subtract(1, 'months').format("YYYY-MM-DD"),
                interval: -1,
                iteration: this.$scope.iteration.id,
                cached:true
            }
            
            this.reportManager.loadCFD(this.organizationSlug, this.$scope.project.slug, -1, reportOptions).then( (result:any) => {
                this.cfdData = result.data.data;
            });
        }

        editMission(){
            this.missionCopy = this.$scope.iteration.vision;
            this.editingMission = true;
        }

        cancelEditMission(){
            this.$scope.iteration.vision = this.missionCopy;
            this.editingMission = false;
        }

        updateMission(){
            this.iterationManager.saveIteration(this.organizationSlug, 
                                                this.projectSlug, 
                                                this.$scope.iteration).then((itr: Iteration) => {
                this.$scope.iteration.vision = this.missionCopy = itr.vision;
                this.editingMission = false;
            })
        }

        private drawConnectingLines = () => {
            let data = [];
            if(this.$scope.$root == null) return;
            delete this.$scope.$root['svgConnectorsData']
            _.forEach(this.$scope.iteration.increment, (inc: IterationIncrement) => {
                data.push({ start: `#iteration-box-${inc.id}`, 
                            end: `#iteration-box-${this.$scope.iteration.id}`, 
                            strokeWidth: 1, 
                            orientation: 'curve1',
                            strokeDasharray: 5});
            });
            
            this.$scope.$root['svgConnectorsData'] = data;
            this.$scope.$broadcast("drawSvgConnectors", null);
        }

        private zoomCfd(){
            this.fullScreenReportService.openGraph('cfd', this.cfdData, "CFD");
        }
    }
}
