/// <reference path='../_all.ts' />

module scrumdo {
    export class GroupedNewsfeedManager {
        public static $inject: Array<string> = [
            "$resource",
            "API_PREFIX"
        ];

        private News: ng.resource.IResourceClass<any>;
        private ProjectNews: ng.resource.IResourceClass<any>;
        private IterationNews: ng.resource.IResourceClass<any>;

        constructor(
            private resource: ng.resource.IResourceService,
            public API_PREFIX: string) {

            this.News = this.resource(API_PREFIX + "organizations/:organizationSlug/newsfeed/grouped/:start/:end");
            this.ProjectNews = this.resource(API_PREFIX + "organizations/:organizationSlug/projects/:projectSlug/newsfeed/grouped/:start/:end");
            this.IterationNews = this.resource(API_PREFIX + "organizations/:organizationSlug/projects/:projectSlug/iterations/:iterationId/newsfeed/grouped/:start/:end");
        }

        loadNewsForOrganization(organizationSlug: string, start, end): ng.IPromise<any> {
            return this.News.query({ organizationSlug: organizationSlug, start: start, end: end }).$promise;
        }

        loadNewsForProject(organizationSlug: string, projectSlug: string, iterationId: number, start, end): ng.IPromise<any> {
            if(iterationId == null){
                return this.ProjectNews.query({ organizationSlug: organizationSlug, 
                                                projectSlug: projectSlug, 
                                                start: start, 
                                                end: end }).$promise;
            }else{
                return this.IterationNews.query({ organizationSlug: organizationSlug, 
                                                projectSlug: projectSlug,
                                                iterationId: iterationId,  
                                                start: start, 
                                                end: end }).$promise;
            }
        }
    }
}