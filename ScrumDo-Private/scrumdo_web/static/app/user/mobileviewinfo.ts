/// <reference path="../_all.ts" />

module scrumdo{

    export class UserMobileViewInfoConroller{

        public static $inject: Array<string> = [
            "$scope",
            "userService"
        ];

        constructor(private $scope: ng.IScope,
                    private userService: UserService){
        }

        me = () => {
            return this.userService.me;
        }
    }
}
