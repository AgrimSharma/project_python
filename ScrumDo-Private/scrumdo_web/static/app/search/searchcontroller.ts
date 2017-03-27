/// <reference path='../_all.ts' /> 

module scrumdo {
 
    export class SearchController {
        public static $inject: Array<string> = [
            "$scope",
            "$stateParams",
            "storyManager",
            "projectManager",
            "organizationSlug",
            "projectSlug",
            "initialSearchTerms",
            "iterationManager"
        ];

        private project;
        private loading: boolean;
        private busyMode: boolean = false;
        private lastQuery: string;
        private currentPage;
        private maxPage;
        private storyCount;
        private stories;
        private searchKey: string;
        private searchBacklog: boolean = false;
        private searchArchive: boolean = false;

        constructor(
            private scope,
            public $stateParams:ng.ui.IStateParamsService,
            private storyManager: StoryManager,
            private projectManager: ProjectManager,
            public organizationSlug: string,
            public projectSlug: string,
            private initialSearch,
            private iterationManager: IterationManager ) {

            if (projectSlug != '') {
                this.projectManager.loadProject(this.organizationSlug, this.projectSlug).then((result) => {
                    this.project = result;
                    this.scope.project = result;
                });
                this.iterationManager.loadIterations(this.organizationSlug, this.projectSlug).then((result) => {
                    this.scope.iterations = result;
                });
            }

            this.loading = false;
            
            if ($stateParams['q'] !== '' || initialSearch !== '') {
                let searchKey = $stateParams['q']? $stateParams['q'] : initialSearch;
                this.searchKey = searchKey;
                if(searchKey != ''){
                    this.search(searchKey);
                }
            }
        }

        search(query) {
            this.loading = true;
            this.searchKey = query;
            this.lastQuery = query;
            if (this.projectSlug === '') {
                this.storyManager.searchOrganization(query).then(this.onStoriesLoaded);
            } else {
                this.storyManager.searchProject(this.projectSlug, query, 1, 
                                                this.searchBacklog, 
                                                this.searchArchive).then(this.onStoriesLoaded);
            }
        }

        pageChanged() {
            this.busyMode = true;
            if (this.projectSlug === '') {
                this.storyManager.searchOrganization(this.lastQuery, this.currentPage).then(this.onStoriesLoaded);
            } else {
                this.storyManager.searchProject(this.projectSlug, this.lastQuery, this.currentPage).then(this.onStoriesLoaded);
            }
        }

        onStoriesLoaded = (stories) => {
            this.loading = false;
            this.busyMode = false;
            this.maxPage = stories.max_page;
            this.storyCount = stories.count;
            this.currentPage = stories.current_page;
            this.stories = _.map(stories.items, this.storyManager.wrapStory); 
        }

        cancel(){
            this.scope.$dismiss();
        }

        refreshSearch(){
            this.search(this.lastQuery);
        }
    }
}