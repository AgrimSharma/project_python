/// <reference path="../_all.ts" />

module scrumdo{

    interface thisScope extends ng.IScope{
        project: Project;
    }

    export class SummarySidebarController{

        public static $inject: Array<string> = [
            "$scope",
            "organizationSlug",
            "projectSlug",
            "reportManager",
            "projectManager",
            "portfolioWindowService",
            "iterationManager",
            "projectDatastore",
            "fullScreenReportService"
        ];

        private portfolio: Portfolio;
        private project: Project;
        private workflow: Workflow;
        private backlogId: number;
        private backlogStats;
        private dependencyData: Array<any>;
        private teamMembers: Array<User>;
        private loadingReport: boolean;
        private reportsData: any;
        private currentReport: string;
        private currentReportData: any;
        private loadingBacklogReport: boolean;
        private canAdmin: boolean;
        private canStaff: boolean;
        private teamIvitationBox: boolean = false;
        private editingMission: boolean = false;
        private missionCopy: string;

        constructor(private $scope: thisScope,
                    private organizationSlug: string,
                    private projectSlug: string,
                    private reportManager: ReportManager,
                    private projectManager: ProjectManager,
                    private portfolioWindowService: PortfolioWindowService,
                    private iterationManager: IterationManager,
                    private projectDatastore: ProjectDatastore,
                    private fullScreenReportService: FullScreenReportService){
            
            this.reportsData = {};
            this.loadingReport = false;

            this.portfolio = cleanPortfolioLevels(this.projectDatastore.portfolio);
            this.project = this.$scope.project;
            this.workflow = this.projectDatastore.workflows[0];
            this.backlogId = this.project.kanban_iterations.backlog;
            this.canAdmin = this.projectDatastore.canAdmin();
            this.canStaff = this.projectDatastore.isOrgStaff();

            this.$scope.$on("projectMembersUpdated", this.onProjectMembersUpdated);

            this.loadDependencies();
            this.loadTeamMembers();
            this.loadReportsData('backlog');
            this.loadBacklogStats();
        }

        private onProjectMembersUpdated = () => {
            this.loadTeamMembers();
        }

        private loadBacklogStats(){
            this.iterationManager.loadStatsForIteration(this.organizationSlug, this.projectSlug, this.backlogId).then((data) => {
                this.backlogStats = data;
            })
        }

        private loadDependencies(){
            this.projectManager.loadDependency(this.projectSlug).then((data) => {
                this.dependencyData = data;
                setTimeout(() => {
                    this.drawConnectingLines();
                }, 100);
            })
        }

        private loadTeamMembers(){
            this.projectManager.loadTeamMembers(this.projectSlug).then((data) => {
                this.teamMembers = data;
            });
        }

        private showPortfolioWindow(){
            for(let level of this.portfolio.levels){
                for(let project of level.projects) {
                    project.color = '#' + colorToHex(<number>project.color);
                }
            }
            this.portfolioWindowService.configure(this.portfolio, true, this.project.slug).then(() => {
                this.projectDatastore.reloadPortfolio().then(() => {
                    this.portfolio = cleanPortfolioLevels(this.projectDatastore.portfolio);
                    this.projectDatastore.reloadCurrentIncrement();
                    this.drawConnectingLines();
                });
                this.projectDatastore.reloadCurrentProject().then(() => {
                    this.drawConnectingLines();
                })
                this.$scope.$root.$broadcast("projectSettingsUpdated", null);
            });
        }

        editMission(){
            this.missionCopy = this.project.vision
            this.editingMission = true;
        }

        cancelEditMission(){
            this.project.vision = this.missionCopy;
            this.editingMission = false;
        }

        updateMission(){
            this.projectManager.saveProject(this.project).then((project: Project) => {
                this.project.vision = this.missionCopy = project.vision;
                this.editingMission = false;
            })
        }

        private drawConnectingLines = () => {
            let data = [];
            if(this.$scope.$root == null) return;
            delete this.$scope.$root['svgConnectorsData']
            _.forEach(this.portfolio.levels, (level: PortfolioLevel) => {
                _.forEach(level.projects, (project: PortfolioProjectStub) => {
                    _.forEach(project.parents, (parent:any) => {
                        if(this.dependencyData!=null && this.project.id != project.id){
                            var r = 0,
                                s = 1;
                        }else{
                            // draw parent to child dependencies lines 
                            var maxDependency = this.getMaxDependency(this.dependencyData),
                                dependency = this.dependencyData['parent'][parent.id],
                                r = (((dependency) * (4)) / (maxDependency)),
                                s = r > 0 && isFinite(r) ? r : 1;
                        }
                        data.push({ start: `#project-box-${parent.id}`, 
                                    end: `#project-box-${project.id}`, 
                                    strokeWidth: s, 
                                    orientation: 'curve1',
                                    strokeDasharray: r>0?0:5});
                    });

                    if(this.dependencyData!=null && this.project.id == project.id){
                        var maxDependency = this.getMaxDependency(this.dependencyData, 'sibling');
                        for(var k in this.dependencyData['sibling']){
                            var dependency =  this.dependencyData['sibling'][k],
                                r = (((dependency) * (3)) / (maxDependency)),
                                s = r > 0 && isFinite(r) ? r : 1;
                            if(r>0){
                                data.push({ start: `#project-box-end-${k}`, 
                                            end: `#project-box-end-${project.id}`, 
                                            strokeWidth: s, 
                                            strokeDasharray: r>0?0:5,
                                            orientation: 'curve',
                                            stroke: '#f7b5a0'  });
                            }
                        }
                    }
                });
            });
            
            this.$scope.$root['svgConnectorsData'] = data;
            this.$scope.$broadcast("drawSvgConnectors", null);
        }

        private getMaxDependency(data, type='parent'){
            var n: number = 0;
            var v = _.max(data[type] , (o:number) => o );
            n = n > v ? n : v;
            return n;
        }

        private loadReportsData(reportType: string = 'blocker'){
            this.loadingReport = true;
            this.currentReport = reportType;
            let startDate = moment().subtract(2, 'months').format('YYYY-MM-DD');
            let endDate = moment().format('YYYY-MM-DD');
            if(this.reportsData[reportType] != null){
                this.loadingReport = false;
                this.currentReportData = this.reportsData[reportType];
                this.$scope.$root.$broadcast("reRenderReportGraph", {});
                return;
            }
            switch (reportType){
                case 'backlog':
                    this.loadingBacklogReport = true;
                    this.reportManager.loadBacklogCFD(this.organizationSlug, this.projectSlug, {cached:true, startdate: startDate, enddate:endDate})
                        .then((result:any) => {
                            this.loadingReport = false;
                            this.loadingBacklogReport = false;
                            this.reportsData[reportType] = result.data.data;
                            this.currentReportData = this.reportsData[reportType];
                    });
                break;
                case 'sentiment':
                    this.reportManager.loadProjectSentimets(this.organizationSlug, this.projectSlug)
                        .then((result) => {
                            this.loadingReport = false;
                            this.reportsData[reportType] = result;
                            this.currentReportData = this.reportsData[reportType];
                    });
                break;

                case 'blocker':
                    this.reportManager.loadBlockersFreq(this.organizationSlug, this.projectSlug, {cached:true, startdate: startDate, enddate:endDate})
                        .then((result) => {
                            this.loadingReport = false;
                            this.reportsData[reportType] = result;
                            this.currentReportData = this.reportsData[reportType];
                    });
                break;

                case 'aging':
                    if(this.workflow == null || this.workflow.steps.length ==0){
                        this.reportsData[reportType] = null;
                    }else{
                        var steps = this.workflow.steps;
                        var option = {agingData: 'step', agingType: 1, detail: false, yaxis:1, agingSteps: ''}
                        option['agingSteps'] = (steps.map((step) => step && step.id || null)).join(",");
                        option['agingTags'] = '';
                        option['cached'] = true;
                        this.reportManager.loadAging(this.organizationSlug, this.projectSlug, this.workflow.id, option)
                            .then((result:any) => {
                                this.loadingReport = false;
                                this.reportsData[reportType] = result;
                                this.currentReportData = this.reportsData[reportType];
                        });
                    }
                break;

                case 'burndown':
                    this.reportManager.loadProjectBurn(this.projectSlug).then((result) => {
                        this.loadingReport = false;
                        this.reportsData[reportType] = result;
                        this.currentReportData = this.reportsData[reportType];
                    });
                break;

                case 'cfd':
                    if(this.workflow == null || this.workflow.steps.length ==0){
                        this.reportsData[reportType] = null;
                    }else{
                        this.reportManager.loadCFD(this.organizationSlug, this.projectSlug, this.workflow.id, {cached:true, startdate: startDate, enddate:endDate})
                            .then((result: any) => {
                                this.loadingReport = false;
                                this.reportsData[reportType] = result.data.data;
                                this.currentReportData = this.reportsData[reportType];
                        });
                    }
                break;

                case 'lead':
                    if(this.workflow == null || this.workflow.steps.length ==0){
                        this.reportsData[reportType] = {data: [{column:0 , count:0, label: "0"}], detail: [], mean: 0, median: 0};
                    }else{
                        this.reportManager.loadLead(this.organizationSlug, this.projectSlug, this.workflow.id, {cached:true})
                            .then((result: any) => {
                                this.loadingReport = false;
                                this.reportsData[reportType] = result.data;
                                this.currentReportData = this.reportsData[reportType];
                        })
                    }
                break;
            }
        }

        private zoomReport(type: string = null, data = null, stitle: string = null){
            var reportType: string,
                reportData: any,
                chartType: number = null,
                legends: Array<any> = [],
                title: string,
                project: Project = this.project;
            
            reportType = type == null ? this.currentReport : type;
            reportData = data == null ? this.currentReportData : data;

            if(reportType == 'burndown' || reportType == 'aging'){
                chartType = 1;
            }

            switch (reportType) {
                case 'cfd':
                    title = 'CFD'
                break;
                case 'lead':
                    title = 'Lead Time'
                break;
                case 'aging':
                    title = 'Aging'
                break;
                case 'burndown':
                    title = 'Burndown'
                break;
                case 'sentiment':
                    title = 'Sentiments'
                break;
                case 'blocker':
                    title = 'Blockers'
                break;
            }
            
            title = `${this.project.name} ${title}`;

            title = stitle == null ? title : stitle;

            this.fullScreenReportService.openGraph(reportType, 
                                        reportData, 
                                        title, 
                                        legends, 
                                        chartType, 
                                        project);
            
        }
    }
}