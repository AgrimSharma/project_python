/// <reference path="../_all.ts" />

module scrumdo{

    interface Column{
        level: PortfolioLevel;
        active: boolean;
        loaded: boolean;
        stories: Array<MiniStory>;
        selected: MiniStory;
        project: any;
        lastcolumn?: boolean;
    }

    export class PortfolioBacklogController{

        public static $inject: Array<string> = [
            "$scope",
            "projectSlug",
            "organizationSlug",
            "projectData",
            "storyManager",
            "storyEditor",
            "projectPickerService",
            "projectManager",
            "iterationManager",
            "userService"
        ];

        private columns: Array<Column>;
        private rootColumn: Column;
        private portfolio: Portfolio;
        private portfolioIterations: Array<Iteration>;

        constructor(private $scope: ng.IScope,
                    private projectSlug: string,
                    private organizationSlug: string,
                    private projectData: ProjectDatastore,
                    private storyManager: StoryManager,
                    private storyEditor: StoryEditor,
                    private projectPickerService: ProjectPickerService,
                    private projectManager: ProjectManager,
                    private iterationManager: IterationManager,
                    private userService: UserService){
            
            this.initData();

        }

        public initData(){
            this.portfolio = this.projectData.portfolio;
            this.rootColumn = {level: null, active: true, loaded: false, stories: null, selected: null, project: null};

            this.columns = this.projectData.portfolio.levels.map((level: PortfolioLevel) => ({
                    level: level,
                    project: level.backlog_project,
                    active: false,
                    loaded: false,
                    stories: null,
                    selected: null,
                    lastcolumn: this.isLastLevel(level)
            }));

            this.loadIterations(this.portfolio.root.slug).then((iterations) => {
                this.portfolioIterations = this._filterIterations(iterations);
                this.loadRootCards(this.portfolio.root.slug, this.rootColumn);
            })
        }

        private loadIterations(projectSlug: string){
            return this.iterationManager.loadIterations(this.organizationSlug, projectSlug);
        }

        private _filterIterations(iterations: Array<Iteration>){
            return _.filter(iterations, (i: Iteration) => (i.iteration_type == 1 || i.iteration_type == 0) && i.hidden == false);
        }

        private isLastLevel(level: PortfolioLevel): boolean{
            let length = this.portfolio.levels.length;
            return this.portfolio.levels[length-1].level_number == level.level_number;
        }

        private loadRootCards(projectSlug: string, column: Column){
            let iterationIds = this.portfolioIterations.map((iteration) => iteration.id);
            this.storyManager.loadIterations(projectSlug, iterationIds).then((stories) => {
                column.stories = stories;
                column.loaded = true;
            });
        }

        private loadReleaseCards(storyId: number, column: Column){
            column.loaded = false;
            this.storyManager.loadStoriesByReleaseId(this.portfolio.root.slug, storyId, "mini", true).then((stories) => {
                column.stories = stories;
                column.loaded = true;
            });
        }

        private selectCard = (event, story: MiniStory, column: Column) => {
            if (event.isDefaultPrevented()) {
                return;
            }
            column.selected = story;
            let nextColumn: Column = null;
            if(column.level==null){
                _.forEach(this.columns, (c:Column) => {
                    this.resetColumn(c);
                });
                nextColumn = _.find(this.columns, (c:Column) => c.level.level_number==1); 
            }else{
                _.forEach(_.filter(this.columns, (c:Column) => c.level.level_number > column.level.level_number), (c:Column) => {
                    this.resetColumn(c);
                });
                nextColumn = _.find(this.columns, (c:Column) => c.level.level_number==column.level.level_number+1);
            }
            if(nextColumn != null){
                nextColumn.active = true;
                this.loadReleaseCards(story.id, nextColumn);
            }else{
                column.selected = null;
            }
        }

        private resetColumn(column: Column){
            column.active = false;
            column.selected = null;
            column.stories = null;
        }

        private editStory = ($event:MouseEvent, story: MiniStory) => {
            $event.preventDefault();
            $event.stopPropagation();
            let project;
            this.iterationManager.loadIterations(this.organizationSlug, story.project_slug).then(() => {
                this.storyEditor.editStory(story, project);
            });
        }

        private addCard(column: Column){
            if(column.level == null){
                this.storyEditor.createStory(this.portfolio.root, {iteration_id:this.portfolio.root.kanban_iterations.backlog});
            }else{
                this.addCardToColumn(column);
            }
        }

        private getPreviousColumn(column){
            let pcol;
            if(column.level.level_number==1){
                pcol = this.rootColumn;
            }else{
                pcol = _.find(this.columns, (c:Column) => c.level.level_number == column.level.level_number-1);
            }
            return pcol;
        }

        private addCardToColumn(column: Column){
            var pcol = this.getPreviousColumn(column);
            this.projectManager
                .loadProject(this.organizationSlug, column.project.slug)
                .then((project) => {
                    this.iterationManager
                        .loadIterations(this.organizationSlug, column.project.slug).then((iterations) => {
                            let iterationId = (_.findWhere(iterations, { iteration_type: 0 }))['id'];
                            this.storyEditor.createStory(project, {release:pcol.selected, iteration_id:iterationId,});
                        });
                });
        }


        private getColumnProjects(column: Column){
            var pcol:Column = this.getPreviousColumn(column);
            var selected: MiniStory = pcol.selected;
            var projects = [];
            _.forEach(column.level.projects, (p:any) => {
                var pids = _.pluck(p.parents, "slug");
                if(pids.indexOf(selected.project_slug) != -1){
                    if(this.userService.canWrite(p.slug) && p.active){
                        projects.push(p);
                    }
                }
            });
            return projects;
        }

        private getProjectName(column: Column, slug:string){
            var project = _.find(column.level.projects, (p:any) => p.slug == slug);
            return project.name;
        }

    }
}