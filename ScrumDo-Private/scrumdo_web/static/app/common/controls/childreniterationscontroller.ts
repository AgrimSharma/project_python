/// <reference path="../../_all.ts" />

module scrumdo{

    interface thisScope extends ng.IScope{
        parentProject: Project;
        parentIteration: Iteration;
        action: string;

    }

    export class ChildrenIterationsController{
        public static $inject: Array<string> = [
            "$scope",
            "organizationSlug",
            "projectSlug",
            "projectManager",
            "iterationManager",
            "iterationWindowService"
        ]

        private selectedProject;
        private loading: boolean = false;
        private iterations: Array<Iteration>;
        private timePeriodName: string;
        private action: string;
        private workingOn: Iteration;

        constructor(private $scope: thisScope,
                    private organizationSlug: string,
                    private projectSlug: string,
                    private projectManager: ProjectManager,
                    private iterationManager: IterationManager,
                    private iterationWindowService: IterationWindowService){

            this.$scope.$on("iterationWindowClosed", this.onIterationWindowClosed);
            if(this.$scope.$root['safeTerms'] != null){
                this.timePeriodName = this.$scope.$root['safeTerms'].children.time_period_name != null?
                                        this.$scope.$root['safeTerms'].children.time_period_name :
                                        'Iteration';
            }else{
                this.timePeriodName = 'Iteration';
            }

            this.action = this.$scope.action == null ? 'edit' : this.$scope.action;

        }

        selectProject(child){
            this.selectedProject = child;
            this.loading = true;
            this.iterations = null;
            this.loadIterations(true);
        }

        loadIterations(forceLoad: boolean = false){
            if(this.selectedProject !=null){
                let child = this.selectedProject;
                this.iterationManager.loadIterations(this.organizationSlug, child.slug, forceLoad).then((iterations) => {
                    this.iterations = _.filter(iterations, (i: Iteration) => i.iteration_type ==1 && i.hidden == false);
                    this.loading = false;
                    this.workingOn = null;
                });
            }
        }

        editIteration(iteration: Iteration){
            this.iterationWindowService.editIteration(this.organizationSlug, this.selectedProject.slug, iteration);
        }

        linkToParent(iteration){
            var iterationCopy:Iteration = angular.copy(iteration);
            this.workingOn = iteration;
            let increment = {
                "name": this.$scope.parentIteration.name,
                "id": this.$scope.parentIteration.id,
                "project_name": this.$scope.parentProject.name,
                "start_date": this.$scope.parentIteration.start_date,
                "end_date": this.$scope.parentIteration.end_date
            }
            if(iterationCopy.increment == null){
                iterationCopy.increment = [increment];
            }else{
                iterationCopy.increment.push(increment);
            }
            this.iterationManager.saveIteration(this.organizationSlug, 
                                                this.selectedProject.slug, 
                                                iterationCopy).then((itr: Iteration) => {
                this.loadIterations(true);
                this.$scope.$emit("onChildIterationUpdated", null);
            });
        }

        isAdded(iteration: Iteration){
            if (this.$scope.parentIteration == null){
                return false;
            }
            return _.find(iteration.increment, (inc: IterationIncrement) => inc.id == this.$scope.parentIteration.id) != null;
        }

        onIterationWindowClosed = () => {
            this.loadIterations(true);
            this.$scope.$emit("onChildIterationUpdated", null);
        }
    }
}
