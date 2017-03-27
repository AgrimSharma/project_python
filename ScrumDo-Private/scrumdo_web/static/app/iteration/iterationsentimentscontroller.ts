/// <reference path="../_all.ts" />

module scrumdo{

    export class IterationSentimentController{
        public static $inject: Array<string> = [
            "$scope",
            "projectSlug",
            "organizationSlug",
            "projectData"
        ];

        private teams: Array<any>;
        private currentProjectTeam: any;

        constructor(private $scope:ng.IScope,
                    private projectSlug: string,
                    private organizationSlug: string,
                    private projectData: ProjectDatastore){
            
            this.setupTeams();
        }

        private setupTeams(){
            var project = this.projectData.currentProject;
            this.currentProjectTeam = {slug:project.slug, name:project.name, icon: project['icon'], color: project['color']};
            if(this.projectData.currentIncrement.schedule == null || this.projectData.currentIncrement.schedule.length == 0){
                return;
            }
            this.teams = this.projectData.getIncrementTeams().map((ii:IncrementIteration) =>
                    ({slug:ii.project_slug, name:ii.project_name, icon: ii.project_icon, color: ii.project_color}));
        }
    }
}