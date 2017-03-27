/// <reference path='../_all.ts' />

module scrumdo {
    export class NoteWindowController {
        public static $inject: Array<string> = [
            "$scope",
            "noteService",
            "organizationSlug",
            "confirmService",
            "attachmentsManager",
            "userService",
            "project", 
            "iteration",
            "noteId"
        ];

        private currentNote:ScrumdoNote;
        private noteCopy:ScrumdoNote = null;
        private newComment:string;
        private busyMode:boolean;
        private canWrite: boolean;

        constructor(
            public scope,
            private service: NoteService,
            public organizationSlug: string,
            public confirmService:ConfirmationService,
            public attachmentsManager:AttachmentsManager,
            public userService:UserService,
            public project:Project,
            public iteration:Iteration,
            public noteId:number) {

            this.scope.project = project;
            this.canWrite = this.userService.canWrite(this.project.slug);
            this.busyMode = false;
            this.setCurrentNote();
        }


        setCurrentNote(){
            if(this.noteId > 0){
                this.service.loadNote(this.project.slug, this.noteId).then((note) => {
                    this.currentNote = note;
                })
            }else{
                this.currentNote = <ScrumdoNote> this.service.dummyNote();
            }
        }

        delete(){
            this.confirmService.confirm("Are you sure?", "Are you sure you want to delete this note?", 
                "No", "Yes").then(this.onDeleteConfirm);
        }

        onDeleteConfirm = () => {
            this.service.window.close();
            this.service.deleteNote(this.project.slug, 
                                    this.iteration.id, 
                                    this.currentNote)
                        .then(this.sendReloadSignal);
        }

        edit(){
            this.noteCopy = angular.copy(this.currentNote);
            this.currentNote.editing = true;
        }

        close(){
            this.service.window.dismiss();
        }

        cancel(){
            if(this.currentNote.id == -1){
                this.attachmentsManager
                    .cleanTempAttachments(this.organizationSlug, 
                                        this.project.slug, 
                                        this.currentNote.id,
                                        -1).then(() => {
                                            this.service.window.dismiss();  
                                        });
            }else{
                this.currentNote = this.noteCopy;
            }
        }

        save(){
            this.busyMode = true;
            if(this.currentNote.id == -1){
                this.service.createNote(this.project.slug, this.iteration.id, this.currentNote, this.newComment).then((note) => {
                    this.newComment = null;
                    this.service.window.close();
                    this.sendReloadSignal();
                });
            }else{
                this.service.saveNote(this.project.slug, this.iteration.id, this.currentNote).then((note) => {
                    this.currentNote.editing = false;
                    this.service.window.close();
                    this.sendReloadSignal();
                });
            }
        }

        isValidNote(){
            if(this.currentNote.title == null) return false;
            return this.currentNote.title.trim() != ''
        }

        isOwner(){
            if(this.currentNote == null) return false;
            return this.currentNote.creator.username == this.userService.me.username;
        }

        sendReloadSignal = () => {
            this.scope.$root.$broadcast("notesUpdated", null);
        }
    }
}