/// <reference path='../../_all.ts' />

var filterwidgetmod: ng.IModule = angular.module("scrumdoFilterWidget", []);

filterwidgetmod.service("filterManager", scrumdo.FilterManager);
filterwidgetmod.controller("FilterWidgetController", scrumdo.FilterWidgetController);
filterwidgetmod.controller("FilterBuilderController", scrumdo.FilterBuilderController);
filterwidgetmod.controller("FilterPopupController", scrumdo.FilterPopupController);

filterwidgetmod.directive("sdFilterButton", function() {
    return {
        scope: {
            project: "=",
            cells: "=",
            order: "=",
            icon: "@",
            filter: "&",
            placeholder: "@",
            projectSearch: "@",
            orgSearch: "@"
        },
        restrict: "E",
        templateUrl: STATIC_URL + "app/common/filter/filterbutton.html",
        controller: "FilterWidgetController"
    };
});

filterwidgetmod.directive("sdFilter", function() {
    return {
        scope: {
            project: "=",
            cells: "=",
            order: "=",
            icon: "@",
            filter: "&",
            placeholder: "@",
            projectSearch: "@",
            orgSearch: "@",
            name: "@",
            showIterations: "<"

        },
        restrict: "E",
        templateUrl: STATIC_URL + "app/common/filter/filterwidget.html",
        controller: "FilterWidgetController"
    };
});

filterwidgetmod.directive("sdFilterPopup", function() {
    return {
        restrict: "E",
        templateUrl: STATIC_URL + "app/common/filter/filterpopup.html",
        controller: "FilterPopupController",
        controllerAs: 'ctrl'
    };
});