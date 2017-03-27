/// <reference path='../_all.ts' />

module scrumdo {

    interface ReleasePickerScope extends ng.IScope {
        story:Story;
        project:Project;
        release:MiniRelease;
    }


    export class ReleasePickerController {

        public tooltip:string;
        public userSearchInput:string = '';

        public options:PagedMiniReleaseResponse;

        public isLoading:boolean = false;

        public menuOpen:boolean = false;
        public selectedParent:MiniParentProject = null;

        private lastSearch:string;
        private currentPage:number = 1;
        private workItemName:string;


        public static $inject:Array<string> = [
            "$scope",
            "storyAssignmentManager"
        ];

        constructor(private $scope:ReleasePickerScope,
                    private storyAssignmentManager:StoryAssignmentManager) {

            if(this.$scope.story == null){
                this.$scope.story = <any> {id: -1};
            }
            if(this.$scope.project.parents.length > 0) {
                this.selectedParent = this.$scope.project.parents[0]
            }

            this.setWorkItemName();
            this.tooltip = `Choose ${this.workItemName} for this card.`;
        }

        setWorkItemName(){
            if(this.$scope.project.parents.length > 0){
                let parent = this.$scope.project.parents[0];
                this.workItemName = parent.work_item_name;
            }else{
                this.workItemName = "Release";
            }
        }

        loadAssignments(pageToLoad:number=1, onSuccess=this.onAssignments) {
            let hash = this.$scope.project.slug + this.$scope.story.id + this.selectedParent.slug + this.userSearchInput + pageToLoad;
            if(this.lastSearch==hash) return;
            this.lastSearch = hash;
            this.isLoading = true;
            this.currentPage = pageToLoad;
            this.storyAssignmentManager
                .loadPossibleAssignments(
                    this.$scope.project.slug,
                    this.$scope.story.id,
                    this.selectedParent.slug,
                    this.userSearchInput,
                    20,
                    pageToLoad).then(onSuccess)
        }

        public doNothing($event: MouseEvent){
            $event.preventDefault();
            $event.stopPropagation();
        }

        private onAssignments = (event) => {
            this.isLoading = false;
            this.options = event.data;
        }

        private onMoreAssignments = (event) => {
            this.isLoading = false;

            let newOptions:PagedMiniReleaseResponse = event.data;
            newOptions.items = this.options.items.concat(newOptions.items);

            this.options = newOptions;
        }

        hasMore():boolean {
            if(!this.options) {
                return false;
            }
            return this.options.current_page < this.options.max_page;
        }

        toggleMenu($event) {
            $event.preventDefault();
            $event.stopPropagation();
            this.menuOpen = !this.menuOpen;
            if(this.menuOpen){
                this.loadAssignments();
            }
        }

        getLabel(option:MiniRelease):string {
            if(!option) {
                return this.workItemName;
            }
            var prefix = option.project_prefix != null ? option.project_prefix : option["prefix"]; 
            return `${prefix}-${option.number} - ${option.summary}`;
        }

        showMore($event){
            $event.preventDefault();
            this.loadAssignments(this.currentPage+1, this.onMoreAssignments)
        }

        select($event, option:MiniRelease) {
            $event.preventDefault();
            this.$scope.release = option;
            this.menuOpen = false;
        }
    }
}