/// <reference path='../_all.ts' />

var calendarModule: ng.IModule = angular.module("scrumdoCalendar", ["ui.calendar",'ui.bootstrap']);

// calendarModule.controller("calenderController", scrumdo.CalendarController);

calendarModule.controller('calenderController', function($scope) {
    /* config object */
    $scope.eventSources = [];

    $scope.uiConfig = {
      calendar:{
        height: 750,
        editable: true,
        header:{
          left: 'month basicWeek basicDay agendaWeek agendaDay',
          center: 'title',
          right: 'today prev,next'
        },
        eventClick: $scope.alertEventOnClick,
        eventDrop: $scope.alertOnDrop,
        eventResize: $scope.alertOnResize
      }
    };
});
// chatModule.controller("ChatController", scrumdo.ChatController);
