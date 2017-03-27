/// <reference path="../_all.ts" />

module scrumdo{

    interface thisScope extends ng.IScope{
        portfolio: Portfolio;
    }

    export class ProjectRisksController{

        public static $inject:Array<string> = [
            "$scope",
            "projectSlug",
            "risksManager",
            "userService",
            "$uibModal",
            "urlRewriter",
            "$q"
        ];

        public riskNames = [
            '', 'Low', 'Medium', 'High', '', 'Urgent'
        ]
        private allRisks: Array<any>;
        private _artifactMap = {};
        private loaded: boolean;
        public topFive: boolean = false;

        constructor(private $scope: thisScope,
                    private projectSlug: string,
                    private risksManager: RisksManager,
                    private userService: UserService,
                    private $modal: ng.ui.bootstrap.IModalService,
                    private urlRewriter: URLRewriter,
                    private $q: ng.IQService){

            this.loaded = false;
            this.loadRisks();
        }

        public score = (risk) => -1 * riskScore(risk);
        public riskColor = (risk:Risk) => '#' + SCRUMDO_BRIGHT_COLORS[risk.id % SCRUMDO_BRIGHT_COLORS.length];
        public portfolio = () => this.$scope.portfolio;
        public risks = () => {
            if(this.topFive){
                return _.first(this.allRisks, 5);
            }else{
                return this.allRisks;
            }
        }

        public loadRisks = () => {
            this.risksManager.loadRisksForProject(this.$scope.portfolio.id, this.projectSlug).then((risks) => {
                this.allRisks = risks;
                this.loaded = true;
            });
        }

        public riskArtifacts(risk) {
            if(!this._artifactMap[risk.id]) {
                let result = risk.cards.map((o) => ({type:'card', card:o}))
                result = result.concat(risk.iterations.map((o) => ({type:'iteration', iteration:o})))
                result = result.concat(risk.projects.map((o) => ({type:'project', project:o})))
                this._artifactMap[risk.id] = result;
            }
            return this._artifactMap[risk.id];
        }


        public editRisk(risk) {
            if(!this.userService.canWrite(this.projectSlug)) return;
            const dialog = this.$modal.open({
                templateUrl: this.urlRewriter.rewriteAppUrl("risks/riskeditwindow.html"),
                backdrop: "static",
                keyboard: false,
                controller: 'RiskEditWindowController',
                controllerAs: 'ctrl',
                resolve: {
                    risk: () => risk,
                    portfolio: this.portfolio
                }
            });

            dialog.result.then((editedrisk)=>{
                if(editedrisk == "DELETE") {
                    this.risksManager
                        .deleteRisk(this.portfolio().id, risk)
                        .then(() => this.removeRisk(risk))
                        .then(this.resetCache)

                } else {
                    angular.copy(editedrisk, risk)

                    this.risksManager
                        .saveRisk(this.portfolio().id, risk)
                        .then(this.loadRisks)
                        .then(this.resetCache)
                }
            });
        }

        private resetCache = () => {
            this._artifactMap = {};
        }

        removeRisk(risk){
            var i = this.allRisks.indexOf(risk);
            if(i !== -1){
                this.allRisks.splice(i, 1);
            }
            return this.$q.resolve(null);
        }


    }
}