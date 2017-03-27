/// <reference path="../_all.ts" />

module scrumdo{

    interface thisScope extends ng.IScope{
        project: Project;
        release: Story;
    }

    export class ReleaseTeamDisplayController{

        public static $inject: Array<string> = [
            "$scope",
            "projectSlug",
            "organizationSlug",
            "releaseStatManager",
            "programIncrementManager"
        ];

        private teams: Array<MiniParentProject>;
        private teamStats: any;
        private increment;

        constructor(private $scope: thisScope,
                    private projectSlug: string,
                    private organizationSlug: string,
                    private releaseStatManager: ReleaseStatManager,
                    private programIncrementManager: ProgramIncrementManager){
            
            this.teams = this.$scope.project.children;
            this.loadTeamStats();
        }


        loadTeamStats(){
            this.releaseStatManager.loadReleaseTeamStats(this.organizationSlug,
                                                this.$scope.project.slug,  
                                                this.$scope.release.iteration_id,
                                                this.$scope.release.id).then((stats) => {
                this.teamStats = stats;
            });
        }

        private filterTeams = (team) => {
            if(!team.active){
                return false;
            }
            if(this.teamStats != null && this.teamStats[team.slug] != null){
                return true;
            }
            return false;
        }

        public percentage(val, total):number {
            if(total==0){return 0;}
            return Math.round(100 * val / total);
        }

        private getTooltip(team: MiniParentProject){
            if(this.teamStats != null && this.teamStats[team.slug] != null){
                var html = `Total Cards: ${this.teamStats[team.slug].cards_total}`;
                html += `<br/>Cards In Progress: ${this.teamStats[team.slug].cards_in_progress}`;
                html += `<br/>Cards Completed: ${this.teamStats[team.slug].cards_completed}`;
                return html;
            }else{
                return null;
            }
        }
    }
}