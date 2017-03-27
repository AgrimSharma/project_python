/// <reference path="../../_all.ts" />

module scrumdo{

    export class IterationSettingsController{

        public static $inject:Array<string> = [
            "$scope",
            "organizationSlug",
            "projectSlug",
            "iterationManager",
            "projectDatastore",
            "iterationWindowService"
        ];

        private allIterations: Array<Iteration>;
        private editing: Iteration;
        private continuousIterations: Array<Iteration>;
        private continousTab: boolean;
        private activeTab: number = 0;

        constructor(private $scope: ng.IScope,
                    private organizationSlug: string,
                    private projectSlug: string,
                    private iterationManager: IterationManager,
                    private projectDatastore: ProjectDatastore,
                    private iterationWindowService: IterationWindowService){
            
            if(this.projectDatastore.currentProject.project_type != 2){
                this.activeTab = 0;
            }else{
                this.activeTab = 1;
            }
            this.allIterations = this.projectDatastore.iterations.sort(this.iterationSortOrder);
            this.filterContinuousIterations();
        }

        filterContinuousIterations(){
            this.continousTab = true;
            this.editing = null;
            this.continuousIterations = _.filter(this.allIterations, (itr: Iteration) => itr.iteration_type == 1 && 
                                                                                        !itr.hidden &&
                                                                                        itr.end_date == null);
        }

        filterIterations(){
            this.continousTab = false; 
            this.allIterations = this.projectDatastore.iterations.sort(this.iterationSortOrder);
        }

        editingIteration = () => {
            return _.findWhere(this.allIterations, {id: this.editing.id});
        }

        private addNew(){
            this.iterationWindowService.createIteration(this.organizationSlug, this.projectSlug, {}, "iteration");
        }

        public iterationSortOrder(a, b) {
            if (a.hidden && !b.hidden) {
                return 1;
            }
            if (b.hidden && !a.hidden) {
                return -1;
            }

            if ((a.end_date == null) && (b.end_date != null)) {
                return -1;
            }

            if ((b.end_date == null) && (a.end_date != null)) {
                return 1;
            }

            if ((a.end_date == null) && (b.end_date == null)) {
                // Both are null, compare by name
                if (a.name > b.name) {
                    return -1;
                } else {
                    return 1;
                }
            }

            if (a.end_date > b.end_date) {
                return -1;
            } else if (a.end_date < b.end_date) {
                return 1;
            }
            return 0;
        }
    }
}