/// <reference path='../_all.ts' />

module scrumdo {
    export class RiskEditWindowController {
        public static $inject:Array<string> = [
            "risk",
            "portfolio",
            "$scope",
            "confirmService"
        ];

        public artifacts = [];
        private mobileView: boolean = false;

        constructor(public risk:Risk,
                    public portfolio:Portfolio,
                    public $scope,
                    private confirmService:ConfirmationService) {
            this.risk = angular.copy(risk);
            this.mobileView = isMobileDevice();

            this.artifacts = risk.iterations.map((i)=>({type:'iteration', iteration:i}))
            this.artifacts = this.artifacts.concat(risk.projects.map((i)=>({type:'project', project:i})))
            this.artifacts = this.artifacts.concat(risk.cards.map((i)=>({type:'card', card:i})))

        }

        public deleteRisk() {
            this.confirmService
                .confirm('Confirm','Are you sure you want to delete this risk?','No','Yes')
                .then(this.confirmDelete)
        }

        public confirmDelete = () => {
            this.$scope.$close("DELETE");
        }

        public ok() {
            this.risk.cards = this.artifacts.filter((a)=>a.type=='card').map((a)=>a.card)
            this.risk.iterations = this.artifacts.filter((a)=>a.type=='iteration').map((a)=>a.iteration)
            this.risk.projects = this.artifacts.filter((a)=>a.type=='project').map((a)=>a.project)
            this.$scope.$close(this.risk);
        }

        private setRiskSeverity(type: number, severity: number){
            this.risk[`severity_${type+1}`] = severity;
        }

        private getRiskSeverityLabel(type: number){
            var label: string;
            let serverity = this.risk[`severity_${type+1}`];
            switch (serverity) {
                case 1:
                    label = 'Low';
                break;
                case 2:
                    label = 'Medium';
                break;
                case 3:
                    label = 'High';
                break;
                case 5:
                    label = 'Urgent';
                break;
            }
            return label;
        }

        private isMobileView(){
            return this.mobileView;
        }
    }
}