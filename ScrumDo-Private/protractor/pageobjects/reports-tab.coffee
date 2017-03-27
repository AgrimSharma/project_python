class ReportsTab
    constructor: (baseUrl, projectSlug) ->
        @appUrl = "#{baseUrl}/projects/#{projectSlug}/"

        @reportsUrl = @appUrl + "#/reports/cfd"
        @timelineUrl = @appUrl + '#/timeline'
        @risksUrl = @appUrl + '#/risks'
        @chatUrl = @appUrl + '#/chat'
        @planningUrl = @appUrl + '#/planning'

        @appTabs = $('.app-tabs')
        @summaryTab = @appTabs.element(By.css('[ui-sref="app.iteration.summary({iterationId:projectData.currentIteration.id})"]'))
        @dependenciesTab = @appTabs.element(By.css('[ui-sref="app.iteration.dependencies({iterationId:projectData.currentIteration.id})"]'))

        @reportsTab = element(By.css('[ui-sref="app.reports.cfd"]'))

        # @cardFirstCell = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.css('.kanban-story-list li'))
        # @sortDropdown = element.all(By.css('.board-sub-nav .action-5 button[uib-tooltip="Sort Cards"]')).get(0)
        # @saveButton = element.all(By.buttonText('Save'))
        # @backlogViewSelect = element(By.css('select[ng-change="ctrl.viewChange()"]'))
        # @newPointScaleBtn = element(By.css('.custom-point-scales a[ng-click="ctrl.addPointScale()"]'))

    get: ->
        browser.get(@appUrl)
        return @

    clickReportsTab: () ->
        return @reportsTab.click();

    clickDependenciesTab: () ->
        return @dependenciesTab.click();

    clickSummaryTab: () ->
        return @dependenciesTab.click();

module.exports = ReportsTab
