/// <reference path='../_all.ts' />

var releasemod: ng.IModule = angular.module("scrumdoRelease", []);

releasemod.service("releaseStatManager", scrumdo.ReleaseStatManager);
releasemod.directive("sdReleaseChart", scrumdo.ReportRelease);
releasemod.controller("ReleaseSelectController", scrumdo.ReleaseSelectController);
releasemod.controller("ReleaseParentsController", scrumdo.ReleaseParentsController);
releasemod.controller("ReleaseTeamDisplayController", scrumdo.ReleaseTeamDisplayController);

releasemod.directive("sdReleaseSelect", () => {
    return {
        restrict: "E",
        templateUrl: STATIC_URL + "app/release/releaseselect.html",
        controller: "ReleaseSelectController",
        controllerAs: 'ctrl',
        require: ['sdReleaseSelect', 'ngModel'],
        replace: true,
        scope: {
            releases: "=",
            parents: "=",
            allowEmpty: "=",
            placeholder: "="
        },
        link: (scope, element, attrs, controllers:ng.INgModelController) => {
            var myCtrl, ngModel;
            myCtrl = controllers[0], ngModel = controllers[1];
            return myCtrl.init(ngModel);
        }
    };
});

releasemod.directive("sdReleaseTeamDisplay", function() {
    return {
        restrict: 'AE',
        controller: 'ReleaseTeamDisplayController',
        controllerAs: 'ctrl',
        scope: {
            release: "=",
            project: "="
        },
        templateUrl: STATIC_URL + "app/release/releaseteamdisplay.html"
    };
});