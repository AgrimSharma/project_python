/// <reference path='../_all.ts' />

module scrumdo {
    
    export class ReleaseStatManager {
        public static $inject: Array<string> = [
            "$resource",
            "API_PREFIX",
            "$q"
        ]; 

        private ReleaseTeamStatsCache: any = {};

        // release stats for organization
        private Stats: ng.resource.IResourceClass<any>;
        // release stats for a specific project cards
        private ProjectStats: ng.resource.IResourceClass<any>;
        // release stats for a specific release
        private ReleaseStats: ng.resource.IResourceClass<any>;
        // release stats for a specific project iteration cards
        private ProjectIterationStats: ng.resource.IResourceClass<any>;
        private ReleaseChildStats: ng.resource.IResourceClass<any>;
        // release stats for a specific child project related to parent release
        private ReleaseTeamsStats: ng.resource.IResourceClass<any>;

        constructor(
            private resource: ng.resource.IResourceService,
            public API_PREFIX: string,
            public $q: ng.IQService) {

            this.Stats = this.resource(API_PREFIX + "organizations/:organizationSlug/releasestats");
            this.ProjectStats = this.resource(API_PREFIX + "organizations/:organizationSlug/releasestats/project/:projectSlug");
            this.ProjectIterationStats = this.resource(API_PREFIX + "organizations/:organizationSlug/releasestats/project/:projectSlug/iteration/:iterationId");
            this.ReleaseStats = this.resource(API_PREFIX + "organizations/:organizationSlug/releasestats/:releaseId/all");
            this.ReleaseChildStats = this.resource(API_PREFIX + "organizations/:organizationSlug/releasestats/project/:projectSlug/iteration/:iterationId/childstats");
            this.ReleaseTeamsStats = this.resource(API_PREFIX + 
                                    "organizations/:organizationSlug/projects/:projectSlug/stories/releaseteamstats/iteration/:iterationId/:releaseId");
        }

        loadStats(organizationSlug: string, releaseId = null): ng.IPromise<any> {
            if (typeof releaseId === "undefined" || releaseId === null) {
                return this.Stats.query({ organizationSlug: organizationSlug }).$promise;
            } else {
                return this.ReleaseStats.query({ organizationSlug: organizationSlug, releaseId: releaseId }).$promise;
            }
        }

        loadProjectStats(organizationSlug: string, projectSlug: string): ng.IPromise<any> {
            return this.ProjectStats.query({ organizationSlug: organizationSlug , projectSlug: projectSlug}).$promise;
        }

        loadIterationStats(organizationSlug: string, projectSlug: string, iterationId: number): ng.IPromise<any> {
            return this.ProjectIterationStats.query({ organizationSlug: organizationSlug , projectSlug: projectSlug, iterationId: iterationId}).$promise;
        }

        // this one is to featch the info about the child stories 
        // having release set for a specific iteration
        loadReleaseChildStats(organizationSlug: string, projectSlug: string, iterationId: number): ng.IPromise<any> {
            return this.ReleaseChildStats.get({ organizationSlug: organizationSlug , projectSlug: projectSlug, iterationId: iterationId}).$promise;
        }

        loadReleaseTeamStats(organizationSlug: string, projectSlug: string, iterationId: number, releaseId: number, reload: boolean = false){
            if(this.ReleaseTeamStatsCache[releaseId] == null || reload){
                var p = this.ReleaseTeamsStats.get({ organizationSlug: organizationSlug , projectSlug: projectSlug, iterationId:iterationId, releaseId:releaseId}).$promise;
                p.then((stats) => {
                    this.ReleaseTeamStatsCache[releaseId] = stats;
                });
                return p;
            }else{
                return this.$q.resolve(this.ReleaseTeamStatsCache[releaseId]);
            }
        }
    }
}