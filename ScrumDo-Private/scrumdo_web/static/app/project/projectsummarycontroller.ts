/// <reference path="../_all.ts" />

module scrumdo{

    export class WorkspaceSummaryController{

        public static $inject:Array<string> = [
            "$scope",
            "projectSlug",
            "organizationSlug",
            "iterationManager",
            "iterationWindowService",
            "projectData",
            "projectSearchManager",
            "realtimeService",
            "$localStorage",
            "projectManager"
        ];

        private allIterations: Array<Iteration>;
        private stats: Array<any>;
        private iterationView: string;
        private iterationTime: number;
        private trashBin: Iteration;
        private backlog: Iteration;
        private archive: Iteration;
        private showArchived: boolean;
        private timePeriodName: string;
        private portfolio: Portfolio;
        private sortOrder: string;
        private storage;
        private sidebar: boolean = true;

        constructor(private $scope: ng.IScope,
                    private projectSlug: string,
                    private organizationSlug: string,
                    private iterationManager: IterationManager,
                    private iterationWindowService: IterationWindowService,
                    private projectData: ProjectDatastore,
                    private projectSearchManager: ProjectSearchManager,
                    private realtimeService: RealtimeService,
                    private localStorage,
                    private projectManager: ProjectManager){
            

            this.initData();
            this.$scope.$on("iterationWindowClosed", this.onIterationUpdated);
        }

        initData(){
            this.projectData.clearCurrentIteration();
            this.portfolio = this.projectData.portfolio;
            this.showArchived = false;
            this.iterationView = 'list';
            this.iterationTime = 4;
            this.storage = this.localStorage.$default({});
            this.initStorage();
            this.loadKStats();
            this.loadIterations();

            if(this.$scope.$root['safeTerms'] == null){
                this.timePeriodName = "Iteration";
            }else{
                this.timePeriodName = this.$scope.$root['safeTerms'].current.time_period_name;
            }
        }

        private loadKStats(){
            this.projectManager.loadKanbanStats(this.projectSlug).then((stats) => {
                this.projectData.currentProject.stats = stats;
                this.stats = getProjectStatsWithLabel(this.projectData.currentProject);
            });
        }

        private initStorage(){
            if (this.storage[this.projectData.currentProject.slug] != null) {
                let pStorage = this.storage[this.projectData.currentProject.slug];
                this.sortOrder = pStorage.iterationSortOrder != null ? pStorage.iterationSortOrder : 'system';   
                this.sidebar = pStorage.summarySidebar != null ? pStorage.summarySidebar : true; 
            }else{
                this.storage[this.projectData.currentProject.slug] = {};
                this.sortOrder = 'system';
            }
        }

        private loadIterations = () => {
            this.iterationManager.loadIterations(this.organizationSlug, this.projectSlug).then((iterations: Array<Iteration>) => {
                this.allIterations = iterations;
                this.allIterations = this.allIterations.sort(this.iterationSortOrder);
                this.trashBin = _.findWhere(iterations, {iteration_type:3});
                this.backlog = _.findWhere(iterations, {iteration_type:0});
                this.archive = _.findWhere(iterations, {iteration_type:2});
            });
        }

        private setIterationView(view: string){
            this.iterationView = view;
        }

        private setIterationTime(type: number){
            this.iterationTime = type;
        }

        private newIteration($event: MouseEvent){
            $event.preventDefault();
            $event.stopPropagation();
            this.iterationWindowService.createIteration(this.organizationSlug, this.projectSlug, null, this.timePeriodName);
        }

        private onIterationUpdated = (event, data) => {
            this.projectData.reloadIterations().then(this.loadIterations);
        }

        private openProjectSearch(){
            this.projectSearchManager.projectSearchPopup();
        }

        private toggleSidebar(){
            this.sidebar = !this.sidebar;
            let pStorage = this.storage[this.projectData.currentProject.slug];
            pStorage.summarySidebar = this.sidebar;
        }

        public filterIteration = (i: Iteration) => {
            var t = moment(),
                s = i.start_date != null ? moment(i.start_date): null,
                e = i.end_date != null ? moment(i.end_date) : null;
            
            switch (this.iterationTime) {
                // all iterations
                case 4:
                    return true
                // recent iterations
                case 0:
                    if(s == null || e == null) return true;
                    if( (s < t && e > t)){
                        return true;
                    }
                    if( s > t) return true;
                    var d = this._getDaysDiff(s, e);
                    if(d <= 1 &&  s < t) return true;
                break;
                // last 2 months
                case 1:
                    if(s == null || e == null || s > t) return false;
                    var d = this._getDaysDiff(s, e);
                    if(d <= 60 && d > 1 && e < t) return true;
                break;
                // last 6 months
                case 2:
                    if(s == null || e == null || s > t) return false;
                    var d = this._getDaysDiff(s, e);
                    if(d <= 180 && d > 30 && e < t) return true;
                break;
                // other old
                case 3:
                    if(s == null || e == null || s > t) return false;
                    var d = this._getDaysDiff(s, e);
                    if(d > 180 && e < t) return true;
                break;
            }
            return false;
        }

        private _getDaysDiff(s, e){
            var t = moment();
            // past Iteration
            if(e < t){
                var d = moment.duration(t.diff(e));
                var months = d.asDays();
                return months;
            }else{
                // upcoming iteration 
                var d = moment.duration(t.diff(s));
                var months = d.asDays();
                return months;
            }
        }


        public iterationSortOrder(a, b) {
            if (a.hidden && !b.hidden) {
                return 1;
            }
            if (b.hidden && !a.hidden) {
                return -1;
            }

            if ((a.end_date == null) && (b.end_date != null)) {
                return -1;
            }

            if ((b.end_date == null) && (a.end_date != null)) {
                return 1;
            }

            if ((a.end_date == null) && (b.end_date == null)) {
                // Both are null, compare by name
                if (a.name > b.name) {
                    return -1;
                } else {
                    return 1;
                }
            }

            if (a.end_date > b.end_date) {
                return -1;
            } else if (a.end_date < b.end_date) {
                return 1;
            }
            return 0;
        }

        private updateSortOrder(order: string){
            this.sortOrder = order;
            let pStorage = this.storage[this.projectData.currentProject.slug];
            pStorage.iterationSortOrder = order;
        }

        private clearOrder(){
            this.sortOrder = 'system';
            let pStorage = this.storage[this.projectData.currentProject.slug];
            if(pStorage.iterationSortOrder != null){
                delete pStorage.iterationSortOrder
            }
        }

        private iterationOrderBy = (iteration: Iteration) : any => {
            if(this.sortOrder != 'system'){
                switch (this.sortOrder) {
                    case 'start_date':
                        return iteration.start_date;
                    break;
                    case 'end_date':
                        return iteration.end_date;
                    break;
                    case 'duration':
                        var now = moment(iteration.start_date),
                            end = moment(iteration.end_date),
                            duration = moment.duration(now.diff(end));
                        return duration
                    break;
                    case 'total_cards':
                        return - iteration.story_count;
                    break;
                }
            }
        }

    }
}