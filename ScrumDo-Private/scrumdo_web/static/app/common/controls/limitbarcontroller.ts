/// <reference path='../../_all.ts' />

module scrumdo {

    interface StatItem {
        label:string;
        value:number;
        limit:number;
        workItemName: string;
    }


    export interface StatGroups extends Array<Array<StatItem>> { }


    export class LimitBarController {
        public static $inject:Array<string> = ["$scope"];

        private displayType: string;
        private workItemName: string;

        constructor(private $scope) {

            this.displayType = this.$scope.displayType == null ? 
                                this.displayType == 'lables' : 
                                this.displayType = this.$scope.displayType

            this.workItemName = this.$scope.workItemName == null ? 
                                this.workItemName == 'Cards' : 
                                this.workItemName = this.$scope.workItemName
        }

        setLimits($event) {
            $event.preventDefault();
            this.$scope.setLimit();
        }

        getToolTip(stats: StatItem){
            var toolTip: string = "";
            toolTip += `Current ${stats.label}: ${stats.value}<br/>`;
            if(stats.limit > 0){ 
                toolTip += `Maximum ${stats.label}: ${stats.limit}<br/>`;
            }
            return toolTip;
        }

    }
}