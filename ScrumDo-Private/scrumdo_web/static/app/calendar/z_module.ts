/// <reference path='../_all.ts' />

var calendarModule: ng.IModule = angular.module("scrumdoCalendar", ["ui.calendar",'ui.bootstrap']);

calendarModule.service("calendarManager",scrumdo.CalendarManager);
calendarModule.controller('calenderController', scrumdo.CalendarController);