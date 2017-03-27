/// <reference path="../_all.ts" />

module scrumdo{

    export class IterationProgressViewController{

        public static $inject: Array<string> = [
            "$scope",
            "projectSlug",
            "iteration",
            "storyAssignmentManager",
            "storyManager",
            "stories",
            "$q"
        ]

        private assignments: any = {};
        private child_stories: Array<Story>;
        private loading: boolean;
        private workItemName: {};
        private rleasesCache: {} = {};

        constructor(private $scope: ng.IScope,
                    private projectSlug: string,
                    private iteration: Iteration,
                    private storyAssignmentManager: StoryAssignmentManager,
                    private storyManager: StoryManager,
                    private stories: Array<Story>,
                    private $q:ng.IQService){
            
            this.loading = true;
            if(this.$scope.$root['safeTerms'] != null){
                this.workItemName = {"current": this.$scope.$root['safeTerms'].current.work_item_name,
                                    "parent": this.$scope.$root['safeTerms'].parent.work_item_name };
            }else{
                this.workItemName = {"current": "Cards",
                                    "parent": "Features" };
            }
            this.loadCards();
        }

        loadAssignments(){
            var loads = [];
            _.forEach(this.iteration.increment, (inc:IterationIncrement) => {
                loads.push(
                    this.storyAssignmentManager
                        .loadAssignments(inc.increment_id, this.projectSlug, true)
                        .then((assignments: {data: any}) => {
                            this.assignments[inc.id] = assignments.data;
                        })
                )
            });

            this.$q.all(loads).then(() => {
                this.loading = false;
            });
        }

        loadCards(){
            if(this.stories == null){
                this.storyManager.loadIteration(this.projectSlug, this.iteration.id)
                    .then((stories) => {
                        this.child_stories = stories;
                        this.loadAssignments();
                    });
            }else{
                this.child_stories = this.stories;
                this.loadAssignments();
            }
        }

        getCardCounts(releaseId: number){
            if(this.rleasesCache[releaseId] != null){
                return this.rleasesCache[releaseId];
            }else{
                let releaseCards = _.filter(this.child_stories, (s: Story) => s.release!=null && s.release.id == releaseId);
                let doneCards = _.filter(releaseCards, (s: Story) => s["cell"] !=null && parseInt(s["cell"]["type"]) == 3);
                let remainingCards = _.filter(releaseCards, (s: Story) => s["cell"] !=null && parseInt(s["cell"]["type"]) != 3);
                let data = {"total": releaseCards.length, "done": doneCards.length, "remaining": remainingCards.length};
                this.rleasesCache[releaseId] = data;
                return data;
            }
        }

        percentage(val, total){
            return Math.round(100 * val / total);
        }

        itemsToShow(){
            if(_.isEmpty(this.assignments)){
                return false;
            }
            var items: boolean = false;
            for(var key in this.assignments){
                if(!items){
                    items = this.assignments[key].length > 0;
                }
            }
            return items;
        }
    }
}