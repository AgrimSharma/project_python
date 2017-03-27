/// <reference path='../_all.ts' /> 

module scrumdo {
    export class SDPeopleController {
        public static $inject: Array<string> = [
            "$scope"
        ];

        private element: HTMLElement;
        private ngModel: ng.INgModelController;
        public menuOpen: boolean;
        public filterQuery: string;
        private defaultLabel: string;

        constructor(private scope) {
            this.menuOpen = false;
            this.filterQuery = "";
            this.scope.$on("hideDropDown", this.hideDropDown);
            if(this.scope.label == null){
                this.defaultLabel = "Nobody";
            }else{
                this.defaultLabel = this.scope.label;
            }
        }

        init(element, ngModel) {
            this.element = element;
            this.ngModel = ngModel;
            this.scope.ctrl = this;
            var t = this;
            ngModel.$render = () => {
                t.scope.currentValue = ngModel.$modelValue;
            }
        }

        hideDropDown = () =>{
            if(this.menuOpen == true){
                this.menuOpen = !this.menuOpen;
            }
        }

        toggleMenu($event: MouseEvent) {
            $event.preventDefault();
            $event.stopPropagation();
            this.menuOpen = !this.menuOpen;
            trace("Menu open: " + this.menuOpen);
        }

        select($event, newValue) {
            this.ngModel.$setViewValue(newValue);
            this.scope.currentValue = newValue;
            $event.preventDefault();
        }

        doFilter = (option) => {
            var v: string;
            if (this.filterQuery == "") return true;
            var u: string, f: string, l: string;
            u = "@"+option.username;
            f = option.first_name != null ? option.first_name : "";
            l = option.last_name != null ? option.last_name : "";
            v = u + " " + f + " " + l;
            return v.toLowerCase().indexOf(this.filterQuery.toLowerCase()) !== -1;
        }
    }
}