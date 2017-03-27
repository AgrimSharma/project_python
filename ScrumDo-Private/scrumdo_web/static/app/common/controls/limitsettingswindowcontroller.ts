/// <reference path='../../_all.ts' />

module scrumdo {
    export class LimitSettingsWindowController {
        public static $inject:Array<string> = [
            "initialSettings",
            "isParent",
            "$scope",
            "workItemName"
        ];

        constructor(initialSettings:LimitSettings, 
                    private isParent:boolean, 
                    private $scope, 
                    private workItemName: string) {
            $scope.settings = angular.copy(initialSettings);

            if(this.workItemName == null){
                this.workItemName =  this.$scope.$root['safeTerms'].current.work_item_name;
            }
        }

        public ok() {
            this.$scope.$close(this.$scope.settings);
        }

        public cancel() {
            this.$scope.$dismiss();
        }

        public validated(){
            return this.$scope.settings.featureLimit <= 10000 && 
                   this.$scope.settings.featurePointLimit <= 10000 &&
                   this.$scope.settings.cardLimit <= 10000 &&
                   this.$scope.settings.cardPointLimit <= 10000;
        }

    }
}