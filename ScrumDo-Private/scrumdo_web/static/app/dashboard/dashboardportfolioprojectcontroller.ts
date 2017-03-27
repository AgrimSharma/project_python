/// <reference path='../_all.ts' />

module scrumdo {
    export class DashboardPortfolioProjectController {
        public static $inject: Array<string> = [
            "$scope",
            "$window"
        ];

        constructor(private scope, private window:ng.IWindowService) {
            if (!((this.scope.project != null) && (this.scope.project.stats != null))) {
                return;
            }

            this.scope.stats = getProjectStatsWithLabel(this.scope.project);
            this.scope.showInactive = false;
            this.scope.showOnlyWatched = false;
            
        }


        onClick($event) {
            if($event.target.nodeName == 'LI') {
                $event.preventDefault();
                this.window.location.replace("/projects/" + this.scope.project.slug + "/board");
            }
        }

    }
}