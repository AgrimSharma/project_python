/// <reference path='../_all.ts' />

module scrumdo {

    // The minimal amount of a BoardProject we need for the backlog
    export interface BacklogBoardProject {
        backlogIterationId: Function;
        backlog: Iteration;
        uiState:UIState;
        projectSlug: string;
        project: Project;
        epics:Array<Epic>;
        iterations:Array<Iteration>;
        boardCells:Array<BoardCell>;
        backlogStories:Array<Story>;
        doBacklogQuickSearch?:boolean;
    }

    export class BacklogController {
        public static $inject: Array<string> = [
            "$scope",
            "$rootScope",
            "$localStorage",
            "iterationManager",
            "organizationSlug",
            "$filter"
        ];

        public sortOrder: any = 'rank';
        public viewType: number;
        public storyLoadLimit: number;
        // public backlog;
        public storage;
        public filterOn: number;
        public storyCount: number;
        public summary: boolean;
        public iterationSummary: boolean;
        public globalBacklog: boolean;
        private stats;
        private quickSearch: string = "";

        constructor(
            public scope,
            public rootScope,
            public localStorage,
            public iterationManager: IterationManager,
            public organizationSlug: string,
            private $filter) {

            this.viewType = 0;
            this.storyLoadLimit = 1000;
            this.scope.newstory = {
                summary: ""
            };

            this.summary = this.scope.summary == null ? false : this.scope.summary
            this.iterationSummary = this.scope.iterationSummary == null ? false : this.scope.iterationSummary
            this.globalBacklog = this.scope.globalBacklog == null ? false : this.scope.globalBacklog

            this.scope.ctrl = this;
            this.scope.$on("projectLoaded", this.setIterationId);
            this.rootScope.$on("backlogFilterChange", this.onFilter);
            this.setIterationId();
            this.scope.$on('sortOrderChanged', this.onSortChange);
            this.scope.$on('backlogStoriesChanged', this.loadStats);
            this.scope.$on('filterValueChanged', this.onFilterValueChanged);
            var loadStats = _.debounce(this.loadStats, 100);
            this.scope.$on("storyModified", loadStats);
            this.storage = this.localStorage.$default({});
            this.loadViewType();
        }

        get boardProject():BacklogBoardProject {
            return this.scope.boardProject;
        }

        loadStats = () => {
            this.stats = getStoryTotals(this.scope.boardProject.backlogStories);
        }

        onFilter = (event, query, name) => {
            if (name === "backlogFilter" && query !== "") {
                this.filterOn = 1;
            } else {
                this.filterOn = 0;
            }
        }

        setIterationId = () => {
            this.scope.backlogId = this.boardProject.backlogIterationId();
            if (this.boardProject.backlog) {
                this.storyCount = this.boardProject.backlog.story_count;
            }
        }
        
        // This filter needs to return a function to act as a filter
        //so it can take a param.
        filterStoryByEpic(epic) {
            return (story) => {
                var ref;
                return ((ref = story.epic) != null ? ref.id : void 0) === epic.id;
            };
        }
        
        filterStoryByNoEpic(){
            return (story) => {
                return story.epic == null;
            };
        }

        filterByNullLabel(story) {
            return story.labels.length == 0;
        }

        filterByLabel(label) {
            return (story) => {
                return _.findWhere(story.labels, { id: label.id }) != null;
            };
        }

        filterEpic(epic) {
            return !epic.archived;
        }

        toggleBacklog($event) {
            $event.preventDefault();
            this.boardProject.uiState.backlogOpen = !this.boardProject.uiState.backlogOpen;
            this.rootScope.$broadcast('backlogToggled');

        }

        _hideSidebarPanels(){
            let uiState = this.boardProject.uiState;
            uiState.backlogOpen = false;
            uiState.iterationOpen = false;
            uiState.loadGlobalBacklog = false;
            uiState.summaryOpen = false;
            uiState['tab'] = false;
        }

        _showBacklogCards(mode){
            if (this.storyCount <= this.storyLoadLimit && mode=='tab') {
                this.boardProject.uiState.backlogOpen = true;
            }
        }

        getActivePanel(){
            let uiState = this.boardProject.uiState;
            if(uiState.iterationOpen) return 'iterationOpen';
            if(uiState.loadGlobalBacklog) return 'loadGlobalBacklog'
            if(uiState.summaryOpen) return 'summaryOpen'
            return 'tab'
        }

        toggleBacklogSidebar($event: MouseEvent, mode: string = 'tab'){
            $event.preventDefault();
            $event.stopPropagation();
            let uiState = this.boardProject.uiState;
            if(uiState.loadBacklog){
                // in open state
                if(uiState[mode]){
                    uiState.loadBacklog = false;
                    uiState.backlogOpen = false;
                    setTimeout(() => {
                        uiState[mode] = false;
                    }, 300);
                }else{
                    this._hideSidebarPanels();
                    uiState[mode] = true;
                    this._showBacklogCards(mode);
                }
            }else{
                // in closed state
                uiState.loadBacklog = true;
                uiState[mode] = true;
                this._showBacklogCards(mode);
            }
            this.rootScope.$broadcast('backlogToggled');
        }

        onSortChange = (event, sort) => {
            if (sort === 'value_time') {
                this.sortOrder = [calculateValueOverTime_withRules,calculateValueOverTime];
            } else if (sort === 'value_point') {
                this.sortOrder = [calculateValueOverPoints_withRules,calculateValueOverPoints];
            } else if (sort === 'wsjf_value') {
                this.sortOrder = calculateWSJFValue;
            } else if (sort !== "rank") {
                this.sortOrder = [sort, "rank"];
            } else {
                this.sortOrder = sort;
            }
        }

        loadViewType() {
            var pStorage;
            if (this.storage[this.boardProject.projectSlug] != null) {
                pStorage = this.storage[this.boardProject.projectSlug];
                this.viewType = pStorage.backlogView != null ? pStorage.backlogView : 0;
            } else {
                this.storage[this.boardProject.projectSlug] = {};
                this.viewType = 0;
            }
        }
        
        viewChange(){
            this.scope.$emit('backlogChanged');
            this.storage[this.boardProject.projectSlug].backlogView = this.viewType;
        }

        selectAll(event) {
            return this.scope.$broadcast("selectAll");
        }

        selectNone(event) {
            return this.scope.$broadcast("selectNone");
        }

        onFilterValueChanged = (event, data) => {
            this.quickSearch = data.query;
            this.scope.$apply();
        }

        quickFilter = (story: Story) => {
            if(this.quickSearch == "" || !this.boardProject.doBacklogQuickSearch){
                return true;
            }

            let summary = this.$filter('htmlToPlaintext')(story.summary);
            let key: string = this.quickSearch.toLowerCase();
            let value: string = `${story.prefix}-${story.number} ${story.number} ${summary}`;
            return value.toLowerCase().indexOf(key) !== -1;
        }
    }
}