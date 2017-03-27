/// <reference path='../../_all.ts' />

module scrumdo {
    export class DashboardTeamsController{
        public static $inject: Array<string> = [
            "$scope",
            "userService"
        ]

        private accessTypeSearch: string;
        private quickSearch: string = "";

        constructor (private $scope : ng.IScope,
                    private userService: UserService){
            this.accessTypeSearch = 'self';

            this.$scope.$on("$stateChangeStart", this.onStateChangeStart);
            if(this.$scope.$root['dashboardTeamsFilters'] == null){
                this.$scope.$root['dashboardTeamsFilters'] = {};
                this.saveSelection();
            }else{
                this.accessTypeSearch = this.$scope.$root['dashboardTeamsFilters'].access_type;
                this.quickSearch = this.$scope.$root['dashboardTeamsFilters'].quickSearch;
            }
        }

        private onStateChangeStart = (event, toState, toParams, fromState, fromParams) => {
            if(toState.name != 'team' && toState.name !='allmembers'){
                delete this.$scope.$root['dashboardTeamsFilters'];
            }
        }

        private saveSelection(){
            this.$scope.$root['dashboardTeamsFilters'].access_type = this.accessTypeSearch;
            this.$scope.$root['dashboardTeamsFilters'].quickSearch = this.quickSearch;
        }

        private filterTeams = (team) => {
            let teamName: string = team.name;
            let projectName: Array<string> = _.pluck(team.projects, "name");
            let userName: Array<string> = _.map(team.members, (user: User) => {
                return this._getUserKey(user);
            });
            let access: string = this._getAccessName(team.access_type);
            let key: string = this.quickSearch.toLowerCase();

            let nameSearch = teamName.toLowerCase().indexOf(key) !== -1;
            let projectSearch = _.find(projectName, (name: string) => name.toLowerCase().indexOf(key) !== -1);
            let userSearch = _.find(userName, (name: string) => name.toLowerCase().indexOf(key) !== -1);
            let accessSearch = access.toLowerCase().indexOf(key) !== -1;
            let quickSearch = nameSearch || projectSearch || userSearch || accessSearch;
            
            if(this.accessTypeSearch != null && this.accessTypeSearch !== ""){
                if(this.accessTypeSearch != 'self'){
                    return quickSearch && team.access_type == this.accessTypeSearch;
                }else{
                    let myTeam = this.userService.me!=null && 
                                 _.find(userName, (name: string) => name.toLowerCase().indexOf(this.userService.me.username.toLowerCase()) !== -1);
                    return quickSearch && myTeam;
                }
            }else{
                return quickSearch;
            }
        }

        private _getAccessName(type: string): string{
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

        private _getUserKey(option: User): string{
            var v:string, u: string, f: string, l: string;
            u = option.username;
            f = option.first_name != null ? option.first_name : "";
            l = option.last_name != null ? option.last_name : "";
            v = u + " " + f + " " + l;
            return v;
        }
    }   
}