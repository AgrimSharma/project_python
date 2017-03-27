/// <reference path='../../_all.ts' />

module scrumdo{
    export class ProjectTeamSettingsController{

        public static $inject:Array<string> = [
            "$scope",
            "organizationSlug",
            "projectSlug",
            "userService",
            "teamManager",
            "$state"
        ];

        private projectTeams: Array<any>;
        private loadingTeams: boolean;
        private newTeamName:string;
        private newTeamAccess_type:string;
        private canAddTeam: boolean;

        constructor(private $scope: ng.IScope,
                    private organizationSlug: string,
                    private projectSlug: string,
                    private userService: UserService,
                    private teamManager: TeamManager,
                    private $state: ng.ui.IStateService){

            this.projectTeams = [];
            this.loadingTeams = true;
            this.newTeamName = "";
            this.newTeamAccess_type = "write";
            this.canAddTeam = this.userService.isOrgStaff();

            if(this.$state.current.name == 'app.settings.newteam' && !this.canAddTeam){
                this.$state.go('app.settings.teams');
                return;
            }
        }

        loadTeams(){
            this.teamManager.loadProjectTeams(this.organizationSlug, this.projectSlug).then((teams) => {
                this.projectTeams = teams;
                this.loadingTeams = false;
            });
        }

        getTeamAccessLabel(team){
            var name: string;
            switch (team.access_type) {
                case 'read':
                    name = "Read Only Access";
                    break;
                case 'write':
                    name = "Read/Write Access";
                    break;
                case 'admin':
                    name = "Workspace Manager Access";
                    break;
                case 'staff':
                    name = "Account Owner Access";
                    break;
            }
            return name;
        }

        createTeam() {
            if (this.newTeamName === '') {
                return;
            }
            this.teamManager.createTeam(this.organizationSlug, { name: this.newTeamName}).then(this.onTeamCreated);
        }

        onTeamCreated = (team) => {
            this.teamManager.addProject(this.organizationSlug, team, this.projectSlug).then(() => {
                this.$state.go("app.settings.teams");
            });
        }
    }
}