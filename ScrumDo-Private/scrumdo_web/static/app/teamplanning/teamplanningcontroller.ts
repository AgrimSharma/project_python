/// <reference path='../_all.ts' />

module scrumdo {


    export class TeamPlanColumn implements CardGridColumn {
        id: string;
        public title: string;
        public visible: boolean;
        iteration: IncrementIteration;
    }

    export class TeamPlanRow implements CardGridRow {
        id: string;
        public title: string;
        public visible: boolean;
        public feature:Story;
        public release:MiniRelease;
        public canWrite:boolean;
    }



    export class TeamPlanningController {

        public noData:boolean;
        public columns:Array<TeamPlanColumn>;
        public rows:Array<TeamPlanRow>;
        public teamOptions:Array<{project_name:string, project_slug:string}>;
        public selectedTeam:{project_name:string, project_slug:string};

        public backlogOpen:Boolean = false;

        private storyLists:Array<Array<Story>> = [];
        private workItemName:string;
        private childWorkItemName:string;
        private stats = [];

        private intervalObj;
        private projectSlug: string;
        private storage: any;
        private childTimePeriodName: string;
        private noFeatureCards: boolean;

        private globalBacklogProject: Project;
        private globalBacklogIterationId: number;
        private teamBacklogQuery: string = "";
        private busyFlag: boolean;

        public static $inject:Array<string> = [
            "projectData",
            "organizationSlug",
            "storyManager",
            "storyAssignmentManager",
            "storyEditor",
            "limitSettingsService",
            "WIPLimitManager",
            "$state",
            "$q",
            "$scope",
            "realtimeService",
            "exportManager",
            "$localStorage",
            "iterationWindowService",
            "projectManager",
            "iterationManager",
            "$filter",
            "userService"
        ];

        constructor(public projectData:ProjectDatastore,
                    private organizationSlug:string,
                    private storyManager:StoryManager,
                    private storyAssignmentManager:StoryAssignmentManager,
                    private storyEditor:StoryEditor,
                    private limitSettingsService:LimitSettingsService,
                    private wipLimitManager:WIPLimitManager,
                    private $state,
                    private $q:ng.IQService,
                    private $scope:ng.IScope,
                    private realtimeService: RealtimeService,
                    private exportManager: ExportManager,
                    private localStorage,
                    private iterationWindowService: IterationWindowService,
                    private projectManager: ProjectManager,
                    private iterationManager: IterationManager,
                    private $filter,
                    private userService: UserService) {

            if(!projectData.currentIncrement.schedule) {
                $state.go('app.iteration.notincrement')
                return
            }
            // check if there are teams in schedule
            let teams = projectData.getIncrementTeams().map((ii:IncrementIteration) => ii.project_slug);
            if(teams.length == 0){
                $state.go('app.iteration.notincrement')
                return
            }
            this.projectSlug = this.projectData.currentProject.slug;
            this.workItemName = this.$scope.$root['safeTerms'].current.work_item_name;
            var ref = this.$scope.$root['safeTerms'].children.work_item_name;
            this.childWorkItemName = ref != null ? ref: 'Card';
            this.noFeatureCards = false;
            this.setLimitBarStats();

            // wait for assignments to load
            this.intervalObj = setInterval(() => {
                this._checkForAssignments();
            }, 10);

            this.$scope.$root['kiosk'] = new Kiosk();
            this.$scope.$on('removeCardRow', this.onRemoveRow)
            this.$scope.$on('newCard', this.onNewCard)

            this.$scope.$on('cardGridDrag', this.onDragCard)
            this.$scope.$on('cardGridRawDrag', this.onRawDragCard)

            this.$scope.$on('onStoryAdded', this.calculateStats)
            this.$scope.$on('storyModified', this.calculateStats)
            this.$scope.$on("$destroy", this.onDestroy);
            this.$scope.$on("iterationWindowClosed", this.onIterationAdded);
            this.$scope.$on("iterationWipSettings", this.onIterationWipSettings);

            this.$scope.$on("filter", this.onFilter);
            this.storage = this.localStorage.$default({});

            if (this.storage[this.projectSlug] == null) {
                this.storage[this.projectSlug] = { };
            }
            if (this.storage[this.projectSlug].lastTeamPlanning == null) {
                this.storage[this.projectSlug].lastTeamPlanning = this.projectData.currentTeam.project.slug;
            }

            this.childTimePeriodName = this.$scope.$root['safeTerms'] != null ? $scope.$root['safeTerms'].children.time_period_name : "Iteration";

            wipLimitManager.getLimits(this.projectData.currentTeam.project.slug,
                                      this.projectData.currentIncrement.iteration_id).then(this.onLimitResponse)

        }

        private onDestroy = () => {
            this.$scope.$root['kiosk'] = null;
            this.realtimeService.unSubscribeProject([this.selectedTeam.project_slug]);
            delete this.$scope.$root['teamPlanningBacklog'];
        }

        public setLimitBarStats(){
            this.stats = [
                            [
                                {value: 0, label:`${pluralize(this.workItemName)}`, limit:0},
                                {value: 0, label:`${this.workItemName} Points`, limit:0},
                            ]
                        ];
        }

        private _checkForAssignments(){
            if(this.projectData.currentTeam.assignments != null){
                clearInterval(this.intervalObj);
                this.setupRowsColumns();
                this.realtimeService.subscribeProject([this.selectedTeam.project_slug]);
            }
        }

        private _backlogBoardProject = null;
        public backlogBoardProject():BacklogBoardProject {
            if(!this._backlogBoardProject) {
                let team = this.projectData.currentTeam;
                let backlogId: number = team.project.kanban_iterations.backlog;
                this._backlogBoardProject = {
                    backlogIterationId: () => backlogId,
                    backlog: _.findWhere(team.iterations, {iteration_type: 0}),
                    uiState: new UIState(),
                    projectSlug: team.project.slug,
                    project: team.project,
                    epics: team.epics,
                    iterations: team.iterations,
                    boardCells: team.boardCells,
                    backlogStories: team.backlog,
                    portfolio: this.projectData.portfolio
                }
                this.setGlobalBacklog();
            }
            this.$scope.$root['teamPlanningBacklog'] = true;
            return this._backlogBoardProject;
        }

        private loadBacklogStories(query=""){
            let team = this.projectData.currentTeam;
            this.storyManager
                .loadIterations(team.project.slug, [team.project.kanban_iterations.backlog], query).then((stories) => {
                    this._backlogBoardProject.backlogStories = stories;
            });
        }

        onFilter = (event, query, filterName) => {
            if (filterName === 'backlogFilter') {
                trace("Downstream Planning Backlog filter changed");
                this.loadBacklogStories(query);
            } 
        }

        setGlobalBacklog(){
            let team = this.projectData.currentTeam;
            let backlogProjectStub: PortfolioProjectStub = this.projectData.getGlobalBacklog(team.project.portfolio_level_id);
            this._backlogBoardProject.globalBacklogSlug = backlogProjectStub.slug;

            this.projectManager.loadProject(this.organizationSlug, backlogProjectStub.slug).then((project) => {
                this.globalBacklogProject = project;
                this.globalBacklogIterationId = project.kanban_iterations.backlog;
            });
        }

        private calculateStats = () => {
            this.calculateFeatureStats();
        }

        private calculateFeatureStats = () => {

            let stats = this.projectData.currentTeam.assignments
                .map((featureId)=> <Story> _.findWhere(this.projectData.currentStories, {id:featureId}))
                .reduce((acc, story:Story)=>{
                    acc.count++;
                    acc.points += parseFloat(<string>story.points_value);
                    return acc;
                },{count:0, points:0})
            this.stats[0][0].value = stats.count;
            this.stats[0][1].value = stats.points;
        }

        private onLimitResponse = (limitResponse:{data:LimitSettings}) => {
            this.setLimits(limitResponse.data);
        }

        private setLimits = (limits:LimitSettings) => {
            this.stats[0][0].limit = limits.featureLimit;
            this.stats[0][1].limit = limits.featurePointLimit;
            this.calculateFeatureStats();
        }


        public getStats():StatGroups {
            return this.stats;
        }

        public setLimit():void {
            const initial = {
                featureLimit: this.stats[0][0].limit,
                featurePointLimit: this.stats[0][1].limit,
                cardLimit: 0,
                cardPointLimit: 0
            }

            this.limitSettingsService
                    .showSettings(initial, false, this.workItemName)
                    .then(this.onSaveLimits)
        }

        private onSaveLimits = (limits:LimitSettings) => {
            this.wipLimitManager.setLimits(this.projectData.currentTeam.project.slug,
                                           this.projectData.currentIncrement.iteration_id,
                                           limits)
                .then(this.onLimitResponse);
        }



        private onRawDragCard = (event, {storyId, placeholder}) => {
            let story = this.storyManager.getStory(storyId);
            var previousId = placeholder.prev(".cards").attr("data-story-id");
            var nextId = placeholder.next(".cards").attr("data-story-id");
            var parent = placeholder.parent();
            var iterationId = parseInt(parent.attr("data-iteration-id"));
            var releaseId = parseInt(parent.attr("data-release-id"));
            releaseId = isNaN(releaseId) ? null : releaseId;
            if(!parent){return;}

            if(iterationId == this.globalBacklogIterationId) {
                if(iterationId != story.iteration_id){
                    this.busyFlag = true;
                    trace('onRawDragCard - drag to global-backlog, from Planning Board')
                    this.storyManager.moveToProject(story, this.globalBacklogProject.slug, this.globalBacklogIterationId, null, releaseId).then((data) => {
                        this.storyManager.moveToRelease(data.data, releaseId);
                        this.busyFlag = false
                        placeholder.remove();
                    });
                }else{
                    trace('onRawDragCard - drag to global-backlog, from itself')
                    if(((releaseId == null && story.release != null) 
                        || (releaseId != null && story.release != null && story.release.id != releaseId)
                        || (releaseId != null && story.release == null)) && !this.busyFlag){
                        this.storyManager.moveToIteration(story, iterationId);
                        this.storyManager.moveToRelease(story, releaseId);
                        story.release = releaseId == null ? null : {id: releaseId};
                        placeholder.remove();
                        this.storyManager.saveStory(story);
                    }
                }
            }else{
                if(iterationId != this.projectData.currentTeam.project.kanban_iterations.backlog) {
                    trace('ERROR: onRawDragCard - drag to a non-backlog, don\'t know what to do.')
                    return;
                }

                this.storyManager.moveToIteration(story, iterationId);

                var other;

                if (nextId) {
                    story.story_id_after = nextId;
                    other = this.storyManager.getStory(story.story_id_after);
                    story.rank = other.rank - 1;
                } else {
                    story.story_id_after = -1;
                }

                if (previousId) {
                    story.story_id_before = previousId;
                    other = this.storyManager.getStory(story.story_id_before);
                    story.rank = other.rank + 1;
                } else {
                    story.story_id_before = -1;
                }

                placeholder.remove();
                
                this.storyManager.saveStory(story);
            }

        }

        private onDragCard = (event, {storyId, row, column, placeholder}) => {
            let story = this.storyManager.getStory(storyId);
            let targetRelease:MiniRelease = row.release;
            let targetIteration:IncrementIteration = column.iteration;
            let team = this.projectData.currentTeam;

            if(team.project.slug != story.project_slug){
                let releaseId = targetRelease.id != -1 ? targetRelease.id : null;
                this.storyManager.moveToProject(story, team.project.slug, targetIteration.iteration_id, null, releaseId).then((data) => {
                    this.storyManager.moveToRelease(data.data, releaseId);
                });
            }else{
                this.storyManager.moveToIteration(story, targetIteration.iteration_id);
                let releaseId = targetRelease.id != -1 ? targetRelease.id : null;
                this.storyManager.moveToRelease(story, releaseId);
                
                var previousId = placeholder.prev(".cards").attr("data-story-id");
                var nextId = placeholder.next(".cards").attr("data-story-id");
                var other;
                if (nextId) {
                    story.story_id_after = nextId;
                    other = this.storyManager.getStory(story.story_id_after);
                    story.rank = other.rank - 1;
                } else {
                    story.story_id_after = -1;
                }

                if (previousId) {
                    story.story_id_before = previousId;
                    other = this.storyManager.getStory(story.story_id_before);
                    story.rank = other.rank + 1;
                } else {
                    story.story_id_before = -1;
                }

                this.storyManager.saveStory(story);
            }
            placeholder.remove();
        }

        private teamProjectSlug():string {
            return this.projectData.currentTeam.project.slug;
        }

        onNewCard = (event, {row, column}) => {
            let iterationId = column.iteration.iteration_id
            var release = null;
            if(row.release.id != -1){
                release = row.release;
            }
            this.storyEditor.createStory(this.projectData.currentTeam.project, {
                iteration_id:iterationId,
                release:release
            });

        }

        teamSelected() {
            let params = _.extend({}, this.$state.params, {teamSlug:this.selectedTeam.project_slug})
            this.storage[this.projectSlug].lastTeamPlanning = this.selectedTeam.project_slug;
            this.$state.go('app.iteration.teamplanningteam', params);
        }

        onRemoveRow = (event, row) => {
            if(row.id == -1){
                // got request for row without EPIC
                this.noFeatureCards = false;
            }else{
                let i = this.projectData.currentTeam.assignments.indexOf(row.feature.id)
                if(i==-1) return;
                this.projectData.currentTeam.assignments.splice(i, 1);
                this.storyAssignmentManager.removeAssignment(this.projectData.currentIncrement.id,
                                                            this.teamProjectSlug(),
                                                            row.feature.id)
            }
            this.setupRowsColumns();
            this.calculateFeatureStats();
            
        }




        public gridCardProvider = (row:TeamPlanRow, column:TeamPlanColumn):CardGridCellData => {
            let currentTeam = this.projectData.currentTeam;
            let iter:IncrementIteration = column.iteration;
            let assignmentId = parseInt(row.id);

            return new CardGridCellData(
                this._loadStoriesForAssignment(currentTeam, iter, assignmentId),
                this.$q.resolve(currentTeam.project),
                this.$q.resolve(currentTeam.epics),
                this.$q
            );
        }

        private _loadStoriesForAssignment(currentTeam, iter, assignmentId){
            if(iter == null){
                return this.$q.resolve([]);
            }
            return this.storyManager
                        .loadStoriesForAssignment(currentTeam.project.slug, iter.iteration_id, assignmentId)
                        .then((stories)=>{
                            this.storyLists.push(stories)
                            return stories
                        });
        }

        public pullFeature(story:Story) {
            if(this.projectData.currentTeam.assignments.indexOf(story.id) === -1) {
                this.projectData.currentTeam.assignments.push(story.id);

                this.storyAssignmentManager.createAssignment(this.projectData.currentIncrement.id,
                                                             this.projectData.currentTeam.project.slug,
                                                             story.id);
                this.setupRowsColumns();
                this.calculateFeatureStats();
            }
        }


        setupRowsColumns = () => {
            if( (!this.projectData.currentIncrement) || (!this.projectData.currentIncrement.id) ){
                this.noData = true;
                return;
            }

            this.teamOptions = this.projectData.getIncrementTeams().map((ii:IncrementIteration) =>
                    ({project_slug:ii.project_slug, project_name:ii.project_name}));
            
            this.columns = this.projectData
                            .getIncrementTeamIterations(this.projectData.currentTeam.project.slug)
                            .map((itr:IncrementIteration) => ({
                                id: String(itr.iteration_id),
                                title: this._getColumnTitle(itr),
                                visible: true,
                                iteration: itr,
                                available: true
                            }));

            this.rows = this.projectData.currentTeam.assignments.map((featureId:number) => {
                let feature = <Story> _.findWhere(this.projectData.currentStories, {id:featureId})
                return {
                    id: String(featureId),
                    title: `${this.projectData.currentProject.prefix}-${feature.number} ${feature.summary}`,
                    visible: true,
                    feature: feature,
                    release: {
                        iteration_id:feature.iteration_id,
                        number:feature.number,
                        id:feature.id,
                        project_slug:this.projectData.currentProject.slug,
                        summary:feature.summary,
                        project_prefix:this.projectData.currentProject.prefix
                    },
                    canWrite: this.projectData.currentTeam.canWrite
                }
            });
            
            this.rows = _.sortBy(this.rows, (r) => r.feature.rank )
            if(this.rows.length > 0 && this.noFeatureCards){
                this.rows.push(this.noFeaturesRow());
            }
            this.selectedTeam = _.findWhere(this.teamOptions, {project_slug: this.projectData.currentTeam.project.slug});
        }

        private _getColumnTitle(itr:IncrementIteration){
            var title: string = `${itr.project_name}/${itr.iteration_name}<br/>`;
            if(itr.is_continuous || itr.start_date == null || itr.end_date == null){
                title += `<i class="column-sub-title">Continuous</i>`;
            }else{
                title += `<i class="column-sub-title">${this.$filter('localdate')(itr.start_date)} - ${this.$filter('localdate')(itr.end_date)}</i>`;
            }
            return title;
        }

        private ShowNoFeatureCards(){
            this.setupRowsColumns();
        }

        private noFeaturesRow(): TeamPlanRow{
            return {
                id: "-1",
                title: `${pluralize(this.childWorkItemName)} without ${this.workItemName}`,
                visible: true,
                feature: null,
                release: {
                    iteration_id: -1,
                    number: -1,
                    id: -1,
                    project_slug: this.projectData.currentProject.slug,
                    summary: "",
                    project_prefix:this.projectData.currentProject.prefix
                },
                canWrite: this.projectData.currentTeam.canWrite
            }
        }

        private isSelectedFeature = (feature: Story) =>{
            return _.find(this.rows, (row:any) => row.id == feature.id) != null;
        } 

        public exportPlanning(event){
            this.exportManager.startTeamPlanningExport(this.projectData.currentProject, this.projectData.currentTeam, this.projectData.currentIteration.id);
        }

        private addIteration(){
            let itr = {increment:[{id: this.projectData.currentIteration.id, 
                                project_name: this.projectData.currentProject.name,
                                name: this.projectData.currentIteration.name}]};
            this.iterationWindowService.createIteration(this.organizationSlug, 
                                                        this.projectData.currentTeam.project.slug, 
                                                        itr,
                                                        this.childTimePeriodName);
        }

        private onIterationAdded = (event, data) => {
            this.projectData.reloadIncrement(this.projectData.currentIteration.id).then(() => {
                this.setupRowsColumns();
            });
        }

        private onIterationWipSettings = (event, data) => {
            let col: TeamPlanColumn = data.column;
            var featureLimit = 0;
            var featurePointLimit = 0;
            if(col['iteration']['wip_limits'] != null){
                featureLimit = col['iteration']['wip_limits'].featureLimit;
                featurePointLimit = col['iteration']['wip_limits'].featurePointLimit; 
            }
            const initial = {
                featureLimit: featureLimit,
                featurePointLimit: featurePointLimit,
                cardLimit: 0,
                cardPointLimit: 0
            }
            var isParent = false;
            this.limitSettingsService
                .showSettings(initial, isParent, this.childWorkItemName)
                .then((limits: LimitSettings) => {
                    this.onSaveIterationLimits(limits, col);
                })
        }

        private onSaveIterationLimits = (limits:LimitSettings, col: TeamPlanColumn) => {
            this.wipLimitManager.
                setLimits(col['iteration'].project_slug,
                        col['iteration'].iteration_id,
                        limits).
                then((limitResponse:{data:LimitSettings}) => {
                    let index = this.columns.indexOf(col);
                    if(index > -1) {
                        this.columns[index]["iteration"]["wip_limits"] = limitResponse.data;
                    }
                });
        }
    }

    export function checkNoIncrement($scope, $state:ng.ui.IStateService, projectDatastore:ProjectDatastore) {
        $scope.projectData = projectDatastore;
        $scope["timePeriodName"] = $scope.$root['safeTerms'] != null ? $scope.$root['safeTerms'].current.time_period_name : "Iteration";
        $scope["childTimePeriodName"] = $scope.$root['safeTerms'] != null ? $scope.$root['safeTerms'].children.time_period_name : "Iteration";
        $scope['reloadPage'] = () => {
            $state.reload();
        }
        $scope.$on("onChildIterationUpdated", () => {
            projectDatastore.reloadCurrentIncrement();
            $scope['showRefresh'] = true;
        });
        if (projectDatastore.currentIncrement.schedule) {
            let teams = projectDatastore.getIncrementTeams();
            if(teams.length != 0){
                $state.go('app.iteration.teamplanning');
                return;
            }
        }
    }

    export function redirectDefaultTeam($state:ng.ui.IStateService, projectDatastore:ProjectDatastore, $localStorage) {
        if(!projectDatastore.currentIncrement.schedule) {
            $state.go('app.iteration.notincrement')
            return
        }
        let teams = projectDatastore.getIncrementTeams().map((ii:IncrementIteration) => ii.project_slug);
        if(teams.length == 0){
            $state.go('app.iteration.notincrement')
            return
        }
        var defaultTeamSlug = teams[0];

        if ($localStorage[projectDatastore.currentProject.slug] 
            && $localStorage[projectDatastore.currentProject.slug].lastTeamPlanning) {
            
            var teamSlug = $localStorage[projectDatastore.currentProject.slug].lastTeamPlanning;
            let res = _.find(teams, (team: any) => team == teamSlug);
            if(res!=null){
                defaultTeamSlug = res;
            }else{
                $localStorage[projectDatastore.currentProject.slug].lastTeamPlanning = null;
            }
        }

        $state.go('app.iteration.teamplanningteam',{teamSlug:defaultTeamSlug})
    }

}
