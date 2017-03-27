/// <reference path='../_all.ts' />

module scrumdo {
    import IModalService = angular.ui.bootstrap.IModalService;
    import HotkeysProvider = angular.hotkeys.HotkeysProvider;
    import IStateService = angular.ui.IStateService;

    interface DashboardScope extends ng.IScope {
        news:Array<any>;
        projectsBySlug:{[slug:string]:Project};
        ctrl:DashboardController;
        showInactive:boolean;
        organizationSlug: string;
        to_trusted: Function;
        teams: Array<any>;
        myStories:Array<Story>;
        myAllStories:Array<Story>;
        projects: Array<Project>;
        watchedProjects: Array<Project>;
        projectByCategory: any;
        safeProjectsLists: any;
    }

    interface PortfolioFilters{
        showOnlyWatched:boolean; 
        showInactive:boolean;
        quickSearch:string;
    }

    export class DashboardController {
        public static $inject:Array<string> = ["$scope",
                                               "$element",
                                               "$timeout",
                                               "groupedNewsfeedManager",
                                               "storyManager",
                                               "projectManager",
                                               "portfolioManager",
                                               "$sce",
                                               "organizationSlug",
                                               "exportManager",
                                               "favoriteManager",
                                               "teamManager",
                                               "$uibModal",
                                               "urlRewriter",
                                               "$window",
                                               "mixpanel",
                                               "$templateCache",
                                               "STATIC_URL",
                                               "hotkeys",
                                               "$state",                                               
                                               "portfolioWindowService",
                                               "betaOptions",
                                               "$localStorage",
                                               "storyEditor",
                                               "userService"
        ];

        protected lastDayLoaded: number;
        protected isLoading: boolean;
        protected newsTemplate: Function;
        protected news:Array<any>;
        protected classicProjects:Array<any>;
        protected portfolios:Array<Portfolio>;
        public storage:any;
        public portfolioFilters: PortfolioFilters;
        protected filterdWatchedHalper:any = {};
        protected filterdCatProjectsHalper:any = {};
        private myCardsSortOrder: string;
        private loadingMyStories: boolean;

        constructor(public scope:DashboardScope,
                    public element,
                    public timeout:ng.ITimeoutService,
                    public groupedNewsfeedManager,
                    public storyManager: StoryManager,
                    public projectManager:ProjectManager,
                    public portfolioManager:PortfolioManager,
                    $sce:ng.ISCEService,
                    public organizationSlug:string,
                    public exportManager,
                    public favoriteManager,
                    public teamManager,
                    public modal:IModalService,
                    public urlRewriter:URLRewriter,
                    public window:ng.IWindowService,
                    public mixpanel,
                    public templateCache:ng.ITemplateCacheService,
                    public STATIC_URL:string,
                    protected hotkeys:HotkeysProvider,
                    protected state:IStateService,
                    protected portfolioWindowService:PortfolioWindowService,
                    protected betaOptions:BetaOptions,
                    public localStorage,
                    private storyEditor: StoryEditor,
                    private userService: UserService) {

            this.scope.news = this.news = [];
            this.scope.projectsBySlug = {};
            this.scope.showInactive = false;
            this.scope.organizationSlug = this.organizationSlug;
            this.scope.to_trusted = (html_code) => $sce.trustAsHtml(html_code);
            this.reloadProjects();
            this.teamManager.loadTeams(this.organizationSlug).then(this.onTeamsLoaded);

            this.lastDayLoaded = -1;
            this.isLoading = false;
            this.loadMore(2);
            this.newsTemplate = Handlebars.compile(this.templateCache.get(this.STATIC_URL + "app/dashboard/newsfeed.html"));
            this.scope.$on("$stateChangeSuccess", this.onStateChange);
            this.scope.$on("reloadDashboardMyStories", this.reloadMyStories);

            hotkeys.bindTo(this.scope)
                .add({combo: "g p", description: "Go to Projects",
                      callback:function(event){event.preventDefault(); state.go("projects");}})
                .add({combo: "g t", description: "Go to Teams",
                      callback:function(event){event.preventDefault(); state.go("teams");}})
                .add({combo: "g o", description: "Go to Overview",
                      callback:function(event){event.preventDefault(); state.go("overview");}});

            this.portfolioFilters = {
                showOnlyWatched: false, 
                showInactive: false,
                quickSearch: "" };
            this.storage = localStorage.$default({});
            this.initPortfolioFilters();
            this.checkCardsSortOrder();
        }

        protected reloadProjects = () => {
            this.projectManager.loadDashBoardProjects(this.organizationSlug, true, true)
                .then(this.onProjectsLoaded);
        }

        public createPortfolio() {
            this.portfolioWindowService
                .openCreateWindow()
                .then(() => {
                    this.reloadProjects();
                    this.reloadTeams();
                });
        }

        public configurePortfolio(portfolio) {
            let portfolioCopy = cleanPortfolioLevels(portfolio)
            this.portfolioWindowService
                .configure(portfolioCopy)
                .then(this.reloadProjects);
        }

        private isOrgStaff(){
            return this.userService.isOrgStaff();
        }


        public onStateChange = (event, toState, toParams, fromState, fromParams) => {
            if (toState.name === "overview") {
                return this.timeout(this.renderNews);
            }
        }

        public search = (query) => {
            var q, url;
            q = encodeURIComponent(query);
            url = "/projects/org/" + this.organizationSlug + "/search?q=" + q;
            return this.window.location.assign(url);
        }

        public reloadProject = (slug) => {
            return this.projectManager.loadProject(this.organizationSlug, slug, true);
        }

        public toggleFavorite = (project) => {
            if (project.watched) {
                this.removeFavorite(project);
            } else {
                this.addFavorite(project);
            }
        }

        public addFavorite = (project) => {
            project.watched = true;
            return this.favoriteManager.addProjectFavorite(project).then(() => this.reloadProject(project.slug));
        }

        public removeFavorite = (project) => {
            project.watched = false;
            return this.favoriteManager.removeProjectFavorite(project);
        }

        public onTeamsLoaded = (teams) => {
            return this.scope.teams = teams;
        }

        public onMyStoriesLoaded = (stories) => {
            var currentList, lastProject, myStoriesByProject;
            this.loadingMyStories = false;
            myStoriesByProject = [];
            lastProject = null;
            currentList = null;
            stories.forEach((story:Story) => {
                if (lastProject !== story.project_slug) {
                    lastProject = story.project_slug;
                    currentList = [];
                    myStoriesByProject.push({
                        "slug": story.project_slug,
                        stories: currentList
                    });
                }
                if (currentList.indexOf(story) < 0) {
                    return currentList.push(story);
                }
            });
            this.scope.myAllStories = stories;
            this.scope.myStories = myStoriesByProject;
        }

        protected onPortfoliosLoaded = (portfolios:Array<Portfolio>) => {
            this.portfolios = portfolios;
            for(var portfolio of this.portfolios) {
                portfolio.rootCache = _.findWhere(this.scope.projects, {id:portfolio.root.id});
                for(var plevel of portfolio.levels) {
                    plevel.projectsCache = [];
                    for(var projectId of plevel.projects) {
                        var p:Project = _.findWhere(this.scope.projects, {id:projectId.id});
                        if(p) plevel.projectsCache.push(p);
                    }
                }
            }
        }

        public onProjectsLoaded = (projects) => {
            var k, v;
            this.scope.projects = <Array<Project>>_.where(projects, {
                project_type: 1  // project type 1 are the normal kanban style projects
            });

            let portfolioRoots = <Array<Project>>_.where(projects, {
                project_type: 2
            });

            // used on team assignees page 
            this.scope.safeProjectsLists = projectByPortfolioV2(projects);

            this.scope.watchedProjects = <Array<Project>>_.where(projects, {
                watched: true
            });

            let individualProjects = _.filter(this.scope.projects,
                (p) => !p.portfolio_level_id && p.project_type<2
            );

            this.scope.projectByCategory = projectsByCategory(individualProjects);


            this.scope.projects.forEach((p) => this.scope.projectsBySlug[p.slug] = p);
            // adding portfolio root to array so can be available for my cards section
            portfolioRoots.forEach((p) => this.scope.projectsBySlug[p.slug] = p);

            this.scope.$root.$emit("fullyLoaded");
            this.projectManager.loadClassicProjectsForOrganization(this.organizationSlug).then((result) => {
                this.classicProjects = result;
                this.loadingMyStories = true;
                return this.storyManager.loadActiveStories().then(this.onMyStoriesLoaded);
            });

            this.portfolioManager.loadPortfolios().then(this.onPortfoliosLoaded);
            this.mixpanel.track("Viewed Dashboard");
        }

        private reloadMyStories = () =>{
            this.loadingMyStories = true;
            this.storyManager.loadActiveStories().then(this.onMyStoriesLoaded);
        }

        public loadMore = (daysToLoad:any = 3) => {
            if (this.isLoading) {
                return;
            }
            this.isLoading = true;
            this.lastDayLoaded += daysToLoad;
            this.groupedNewsfeedManager.loadNewsForOrganization(this.organizationSlug,
                                                                this.lastDayLoaded - (daysToLoad - 1),
                                                                this.lastDayLoaded)
                .then(this.onNewsLoaded);
        }

        public onNewsLoaded = (news) => {
            var count;
            this.isLoading = false;

            news.forEach((day) => this.processDay(day));
            this.news.sort((a, b) => {
                if (a.tday < b.tday) {
                    return 1;
                }
                if (a.tday > b.tday) {
                    return -1;
                }
                return 0;
            });

            function countItems(news) {
                return _.reduce(news.data, ((memo, item:any) => memo + item.entries.length), 0);
            }

            count = _.reduce(this.news, ((memo, news) => memo + countItems(news)), 0);
            trace(count + " news items loaded");
            if (count < 4 && this.lastDayLoaded < 60) {
                // trace("Not enough news initially loaded, getting more... #{@news.length}")
                // We're going to try to get at least 5 news items loaded up.
                // But we don't really care if it's stuff older than 60 days
                this.loadMore(this.lastDayLoaded);
            } else {
                this.renderNews();
            }
        }

        public renderNews = () => {
            if (this.isLoading) {
                return;
            }
            return $(".timeline-container").html(this.newsTemplate({
                news: this.news
            }));
        }

        public processDay(day) {
            day.tday = moment(day.day).format();

            if (!_.findWhere(this.news, {
                    tday: day.tday
                })) {
                this.news.push(day);
            }

            if (day.day === moment().format("MMM D, YYYY")) {
                day.day = "Today";
            }
            return day.data.map((data) => this.processData(data));
        }

        public processData(data) {
            if (data.type === "story") {
                return this.processStoryData(data);
            }
        }

        public processStoryData(data) {
            return data.story = this.storyManager.wrapStory(data.story);
        }

        public goToFiles(project) {
        }

        public exportProject(project) {
            return this.exportManager.startProjectExport(project);
        }

        public upgradeProject(project) {
            var dialog;
            return dialog = this.modal.open({
                templateUrl: this.urlRewriter.rewriteAppUrl("dashboard/upgradewindow.html"),
                controller: "UpgradeWindowController",
                controllerAs: "ctrl",
                backdrop: "static",
                keyboard: false,
                resolve: {
                    project: () => project
                }
            });
        }

        public sameProjectCategory(p1, p2) {
            return p1.name[0] === p2.name[0];
        }

        public projectCategory(p) {
            return p[0];
        }


        public initPortfolioFilters() {
            var pStorage;
            if (this.storage[this.organizationSlug] != null) {
                pStorage = this.storage[this.organizationSlug];
                this.portfolioFilters.showInactive = pStorage.portfolioShowInactive != null ? pStorage.portfolioShowInactive : false;
                this.portfolioFilters.showOnlyWatched = pStorage.portfolioShowOnlyWatched != null ? pStorage.portfolioShowOnlyWatched : false;
            } else {
                this.storage[this.organizationSlug] = {};
            }
        }

        public setPortfolioFilters(){
            var pStorage = this.storage[this.organizationSlug];
            pStorage.portfolioShowInactive = this.portfolioFilters.showInactive;
            pStorage.portfolioShowOnlyWatched = this.portfolioFilters.showOnlyWatched;
        }

        public checkCardsSortOrder(){
            var pStorage;
            if (this.storage[this.organizationSlug] != null) {
                pStorage = this.storage[this.organizationSlug];
                this.myCardsSortOrder = pStorage.myCardsSortOrder != null ? pStorage.myCardsSortOrder : 'system';
            }else{
                this.storage[this.organizationSlug] = {};
                this.myCardsSortOrder = 'system';
            }
        }

        public updatemyCardsSortOrder(order: string){
            this.myCardsSortOrder = order;
            let pStorage = this.storage[this.organizationSlug];
            pStorage.myCardsSortOrder = order;
        }

        public clearOrder(){
            this.myCardsSortOrder = 'system';
            let pStorage = this.storage[this.organizationSlug];
            if(pStorage.myCardsSortOrder != null){
                delete pStorage.myCardsSortOrder
            }
        }

        public myCardsOrder = (card: Story) => {
            var value;
            switch (this.myCardsSortOrder) {
                case 'due_date':
                    if(card['due_date'] != null){
                        value = moment(card['due_date']);
                    }else if(card['iteration_end_date'] != null){
                        value = moment(card['iteration_end_date']);
                    }
                    break;
                 case 'card_aging':
                    value = - card.age_hours;
                    break;
                 case 'card_points':
                    value = - card.points_value;
                    break;
            }
            return value;
        }

        public filterPortfolioProject = (project) => {
            var name = project.name;
            var k = this.portfolioFilters.quickSearch.toLowerCase();
            return name.toLowerCase().indexOf(k) !== -1 && (!this.portfolioFilters.showOnlyWatched || project.watched);
        }

        public filterPortfolioRoot = (portfolio) => {
            var childMatch:boolean = false;
            var found:boolean = false;
            for(var l in portfolio.levels){
                var level = portfolio.levels[l];
                for(var p in level.projectsCache){
                    var project = level.projectsCache[p];
                    childMatch = this.filterPortfolioProject(project);
                    if(childMatch){
                        found = true;
                        break;
                    }
                }
                if(found) break;
            }
            return this.filterPortfolioProject(portfolio.root) || childMatch; 
        }

        public isHaveChildWatched(portfolio){
            var found:boolean = false;
            for(var l in portfolio.levels){
                var level = portfolio.levels[l];
                for(var p in level.projectsCache){
                    var project = level.projectsCache[p];
                    if(project.watched){
                        found = true;
                        break;
                    }
                }
                if(found) break;
            }
            return found;
        }

        public clearPortfolioFilters(){
            this.portfolioFilters.showInactive = false;
            this.portfolioFilters.showOnlyWatched = false;
            this.portfolioFilters.quickSearch = "";
            this.setPortfolioFilters();
        }

        public isWatchedProject = (project) :any => {
            return _.find(this.scope.watchedProjects, (p) => p.slug == project.slug) != null;
        }

        public onEditCard(story, project){
            this.storyEditor.editStory(story, project);
        }

        private reloadTeams(){
            this.teamManager.loadTeams(this.organizationSlug).then(this.onTeamsLoaded);
        }
    }
}
