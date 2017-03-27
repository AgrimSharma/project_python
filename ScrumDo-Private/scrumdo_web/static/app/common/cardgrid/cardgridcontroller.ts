/// <reference path='../../_all.ts' />

/*
 A reusable grid with cards in each cell.  Useful for our dependency view, our team-plan view, perhaps
 others in the future.

 To use:

 <sd-card-grid card-provider="ctrl.gridCardProvider" rows="ctrl.rows" columns="ctrl.columns"></sd-card-grid>

 rows - Array of CardGridRow
 columns - Array of CardGridColumn
 cardProvider - A function that will return a list of card that should go in a particular cell.
                function(row:CardGridRow, column:cardGridColumn):CardGridCellData

 */

module scrumdo {

    interface BaseCardGrid {
        id: string;
        title: string;
        visible: boolean;
    }

    export interface CardGridRow extends BaseCardGrid { }

    export interface CardGridColumn extends BaseCardGrid { }

    interface CardGridScope extends ng.IScope {
        ctrl: CardGridController;
        rows:Array<CardGridRow>;
        columns:Array<CardGridColumn>;
        cardProvider: Function;
        sortOrder: string|Function;
    }

    export class CardGridController {
        public static $inject:Array<string> = [
            "organizationSlug",
            "$scope",
            "epicManager",
            "STATIC_URL",
            "$element",
            "$filter"
        ];

        public epics:Array<Epic>;
        public sidebarVisible:boolean = false;
        protected providerCache = {};
        public setupSortable;

        constructor(private organizationSlug:string,
                    private $scope:CardGridScope,
                    epicManager:EpicManager,
                    STATIC_URL,
                    private $element,
                    private $filter) {

            $scope['STATIC_URL'] = STATIC_URL;  // TODO: some sub components have a dependency on this, refactor those
            this.setupSortable = _.debounce(this._setupSortable, 100);
            this.setupSortable();

            this.$scope.$watch('rows.length', this.setupSortable);
            this.$scope.$on('backlogToggled', this.setupSortable);
            this.$scope.$on('cardGridLayoutChanges', this.setupSortable);
            this.$scope.$on('purgeCardProviderCache', this.onPurgeCardProviderCache);

        }


        private sortables:Array<any> = [];

        _setupSortable = () => {

            trace('cardGridController._setupSortable()')
            if(isMobileDevice()){
                return;
            }
            for(let sortable of this.sortables) {
                sortable.destroy();
            }

            this.sortables = [];

            let dragElements = ".card-grid-list, .card-sortable-cell";

            // this.element.find(dragElements).unbind("sortablestart", this.onDragStart);
            // this.element.find(dragElements).bind("sortablestart", this.onDragStart);

            $(dragElements).each( (index, el) => {
                this.sortables.push(new Sortable(el, {
                    group: 'stories',
                    filter: ".task-view, .no-drag, .embedded-task-window, .task-view",
                    draggable: ".cards",
                    onEnd: this.dragStopped,
                    onAdd: this.onSortStory,
                    onUpdate: this.onSortStory
                }));
            })

            trace("Setting up drag & drop " + this.sortables.length);
        }

        dragStopped = () => {
            this.$scope.$root.$broadcast('cardDragStop');
        }

        onSortStory = (event) => {
            trace("CardGridController::onSortStory");
            this.dragStopped();

            // This is the html element that was dragged.
            // for single select, it is the story view
            // for multi select, it doesn't matter, get story id's from selected stories.
            let item = $(event.item);
            let placeholder = $(event.placeholder);
            let parentList = placeholder.parent();
            let parent = parentList.parent();


            if (!((parentList != null) && parentList.length > 0)) {
                return;
            }

            if(parentList[0].nodeName == 'TD') {
                parent = parentList;
            }

            // var cellId = parseInt(parentList.attr("data-cell-id"));
            //let iterationId = parseInt(parentList.attr("data-iteration-id"));
            let rowId = parent.attr("data-row-id");
            let columnId = parent.attr("data-column-id");
            let storyId = parseInt(item.attr("data-story-id"));
            let distance = Math.abs(placeholder.index() - item.index());



            if ((distance === 1) && (parentList[0] === item.parent()[0])) {
                trace("Dropped an item above or below itself, skipping");
                placeholder.remove();
                return;
            }

            if ((storyId == null) || isNaN(storyId)) {
                trace("ERROR: Dragged an element without a data-story-id");

                this.$scope.$emit("cardGridRawDrag",{
                    storyId: storyId,
                    placeholder:placeholder
                });

                return;
            }

            if (rowId == null) {
                trace("ERROR: Dragged to container with no row id");

                this.$scope.$emit("cardGridRawDrag",{
                    storyId: storyId,
                    placeholder:placeholder
                });

                return
            }

            if (columnId == null) {
                trace("ERROR: Dragged to container with no column id");

                this.$scope.$emit("cardGridRawDrag",{
                    storyId: storyId,
                    placeholder:placeholder
                });

                return
            }

            trace(`Card dropped on ${rowId} ${columnId}`);
            this.$scope.$emit("cardGridDrag",{
                storyId: storyId,
                row: _.findWhere(this.$scope.rows, {id:rowId}),
                column: _.findWhere(this.$scope.columns, {id:columnId}),
                placeholder:placeholder
            });

            placeholder.remove();

            this.$scope.$apply();
        }

        newCard(row, column) {
            this.$scope.$emit("newCard",{
                row: row,
                column: column
            });
        }

        showAll() {
            for(var row of this.$scope.rows) {row.visible = true;}
            for(var column of this.$scope.columns) {column.visible = true;}
            this.setupSortable();
        }

        toggleSidebar() {
            this.sidebarVisible = !this.sidebarVisible;
            this.setupSortable();
        }

        removeRow(row) {
            this.$scope.$emit('removeCardRow', row);
        }

        toggleColumn(column) {
            column.visible = ! column.visible ;
            this.signalDependenciesChanged();
            this.setupSortable();
        }

        toggleRow(row) {
            row.visible = ! row.visible ;
            this.signalDependenciesChanged();
            this.setupSortable();
        }

        tableWidth():string {
            if(this.$scope.columns == null){
                return 120 + "px";
            }
            if(this.$scope.columns.length > 1 && !this.haveContinousRow()){
                return 120 + 295 * _.where(this.$scope.columns,{visible:true}).length + 'px';
            }else{
                if(this.haveContinousRow()){
                    return '';
                }else{
                    return '100%';
                }
            }
        }

        getCellData(row:CardGridRow, column:CardGridColumn):CardGridCellData {
            let cacheHash = `${row.id}::${column.id}`;
            if(cacheHash in this.providerCache) { return this.providerCache[cacheHash]; }

            let provider = this.$scope.cardProvider(row, column);
            this.providerCache[cacheHash] = provider;
            return provider;
        }

        private getRowColSpan(row){
            if(row.extraInfo == null || row.extraInfo["spanEntire"] == null){
                return 1;
            }
            if(row.extraInfo["spanEntire"] === true){
                return _.filter(this.$scope.columns, (col) => col.visible == true).length;
            }
            return 1;
        }

        private orderRows = (row) => {
            if(row.extraInfo == null || row.extraInfo["spanEntire"] == null){
                return 1;
            }
            if(row.extraInfo["spanEntire"] === true){
                return 0;
            }
            return 1;
        }

        private haveContinousRow(){
            return _.find(this.$scope.rows, (row: any) => row.extraInfo != null && row.extraInfo.spanEntire === true) != null;
        }

        onPurgeCardProviderCache = () => {
            this.providerCache = {};
        }

        getRowItems(row: CardGridRow){
            var total: number = 0;
            _.forEach(this.$scope.columns, (col: CardGridColumn) => {
                let cellData = this.getCellData(row, col);
                total += cellData.cards.length;
            });
            return total;
        }

        getColItems(col: CardGridColumn){
            var items: Array<Story> = [];
            _.forEach(this.$scope.rows, (row: CardGridRow) => {
                let cellData = this.getCellData(row, col);
                items = items.concat(cellData.cards);
            });
            return items;
        }

        getColPoints(col: CardGridColumn){
            let stories = this.getColItems(col);
            return Math.round(_.reduce(stories, this.sumPoints, 0) * 100) / 100;
        }

        public sumPoints(n, story) {
            return n + story.points_value;
        }

        getColWipTooltip(col: CardGridColumn, limit: number, type: string = "cards"){
            var toolTip:string = "<div class='wip-tooltip'>";
            let stories = this.getColItems(col);
            if(type == "cards"){
                toolTip += "Current cards: " + stories.length + "<br/>";
                if(limit > 0){ 
                    toolTip += "Maximum cards: " + limit + "<br/>";
                }
            }else{
                let points = Math.round(_.reduce(stories, this.sumPoints, 0) * 100) / 100;
                toolTip += "Current points: " + points + "<br/>";
                if(limit > 0){ 
                    toolTip += "Maximum points: " + limit + "<br/>";
                }
            }
            toolTip += "</div>";
            return toolTip;
        }

        overWip(col: CardGridColumn, limit: number, type: string = "cards"){
            let stories = this.getColItems(col);
            if(type == "cards"){
                let value = stories.length;
                return (value > limit && limit > 0);
            }else{
                let points = Math.round(_.reduce(stories, this.sumPoints, 0) * 100) / 100;
                return (points > limit && limit > 0);
            }
        }

        updateWIPLimits(col: CardGridColumn){
            this.$scope.$emit("iterationWipSettings",{
                column: col
            });
        }

        signalDependenciesChanged() {
            this.$scope.$root.$broadcast('dependencyChanged');
        }

        getColumnTooltipText(column){
            if(column.iteration.mission != '' && column.iteration.mission != null){
                return `Mission: ${this.$filter('htmlToPlaintext')(column.iteration.mission)}`;
            }else{
                return null;
            }
        }

    }
}