/// <reference path='../_all.ts' />

module scrumdo {
    export class ChatController {
        public static $inject: Array<string> = [
            "$scope",
            "chatService",
            "organizationSlug",
            "FileUploader",
            "projectData",
            "$location",
            "projectManager"
        ];

        public message: string;
        private teamMembers: Array<User>;

        constructor(
            public scope,
            public chat: ChatService,
            public organizationSlug: String,
            public FileUploader,
            private projectData:ProjectDatastore,
            public $location,
            private projectManager: ProjectManager) {
            
            if(!projectData.currentProject.tab_chat){
                this.$location.path('/');
            }
            
            this.loadTeamMembers();
            this.chat.joinProject(projectData.currentProject);


        }

        loadTeamMembers(){
            this.projectManager.loadTeamMembers(this.projectData.currentProject.slug).then((data) => {
                this.teamMembers = data;
            });
        }

        send() {
            // retrun if user mention popup is open
            if ($('.sdMentio:visible').length > 0) {
                return;
            }
            if (this.message === '') {
                return;
            }
            this.chat.sendMessage(this.message);
            this.message = "";
        }
    }
}