/// <reference path='../_all.ts' />

var notemodule: ng.IModule = angular.module("scrumdoNotes", ['scrumdoCommon','scrumdoEditor']);

notemodule.service("noteService", scrumdo.NoteService);
notemodule.controller("notesController", scrumdo.NotesController);
notemodule.controller("SdNoteController", scrumdo.SdNoteController);
notemodule.controller("notewindowcontroller", scrumdo.NoteWindowController)

notemodule.directive("sdNotes", function() {
    return {
        restrict: "E",
        templateUrl: STATIC_URL + "app/note/notes.html",
        controller: "notesController",
        controllerAs: 'ctrl'
    };
});

notemodule.directive("sdNote", function() {
    return {
        restrict: "E",
        templateUrl: STATIC_URL + "app/note/sdnote.html",
        scope:{
            noteId: "=",
            project :"="
        },
        controller: "SdNoteController",
        controllerAs: 'ctrl'
    };
});