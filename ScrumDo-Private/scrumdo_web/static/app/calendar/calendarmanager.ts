/// <reference path='../_all.ts' />

module scrumdo {


    export class CalendarManager {
          public static $inject: Array<string> = [
            "organizationSlug",
            "projectSlug",
            "STATIC_URL",
            "mixpanel",
            "projectManager",
            "API_PREFIX",
            "$resource",
            "$http"
        ];
          public CalendarData: ng.resource.IResourceClass<any>;

          constructor(
            private organizationSlug: string,
            private projectSlug: string,
            private STATIC_URL: string,
            private mixpanel,
            private projectManager,
            public API_PREFIX: string,
            public resource: ng.resource.IResourceService,
            public http: ng.IHttpService
          ) {

            // this.calendarData();
            // this.CalendarData = ;
            // this.CalendarData = this.resource(API_PREFIX + "calendar");

           }

           public fetchEvents() {
               trace("Fetching calendar events...");
               // let events;
               this.http.get(API_PREFIX + "calendar").then(function (response) {
                   // console.error(response.data);
                   var events = [];
                   let gists = response.data;
                   // console.log(typeof gists);
                   var i;
                   for(i in gists){
                       var summary = gists[i].summary;
                       var date = gists[i].due_date;
                       // console.log(i, summary, date);
                       events.push({
                           "title": summary,
                           "start": date
                       })
                   }
                   console.log("drtyuhgvj bj",events);
                   return events;
               })
                   .catch(function (response) {
                       console.error('Gists error', response.status, response.data);
                   })
                   .finally(function () {
                       console.log("finally finished gists");
                       // return events
                   });

           }

        // public calendarData() {
        //       // var events = [{
        //       //     "title":"test1",
        //       //     "start": "2017-04-04"
        //       // }];
        //       // return events;
        //     var events = [];
        //     this.http.get(API_PREFIX+"calendar").then(function(response) {
        //         console.log('Success');
        //         let gists = response.data;
        //         for(var i=0;i<gists.length;i++){
        //             var summary = gists[i].summary;
        //             var date = gists[i].due_date;
        //             events.push({
        //                 "title":summary,
        //                 "start": date,
        //                 })
        //
        //         }
        //     console.log(events);
        //     alert(events);
        //     // return events
        //  })
        //  .catch(function(response) {
        //    console.error('Gists error', response.status, response.data);
        //  })
        //  .finally(function() {
        //    console.log("finally finished gists");
        //     // return events
        //  });
            // this.mixpanel.track('Board Wizard', { columns: this.steps.length, rows: this.rows.length });
        // }

    }
}