/// <reference path='../_all.ts' />

module scrumdo {

    interface SentimentsScope extends ng.IScope{
        iteration: Iteration;
        team: Project;
        members: Array<User>;
        parent: Project;
    }

    export class TeamSentimentController {
        public static $inject:Array<string> = [
            '$scope',
            'organizationSlug',
            'projectSlug',
            'SentimentsManager',
            'userService'

        ];

        private sentiments: Array<Sentiment>;
        public sentiment: Sentiment;
        public loading: boolean;
        public numberOptions: Array<number>;
        public emojiOptions: Array<any>;
        public MembersVoted: Array<any>;
        private isBusy: boolean;

        constructor(
                public $scope:SentimentsScope,
                public organizationSlug:string,
                public projectSlug:string,
                private SentimentsManager:SentimentsManager,
                private userService: UserService
            ) {
                this.loading = true;
                this.sentiment = {id: -1, number: 6, reason: ""};
                this.numberOptions = [1,2,3,4,5,6,7,8,9,10];
                this.emojiOptions = [
                                    {'code' : '1f62d', 'title' : ':sob:'},
                                    {'code' : '1f622', 'title' : ':cry:'},
                                    {'code' : '1f620', 'title' : ':angry:'},
                                    {'code' : '1f61e', 'title' : ':disappointed:'},
                                    {'code' : '1f612', 'title' : ':unamused:'},
                                    {'code' : '1f60f', 'title' : ':smirk:'},
                                    {'code' : '1f60c', 'title' : ':satisfied:'},
                                    {'code' : '1f609', 'title' : ':wink:'},
                                    {'code' : '1f60a', 'title' : ':blush:'},
                                    {'code' : '1f601', 'title' : ':grin:'}
                                    ];
                this.MembersVoted = [];
                this.loadsentiments();
                this.$scope['project'] = this.$scope.parent;

                this.$scope.$on("sentimet_added", this.updateMembers);
                this.adjustRowHeight();
            
        }

        private loadsentiments(){
            this.SentimentsManager.loadTeamSentiments(this.organizationSlug, 
                                                    this.projectSlug, 
                                                    this.$scope.iteration.id, 
                                                    this.$scope.team.slug).then((result) => {
                    this.loading = false;
                    this.sentiments = result;
                    this.adjustRowHeight();
                    this.updateMembers();
            })
        }

        private updateMembers = () => {
            this.MembersVoted = _.map(this.sentiments, (s: Sentiment) => {
                return s.creator;
            });
        }

        public filterMembers = (member: User) => {
            if(!_.find(this.MembersVoted, (m:User) => m.username == member.username)){
                return true;
            }
            return false;
        }

        public averageValue(){
            if(this.sentiments == null){
                return 0;
            }
            let totalValue = _.reduce(this.sentiments, (i, s:any) => s.number + i, 0);
            let total = this.sentiments.length;
            return Math.round(totalValue / (total || 1));
        }

        public emojiUcode(index){
            return this.emojiOptions[index-1].code;
        }

        public emojiTitle(index){
            return this.emojiOptions[index-1].title;
        }

        public enterKeyPressed(form){
            if(this.isBusy){
                return;
            }
            this.isBusy = true;
            this.SentimentsManager.createSentiment(this.organizationSlug, 
                                                    this.projectSlug, 
                                                    this.$scope.iteration.id, 
                                                    this.$scope.team.slug, this.sentiment).then(() => {
                                                        this.sentiment.number = 6;
                                                        this.sentiment.reason = "";
                                                        this.isBusy = false;
                                                        form.$setPristine();
                                                        this.adjustRowHeight();
                                                    });
        }

        adjustRowHeight(){
            setTimeout(function(){
                var boxes = jQuery(".child-team", ".sentiments-section");
                var maxHeight: number = 0;
                boxes.css({height: ''});
                boxes.each(function(){
                    var height= jQuery(this).innerHeight();
                    maxHeight = height > maxHeight ? height : maxHeight;
                });
                boxes.css("height", maxHeight);
            }, 50);
        }

    }
}