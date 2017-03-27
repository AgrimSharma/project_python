/// <reference path='../_all.ts' />

module scrumdo {
    export class GithubProjectController {
        public static $inject: Array<string> = [
            "$scope",
            "$state",
            "boardProject",
            "githubExtraManager",
            "alertService"
        ];


        private githubImport: {
            name: string,
            commit_messages: boolean,
            upload_issues: boolean,
            download_issues: boolean,
            close_on_delete: boolean
        };
        private cellNames:Array<string>;
        private extraConfig;
        private isBusy: boolean = false;

        constructor(
            private scope,
            private state,
            public boardProject,
            private githubExtraManager: GithubExtraManager,
            public alertService: AlertService) {

            this.githubExtraManager.loadProject(this.boardProject.projectSlug).then((result) => {
                this.onLoaded(result);
                this.loadBoardCells();
            });
            this.githubImport = {
                name: '',
                commit_messages: true,
                upload_issues: false,
                download_issues: false,
                close_on_delete: false
            };
        }

        loadBoardCells() {
            this.cellNames = (function() {
                var i, len, ref, results;
                ref = this.boardProject.boardCells;
                results = [];
                for (i = 0, len = ref.length; i < len; i++) {
                    var cell = ref[i];
                    results.push(cell.label);
                }
                return results;
            }).call(this);

            this.cellNames = _.uniq(this.cellNames.concat((function() {
                var i, len, ref, results;
                ref = this.boardProject.boardCells;
                results = [];
                for (i = 0, len = ref.length; i < len; i++) {
                    var cell = ref[i];
                    results.push(cell.full_label);
                }
                return results;
            }).call(this)));
        }

        removeBinding(bindingId) {
            if(this.isBusy){
                return;
            }
            this.isBusy = true;
            this.githubExtraManager.removeRepoFromProject(this.boardProject.projectSlug, bindingId).then((result) => {
                this.extraConfig = result.data;
                this.isBusy = false;
            });
        }

        addRepo(config) {
            if(this.isBusy){
                return;
            }
            this.isBusy = true;
            this.githubExtraManager.addRepoToProject(this.boardProject.projectSlug, config).then((result) => {
                this.extraConfig = result.data;
                this.isBusy = false;
            });
        }

        onLoaded = (result) => {
            this.extraConfig = result
        }

        canAddRepo(config){
             if(this.extraConfig == null){
                 return true;
             }
            return _.find(this.extraConfig.existing_configs, (c: any) => c.github_slug == config.name) == null;
        }
    }
}