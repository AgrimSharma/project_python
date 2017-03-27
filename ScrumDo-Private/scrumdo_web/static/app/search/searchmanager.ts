/// <reference path="../_all.ts" />

module scrumdo{

    export class ProjectSearchManager{

        public static $inject:Array<string> = [
            "$uibModal",
            "urlRewriter"
        ];

        private popup: ng.ui.bootstrap.IModalServiceInstance;

        constructor(private $uibModal: ng.ui.bootstrap.IModalService,
                    private urlWriter: URLRewriter){

        }

        public projectSearchPopup(){
            this.popup = this.$uibModal.open({
                backdrop: 'static',
                controller: 'SearchController',
                controllerAs: 'ctrl',
                templateUrl: this.urlWriter.rewriteAppUrl("search/popupsearch.html"),
                size: 'lg',
                windowClass: 'project-search-modal',
                keyboard: false
            });

            return this.popup.result;
        }

        public orgSearchPopup(initialSearchTerms: string = ''){
            this.popup = this.$uibModal.open({
                backdrop: 'static',
                controller: 'SearchController',
                controllerAs: 'ctrl',
                templateUrl: this.urlWriter.rewriteAppUrl("search/popupsearch.html"),
                size: 'lg',
                windowClass: 'project-search-modal',
                keyboard: false,
                resolve: {
                    projectSlug: () => '',
                    initialSearchTerms: () => initialSearchTerms
                }
            });

            return this.popup.result;
        }
    }
}