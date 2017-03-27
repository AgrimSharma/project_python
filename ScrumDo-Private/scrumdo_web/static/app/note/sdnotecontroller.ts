/// <reference path='../_all.ts' />

module scrumdo {
    export class SdNoteController {
        public static $inject: Array<string> = [
            "$scope",
            "organizationSlug",
            "API_PREFIX",
            "$resource",
            "userService",
            "noteService",
            "projectManager"
        ];

        private noteId: number = null;
        private project: Project;
        private currentNote:ScrumdoNote = null;
        public canWrite:boolean;
        private loading: boolean;

        constructor(
            public scope,
            private organizationSlug:string,
            private API_PREFIX:string,
            public resource: ng.resource.IResourceService,
            private userService:UserService,
            private noteService: NoteService,
            private projectManager: ProjectManager) {
            
            this.currentNote = null;
            this.noteId = null;
            this.loading = true;

            this.scope.$watch('project', this.loadAssets);
            this.scope.$watch('noteId', this.loadAssets);
        }

        loadAssets = () => {
            if(this.scope.project == null || this.scope.noteId==null) return;
            this.loading = true;
            this.noteId = this.scope.noteId;
            this.project = this.scope.project;
            this.canWrite = this.userService.canWrite(this.scope.project.slug);
            this.loadNote(this.noteId)
        }

        loadNote(id){
            this.noteService.loadNote(this.scope.project.slug, this.scope.noteId)
                            .then((note:any) => {
                                this.currentNote = note;
                                this.loading = false;
                            },() => {
                                this.currentNote = <any> {title:"Note Deleted!", body: "", id:-1, active: false};
                                this.loading = false;
                            });
        }
    }

}