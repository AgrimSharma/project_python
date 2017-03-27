/// <reference path='../_all.ts' />

module scrumdo {

    export class DependencyColumn implements CardGridColumn {
        // public iteration:Iteration;
        // public get title(): string {
        //     return this.iteration.name;
        // }
        id: string;
        public title: string;
        public visible: boolean;
        schedule: ProgramIncrementSchedule;
    }

    export class DependencyColumnForCurrent implements CardGridColumn {
        id: string;
        public title: string;
        public visible: boolean;
        project: Project;
        iteration: Iteration;
    }

    export class DependencyRow implements CardGridRow {
        // public team:Project;
        // public get title(): string {
        //     return this.team.name;
        // }
        // public visible: boolean;
        id: string;
        public title: string;
        public visible: boolean;
        public canWrite: boolean;
    
    }

    // ------------------------------------------------------------------------------------------------------------
    export class DependenciesController {
        public static $inject:Array<string> = [
            "projectData",
            "projectManager",
            "epicManager",
            "storyManager",
            "dependencyManager",
            "organizationSlug",
            "$q",
            "$scope",
            "realtimeService",
            "userService",
            "storyEditor",
            "$localStorage",
            "iterationManager",
            "urlRewriter",
            "$filter",
            "$state"
        ];

        public noData;
        public columns:Array<DependencyColumn | DependencyColumnForCurrent> = [];
        public rows:Array<DependencyRow> = [];
        public dependencies:Array<Array<number>>;
        private teamsSlug:Array<string>;
        public renderMode: string = 'current';
        public showSiblings: boolean = true;
        private storage;
        private filters: any = {};
        private searchQuery: string = "";
        private filterTemplate: string;
        private showRefresh: boolean;
        private hideIndependent: boolean = false;

        // Map from project:scheduleid to an iterationid in that project
        public iterationIds = {};

        constructor(public project:ProjectDatastore,
                    private projectManager:ProjectManager,
                    private epicManger:EpicManager,
                    private storyManager:StoryManager,
                    private dependencyManager:DependencyManager,
                    private organizationSlug:string,
                    private $q:ng.IQService,
                    private $scope:ng.IScope,
                    private realtimeService: RealtimeService,
                    private userService: UserService,
                    private storyEditor: StoryEditor,
                    private localStorage,
                    private iterationManager: IterationManager,
                    private urlRewriter: URLRewriter,
                    private $filter,
                    private $state:ng.ui.IStateService) {
            
            this.initStorageData();
            this.setupRowsColumns();
            this.initFilters();
            $scope.$root['kiosk'] = new Kiosk();
            $scope.$on("$destroy", this.onDestroy);
            $scope.$on("incrementChanged", this.setupRowsColumns);
            $scope.$on("cardGridDrag", this.onCardGridDrag)
            $scope.$on("dependencyChanged", this.setupDependencies)
            $scope.$on("$destroy", this.onDestroy);
            $scope.$on('newCard', this.onNewCard);
            $scope.$on('onChildIterationUpdated', this.onChildIterationUpdated);
            this.subscribeTeamProjects();
            $scope["timePeriodName"] = $scope.$root['safeTerms'] != null ? $scope.$root['safeTerms'].current.time_period_name : "Iteration";
            $scope["childTimePeriodName"] = $scope.$root['safeTerms'] != null ? $scope.$root['safeTerms'].children.time_period_name : "Iteration";

        }

        onChildIterationUpdated = () => {
            this.project.reloadCurrentIncrement();
            this.showRefresh = true;
        }

        reloadPage(){
            this.$state.reload();
        }

        initStorageData(){
            this.storage = this.localStorage.$default({});
            let slug = this.project.currentProject.slug;
            if (this.storage[slug] == null) {
                this.storage[slug] = { };
            }
            if (this.storage[slug].dependencyMode == null) {
                this.storage[slug].dependencyMode = 'current';
            }else{
                this.renderMode = this.storage[slug].dependencyMode;
            }
        }

        private subscribeTeamProjects(){
            if(this.renderMode == 'downstream'){
                if(this.project.currentIncrement.schedule != null){
                    this.teamsSlug = _.reduce(this.project.getIncrementTeams(), (list, iteration:IncrementIteration)=>{
                        return list.concat(iteration.project_slug);
                    }, []);
                    this.realtimeService.subscribeProject(this.teamsSlug);
                }
            }else{
                this.teamsSlug = [];
                this.realtimeService.subscribeProject(this.teamsSlug);
            }
        }

         private onDestroy = () => {
            this.$scope.$root['kiosk'] = null;
            this.realtimeService.unSubscribeProject(this.teamsSlug);
        }

        onNewCard = (event, {row, column}) => {
            if(this.renderMode == 'downstream'){
                let schedule:ProgramIncrementSchedule = column.schedule;
                let iterationId = _.findWhere(schedule.iterations,{project_slug:row.id}).iteration_id;
                this.projectManager.loadProject(this.organizationSlug, row.id)
                                    .then((teamProject)=> {
                                        this.storyEditor.createStory(teamProject, {
                                            iteration_id:iterationId,
                                            release:row.release
                                        });
                                    });

            }else{
                this.projectManager.loadProject(this.organizationSlug, column['project'].slug)
                                    .then((project)=> {
                                        this.storyEditor.createStory(project, {
                                            iteration_id: column['iteration'].id
                                        });
                                    });
            }
        }
        
        onCardGridDrag = (event, data) => {
            let row:DependencyRow = data.row;
            let column:DependencyColumn = data.column;
            let storyId = data.storyId;
            let story = this.storyManager.getStory(storyId);

            trace("DependenciesController::onCardGridDrag");
            if(this.renderMode == 'downstream'){
                let schedule:ProgramIncrementSchedule = column.schedule;
                let iter:IncrementIteration = _.findWhere(schedule.iterations,{project_slug:row.id})

                let projectSlug = row.id;
                let iterationId = iter.iteration_id;
                
                this.storyManager.moveToProject(story, projectSlug, iterationId);
            }else{
                let projectSlug = column['project'].slug;
                let iterationId = column['iteration'].id;
                this.storyManager.moveToProject(story, projectSlug, iterationId);
            }
        }

        setupDependencies = () => {
            if(this.renderMode == 'downstream'){
                this.dependencyManager
                    .loadIncrementDependencies(this.project.currentIncrement.id)
                    .then((result) => this.dependencies = result.data.map((dep) => [dep.dependency, dep.story]));
            }else{
                this.projectManager.loadDependency(this.project.currentProject.slug, false, true).then((result) => {
                    this.dependencies = result.data.map((dep) => [dep.dependency, dep.story]);
                });
            }
        }


        setupRowsColumns = () => {
            if(this.renderMode =='downstream'){
                if( (!this.project.currentIncrement) || (!this.project.currentIncrement.id) ){
                    this.noData = true;
                    return;
                }
                let teams = this.project.getIncrementTeams();
                if(teams.length == 0){
                    this.noData = true;
                    return;
                }
                this.columns = this.project.currentIncrement.schedule.map((schedule:ProgramIncrementSchedule) => ({
                    id: String(schedule.id),
                    title: this._getDownStreamColumnTitle(schedule),
                    visible: true,
                    schedule: schedule,
                    available: this.getColumnsAvailability(schedule)
                }));

                this.rows = this.project.getIncrementTeams().map((iter: IncrementIteration) => ({
                    id: iter.project_slug,
                    title: iter.project_name,
                    visible: true,
                    extraInfo: {"spanEntire": iter.is_continuous, "spanEntireColumn_id": this._getContinousTeamSchedule(iter).id},
                    canWrite: this.userService.canWrite(iter.project_slug)
                }));
            }else{
                this.setupRowsColumnsForCurrent();
            }
            this.setupDependencies();
        }

        private _getDownStreamColumnTitle(schedule:ProgramIncrementSchedule){
            var title: string = `${schedule.default_name}<br/>`;
            title += `<i class="column-sub-title">Start Date: ${this.$filter('localdate')(schedule.start_date)}</i>`;
            return title;
        }

        private _getContinousTeamSchedule(iter: IncrementIteration): ProgramIncrementSchedule | {"id": number}{
            if(!iter.is_continuous){
                return {"id": null};
            }
            let schedule = _.find(this.project.currentIncrement.schedule, (schedule:ProgramIncrementSchedule)=> 
                                _.find(schedule.iterations, (i: IncrementIteration) => i.iteration_id == iter.iteration_id) != null
                            );
            return schedule;
        }

        setupRowsColumnsForCurrent = () => {
            this.noData = false;
            let project: Project = this.project.currentProject;
            let siblings: Array<PortfolioProjectStub> = this.getSibling();
            
            let currentIterationColumn = this._iterationToColumn(project, this.project.currentIteration);
            this.columns = [currentIterationColumn];

            let o_columns = this.project.iterations.filter((i) =>i.iteration_type == 1 && i.hidden == false 
                                                                && i.id != this.project.currentIteration.id
                                                                && (i.end_date == null || moment(i.end_date) > moment()))
                .map((iteration: Iteration) => (
                    this._iterationToColumn(project, iteration)
                ));
            
            this.columns = this.columns.concat(o_columns);

            if(this.showSiblings){
                siblings.map((s_project) => {
                    this.iterationManager.loadIterations(this.organizationSlug, s_project.slug).then((iterations) =>{
                        let s_columns = iterations.filter((i) =>i.iteration_type == 1 && i.hidden == false
                                                                && (i.end_date == null || moment(i.end_date) > moment()))
                                        .map((iteration: Iteration) => (
                                            this._iterationToColumn(s_project, iteration)
                                        ));
                        this.columns = this.columns.concat(s_columns);
                    });
                });
            }
            this.rows = [{
                id: project.slug,
                title: '',
                visible: true,
                canWrite: this.userService.canWrite(project.slug)
            }];
        }

        private getSibling(): Array<PortfolioProjectStub>{
            let project: Project = this.project.currentProject;

            var siblings: Array<PortfolioProjectStub> ;
            if(project.portfolio_level_id != null) {
                siblings = this.project.getSiblingProjects(project.slug, project.portfolio_level_id);
            } else {
                siblings = [];
            }
            return siblings;
        }

        private _iterationToColumn(project, iteration: Iteration){
            return {
                    id: String(iteration.id),
                    title: this._getColumnTitle(project, iteration),
                    visible: true,
                    project: project,
                    iteration: iteration,
                    available: this.userService.canWrite(project.slug)
                }
        }

        private _getColumnTitle(project: Project, itr: Iteration){
            var title: string = `${project.name}/${itr.name}<br/>`;
            if(project.continuous_flow || itr.start_date == null || itr.end_date == null){
                title += `<i class="column-sub-title">Continuous</i>`;
            }else{
                title += `<i class="column-sub-title">${this.$filter('localdate')(itr.start_date)} - ${this.$filter('localdate')(itr.end_date)}</i>`;
            }
            return title;
        }

        public gridCardProvider = (row:DependencyRow, column:DependencyColumn):CardGridCellData => {
            if(this.renderMode == 'downstream'){
                let schedule:ProgramIncrementSchedule = column.schedule;
                let iter:IncrementIteration = _.findWhere(schedule.iterations,{project_slug:row.id})

                return new CardGridCellData(
                    this._loadIterationStories(row, iter),
                    this.projectManager.loadProject(this.organizationSlug, row.id),
                    this.epicManger.loadEpics(this.organizationSlug, row.id),
                    this.$q
                );
            }else{

                return new CardGridCellData(
                    this._loadIterationStories({id: column['project'].slug}, {iteration_id: column['iteration'].id}),
                    this.projectManager.loadProject(this.organizationSlug, column['project'].slug),
                    this.epicManger.loadEpics(this.organizationSlug, column['project'].slug),
                    this.$q
                );
            }
        }

        private _loadIterationStories(row, iter){
            if(iter == null){
                return this.$q.resolve([]);
            }
            if(this.renderMode == 'current' && iter.iteration_id == this.project.currentIteration.id){
                return this.storyManager.loadIteration(row.id, iter.iteration_id, this.searchQuery);
            }else{
                return this.storyManager.loadIteration(row.id, iter.iteration_id);
            }
        }

        private getColumnsAvailability(schedule:ProgramIncrementSchedule){
            var res = {};
            _.forEach(this.project.getIncrementTeams(), (itr:IncrementIteration) => {
                res[itr.project_slug] = this.project.isTeamInSchedule(itr.project_slug, schedule);
            });
            return res;
        }

        private updateRenderMode(downstream: boolean){
            if(downstream){
                this.renderMode = "downstream";
            }else{
                this.renderMode = "current";
            }
            let slug = this.project.currentProject.slug;
            this.storage[slug].dependencyMode = this.renderMode;
            this.setupRowsColumns();
            this.$scope.$broadcast("cardGridLayoutChanges", null);
        }

        private updateSiblingMode(){
            this.setupRowsColumns();
            this.$scope.$broadcast("cardGridLayoutChanges", null);
        }

        private initFilters(){
            this.filterTemplate = this.urlRewriter.rewriteAppUrl("dependencies/filters.html");
            let project : Project = this.project.currentProject;
            this.filters['currentLabel'] = [];
            this.filters['currentTag'] = [];
            this.filters['currentUser'] = [];
            this.filters['allLabels'] = project.labels;
            this.filters['allTags'] = project.tags;
            this.filters['allUsers'] = project.members;
        }

        private updateFilters(option, type: string){
            if(type == 'user'){
                this.filters.currentUser = option;
            }
            if(type == 'label'){
                this.filters.currentLabel = option;
            }
            if(type == 'tag'){
                this.filters.currentTag = option;
            }
            this.$scope.$broadcast("purgeCardProviderCache", null);
            this.buildSearchQuery();
            this.updateSiblingMode();
        }

        private buildSearchQuery(){
            this.searchQuery = "";
            if(this.filters.currentLabel.length){
                _.forEach(this.filters.currentLabel, (label: any) => {
                    this.searchQuery += `label: ${label.name}, `
                });
            }
            if(this.filters.currentTag.length){
                _.forEach(this.filters.currentTag, (tag: any) => {
                    this.searchQuery += `tag: ${tag.name}, `
                });
            }
            if(this.filters.currentUser.length){
                _.forEach(this.filters.currentUser, (user: User) => {
                    this.searchQuery += `assignee: ${user.username}, `
                });
            }
            if(this.searchQuery !== ""){
                $('.dependencies-grid').addClass("filter-data");
            }else{
                $('.dependencies-grid').removeClass("filter-data");
            }
        }


        private filterCards(){
            this.$scope.$broadcast("purgeCardProviderCache", null);
            this.buildSearchQuery();
            this.updateSiblingMode();
        }

        private toggleIndependentCards(){
            this.$scope.$broadcast("reRenderDependencyGraph", null);
        }
    }
}
