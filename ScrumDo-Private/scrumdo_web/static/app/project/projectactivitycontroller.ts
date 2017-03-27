/// <reference path="../_all.ts" />

module scrumdo{

    export class ProjectActivityController{

        public static $inject:Array<string> = [
            "$scope",
            "projectSlug",
            "organizationSlug",
            "projectData",
            "$templateCache",
            "STATIC_URL",
            "groupedNewsfeedManager",
            "storyManager"
        ];

        private isLoading: boolean;
        private lastDayLoaded: number;
        private news: Array<any>;
        private newsTemplate: Function;

        constructor(private $scope: ng.IScope,
                    private projectSlug: string,
                    private organizationSlug: string,
                    private projectData: ProjectDatastore,
                    private templateCache:ng.ITemplateCacheService,
                    private STATIC_URL: string,
                    private groupedNewsfeedManager: GroupedNewsfeedManager,
                    private storyManager: StoryManager){
            
            this.news = [];
            this.lastDayLoaded = -1;
            this.isLoading = false;
            this.loadMore(2);
        }

        public loadMore = (daysToLoad:any = 3) => {
            if (this.isLoading) {
                return;
            }
            this.isLoading = true;
            this.newsTemplate = Handlebars.compile(this.templateCache.get(this.STATIC_URL + "app/dashboard/newsfeed.html"));
            this.lastDayLoaded += daysToLoad;
            
            let iterationId = this.projectData.currentIteration != null ? this.projectData.currentIteration.id: null; 
            this.groupedNewsfeedManager.loadNewsForProject(this.organizationSlug,
                                                            this.projectSlug,
                                                            iterationId,
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

    }
}