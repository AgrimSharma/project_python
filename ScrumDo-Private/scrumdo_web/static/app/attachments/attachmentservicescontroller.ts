/// <reference path='../_all.ts' />

module scrumdo {
    export class SDAttachmentServices {
        public static $inject: Array<string> = [
            "$scope",
            "urlRewriter",
            "attachmentsManager",
            "organizationSlug",
            "confirmService",
            "userService",
            "story",
            "project",
            "note"
        ];

        public loaded: boolean;
        private mobileView: boolean = false;

        constructor(private scope,
            private urlRewriter: URLRewriter,
            private attachmentsManager: AttachmentsManager,
            public organizationSlug: string,
            private confirmService: ConfirmationService,
            private userService: UserService,
            public story: Story,
            public project: Project,
            public note: ScrumdoNote) {

            this.mobileView = isMobileDevice();
            this.scope.story = this.story;
            this.scope.mobileView = this.mobileView;
            if(this.scope.project == null){
                this.scope.project = this.project;
            }
            this.scope.note = this.note;
            this.scope.ctrl = this;
            this.loaded = false;
            this.scope.fileSuccess = '';
            this.scope.$on('fileUploaded', this.fileUploaded);
            this.scope.$on('fileNotUploaded', this.fileNotUploaded);
        }

        fileUploaded = (event, file) => {
            var message: string = "\"" + file.fileName + "\" Uploaded Successfully.";
            $('.file-success-message').html(message).show();
            setTimeout(() => {
                $('.file-success-message').fadeOut();
            }, 3000);
        }

        fileNotUploaded = (event, file) => {
            var message: string = "\"" + file.fileName + "\"  Unable to upload file. Please try again.";
            $('.file-success-message').html(message).show();
            setTimeout(() => {
            }, 3000);
        }
    }
}
