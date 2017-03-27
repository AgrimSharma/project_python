/// <reference path='../_all.ts' />

module scrumdo {
    export class UIState {
        public backlogOpen: boolean;
        public archiveOpen: boolean;
        public backlogSize: number;
        public loadBacklog: boolean;
        public loadGlobalBacklog: boolean;
        public summaryOpen: boolean;
        public iterationOpen: boolean;
        constructor() {
            this.backlogOpen = false;
            this.archiveOpen = false;
            this.loadBacklog = false;
            this.loadGlobalBacklog = false;
            this.summaryOpen = false;
            this.iterationOpen = false;
            this.backlogSize = 0;
        }
    }
}