/// <reference path="../../_all.ts" />

module scrumdo{
    interface thisScope extends ng.IScope{
        project: Project;
    }

    export class ProjectTeamsInviteController{

        public static $inject:Array<string> = [
            "$scope",
            "organizationSlug",
            "projectSlug",
            "teamManager",
            "userService",
            "ngToast",
            "STATIC_URL"
        ];

        private teams: Array<any>;
        private orgTeams: Array<any>;
        private allMembers: Array<User>;
        private selectedTeam;
        private invitees: Array<any>;
        private canAdmin: boolean;
        private isTeamAdmin: boolean;
        private filteredTeams: Array<any>;
        private orgFilteredTeams: Array<any>;
        private loading: boolean = false;

        constructor(private $scope: thisScope,
                    private organizationSlug: string,
                    private projectSlug: string,
                    private teamManager: TeamManager,
                    private userService: UserService,
                    private ngToast,
                    private STATIC_URL: string){

            this.isTeamAdmin = true;
            this.loadAllTeams();
            this.loadProjectTeams();

            this.invitees = [{ 'name': "" }];
        }


        loadProjectTeams(){
            this.loading = true;
            this.teamManager.loadProjectTeams(this.organizationSlug, this.projectSlug).then((teams) => {
                this.teams = teams.self_teams;
                this.loading = false;
            });
        }

        loadAllTeams(){
            this.teamManager.loadTeams(this.organizationSlug).then((teams) => {
                this.orgTeams = teams;
                this.getAllMembers();
            });
        }

        getAllMembers(){
            var members = [];
            var ref = this.orgTeams;

            for (var i = 0, len = ref.length; i < len; i++) {
                let team = ref[i];
                members = members.concat(team.members);
            }
            this.allMembers = _.uniq(members, false, (user) => user.username);
        }

        selectTeam(team){
            this.selectedTeam = team;
        }

        sendInvitations() {
            this.teamManager.inviteUser(this.organizationSlug, this.selectedTeam, this.invitees).success(this.onInvite);
        }
        
        doNothing($event: MouseEvent){
            $event.preventDefault();
            $event.stopPropagation();
        }

        onInvite = (response) => {
            this.invitees = _.filter(response.users, (user: { result }) => (user.result == null) || !user.result.success);
            var successCount = (_.filter(response.users, (user: { result }) => (user.result != null) && user.result.success)).length;
            var addedCount = (_.filter(response.users, (user: { result }) => (user.result != null) && user.result.reason === 'User Added')).length;

            if (successCount > 0 && addedCount === 0) {
                this.ngToast.create((successCount - addedCount) + " Invitations Sent for Team "+ this.selectedTeam.name);
            } else if (successCount > addedCount && addedCount > 0) {
                this.ngToast.create((successCount - addedCount) + " Invitations Sent, " + addedCount + " users added to Team"+ this.selectedTeam.name);
            } else if (addedCount > 0) {
                this.ngToast.create(addedCount + " users added to Team"+ this.selectedTeam.name);
            }

            this.$scope.$emit("projectMembersUpdated", null);
        }

        teamFilter = (team) => {
            if(this.$scope.project.project_type == 2){
                return team.access_type == 'staff' && this.userService.me.staff;
            }else{
                return this.canAdminTeam(team) && team.access_type != 'staff' && this.canStaff(team);
            }
        }

        inviteeChanged() {
            var invitees = this.invitees;
            if (invitees[invitees.length - 1].name.length > 0) {
                invitees.push({ 'name': "" });
            }
        }

        canAdminTeam(team){
            var isTeamAdmin: boolean = true;
            if(this.userService.me == null){
                isTeamAdmin = false;
            }
            if(!this.userService.me.staff && team.projects.length == 0){
                isTeamAdmin = false;
            }
            _.forEach(team.projects, (p:any) => {
                if(!this.userService.canAdmin(p.slug)){
                    isTeamAdmin = false;
                }
            });
            return isTeamAdmin;
        }

        canStaff(team){
            var isTeamStaff: boolean = true;
            if(this.userService.me == null){
                isTeamStaff = false;
            }
            if(!this.userService.me.staff && team.access_type == 'admin'){
                isTeamStaff = false;
            }
            return isTeamStaff;
        }

        private getAccessName(type: string): string{
            var name: string;
            switch (type){
                case 'read':
                    name = "Read Only";
                break;
                case 'write':
                    name = "Read/Write";
                break;
                case 'admin':
                    name = "Workspace Manager";
                break;
                case 'staff':
                    name = "Account Owner";
                break;
            }
            return name;
        }
         
    }
}
