/// <reference path='../_all.ts' />

module scrumdo {
    export class NotesController {
        public static $inject: Array<string> = [
            "$scope",
            "noteService",
            "projectSlug",
            "organizationSlug",
            "editorManager",
            "confirmService",
            "$location",
            "$state",
            "attachmentsManager",
            "userService",
            "projectDatastore",
            "$stateParams",
            "urlRewriter"
        ];

        private notes:Array<ScrumdoNote> = [];
        private currentNote:ScrumdoNote;
        private noteCopy:ScrumdoNote = null;
        private iterations:Array<any>;
        private filterIteration;
        private newComment:string;
        private iteration: Iteration;
        private project: Project;
        private templateName: string;
        private canWrite: boolean;
        private loading: boolean;

        constructor(
            public scope,
            private service: NoteService,
            public projectSlug:string,
            public organizationSlug: string,
            public editorManager,
            public confirmService:ConfirmationService,
            public location:ng.ILocationService,
            public state:ng.ui.IStateService,
            public attachmentsManager:AttachmentsManager,
            public userService:UserService,
            private projectData: ProjectDatastore,
            public routeParams: ng.ui.IStateParamsService,
            private urlRewriter: URLRewriter) {

            this.iteration = this.projectData.currentIteration;
            this.project = this.projectData.currentProject;
            this.canWrite = this.userService.canWrite(this.project.slug);
            this.templateName = this.urlRewriter.rewriteAppUrl("note/note.html");

            this.scope.$on("notesUpdated", this.reloadNotes);

            this.loading = true;
            this.loadIteartionNotes();
        }

        reloadNotes = () => {
            this.loadIteartionNotes();
        }

        loadIteartionNotes = () => {
            this.service.loadNotes(this.projectSlug, this.iteration.id).then((notes) => {
                this.notes = notes;
                if("noteId" in this.routeParams){
                    this.currentNote = _.find(this.notes, (note) => note.id == this.routeParams["noteId"]);
                }
                this.loading = false;
            });
        }

        delete(){
            this.confirmService.confirm("Are you sure?", "Are you sure you want to delete this note?", 
                "No", "Yes").then(this.onDeleteConfirm);
        }

        onDeleteConfirm = () => {
            this.service.deleteNote(this.projectSlug, this.iteration.id, this.currentNote).then( () => {
                this.state.go(`app.iteration.notes`);
            })
        }

        edit(){
            this.noteCopy = angular.copy(this.currentNote);
            this.currentNote.editing = true;
        }

        cancel(){
            this.currentNote = this.noteCopy;
            this.scope.$emit('revertNote', this.noteCopy);
        }

        save(){
            if(this.currentNote.id == -1){
                this.service.createNote(this.projectSlug, this.iteration.id, this.currentNote, this.newComment).then((note) => {
                    this.state.go(`app.iteration.note({iterationId: ${this.iteration.id}, noteId:${note.id})`);
                    this.newComment = null;
                });
            }else{
                this.service.saveNote(this.projectSlug, this.iteration.id, this.currentNote).then((note) => {
                    this.currentNote.editing = false;
                });
            }
        }

        isValidNote(){
            if(this.currentNote.title == null) return false;
            return this.currentNote.title.trim() != '';
        }

        createNote(noteId: number){
            this.service.showNoteWindow(this.project, this.iteration, noteId);
        }

        isOwner(){
            if(this.currentNote == null) return false;
            return this.currentNote.creator.username == this.userService.me.username;
        }
    }
}