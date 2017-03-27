/// <reference path='../_all.ts' />

module scrumdo {
    
    interface thisScope extends ng.IScope{
        iteration: Iteration;
        dateOptions: any;
        projectSlug: string;
        iterationCopy: Iteration;
        iterationForm: ng.IFormController;
    }

    export class IterationEditorController {
        public static $inject: Array<string> = [
            "$scope",
            "iterationManager",
            "projectSlug",
            "organizationSlug",
            "confirmService",
            "scrumdoTerms",
            "projectManager",
            "programIncrementManager",
            "ngToast"
        ];

        private startOpened: boolean;
        private endOpened: boolean;
        private busyMode: boolean;
        private validDate: boolean;
        private parentProjects: Array<any>;
        private parentProject: any;
        private parentIterations: Array<any>;
        private parentIteration: any;
        private parentScedules: Array<any>;
        private parentScedule: any;
        private iterationCopy: Iteration;
        private timePeriodName: string;
        private currentTimePeriodName: string;
        private previousIteration: Iteration;
        private advanceOpen: boolean = true;
        private allSet: boolean;
        

        constructor(
            private scope : thisScope,
            private iterationManager: IterationManager,
            public projectSlug: string,
            public organizationSlug: string,
            private confirmService: ConfirmationService,
            private scrumdoTerms: ScrumDoTerms,
            private projectManager: ProjectManager,
            private programIncrementManager: ProgramIncrementManager,
            private ngToast) {

            this.startOpened = false;
            this.endOpened = false;
            this.busyMode = false;
            this.validDate = true;
            this.scope.dateOptions = {
                formatYear: 'yy',
                startingDay: 1
            };
            if(this.scope.projectSlug != null){
                this.projectSlug = this.scope.projectSlug;
            }
            this.parentProjects = [];
            this.parentIterations = null;
            this.parentScedule = null;
            this.setParentProjects();
            this.scope.iteration = angular.copy(this.scope.iterationCopy);

            if(this.scope.$root['safeTerms'] == null){
                this.timePeriodName = "Iteration";
                this.currentTimePeriodName = "Iteration";
            }else{
                if(this.scope.$root['safeTerms'].parent.time_period_name == null){
                    this.timePeriodName = this.scope.$root['safeTerms'].current.time_period_name;
                }else{
                    this.timePeriodName = this.scope.$root['safeTerms'].parent.time_period_name;
                }
                this.currentTimePeriodName = this.scope.$root['safeTerms'].current.time_period_name;
            }

            if(this.scope.iteration.id === -1){
                // auto fill some fields based on Previous one
                this.loadProjectIterations();
            }

            if(this.scope.iteration.increment != null){
                this.advanceOpen = false;
            }

        }

        loadProjectIterations(){
            this.iterationManager.loadIterations(this.organizationSlug, this.projectSlug).then((iterations) => {
                this.previousIteration = this._getPreviousIteration(iterations);
                this.newIterationProps();
            });
        }

        newIterationProps(){
            if(this.previousIteration != null){
                let itr = this.previousIteration;
                if(itr.end_date != null){
                    this.scope.iteration.start_date = moment(itr.end_date).add(1, 'day').format('YYYY-MM-DD');
                    if(itr.start_date != null){
                        let e = moment(itr.end_date)
                        var d = moment.duration(e.diff(moment(itr.start_date))).asDays();
                        this.scope.iteration.end_date = moment(itr.end_date).add(d, 'day').format('YYYY-MM-DD');
                    }
                }
                this.scope.iteration.increment = itr.increment;
                this.scope.iteration.name = this._checkForIterationName();
                if(this.scope.iteration.increment != null){
                    this.advanceOpen = false;
                }
                this.allSet = true;
            }
        }

        _checkForIterationName(){
            // this will detect if there is any sequesnce in previous Iteration
                let name = this.previousIteration.name;
                let index = name.lastIndexOf('.');
                var iterationName: string = "";
                if(index > -1){
                    iterationName = this._getSeperatedString(name, '.');
                }else{
                    let index = name.lastIndexOf(' ');
                    if(index > -1){
                        iterationName = this._getSeperatedString(name, ' ');
                    }else{
                        iterationName = `${name}.2`;
                    }
                }
                return iterationName
        }

        _getSeperatedString(name:string, sep:string){
            var iterationName: string = "";
            let parts = name.split(sep);
            let no = parseInt(parts[parts.length - 1]);
            if(!isNaN(no)){
                let next = no + 1;
                parts[parts.length - 1] = next.toString();
                iterationName = parts.join(sep);
            }else{
                if(sep == ' '){
                    iterationName = `${name}.2`;
                }
            }
            return iterationName;
        }

        _getPreviousIteration(iterations: Array<Iteration>){
            let non_continous = _.filter(iterations, (i: Iteration) => i.end_date != null && i.hidden == false && i.iteration_type == 1);
            let continous = _.filter(iterations, (i: Iteration) => i.end_date == null && i.hidden == false && i.iteration_type == 1);
            var sorted;
            if(non_continous.length > 0){
                sorted = _.sortBy(non_continous, 'end_date')
            }else{
                sorted = _.sortBy(continous, 'id')
            }
            if(sorted.length > 0){
                return sorted[sorted.length - 1];
            }else{
                return null;
            }
        }
        

        checkDates() {
            if ((this.scope.iteration.start_date == null) || !this.scope.iteration.end_date) {
                this.validDate = true;
                return;
            }
            this.validDate = this.scope.iteration.start_date <= this.scope.iteration.end_date;
        }

        openStartDatePicker = ($event: MouseEvent) => {
            trace("openStartDatePicker");
            this.startOpened = true;
            $event.preventDefault();
            $event.stopPropagation();
        }

        openEndDatePicker = ($event: MouseEvent) => {
            trace("openEndDatePicker");
            this.endOpened = true;
            $event.preventDefault();
            $event.stopPropagation();
        }

        deleteIteration() {
            this.confirmService.confirm("Are you sure?",
                "This will delete the iteration.  Any stories in it will be moved to your backlog.  Are you sure?",
                "Cancel",
                "Delete",
                "btn-warning").then(this.onDeleteConfirm);
        }

        onDeleteConfirm = () => {
            var iterationCopy = angular.copy(this.scope.iterationCopy);
            this.iterationManager.deleteIteration(this.organizationSlug, this.projectSlug, this.scope.iterationCopy).then(()=>{
                // for planning app to set currentIteration to null if deleted same
                this.scope.$emit("iterationDeleted", iterationCopy);
                try{
                    this.scope.$parent["$dismiss"]("deleted");
                }catch(e){
                    this.showToast(`${this.timePeriodName} ${iterationCopy.name} deleted.`);
                }
            });
        }

        save() {
            this.busyMode = true;
            if (this.scope.iterationCopy.id === -1) {
                this.iterationManager.createIteration(this.organizationSlug, this.projectSlug, this.scope.iteration).then((iteration) => {
                    angular.copy(this.scope.iteration, this.scope.iterationCopy);
                    iteration.selected = true;
                    try{
                        this.scope.$parent["$dismiss"]("created");
                    }catch(e){
                        this.showToast(`${this.timePeriodName} ${this.scope.iteration.name} created.`);
                    }
                    // inform on team planning to reload increment
                    this.scope.$root.$broadcast("iterationWindowClosed", iteration);
                });
            } else {
                this.iterationManager.saveIteration(this.organizationSlug, this.projectSlug, this.scope.iteration).then(() => {
                    this.busyMode = false;
                    angular.copy(this.scope.iteration, this.scope.iterationCopy);
                    try{
                        this.scope.$parent["$dismiss"]("created");
                    }catch(e){
                        this.showToast(`${this.timePeriodName} ${this.scope.iteration.name} updated.`);
                    }
                    // inform on team planning to reload increment
                    this.scope.$root.$broadcast("iterationWindowClosed", this.scope.iteration);
                });
            }
        }

        private setParentProjects(){
            this.projectManager.loadProject(this.organizationSlug, this.projectSlug).then((project:Project) => {
                this.parentProjects = project.parents;
            });
        }

        private loadParentIterations(){
            if(this.parentProject == null){
                this.parentIterations = null;
                return;
            }
            this.iterationManager.loadIterations(this.organizationSlug, this.parentProject.slug).then( (iterations) =>{
                this.parentIterations = iterations;
            });
        }

        private addParentIncrement(){
            if(this.parentIterations == null){
                return;
            }
            if(this.scope.iteration.increment == null){
                this.scope.iteration.increment = [];
            }
            this.scope.iteration.increment.push({
                "name": this.parentIteration.name,
                "id": this.parentIteration.id,
                "project_name": this.parentProject.name,
                "start_date": this.parentIteration.start_date,
                "end_date": this.parentIteration.end_date
            });
        }

        private alreadyAdded(){
            if (this.parentIteration == null){
                return false;
            }
            return _.find(this.scope.iteration.increment, (inc: IterationIncrement) => inc.id == this.parentIteration.id) != null;
        }

        private showToast(message:string){
            this.ngToast.create({
                content: message,
                timeout: 1000,
                dismissButton: true
            });
        }

        private removeParent(inc: IterationIncrement){
            var index = this.scope.iteration.increment.indexOf(inc);
            if(index > -1){
                this.scope.iteration.increment.splice(index, 1);
            }
            if(this.scope.iteration.increment.length == 0){
                this.scope.iteration.increment = null;
            }
            this.scope.iterationForm.$setDirty();
        }

        toggleAdvanceSection($event: MouseEvent){
            $event.preventDefault()
            this.advanceOpen = !this.advanceOpen;
        }
    }
}