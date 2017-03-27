/// <reference path="../_all.ts" />

module scrumdo{

    interface thisScope extends ng.IScope{
        iteration: Iteration;
        viewType: string;
    }

    export class IterationOverviewController{

        public static $inject:Array<string> = [
            "$scope",
            "iterationManager",
            "iterationWindowService",
            "projectSlug",
            "organizationSlug",
            "confirmService",
            "boardHeadersManager",
            "boardCellManager",
            "$state"
        ];

        private cells: Array<BoardCell>;
        private headers: Array<BoardHeader>;
        private timePeriodName: string;

        constructor(private $scope: thisScope,
                    private iterationManager: IterationManager,
                    private iterationWindowService: IterationWindowService,
                    private projectSlug: string,
                    private organizationSlug: string,
                    private confirmService: ConfirmationService,
                    private headersManager: BoardHeadersManager,
                    private cellManager: BoardCellManager,
                    private $state: ng.ui.IStateService){
            
            this.$scope.$watch("viewType", this.onViewChange);
            
            if(this.$scope.$root['safeTerms'] == null){
                this.timePeriodName = "Iteration";
            }else{
                this.timePeriodName = this.$scope.$root['safeTerms'].current.time_period_name;
            }
        }

        onViewChange = () => {
            if(this.$scope.viewType == 'kanban'){
                this.loadCellHeaders();
            }
        }

        public gotoIteration(){
            if(this.$scope.iteration.iteration_type == 1){
                this.$state.go("app.iteration.board", {iterationId: this.$scope.iteration.id});
            }else{
                this.$state.go("app.iteration.cards", {iterationId: this.$scope.iteration.id});
            }
        }

        editIteration(){
            this.iterationWindowService.editIteration(this.organizationSlug, 
                                                      this.projectSlug, 
                                                      this.$scope.iteration,
                                                      this.timePeriodName);
        }

        public deleteIteration(){
            this.confirmService.confirm("Are you sure?",
                `This will delete the ${this.timePeriodName} ${this.$scope.iteration.name}. Any stories in it will be moved to your backlog.`,
                "Cancel",
                "Delete",
                "btn-warning").then(() => this.onDeleteConfirm());
        }

        public onDeleteConfirm(){
            this.iterationManager.deleteIteration(this.organizationSlug, this.projectSlug, this.$scope.iteration).then(()=>{

            });
        }

        private percentage(val, total) {
            return Math.round(100 * val / total);
        }

        private todoPercentage() {
            var todo = this.$scope.iteration.story_count - this.$scope.iteration.done_count - this.$scope.iteration.doing_count;
            return this.percentage(todo, this.$scope.iteration.story_count);
        }

        private loadCellHeaders(){
            this.headersManager.loadHeaders(this.organizationSlug, this.projectSlug).then((headers: Array<BoardHeader>) => {
                this.headers = headers;
            });
            this.cellManager.loadCells(this.organizationSlug, this.projectSlug).then((cells: Array<BoardCell>) => {
                this.cells = cells;
            });
        }

        private showProgress(){
            this.iterationWindowService.iterationProgress(this.projectSlug, this.$scope.iteration);
        }
    }
}