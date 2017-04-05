/// <reference path='../_all.ts' />

module scrumdo {

    import IStateParamsService = angular.ui.IStateParamsService;



    // If no state is specified in the URL, we need to pick where to send the user to.
    // We'll prioritize in this order: timeline, releases, board, card list depending on
    // what features are enabled for this project.
    function redirectDefaultRoute($state:ng.ui.IStateService, projectDatastore:ProjectDatastore) {

        if(projectDatastore.currentProject.tab_board) 
            return $state.go('app.board')

        if(projectDatastore.currentProject.tab_milestones)
            return $state.go('app.releases')

        $state.go('app.iteration.cards')
    }


    function iterationRoutes($stateProvider: ng.ui.IStateProvider, urlRewriter:URLRewriter) {

        $stateProvider.state('app.iteration',{
            abstract: true,
            url: "/iteration/:iterationId",
            controller: 'IterationController',
            controllerAs: 'iterCtrl',
            views: {
                appContent: {
                    template: "<ui-view/>",
                }
            },
            resolve: {
                projectData: ['projectDatastore','projectSlug', '$stateParams',
                    (projectData:ProjectDatastore, projectSlug:string, $stateParams:ng.ui.IStateParamsService) => {
                        return projectData.setCurrentIteration(projectSlug, $stateParams['iterationId'])
                    }]
            }
        });


        $stateProvider.state('app.iteration.sentiments',{
            url: "/sentiments",
            controller: 'IterationSentimentController',
            controllerAs: 'ctrl',
            templateUrl: urlRewriter.rewriteAppUrl('iteration/iterationsentiments.html')
        });

        $stateProvider.state('app.iteration.dependencies',{
            url: "/dependencies",
            controller: 'DependenciesController',
            controllerAs: 'ctrl',
            templateUrl: urlRewriter.rewriteAppUrl('dependencies/dependencies.html'),
        });
        
        $stateProvider.state('app.iteration.cards',{
            url: "/cards",
            controller: 'IterationListController',
            controllerAs: 'ctrl',
            templateUrl: urlRewriter.rewriteAppUrl('iterationlist/iterationlist.html'),
        });

        $stateProvider.state('app.iteration.board',{
            url: "/board",
            controller: 'BoardController',
            templateUrl: urlRewriter.rewriteAppUrl('board/board.html')
        });

        

        $stateProvider.state('app.iteration.viewStory', {
            url: "/board/story/:storyid",
            controller: 'BoardController',
            templateUrl: urlRewriter.rewriteAppUrl('board/board.html'),
        });



        // This state just looks up the default team and redirects us to the right teamplanningteam state
        // that has a team slug on it.
        $stateProvider.state('app.iteration.teamplanning', {
            url: "/teamplanning/",
            controller: ["$state", "projectDatastore", "$localStorage", redirectDefaultTeam]
        });


        $stateProvider.state('app.iteration.notincrement', {
            url: "/teamplanning/noincrement",
            templateUrl: urlRewriter.rewriteAppUrl('teamplanning/notincrement.html'),
            controller: ["$scope","$state", "projectDatastore", checkNoIncrement]
        });

        $stateProvider.state('app.iteration.teamplanningteam',{
            url: "/teamplanning/:teamSlug",
            params: {
                teamId: null,
            },
            controller: "TeamPlanningController",
            controllerAs: "ctrl",
            templateUrl: urlRewriter.rewriteAppUrl('teamplanning/teamplanning.html'),
            resolve: {
                projectData: (projectData:ProjectDatastore, projectSlug:string, $stateParams:IStateParamsService) =>
                    projectData.setCurrentTeam(projectSlug, $stateParams['iterationId'], $stateParams['teamSlug'])
            }
        })

        $stateProvider.state('app.iteration.bigpicture',{
            url: "/bigpicture",
            controller: "BigPictureItrController",
            controllerAs: "ctrl",
            templateUrl: urlRewriter.rewriteAppUrl('bigpicture/iterationview.html')
        })

        $stateProvider.state('app.iteration.activity', {
            url: "/activity",
            templateUrl: urlRewriter.rewriteAppUrl('project/projectactivity.html'),
            controller: 'ProjectActivityControllerr',
            controllerAs: 'ctrl'
        });

        $stateProvider.state('app.iteration.notes', {
            url: "/notes",
            templateUrl: urlRewriter.rewriteAppUrl('note/notes.html'),
            controller: 'notesController',
            controllerAs: 'ctrl'
        });

        $stateProvider.state('app.iteration.note', {
            url: "/notes/:noteId",
            templateUrl: urlRewriter.rewriteAppUrl('note/notes.html'),
            controller: 'notesController',
            controllerAs: 'ctrl'
        });

    }

    function boardSettingRoutes($stateProvider: ng.ui.IStateProvider,
                         urlRewriter:URLRewriter) {

        $stateProvider.state('app.settings', {
            abstract: true,
            url: "/settings",
            views: {
                appContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/settings.html'),
                    controller: 'SettingsController',
                    controllerAs: "settingsCtrl"
                }
            },
        });


        $stateProvider.state('app.settings.board', {
            url: "/board",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/boardeditor/boardeditor.html')
                }
            }
        });

        $stateProvider.state('app.settings.reports', {
            url: "/reports",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/boardeditor/boardeditor.html')
                }
            }
        });

        $stateProvider.state('app.settings.project', {
            url: "/project",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/projectsettings.html')
                }
            }
        });

        $stateProvider.state('app.settings.teams', {
            url: "/teams",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/projectteams.html')
                }
            }
        });

        $stateProvider.state('app.settings.newteam', {
            url: "/teams/new",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/projectteam.html')
                }
            }
        });

        $stateProvider.state('app.settings.labeltags', {
            url: "/labeltags",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/projectlabeltags.html')
                }
            }
        });


        $stateProvider.state('app.settings.card', {
            url: "/card",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/cardsettings.html')
                }
            }
        });


        $stateProvider.state('app.settings.admin', {
            url: "/admin",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/adminsettings.html')
                }
            }
        });

        $stateProvider.state('app.settings.extras', {
            url: "/extras",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/extrassettings.html')
                }
            }
        });

        $stateProvider.state('app.settings.githubextra', {
            url: "/extras/github",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/githubextrassettings.html'),
                    controllerAs: 'githubctrl',
                    controller: "GithubProjectController"
                }
            }
        });

        $stateProvider.state('app.settings.slackextra', {
            url: "/extras/slack",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/slackextrasettings.html'),
                    controllerAs: 'slackctrl',
                    controller: "SlackExtraController"
                }
            }
        });

        $stateProvider.state('app.settings.flowdockextra', {
            url: "/extras/flowdock",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/flowdockextrasettings.html'),
                    controllerAs: 'flowdockctrl',
                    controller: "FlowdockExtraController"
                }
            }
        });

        $stateProvider.state('app.settings.emailcardextra', {
            url: "/extras/emailcard",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/emailcardextrasettings.html'),
                    controllerAs: 'emailctrl',
                    controller: "EmailCardExtraController"
                }
            }
        });

        $stateProvider.state('app.settings.hipchatextra', {
            url: "/extras/hipchat",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/hipchatextrassettings.html'),
                    controllerAs: 'hipchatctrl',
                    controller: "HipChatExtraController"
                }
            }
        });

        $stateProvider.state('app.settings.sharing', {
            url: "/sharing",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/sharingsettings.html'),
                    controllerAs: 'sharectrl',
                    controller: "SharingController"
                }
            }
        });

        $stateProvider.state('app.settings.basecampextra', {
            url: "/extras/basecamp",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/basecampextrassettings.html')
                }
            }
        });

        $stateProvider.state('app.settings.iterations', {
            url: "/iterations",
            views: {
                settingsContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('board/settings/iterationsettings.html'),
                    controller: "IterationSettingsController",
                    controllerAs: "iCtrl"
                }
            }
        });
    }


    export function projectRoutes($stateProvider: ng.ui.IStateProvider,
                                  $urlRouterProvider: ng.ui.IUrlRouterProvider,
                                  urlRewriter: URLRewriter,
                                  $state: ng.ui.IState) {

        $urlRouterProvider.otherwise(($injector, $location) => {
            var projectData: ProjectDatastore = $injector.get('projectDatastore'),
                state = $injector.get('$state'),
                projectSlug = $injector.get('projectSlug');

            projectData.setCurrentProject(projectSlug).then(() => {
                if(projectData.currentProject.continuous_flow){
                    state.go('app.iteration.board', {'iterationId':projectData.currentProject.continuous_flow_iteration_id});
                }else{
                    state.go('app.summary')
                }
            })
        });

        $stateProvider.state('app', {
            abstract: true,
            resolve: {
                userService: (userService:UserService) => userService.loaded,
                projectData: (projectSlug:string, projectDatastore:ProjectDatastore) => projectDatastore.setCurrentProject(projectSlug)
            },
            views: {
                mainApp: {
                    templateUrl: urlRewriter.rewriteAppUrl('projectapp/app.html'),
                    controller: 'ProjectAppController',
                    controllerAs: 'projcCtrl'
                }
            }
        });



        $stateProvider.state('app.redirectdefault', {
            url: "/redirectdefault/",
            views: {
                appContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('projectapp/redirect.html'),
                    controller: ["$state", "projectDatastore", redirectDefaultRoute]
                }
            }
        });



        $stateProvider.state('app.summary', {
            url: "/summary",
            views: {
                appContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('project/projectsummary.html'),
                    controller: 'WorkspaceSummaryController',
                    controllerAs: 'ctrl'
                }
            }

        });

        $stateProvider.state('app.calendar', {
            url: "/calendar",
            views: {
                appContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('calendar/calendar.html'),
                    controller: 'calenderController',
                    controllerAs: 'ctrl'
                }
            }
        });

        $stateProvider.state('app.activity', {
            url: "/activity",
            views: {
                appContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('project/projectactivity.html'),
                    controller: 'ProjectActivityControllerr',
                    controllerAs: 'ctrl'
                }
            }

        });


        $stateProvider.state('app.releases', {
            url: "/release",
            views: {
                appContent: {
                    controller: 'ReleasesController',
                    controllerAs: 'releasesCtrl',
                    templateUrl: urlRewriter.rewriteAppUrl('orgplanning/releases.html')
                }
            }
        });

        $stateProvider.state('app.releases.release', {
            url: "/release/{id:[0-9]+}/",
            views: {
                releasesArea: {
                    controller: 'ReleaseController',
                    controllerAs: 'releaseCtrl',
                    templateUrl: urlRewriter.rewriteAppUrl('orgplanning/release.html')
                }
            }
        });



        $stateProvider.state('app.chat', {
            url: "/chat",
            views: {
                appContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('chat/chat.html'),
                    controller: 'ChatController',
                    controllerAs: 'ctrl'
                }
            }
        });

        $stateProvider.state('app.risks', {
            url: "/risks",
            views: {
                appContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('risks/risks.html'),
                    controller: 'RisksController',
                    controllerAs: 'ctrl'
                }
            }
        });

        $stateProvider.state('app.viewrisks', {
            url: "/risks/risk/:riskid",
            views: {
                appContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('risks/risks.html'),
                    controller: 'RisksController',
                    controllerAs: 'ctrl'
                }
            }
        });

        $stateProvider.state('app.search', {
            url: "/search?q",
            params: {
               q: null,
            },
            views: {
                appContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('search/project_search.html'),
                    controller: 'SearchController',
                    controllerAs: 'ctrl'
                }
            }
        });


        $stateProvider.state('app.storyqueue', {
            url: "/storyqueue",
            views: {
                appContent: {
                    templateUrl: urlRewriter.rewriteAppUrl('storyqueue/storyqueue.html'),
                    controller: 'StoryQueueController',
                    controllerAs: 'ctrl'
                }
            }
        });

        iterationRoutes($stateProvider, urlRewriter);
        reportRoutes($stateProvider, urlRewriter);
        planningRoutes($stateProvider, urlRewriter);
        boardRoutes($stateProvider, urlRewriter, $state);
        boardSettingRoutes($stateProvider, urlRewriter);

    }



    function reportRoutes($stateProvider, urlRewriter) {
        $stateProvider.state('app.reports', {
            abstract: true,
            url: "/reports",
            views: {
                appContent: {
                    controller: "ReportsController",
                    controllerAs: "ctrl",
                    templateUrl: urlRewriter.rewriteAppUrl('reports/reports.html')
                }
            }

        });

        $stateProvider.state("app.reports.cfd", {
            url: "/cfd",
            views: {
                reportArea: {
                    templateUrl: urlRewriter.rewriteAppUrl("reports/cfd.html")
                }
            }
        });

        $stateProvider.state("app.reports.lead", {
            url: "/lead_time",
            views: {
                reportArea: {
                    templateUrl: urlRewriter.rewriteAppUrl("reports/lead.html")
                }
            }
        });
        $stateProvider.state("app.reports.burn:1", {
            url: "/burnup",
            views: {
                reportArea: {
                    templateUrl: urlRewriter.rewriteAppUrl("reports/burn.html")
                }
            }
        });
        $stateProvider.state("app.reports.burn:2", {
            url: "/burndown",
            views: {
                reportArea: {
                    templateUrl: urlRewriter.rewriteAppUrl("reports/burn.html")
                }
            }
        });
        $stateProvider.state("app.reports.burn:3", {
            url: "/burnstacked",
            views: {
                reportArea: {
                    templateUrl: urlRewriter.rewriteAppUrl("reports/burn.html")
                }
            }
        });
        $stateProvider.state("app.reports.aging:1", {
            url: "/agingtis",
            views: {
                reportArea: {
                    templateUrl: urlRewriter.rewriteAppUrl("reports/aging.html")
                }
            }
        });
        $stateProvider.state("app.reports.aging:2", {
            url: "/agingbreakdown",
            views: {
                reportArea: {
                    templateUrl: urlRewriter.rewriteAppUrl("reports/aging.html")
                }
            }
        });
        $stateProvider.state("app.reports.aging:3", {
            url: "/agingrelative",
            views: {
                reportArea: {
                    templateUrl: urlRewriter.rewriteAppUrl("reports/aging.html")
                }
            }
        });

        $stateProvider.state("app.reports.milestones", {
            url: "/milestones",
            views: {
                reportArea: {
                    templateUrl: urlRewriter.rewriteAppUrl("reports/milestones.html")
                }
            }
        });

        $stateProvider.state("app.reports.block", {
            url: "/blockerscluster",
            views: {
                reportArea: {
                    templateUrl: urlRewriter.rewriteAppUrl("reports/blockerscluster.html")
                }
            }
        });

        $stateProvider.state("app.reports.blockfreq", {
            url: "/blockersfrequency",
            views: {
                reportArea: {
                    templateUrl: urlRewriter.rewriteAppUrl("reports/blockersfreq.html")
                }
            }
        });

        $stateProvider.state("app.reports.blocklist", {
            url: "/blockersreport",
            views: {
                reportArea: {
                    templateUrl: urlRewriter.rewriteAppUrl("reports/blockersreport.html")
                }
            }
        });
    }
    
    function planningRoutes($stateProvider, urlRewriter) {
        $stateProvider.state('app.planning', {
            abstract: true,
            url: "/planning",
            views: {
                appContent: {
                    template: "<ui-view/>",
                }
            },
        });
        
        $stateProvider.state('app.planning.planningcolumn', {
            url: "/planningcolumn?newIteration",
            controller: "PlanningController",
            controllerAs: "planningCtrl",
            templateUrl: urlRewriter.rewriteAppUrl('planning/planning.html')
        });
        
        $stateProvider.state('app.planning.storymapping', {
            url: "/storymapping",
            controller: "StoryMappingController",
            controllerAs: "mappingCtrl",
            templateUrl: urlRewriter.rewriteAppUrl('planning/storymapping/storymapping.html')
        });

        $stateProvider.state('app.planning.portfoliobacklog', {
            url: "/portfoliobacklog",
            controller: "PortfolioBacklogController",
            controllerAs: "backlogCtrl",
            templateUrl: urlRewriter.rewriteAppUrl('portfolio/portfoliobacklog.html')
        });
    }

    function boardRoutes($stateProvider, urlRewriter, $state) {
        $stateProvider.state('app.board', {
            url: '/defaultboard',
            views: {
                appContent: {
                    controller: (projectData: ProjectDatastore, $state) => {
                        let iteration = _.find( projectData.iterations, (iter: Iteration) => {
                            return iter.iteration_type == 1 && !iter.hidden;
                        });

                        if(projectData.currentProject.continuous_flow){
                            iteration = _.find( projectData.iterations, (iter: Iteration) => {
                                            return iter.id == projectData.currentProject.continuous_flow_iteration_id
                                        }); 
                        }

                        let iterationId = iteration? iteration.id : projectData.iterations[0].id;
                        $state.go('app.iteration.board', {'iterationId':iterationId});
                    }
                }
            }
        });
    }
}
