/// <reference path='../_all.ts' />

module scrumdo {


    export class CalendarController {
        public static $inject: Array<string> = [
            "$scope",
            "API_PREFIX",
            "$http",
            "$resource",
            "organizationSlug",
            "projectSlug",
            // "calendarManager"
        ];

        private calConfig: any;
        private eventSources;
        private events;
        // public datas;
        constructor(
            private $scope: ng.IScope,
            private API_PREFIX: string,
            public http: ng.IHttpService,
            public resource: ng.resource.IResourceService,
            private organizationSlug: string,
            private projectSlug: string
            // public calendarManager: CalendarManager
            ){
            // this.calendarData();
            // this.fetchEvents();
            this.setCalendarConfig();
            this.setEvents();

            // console.log(this.datas);
        }

        setCalendarConfig(){

            this.calConfig = {
                height: 750,
                editable: true,
                header:{
                    left: 'month basicWeek basicDay agendaWeek agendaDay',
                    center: 'title',
                    right: 'today prev,next'
                },
                eventClick: this.alertEventOnClick,
                eventDrop: this.alertOnDrop,
                eventResize: this.alertOnResize
            }
        }
//         private htmlToPlaintext(text) {
//          return text ? String(text).replace(/<[^>]+>/gm, '') : '';
// }
        private fetchEvents() {
               trace("Fetching calendar events...");
               // let events;
                var events = [];
                this.http.get(API_PREFIX + "calendar").then(function (response) {
                   // console.error(response.data);
                   let gists = response.data;
                   // console.log(typeof gists);
                   var i;
                   for(i in gists){
                       var summary = gists[i].summary;
                       var sdate = gists[i].created;
                       var edate = gists[i].due_date;
                       var summary1 = summary ? String(summary).replace(/<[^>]+>/gm, '') : '';
                       // console.log(i, summary, date);
                       events.push({
                           "title": summary1,
                           "start": sdate,
                           "end": edate
                       })
                   }
                   // console.log("drtyuhgvj bj",events);
                   return events;
               })
                   .catch(function (response) {
                       console.error('Gists error', response.status, response.data);
                   })
                   .finally(function () {
                       console.log("finally finished gists");
                       // return events
                   });
            return events
           }
        private setEvents(){
            // call calendar manager to fetch events
            
            // this.calendarManager.fetchEvents();
            this.events = {
                color: '#f00',
                textColor: 'yellow',
                events: this.fetchEvents()

                };
            

            this.eventSources =  [ this.events ]
        }

        private alertEventOnClick () {
            this.setCalendarConfig();
            this.fetchEvents();
            this.setEvents();
        }

        private alertOnDrop() {
            this.setCalendarConfig();
            this.fetchEvents();
            this.setEvents();        }

        private alertOnResize() {
            this.setCalendarConfig();
            this.fetchEvents();
            this.setEvents();

        }
    }
}