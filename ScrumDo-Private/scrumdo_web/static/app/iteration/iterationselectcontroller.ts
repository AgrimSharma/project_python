/// <reference path='../_all.ts' />

module scrumdo {


    interface IterationSelectScope extends ng.IScope {
        currentValue: any;
        iterationSortOrder: Array<any>;
        defaultLabel: string;
        alignment: string;
        iterations: Array<Iteration>;
        timePeriodName: string;
        showArchiveOption?: boolean;
        workingOnly?: boolean;
    }

    export class IterationSelectController {
        public static $inject:Array<string> = ["$scope","$rootScope", "$timeout"];

        public showArchived:boolean = false;
        public ngModel:ng.INgModelController;
        public defaultLabel :string;
        private iterationTree:any;
        private menuOpen:boolean;
        public timePeriodName: string;
        private parentToggle: any = {};
        private workingOnly: boolean;

        constructor(private scope:IterationSelectScope, public rootScope, public timeout) {

            scope.iterationSortOrder = ['hidden', 'iteration_type', this.hasNullEnd, '-end_date','name'];
            this.defaultLabel = "None Selected";
            if(scope.defaultLabel != null){
                this.defaultLabel = scope.defaultLabel;
            }
            scope.alignment = scope.alignment || "dropdown-menu-right";
            this.menuOpen = false;
            this.scope.$on("hideDropDown", this.hideDropDown);
            this.timePeriodName = "Iteration";
            if(scope.timePeriodName != null){
                this.timePeriodName = scope.timePeriodName;
            }
            this.workingOnly = this.scope.workingOnly == null ? false : this.scope.workingOnly == true;
        }

        hideDropDown = () => {
            if(this.menuOpen == true){
                this.menuOpen = !this.menuOpen;
            }
        }

        toggleMenu($event: MouseEvent) {
            $event.preventDefault();
            $event.stopPropagation();
            this.menuOpen = !this.menuOpen;
            if(this.menuOpen){
                if($('#safe-iteration-select','.card-project-move-modal').length > 0){
                    $('.modal-body').css({overflow:'hidden'});
                    this.timeout( ()=> {
                        var dropdown = $('.iteration-dropdown', '#safe-iteration-select');
                        var toggleBtn = $('.safe-iteration-dropdown-toggle', '#safe-iteration-select');
                        dropdown.css({ position:'fixed', top:toggleBtn.offset().top, width:'100%' });
                        $('.modal-body').css({overflow:''});
                    },100);
                }
            }else{
                this.parentToggle = {};
            }

        }

        private hasNullEnd(iteration):boolean {
            return iteration.end_date != null;
        }

        public init = (ngModel:ng.INgModelController) => {
            this.ngModel = ngModel;
            if (this.ngModel.$modelValue) {
                this.scope.currentValue = this.ngModel.$modelValue;
            }

            this.ngModel.$render = () => {
                return this.scope.currentValue = this.ngModel.$modelValue;
            };
        }


        public displayArchived($event) {
            this.showArchived = !this.showArchived;
            $event.stopPropagation();
            $event.preventDefault();
        }


        public filterIteration = (iteration) => {
            if(iteration == this.scope.currentValue) {return true;}
            return this.showArchived || ! iteration.hidden;
        }


        public select($event, iteration) {
            this.ngModel.$setViewValue(iteration);
            this.scope.currentValue = iteration;
            // TODO - MARC - The next two lines you merged in, need to understand them.
            this.scope.$emit("filterIterationChanged", iteration);
            this.rootScope.$broadcast("IterationSelected");
            return $event.preventDefault();
        }

        private showParents($event: MouseEvent, iteration: Iteration){
            $event.preventDefault();
            $event.stopPropagation();
            if(this.parentToggle[iteration.id] == null){
                this.parentToggle[iteration.id] = true;
            }else{
                this.parentToggle[iteration.id] = ! this.parentToggle[iteration.id];
            }
        }
    }
}
