/// <reference path="../../_all.ts" />

module scrumdo{

    export class FilterPopupController{

        public static $inject:Array<string> = [
            "projectSlug",
            "projectSearchManager"
        ];

        constructor(private projectSlug:string,
                    private projectSearchManager: ProjectSearchManager){

        }

        openSearch(){
            this.projectSearchManager.projectSearchPopup();
        }
    }
}

