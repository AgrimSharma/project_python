/// <reference path='../_all.ts' />

module scrumdo {
    export class IterationWindowController {
        public static $inject: Array<string> = [
            "$scope",
            "iteration",
            "projectSlug",
            "organizationSlug",
            "windowType"
        ];

        constructor(
            private scope,
            private iteration,
            public projectSlug: string,
            public organizationSlug: string,
            private windowType: string) {

            this.scope.ctrl = this;
        }
    }
}