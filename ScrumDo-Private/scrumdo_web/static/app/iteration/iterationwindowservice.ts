/// <reference path='../_all.ts' />

module scrumdo {
    export class IterationWindowService {
        public static $inject: Array<string> = [
            "iterationManager",
            "$uibModal",
            "urlRewriter"
        ];

        private dialog: ng.ui.bootstrap.IModalServiceInstance;

        constructor(
            private iterationManager: IterationManager,
            private modal: ng.ui.bootstrap.IModalService,
            public urlRewriter: URLRewriter) {

        }

        createIteration(organizationSlug: string, projectSlug: string, initialParams, windowType = "Iteration") {
            var iteration = _.extend({
                hidden: false,
                include_in_velocity: true,
                locked: false,
                name: "",
                default_iteration: false,
                id: -1,
                iteration_type: 1,
                end_date: null,
                start_date: null,
                increment: null,
            }, initialParams);

            this.dialog = this.modal.open({
                templateUrl: this.urlRewriter.rewriteAppUrl("iteration/iterationwindow.html"),
                controller: 'IterationWindowController',
                size: "lg",
                backdrop: "static",
                keyboard: false,
                resolve: {
                    projectSlug: () => projectSlug,
                    iteration: () => iteration,
                    windowType: () => windowType
                }
            });
            return this.dialog;
        }

        editIteration(organizationSlug: string, projectSlug: string, iteration, windowType = "Iteration") {
            this.dialog = this.modal.open({
                templateUrl: this.urlRewriter.rewriteAppUrl("iteration/iterationwindow.html"),
                controller: 'IterationWindowController',
                size: "lg",
                backdrop: "static",
                keyboard: false,
                resolve: {
                    projectSlug: () => projectSlug,
                    iteration: () => iteration,
                    windowType: () => windowType
                }
            });
            return this.dialog;
        }

        iterationProgress(projectSlug: string, iteration, stories: Array<Story> = null){
            this.dialog = this.modal.open({
                templateUrl: this.urlRewriter.rewriteAppUrl("iteration/iterationprogress.html"),
                controller: 'IterationProgressViewController',
                controllerAs: 'ctrl',
                size: "lg",
                backdrop: "static",
                keyboard: false,
                resolve: {
                    projectSlug: () => projectSlug,
                    iteration: () => iteration,
                    stories: () => stories
                }
            });
            return this.dialog;
        }
    }
}