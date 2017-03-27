/// <reference path='../_all.ts' /> 

module scrumdo {
    export class TrackTimeController {
        public static $inject: Array<string> = [
            "timeManager",
            "trackTimeService",
            "teamManager",
            "organizationSlug",
            "projectManager",
            "$scope",
            "NgTableParams",
            "iterationManager",
            "userService",
            "confirmService",
            "$filter",
            "ngToast"
        ];

        private currentProjectSlug: string;
        private endDate;
        private startDate;
        private date;
        private startDateOpen: boolean;
        private endDateOpen: boolean;
        private userId;
        private users: Array<any>;
        private entries: Array<any>;
        private timeTrackingMode: string;
        private timeTable: any;
        private isTableEmpty: boolean = true;
        private iterations: Array<any> = [];
        private workspace:Project;
        private currentProject: Project;
        private currentIteration: Iteration;
        private pointScale;
        private currentPointScale;
        private currentLabel;
        private allLabels;
        private allTags;
        private allPoints;
        private currentTag;
        private filterOpen: boolean;
        private loading: boolean = false;
        private timeEditing;
        private currentUser: User;

        constructor(
            private timeManager: TimeManager,
            private trackTimeService: TrackTimeService,
            private teamManager,
            public organizationSlug: string,
            private projectManager,
            private scope,
            private NgTableParams,
            private iterationManager,
            private userService: UserService,
            private confirmService: ConfirmationService,
            private $filter,
            private ngToast) {
            this.currentProjectSlug = null;

            var d = new Date();
            this.endDate = this.date = moment(d).format('YYYY-MM-DD');
            d.setDate(d.getDate() - 7);
            this.startDate = this.date = moment(d).format('YYYY-MM-DD');
            this.startDateOpen = false;
            this.endDateOpen = false;
            this.userId = "";
            this.users = [];
            this.entries = [];
            this.timeTrackingMode = "scrumdo";
            this.filterOpen = true;

            this.teamManager.allUsers(organizationSlug).then((results) => {
                this.users = results;
            });

            this.viewTime();

            this.scope.$watch(() => {
                return this.workspace;
            }, (val) => {
                if (val) {
                    this.setProject();
                }
            });

            this.scope.$on("timeEntryCreated", this.viewTime);
        }

        isStaffUser(){
            if(this.userService.scope.user!=null){
                return this.userService.isOrgStaff();
            }
        }

        toggleFilters(){
            this.filterOpen = !this.filterOpen;
        }

        openStart(event: MouseEvent) {
            trace("opening start");
            this.startDateOpen = true;
            event.preventDefault();
            event.stopPropagation();
        }

        eow() {
            return moment(this.endDate).format("MM/DD/YYYY");
        }

        bow() {
            return moment(this.startDate).format("MM/DD/YYYY");
        }

        enterTime() {
            this.trackTimeService.trackTimeOnStory(null, null, null, null);
        }

        getExportTooltip(){
            if(this.startDate == null || this.endDate == null){
                return "Please specify Start and End date"
            }
        }

        setProject() {
            let projectSlug: string = this.workspace != null ? this.workspace.slug : null;

            if (typeof projectSlug !== "undefined" && projectSlug !== null) {
                this.projectManager.loadProject(this.organizationSlug, projectSlug).then((result) => {
                    this.currentProject = result;
                    this.currentProjectSlug = projectSlug;
                    this.timeTrackingMode = result.time_tracking_mode;
                    this.currentTag = null;
                    this.currentLabel = null;
                    if(this.timeTrackingMode == "scrumdo"){
                        this.loadIterations();
                        this.viewTime();
                    }
                });
            } else {
                this.timeTrackingMode = "scrumdo";
                this.currentProjectSlug = projectSlug;
                this.iterations = [];
            }
        }

        iterationChanged(){
            this.viewTime();
        }

        timeLabel(minutes) {
            var hours, minutes, ref;
            ref = minutesToHoursMinutes(minutes), hours = ref[0], minutes = ref[1];
            return hours + ":" + (pad(minutes, 2));
        }

        getAllLabels(){
            _.forEach(this.entries, (entry) => {
                _.forEach(entry.story_labels, (label:any) => {
                    if(this.allLabels == null){
                        this.allLabels = {};
                    }
                    this.allLabels[label.id] = label;
                });
                _.forEach(entry.story_tags, (tag:string) => {
                    if(this.allTags == null){
                        this.allTags = {};
                    }
                    this.allTags[tag] = tag;
                });
                if(entry.story_points != null){
                    if(this.allPoints == null){
                        this.allPoints = {};
                    }
                    this.allPoints[entry.story_points.label] = {"label":entry.story_points.label, "value": entry.story_points.value};
                }
            });
        }

        filterByLabel = (label) => {
            this.currentLabel = label;
            if(label != null){
                this.timeTable.filter()['filter_labels'] = `${label.name}_${label.id}`;
            }else{
                this.timeTable.filter()['filter_labels'] = null;
            }
        }

        filterByTag = (tag) => {
            this.currentTag = tag;
            if(tag != null){
                this.timeTable.filter()['filter_tags'] = tag;
            }else{
                this.timeTable.filter()['filter_tags'] = null;
            }
        }

        allProjects(){
            this.currentTag = null;
            this.currentLabel = null;
            this.currentProjectSlug = null;
            this.workspace = null;
            this.currentProject = null;
            this.setProject();
            this.viewTime();
        }

        viewTime = () => {
            var end, start;
            if (this.startDate !== null) {
                start = this.startDate;
            } else {
                start = "2000-01-01";
            }
            if (this.endDate !== null) {
                end = this.endDate;
            } else {
                end = "2030-01-01";
            }
            this.loading = true;
            this.allLabels = null;
            this.allPoints = null;
            this.allTags = null;
            this.timeManager.getTimeEntries(this.currentProjectSlug, this.userId, start, end, this.currentIteration).then((entries) => {
                this.loading = false;
                if (entries.length != 0) {
                    this.isTableEmpty = false;
                    entries = entries.map((entry) => {
                        entry.display_time = this.timeLabel(entry.minutes_spent);
                        return entry;
                    });
                    this.entries = entries;
                    this.createUsingFullOptions(entries);
                    this.getAllLabels();
                }else{
                    this.isTableEmpty = true;
                }
            });
        }

        public createUsingFullOptions(entries) {
            var initialParams = {
                count: 5,
                group: {project_name: "desc"}
            };
            var initialSettings = {
                counts: [5, 10, 20, 50],
                paginationMaxBlocks: 13,
                paginationMinBlocks: 2,
                dataset: entries
            };

            this.timeTable = new this.NgTableParams(initialParams, initialSettings);
        }

        deleteEntry(entry) {
            this.confirmService.confirm("Delete Entry?", 
                                        "Are you sure you want to delete this entry?", "No", "Yes").then(() => {
                                        this.onDeleteConfirm(entry) });
        }

        onDeleteConfirm = (entry) => {
            this.timeManager.deleteEntry(entry).then(this.viewTime);
        }

        updateNote(entryId, text) {
            var entry = _.find(this.entries, (e) => e.id == entryId);
            if(entry != null){
                entry.notes = text;
                this.timeManager.updateEntry(entry).then(this.onEntryUpdated);
            }
        }

        updateTimeSpent(entryId, time) {
            time = HourMinutesToMinutes(time);
            var entry = _.find(this.entries, (e) => e.id == entryId);
            if(entry != null){
                entry.minutes_spent = time;
                this.timeManager.updateEntry(entry).then(this.onEntryUpdated);
            }
        }

        onEntryUpdated = (entry) => {
            this.ngToast.create({
                content: `<i class="fa fa-check" aria-hidden="true"></i> Entry Updated`,
                timeout: 1000,
                dismissButton: true
            });
        }

        loadIterations() {
            this.iterationManager.loadIterations(this.organizationSlug, this.workspace.slug).then((result) => {
                this.iterations = result;
            });
        }

        public filterIterations = (iteration: Iteration) => {
            return iteration.iteration_type != 3;
        }

        sum(data, field, returnType: string = 'label'): number | string {
            var sum = 0;
            _.forEach(data, (ele:any) => {
                sum += ele.minutes_spent;
            })
            if(returnType == 'label'){
                return this.timeLabel(sum);
            }else{
                return sum;
            }
        }

        totalSum(data){
            var sum = 0;
            _.forEach(data, (group:any) => {
                sum += <number> this.sum(group.data ,"minutes_spent", "value");
            })
            return this.timeLabel(sum);
        }

        setUserId(user: User = null){
            if(user != null && user.id == -1){
                this.userId = "";
                this.currentUser = null;
            }else{
                this.userId = this.currentUser.id;
            }
            this.viewTime();
        }
    }
}