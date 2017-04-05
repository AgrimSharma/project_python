/// <reference path="../_all.ts" />

module scrumdo{
    interface thisScope extends ng.IScope{
        portfolio: Portfolio;
        currentProject: Project;
        backlogSlug: string;
    }

    export class BacklogCommonController{

        public static $inject:Array<string> = [
            "$scope",
            "organizationSlug",
            "storyManager",
            "iterationManager",
            "projectManager",
            "$localStorage",
            "storyEditor",
            "$state",
            "$filter"
        ];


        private globalBacklogProject: Project;
        private globalBacklogIterations: Array<Iteration>;
        private globalBacklog: Iteration;
        private globalBacklogStories: Array<Story>;
        private parentStories: Array<Story>;
        private sortOrder: any = 'rank';
        private noReleaseCollapsed: boolean = false;
        private parentWorkItemName: string;
        private WorkItemName: string;
        private loading: boolean;
        private showGlobalSelect: boolean = false;
        private showSelectMenu: boolean = false;
        private stats;
        private quickSearch: string = "";
        private doQuickSearch: boolean = true;

        constructor(private $scope: thisScope,
                    private organizationSlug: string,
                    private storyManager: StoryManager,
                    private iterationManager: IterationManager,
                    private projectManager: ProjectManager,
                    private localStorage,
                    private storyEditor: StoryEditor,
                    private $state: ng.ui.IStateService,
                    private $filter){

            this.$scope.$root.$on("filter", this.onFilter);
            this.$scope.$on('sortOrderChanged', this.onSortChange);
            this.$scope.$on("$destroy", this.onDestroy);
            this.$scope.$root['globalBacklogStories'] = null;
            var loadStats = _.debounce(this.loadStats, 100);
            this.$scope.$on("storyModified", loadStats);
            this.$scope.$on('filterValueChanged', this.onFilterValueChanged);

            if(this.$state.current.name != "app.iteration.teamplanningteam"){
                this.showSelectMenu = true;
            }
            try{
                this.$scope.$root['currentSort'] = this.localStorage[this.$scope.currentProject.slug].boardSortSelection;
                if (this.$scope.$root['currentSort'] != "rank") {
                    this.sortCards(this.$scope.$root['currentSort']);
                }else {
                    this.sortOrder = this.$scope.$root['currentSort'];
                }
            }catch(e){
                this.sortOrder = 'rank';
            }
            
            this.initBacklog();
        }

        loadStats = () => {
            this.stats = getStoryTotals(this.globalBacklogStories);
        }

        toggleRelease(Release){
            if(Release['collapsed'] == null){
                Release['collapsed'] = false;
            }else{
                Release['collapsed'] = !Release['collapsed'];
            }
            this.$scope.$emit('storiesChanged');
        }

        toggleNoRelease(){
            this.noReleaseCollapsed = !this.noReleaseCollapsed;
        }

        onDestroy = () => {
            delete this.$scope.$root['globalBacklogStories'];
            delete this.$scope.$root['globalBacklogIteration'];
            this.$scope.$emit('globalBacklogStoriesUpdate', null);
        }

        initBacklog(){
            this.loading = true;
            this.projectManager.loadProject(this.organizationSlug, this.$scope.backlogSlug).then((project) => {
                this.globalBacklogProject = project;
                this.WorkItemName = project.work_item_name;
                this.iterationManager.loadIterations(this.organizationSlug, this.$scope.backlogSlug)
                                    .then((iterations) => {
                                        this.globalBacklogIterations = iterations;
                                        this.globalBacklog = _.find(iterations, (i: Iteration) => i.iteration_type == 0);
                                        this.loadParentCards();
                                    });
            });
        }

        onFilter = (event, query, filterName) => {
            if (filterName === 'globalBacklogFilter') {
                trace("Global Backlog filter changed");
                this.loadGlobalBacklogStories(query);
            }
        }

        loadGlobalBacklogStories(query = ''){
            this.storyManager.loadIterations(this.globalBacklogProject.slug, [this.globalBacklog.id], query)
                            .then((stories) => {
                                if(query != ""){
                                    this.doQuickSearch = false;
                                }else{
                                    this.doQuickSearch = true;
                                }
                                this.globalBacklogStories = stories;
                                this.loadStats();
                                this.$scope.$root['globalBacklogStories'] = stories;
                                this.$scope.$root['globalBacklogIteration'] = this.globalBacklog;
                                this.$scope.$emit('globalBacklogStoriesUpdate', null);
                                this.$scope.$root.$broadcast('backlogToggled');
                                this.loading = false;
                            });
        }

        loadParentCards(){
            let currentLevelNumber = portfolioLevelIdToNumber(this.$scope.portfolio.levels, this.$scope.currentProject.portfolio_level_id);
            var parentBacklogProject;
            if(currentLevelNumber > 1){
                let parentLevel:PortfolioLevel = _.find(this.$scope.portfolio.levels, (l: PortfolioLevel) => 
                                                    l.level_number == currentLevelNumber-1);
                parentBacklogProject = parentLevel.backlog_project;
            }else{
                parentBacklogProject = this.$scope.portfolio.root;
            }

            this.parentWorkItemName = parentBacklogProject.work_item_name;
            this.storyManager.loadProjectReleases(parentBacklogProject.slug)
                                .then((stories) => {
                                    this.parentStories = stories;
                                    this.loadGlobalBacklogStories();
                                });
        }

        onSortChange = (event, sort) => {
            this.sortCards(sort);
        }

        sortCards = (sort) => {
            if (sort === 'value_time') {
                this.sortOrder = [calculateValueOverTime_withRules, calculateValueOverTime];
            } else if (sort === 'value_point') {
                this.sortOrder = [calculateValueOverPoints_withRules, calculateValueOverPoints];
            } else if (sort === 'wsjf_value') {
                this.sortOrder = calculateWSJFValue;
            } else if (sort !== "rank") {
                this.sortOrder = [sort, "rank"];
            } else {
                this.sortOrder = sort;
            }         
         }

         filterStory = (releaseId: number) => {
             return (story: Story) => {
                 if(releaseId != null){
                     return story.release!=null && story.release.id == releaseId;
                 }else{
                     return story.release == null;
                 }
             }
         }

        selectAll(event, releaseId = null) {
            if(releaseId == null){
                return this.$scope.$broadcast("selectAll");
            }else{
                var count = this.$scope.$root['selectedCount'] ? this.$scope.$root['selectedCount'] : 0;
               _.forEach(this.globalBacklogStories, (s:Story) => {
                    if(s.release != null && s.release.id == releaseId && releaseId > 0){
                        s['selected'] = true;
                        count +=1;
                    }else if(releaseId == -1 && s.release == null){
                        s['selected'] = true;
                        count +=1;
                    }
                });
                this.$scope.$root['selectedCount'] = count;
            }
        }

        selectNone(event, releaseId = null) {
            if(releaseId == null){
                return this.$scope.$broadcast("selectNone");
            }else{
                var count = this.$scope.$root['selectedCount'] ? this.$scope.$root['selectedCount'] : 0;
                _.forEach(this.globalBacklogStories, (s:Story) => {
                    if(s.release != null && s.release.id == releaseId && releaseId > 0){
                        s['selected'] = false;
                        count -=1;
                    }else if(releaseId == -1 && s.release == null){
                        s['selected'] = false;
                        count -=1;
                    }
                });
                this.$scope.$root['selectedCount'] = count;
            }
        }

        private addCard($event: MouseEvent, releaseId: number){
            var release;
            if(releaseId > 0){
                release = {id: releaseId};
            }else{
                release = null;
            }
            this.storyEditor.createStory(this.globalBacklogProject, {release: release, iteration_id: this.globalBacklog.id});
        }

        onFilterValueChanged = (event, data) => {
            this.quickSearch = data.query;
            this.$scope.$apply();
        }

        quickFilter = (story: Story) => {
            if(this.quickSearch == "" || !this.doQuickSearch){
                return true;
            }

            let summary = this.$filter('htmlToPlaintext')(story.summary);
            let key: string = this.quickSearch.toLowerCase();
            let value: string = `${story.prefix}-${story.number} ${story.number} ${summary}`;
            return value.toLowerCase().indexOf(key) !== -1;
        }
    }
}
