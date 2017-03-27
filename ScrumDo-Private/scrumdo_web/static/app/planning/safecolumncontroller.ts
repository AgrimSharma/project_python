/// <reference path='../_all.ts' />

module scrumdo {

    interface thisScope extends ng.IScope{
        project: Project;
        cardSize: string;
        planningCtrl: scrumdo.PlanningController
    }

    export class SafeColumnController {
        public static $inject: Array<string> = [
            "organizationSlug",
            "$scope"
        ];

        private parentsExpended: boolean = false;
        private siblingExtended: boolean = false;
        private backlogExtended: boolean = false;
        private siblingProjects: Array<PortfolioProjectStub>;
        private backlogProject: PortfolioProjectStub;
        private portfolio: Portfolio;

        constructor(
            public organizationSlug: string,
            private scope: thisScope) {
            this.portfolio = this.scope.planningCtrl.projectData.portfolio;
            this.setSiblingProjects();
            this.setBacklogProject();
        }

        private toggleParents(){
            this.parentsExpended = ! this.parentsExpended;
        }

        private toggleSibling(){
            this.siblingExtended = ! this.siblingExtended;
        }


        private toggleGlobalBacklog(){
            this.backlogExtended = ! this.backlogExtended;
        }

        setSiblingProjects(){
            this.siblingProjects = this.scope.planningCtrl.projectData.getSiblingProjects(
                                                this.scope.project.slug, 
                                                this.scope.project.portfolio_level_id);
        }

        setBacklogProject(){
            this.backlogProject = this.scope.planningCtrl.projectData.getGlobalBacklog(this.scope.project.portfolio_level_id)
        }
    }
}