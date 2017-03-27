/// <reference path='../_all.ts' />

module scrumdo {
    export interface ScrumdoNote{
        title:string;
        body:string;
        project_id:number;
        iteration_id:number;
        creator:User;
        id:number;
        created_date:string;
        modified_date:string;
        editing:boolean;
    }

    interface IterationNoteResource extends ng.resource.IResourceClass<any>{
    }

    interface ProjectNoteResource extends ng.resource.IResourceClass<any>{
        loadNote: any;
    }

    export class NoteService {
        public static $inject: Array<string> = [
            "$rootScope",
            "$resource",
            "API_PREFIX",
            "projectSlug",
            "organizationSlug",
            "$q",
            "$uibModal",
            "urlRewriter"
        ];

        public notes:Array<ScrumdoNote> = [];
        public IteartionNote: IterationNoteResource;
        public ProjectNote: ProjectNoteResource;
        public window: ng.ui.bootstrap.IModalServiceInstance;

        constructor(
            public rootScope,
            public resource: ng.resource.IResourceService,
            private API_PREFIX: string,
            public projectSlug:string,
            public organizationSlug: string,
            private $q: ng.IQService,
            private modal: ng.ui.bootstrap.IModalService,
            private urlRewriter: URLRewriter) {
                
            this.IteartionNote = <IterationNoteResource> this.resource(API_PREFIX + 
                                "organizations/:organizationSlug/projects/:projectSlug/iteration/:iterationId/notes/:id", { id: '@id' },
            {
                create: {
                    method: 'POST',
                    params: {
                        organizationSlug: "organizationSlug",
                        projectSlug: "projectSlug"
                    }
                },
                save: {
                    method: 'PUT',
                    params: {
                        organizationSlug: "organizationSlug",
                        projectSlug: "projectSlug",
                        id: "@id"
                    }
                },
                loadNote: {
                    method: 'GET',
                    isArray: false,
                    params: {
                        organizationSlug: "organizationSlug",
                        projectSlug: "projectSlug",
                        id: "@id"
                    }
                }
            });

            this.ProjectNote = <ProjectNoteResource> this.resource(API_PREFIX + 
                                "organizations/:organizationSlug/projects/:projectSlug/notes/:id", { id: '@id' },
            {
                loadNote: {
                    method: 'GET',
                    isArray: false,
                    params: {
                        organizationSlug: "organizationSlug",
                        projectSlug: "projectSlug",
                        id: "@id"
                    }
                }
            });

            var loads: Array<any> = [];
            this.rootScope.$on('revertNote', this.revertNote);
        }

        dummyNote(){
            var note = {id:-1, title:"", body:"", editing:true};
            return note;
        }

        revertNote = (event, note) => {
            var n = _.find(this.notes, (n:any) => { return n.id==note.id });
            var index = this.notes.indexOf(n);
            if (index !== -1) {
                this.notes[index] = note;
            }
        }

        loadNotes(projectSlug: string, iterationId: number){
            var p = this.IteartionNote.query({organizationSlug:this.organizationSlug, 
                                    projectSlug:projectSlug, 
                                    iterationId: iterationId}).$promise;
            p.then((notes) => {
                this.notes = notes;
            })
            return p;
        }

        loadNote(projectSlug: string, noteId: number){
            var note = new this.ProjectNote({id: noteId});

            var p = note.$loadNote({organizationSlug:this.organizationSlug, 
                                    projectSlug:projectSlug});
            return p;
        }

        createNote(projectSlug: string, iterationId: number, note, comment = null){
            var newNote = new this.IteartionNote();
            _.extend(newNote, note);
            if ("id" in newNote) {
                delete newNote.id;
                delete newNote.editing;
            }
            if(note.id == -1 && comment != null){
                newNote.newComment = comment;
            }
            var p = newNote.$create({ organizationSlug: this.organizationSlug, projectSlug: projectSlug, iterationId: iterationId});
            return p;
        }

        saveNote(projectSlug: string, iterationId: number, note) {
            var index;
            var N = new this.IteartionNote();
            _.extend(N, note);

            var p = N.$save({organizationSlug: this.organizationSlug, 
                                projectSlug: projectSlug, 
                                iterationId: iterationId }).then((newNote) => {
                var n = _.find(this.notes, (n:any) => { return n.id==newNote.id });
                
                index = this.notes.indexOf(n);
                if (index !== -1) {
                    this.notes[index] = newNote;
                }
            });
            return p;
        }

        deleteNote(projectSlug:string, iterationId: number, note){
            var N = new this.IteartionNote();
            _.extend(N, note);
            var p = N.$delete({organizationSlug: this.organizationSlug, 
                                projectSlug: projectSlug, 
                                iterationId: iterationId });
            var index;
            p.then(() => {
                index = this.notes.indexOf(note);
                if (index !== -1) {
                    this.notes.splice(index, 1);
                }
            });
            return p;
        }

        showNoteWindow(project:Project, iteration:Iteration, noteId:number = null){
            this.window = this.modal.open({
                templateUrl: this.urlRewriter.rewriteAppUrl("note/notewindow.html"),
                controller: "notewindowcontroller",
                controllerAs: "ctrl",
                windowClass: "scrumdo-modal primary scrumdo-note",
                backdrop: "static",
                keyboard: false,
                size: "lg",
                resolve: {
                    project: () => project,
                    iteration: () => iteration,
                    noteId: () => noteId
                }
            });
        }
    }
}