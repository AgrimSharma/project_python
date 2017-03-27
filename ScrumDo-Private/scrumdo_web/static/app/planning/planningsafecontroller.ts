/// <reference path='../_all.ts' />

module scrumdo {
    export class PlanningSafeController {
        public static $inject: Array<string> = [
            "$scope",
            "storyManager",
            "projectSlug",
            "storyEditor",
            "projectManager",
            "iterationManager",
            "organizationSlug",
            "userService"
        ];

        private project: Project;
        private sortOrder:any;
        private isExpanded: boolean;
        private stories = {};
        private programIncreaments: Array<any>;
        private features = {};
        private showArchived:boolean;

        constructor(
            private scope,
            private storyManager: StoryManager,
            public projectSlug: string,
            private storyEditor: StoryEditor,
            private projectManager: ProjectManager,
            private iterationManager: IterationManager,
            public organizationSlug: string,
            private userService: UserService) {

            this.scope.$on('sortOrderChanged', this.onSortChange);
            this.scope.canWrite = this.userService.canWrite(this.scope.project.slug);
            this.isExpanded = false;
            this.showArchived = false;
        }

        onSortChange = (event, sort) => {
            if (sort === 'value_time') {
                this.sortOrder = [calculateValueOverTime_withRules, calculateValueOverTime];
            } else if (sort === 'value_point') {
                this.sortOrder = [calculateValueOverPoints_withRules, calculateValueOverPoints];
            } else if (sort === 'wsjf_value') {
                this.sortOrder = calculateWSJFValue;
            } else if (sort !== "rank") {
                this.sortOrder = [sort, "release_rank"];
            } else if (sort === "rank") {
                this.sortOrder = "release_rank";
            } else {
                this.sortOrder = sort;
            }
        }

        resetPrograms(){
            for(var i in this.programIncreaments){
                var f = this.programIncreaments[i];
                f.isExpanded = false;
            }
        }
        resetFeatures(program = null){
            if(program != null){
                var f = this.features[program.id];
                _.forEach(f, (i:any) => i.isExpanded = false);
            }else{
                for(var i in this.features){
                    var f = this.features[i];
                    _.forEach(f, (i:any) => i.isExpanded = false);
                }
            }
        }

        toggleExpanded() {
            this.isExpanded = !this.isExpanded;
            if (this.isExpanded) {
                this.loadPrograms();
            }else{
                this.resetPrograms();
                this.resetFeatures();
            }
        }

        toggleExpandedItr(program) {
            program.isExpanded = !program.isExpanded;
            if(program.isExpanded){
                this.loadFeatures(program);
            }else{
                this.resetFeatures(program);
            }
        }

        toggleExpandedFeature(feature) {
            feature.isExpanded = !feature.isExpanded;
            if(feature.isExpanded){
                this.loadStories(feature);
            }
        }

        setFeatures = (features, program) => {
            this.features[program.id] = features;
        }

        setStories = (stories, feature) => {
            this.stories[feature.id] = stories;
        }

        addCard(feature){
            this.storyEditor.createStory(this.scope.project, { release: feature });
        }

        siblingAddCard(iteration){
            this.projectManager.loadProject(this.organizationSlug, this.scope.parent.slug).then((project) => {
                this.storyEditor.createStory(project, { iteration_id:iteration.id });
            });
        }

        loadPrograms(){
            this.iterationManager.loadIterations(this.organizationSlug, this.scope.parent.slug).then( (iteraions) => {
                this.programIncreaments = _.filter(iteraions, (i: Iteration) => i.iteration_type != 2 && i.iteration_type != 3);
                this.resetPrograms();
            });
        }

        loadFeatures(program){
            this.storyManager.loadIteration(this.scope.parent.slug, program.id).then((features) => {
                this.setFeatures(features, program);
                this.scope.$emit("storiesChanged");
            });
        }

        loadStories(feature){
            this.storyManager.loadStoriesForRelease(this.projectSlug, feature.id).then((stories) => {
                this.setStories(stories, feature);
                this.scope.$emit("storiesChanged");
            });
        }

        selectAll(feature) {
            if(feature != null){
                _.forEach(this.stories[feature.id], (d:any) => d.selected = true)
                this.scope.$emit("selectionChanged");
            }else{
                this.scope.$broadcast("selectAll");
            }
        }

        siblingSelectAll(iteration: Iteration){
            _.forEach(this.features[iteration.id], (d:any) => d.selected = true)
            this.scope.$emit("selectionChanged");
        }

        selectNone(feature) {
            if(feature != null){
                _.forEach(this.stories[feature.id], (d:any) => d.selected = false)
                this.scope.$emit("selectionChanged");
            }else{
                this.scope.$broadcast("selectNone");
            }
        }

        siblingSelectNone(iteration) {
            _.forEach(this.features[iteration.id], (d:any) => d.selected = false)
            this.scope.$emit("selectionChanged");
        }

        filterPrograms = (program) => {
            if(!this.showArchived && program.hidden) return false;
            return true;
        }

        featureStats(feature){
            var stats = {};
            stats['totalCards'] =  this.stories[feature.id].length;
            stats['totalPoints'] = this.getTotals(this.stories[feature.id]).points;
            stats['totalMinutes'] = this.getTotals(this.stories[feature.id]).minutes;
            stats['businessValue'] = this.getTotals(this.stories[feature.id]).businessValue;
            return stats;
        }

        programStats(program){
            var stats = {};
            stats['totalCards'] =  this.features[program.id].length;
            stats['totalPoints'] = this.getTotals(this.features[program.id]).points;
            stats['totalMinutes'] = this.getTotals(this.features[program.id]).minutes;
            stats['businessValue'] = this.getTotals(this.features[program.id]).businessValue;
            return stats;
        }

        getTotals = (stories) => {
            var ref = getStoryTotals(stories);
            return {points: ref[0], minutes: ref[1], businessValue: ref[2]};
        }

        closeAll(event){
            this.isExpanded = false;
            this.resetPrograms();
            this.resetFeatures();
        }
    }


    export class PlanningSafeBacklogController {
        public static $inject: Array<string> = [
            "$scope",
            "storyManager",
            "projectSlug",
            "storyEditor",
            "projectManager",
            "iterationManager",
            "organizationSlug",
            "userService"
        ];

        private project: Project;
        private sortOrder:any;
        private isExpanded: boolean;
        private stories: Array<Story>;
        private backlogIteration: Iteration;
        private loading: boolean;
        private backlogProject: Project;
        private WorkItemName: string;
        private parentWorkItemName: string;
        private parentStories: Array<Story>;
        private noReleaseCollapsed: boolean = false;

        constructor(
            private scope,
            private storyManager: StoryManager,
            public projectSlug: string,
            private storyEditor: StoryEditor,
            private projectManager: ProjectManager,
            private iterationManager: IterationManager,
            public organizationSlug: string,
            private userService: UserService) {

            this.scope.$on('sortOrderChanged', this.onSortChange);
            this.scope.canWrite = this.userService.canWrite(this.scope.project.slug);
            this.isExpanded = false;
        }

        onSortChange = (event, sort) => {
            if (sort === 'value_time') {
                this.sortOrder = [calculateValueOverTime_withRules, calculateValueOverTime];
            } else if (sort === 'value_point') {
                this.sortOrder = [calculateValueOverPoints_withRules, calculateValueOverPoints];
            } else if (sort === 'wsjf_value') {
                this.sortOrder = calculateWSJFValue;
            } else if (sort !== "rank") {
                this.sortOrder = [sort, "release_rank"];
            } else if (sort === "rank") {
                this.sortOrder = "release_rank";
            } else {
                this.sortOrder = sort;
            }
        }

        toggleExpanded() {
            this.isExpanded = !this.isExpanded;
            if (this.isExpanded) {
                this.initBacklog();
            }
        }

        toggleNoRelease(){
            this.noReleaseCollapsed = !this.noReleaseCollapsed;
        }

        initBacklog(){
            if(this.loading !== false){
                this.loading = true;
            }
            this.projectManager.loadProject(this.organizationSlug, this.scope.backlogProject.slug).then((project) => {
                this.backlogProject = project;
                this.WorkItemName = project.work_item_name;
                this.iterationManager.loadIterations(this.organizationSlug, this.scope.backlogProject.slug)
                    .then((iterations) => {
                        this.backlogIteration = _.find(iterations, (i: Iteration) => i.iteration_type == 0);
                        this.loadParentCards();
                    });
            });
        }

        loadParentCards(){
            let currentLevelNumber = portfolioLevelIdToNumber(this.scope.portfolio.levels, this.scope.project.portfolio_level_id);
            var parentBacklogProject;
            if(currentLevelNumber > 1){
                let parentLevel:PortfolioLevel = _.find(this.scope.portfolio.levels, (l: PortfolioLevel) => 
                                                    l.level_number == currentLevelNumber-1);
                parentBacklogProject = parentLevel.backlog_project;
            }else{
                parentBacklogProject = this.scope.portfolio.root;
            }

            this.parentWorkItemName = parentBacklogProject.work_item_name;

            this.iterationManager.loadIterations(this.organizationSlug, parentBacklogProject.slug).then((iterations) => {
                let backlogIteration = _.find(iterations, (itr: Iteration) => itr.iteration_type == 0);

                this.storyManager.loadIteration(parentBacklogProject.slug, backlogIteration.id)
                                    .then((stories) => {
                                        this.parentStories = stories;
                                        this.loadStories();
                                    });
            });
        }

        loadStories(){
            this.storyManager.loadIteration(this.scope.backlogProject.slug, this.backlogIteration.id).then((stories) => {
                this.stories = stories;
                this.loading = false;
                this.scope.$emit("storiesChanged");
            });
        }

        programStats(){
            var stats = {};
            stats['totalCards'] =  this.stories.length;
            stats['totalPoints'] = this.getTotals(this.stories).points;
            stats['totalMinutes'] = this.getTotals(this.stories).minutes;
            stats['businessValue'] = this.getTotals(this.stories).businessValue;
            return stats;
        }

        getTotals = (stories) => {
            var ref = getStoryTotals(stories);
            return {points: ref[0], minutes: ref[1], businessValue: ref[2]};
        }

        backlogAddCard($event, releaseId){
            var release;
            if(releaseId > 0){
                release = {id: releaseId};
            }else{
                release = null;
            }
            this.storyEditor.createStory(this.backlogProject, { release: release, iteration_id:this.backlogIteration.id });
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

         toggleRelease(Release){
            if(Release['collapsed'] == null){
                Release['collapsed'] = false;
            }else{
                Release['collapsed'] = !Release['collapsed'];
            }
        }

        selectAll(event, releaseId = null) {
            if(releaseId == null){
                return this.scope.$broadcast("selectAll");
            }else{
                var count = this.scope.$root['selectedCount'] ? this.scope.$root['selectedCount'] : 0;
               _.forEach(this.stories, (s:Story) => {
                    if(s.release != null && s.release.id == releaseId && releaseId > 0){
                        s['selected'] = true;
                        count +=1;
                    }else if(releaseId == -1 && s.release == null){
                        s['selected'] = true;
                        count +=1;
                    }
                });
                this.scope.$root['selectedCount'] = count;
            }
        }

        selectNone(event, releaseId = null) {
            if(releaseId == null){
                return this.scope.$broadcast("selectNone");
            }else{
                var count = this.scope.$root['selectedCount'] ? this.scope.$root['selectedCount'] : 0;
                _.forEach(this.stories, (s:Story) => {
                    if(s.release != null && s.release.id == releaseId && releaseId > 0){
                        s['selected'] = false;
                        count -=1;
                    }else if(releaseId == -1 && s.release == null){
                        s['selected'] = false;
                        count -=1;
                    }
                });
                this.scope.$root['selectedCount'] = count;
            }
        }
    }
}