/// <reference path='../_all.ts' />

module scrumdo {


    export class RisksController {
        public static $inject:Array<string> = [
            "risksManager",
            "projectDatastore",
            "urlRewriter",
            "$uibModal",
            "$q",
            "$stateParams"
        ];

        public userFilter:string='';
        public hoverRisk = null;
        public systemRisks: Array<any>;
        public userRisks: Array<any>;
        private topFiveRisksCache;
        private loaded: boolean;

        public riskNames = [
            '', 'Low', 'Medium', 'High', '', 'Urgent'
        ]


        public topFive:boolean = false;

        constructor(private risksManager:RisksManager,
                    public projectData:ProjectDatastore,
                    private urlRewriter:URLRewriter,
                    private $modal,
                    private $q: ng.IQService,
                    private routeParams: ng.ui.IStateParamsService) {
            this.loaded = false;
            this.loadRisks();
        }

        public score = (risk) => -1 * riskScore(risk)

        public filterRisk = (risk):boolean => {
            if(this.userFilter == '') return true;
            const filter = this.userFilter.toLowerCase();
            return risk.description.toLowerCase().indexOf(filter) != -1;
        }

        public highSeverityCount():number {
            if(this.userRisks == null) return 0;
            return this.userRisks.filter((risk)=>{
                return risk.severity_1 > 2 ||
                        risk.severity_2 > 2 ||
                        risk.severity_3 > 2 ||
                        risk.severity_4 > 2 ||
                        risk.severity_5 > 2 ||
                        risk.severity_6 > 2 ||
                        risk.severity_7 > 2;
            })
            .length;
        }

        public editRisk(risk) {
            if(!this.projectData.canWrite()) return;
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
                        .then(this.reloadRisks)
                        .then(this.resetCache)
                }
            });
        }

        removeRisk(risk){
            var i = this.projectData.userRisks.indexOf(risk);
            if(i !== -1){
                this.projectData.userRisks.splice(i, 1);
            }
            return this.$q.resolve(null);
        }

        private resetCache = () => {
            this._artifactMap = {};
            this.topFiveRisksCache = null;
        }

        public allRisks = ():Array<Risk> => {
            return this.userRisks = this.projectData.userRisks;
        }

        public risks = ():Array<Risk> => {

            if(this.topFive) {
                if(!this.topFiveRisksCache) {
                    this.topFiveRisksCache = this.allRisks().slice(0,5);
                }
                return this.topFiveRisksCache;
            }

            return this.allRisks()
        }

        public portfolio = ():Portfolio => {
            return this.projectData.portfolio;
        }

        private _artifactMap = {};
        public riskArtifacts(risk) {

            if(!this._artifactMap[risk.id]) {
                let result = risk.cards.map((o) => ({type:'card', card:o}))
                result = result.concat(risk.iterations.map((o) => ({type:'iteration', iteration:o})))
                result = result.concat(risk.projects.map((o) => ({type:'project', project:o})))
                this._artifactMap[risk.id] = result;
            }

            return this._artifactMap[risk.id];
        }

        public reloadRisks = () => this.projectData.reloadRisks();

        public riskColor = (risk:Risk) => '#' + SCRUMDO_BRIGHT_COLORS[risk.id % SCRUMDO_BRIGHT_COLORS.length];


        public hover = (risk) => {
            if(!risk) return this.hoverRisk = null;
            this.hoverRisk = risk;
        }

        public addRisk() {
            let risk = this.risksManager.createStub(this.projectData.portfolio);


            risk.projects = [
                {
                    name: this.projectData.currentProject.name,
                    slug: this.projectData.currentProject.slug,
                    color: this.projectData.currentProject.color,
                    icon: this.projectData.currentProject.icon
                }
            ];

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

            dialog.result.then((risk)=>{
                this.risksManager
                    .createRisk(this.portfolio().id, risk)
                    .then(this.reloadRisks)
                    .then(this.resetCache)

            });
        }


        public loadRisks() {
            this.projectData.loadRisks(this.projectData.currentProject.slug).then(() => {
                this.systemRisks = this.projectData.systemRisks;
                this.loaded = true;
                this.viewRisk();
            });
        }

        public viewRisk(){
            var ref = _.find(this.risks(), (r: any) => r.id == this.routeParams["riskid"]);
            if("riskid" in this.routeParams && ref != null ){
                this.editRisk(ref);
            }
        }

        public getsystemrisks = ():Array<any> => {
            if(this.systemRisks == null) return []
            if(this.topFive){
                return this.systemRisks.slice(0,5);
            }else{
                return this.systemRisks;
            }
        }
    }
}