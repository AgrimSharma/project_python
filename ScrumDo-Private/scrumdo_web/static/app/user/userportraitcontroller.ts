/// <reference path='../_all.ts' /> 

module scrumdo {

    interface thisScope extends ng.IScope{
        user: User;
        size: number;
    }

    export class UserPortraitController{

        public static $inject: Array<string> = [
            "$scope",
            "realtimeService"
        ];

        private isOnline: boolean;
        
        constructor(private $scope: thisScope,
                    private realtimeService: RealtimeService){

            this.isOnline = false;
            this.$scope.$on("presenceDataUpdated", this.onPresenceDataUpdated);
            this.updateUserStatus();

        }

        public updateUserStatus(){
            this.isOnline = this.checkUserPresense();
        }

        onPresenceDataUpdated = (event, data) => {
            this.isOnline = this.checkUserPresense();
        }

        private checkUserPresense(): boolean{
            if(this.$scope.user == null){
                return false;
            }
            return _.findWhere(_.values(this.realtimeService.allUsers), {user_id: this.$scope.user.id}) != null;
        }

        private getMemberTooltip(){
            if(this.isOnline){
                return "Online";
            }else{
                return "Offline";
            }
        }
    }   
}