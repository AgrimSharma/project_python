class StoryEditWindow
    constructor: (baseUrl) ->
        @loginUrl = "#{baseUrl}/account/login/"
        @loginLink = element(By.id('loginLink'))
        @dropdownMenu = element(By.css('.nav-settings .dropdown-menu li'))

        @iterationsDropdown = element(By.css('.card-modal sd-story-fields .iterations-dropdown'))
        @pointsDropDown = element(By.css('.card-modal sd-story-fields .points-dropdown'))
        @cellsDropdown = element(By.css('.card-modal sd-story-fields .cells-dropdown'))
        @businessValue = element(By.css('.card-modal sd-story-fields .business-input'))
        @estimateTime = element(By.css('.card-modal sd-story-fields .estimate-input'))
        @timeCriticality = element(By.css('.card-modal sd-story-fields .time-criticality'))
        @riskReduction = element(By.css('.card-modal sd-story-fields .risk-reduction'))
        @saveButton = element.all(By.buttonText('Save Card'))
        @closeButton = element(By.css('button[ng-click="ctrl.cancel()"]'))
        @minimizeButton = element(By.css('button[ng-click="ctrl.minimize()"]'))
        @releaseDropDown = element(By.css('.card-modal sd-story-fields .release-dropdown'))
        @summaryBox = element(By.css('#summaryEditor div.scrumdo-mce-editor'))
        @tagsBox = element.all(By.css('.modal-body input.tags-input')).get(0)
        @addTagButton = element.all(By.css('button[ng-click="ctrl.addTag()"]'))
        @commentBox = element.all(By.css('#ticketMessage')).get(0)
        @dueDate = element(By.model('story.due_date')).element(By.css('button'))
        @blockerButton = element(By.css('button[ng-click="ctrl.promptBlocker()"]'))
        @blockerReasonInput = element(By.css('input[sd-enter="ctrl.blockStory()"]'))
        @blockerResolutionInput = element(By.css('input[sd-enter="ctrl.resolveBlocker()"]'))
        @playPokerButton = element(By.css('button[ng-click="ctrl.playPoker()"]'))
        @labelDropdown = element(By.css('.card-modal .scrumdo-labels-box .scrumdo-select'))
        @assigneeBox = element(By.css('.card-modal sd-assignee-box .scrumdo-select'))


        @minimizedCloseButton = element(By.css('.minimized-controls button[ng-click="ctrl.cancel()"]'))
        @maximizeButton = element(By.css('.minimized-controls button[ng-click="ctrl.maximize()"]'))

    switchToTab: (index) ->
        # index
        # 0 -> Detials , 1 -> Hostory, 2 -> Comments 3 -> Links, 4 -> Tasks
        return element(By.css(".nav-tabs li[index='#{index}'] a")).click()

    setCardSummary: (summary) ->
        return @summaryBox.sendKeys(summary)

    setTag: (tag) ->
        return  @tagsBox.sendKeys(tag)

    setComment: (comment) ->
        return @commentBox.sendKeys(comment)

    setPoints: (index) =>
        return  @pointsDropDown.element(By.css(".dropdown-toggle")).click().then =>
                    @pointsDropDown.element(By.css(".dropdown-menu")).all(By.css('li')).get(index).click()

    setBusinessValue: (value) =>
        return @businessValue.element(By.css('input[type="text"]')).sendKeys(value)

    setEstimateTime: (time) =>
        return @estimateTime.element(By.css('input[type="text"]')).sendKeys(time)

    setRiskReduction: (index) =>
        return  @riskReduction.element(By.css(".dropdown-toggle")).click().then =>
                    @riskReduction.element(By.css(".dropdown-menu")).all(By.css('li')).get(index).click()

    setTimeCriticality: (index) =>
        return  @timeCriticality.element(By.css(".dropdown-toggle")).click().then =>
                    @timeCriticality.element(By.css(".dropdown-menu")).all(By.css('li')).get(index).click()

    setDate: (type) =>
        switch type
            when "past"
                return  @dueDate.click().then =>
                            element.all(By.css('.uib-datepicker-popup')).get(0).element(By.css('button[ng-click="move(-1)"]')).click().then ->
                                element.all(By.css('.uib-datepicker-popup')).get(0).element(By.css('table tbody tr:nth-child(2) td:nth-child(3) button')).click()
            when "today"
                return  @dueDate.click().then =>
                            element.all(By.css('.uib-datepicker-popup')).get(0).element(By.buttonText("Today")).click()
            when "future"
                return  @dueDate.click().then =>
                            element.all(By.css('.uib-datepicker-popup')).get(0).element(By.css('button[ng-click="move(1)"]')).click().then ->
                                element.all(By.css('.uib-datepicker-popup')).get(0).element(By.css('table tbody tr:nth-child(2) td:nth-child(3) button')).click()

    clickSave: =>
        return @saveButton.click()

    close: =>
        return @closeButton.click()

    playPoker: =>
        return @playPokerButton.click()

    addBlocker: (reason, isExternal=false) =>
        @blockerButton.click().then =>
            @blockerReasonInput.sendKeys(reason).then =>
                if isExternal
                    element(By.css("#is_external_cause")).click()
                element(By.css('button[ng-click="ctrl.blockStory()"]')).click()
        browser.waitForAngular()

    resolveBlocker: (resolution, blockerIndex=0) =>
        element.all(By.css('.blockers-box a[ng-click="ctrl.promptBlocker(entry)"]')).get(blockerIndex).click().then =>
            @blockerResolutionInput.sendKeys(resolution).then =>
                element(By.css('button[ng-click="ctrl.resolveBlocker()"]')).click()
        browser.waitForAngular()

    hasClass: (element, cls) ->
        return element.getAttribute('class').then (classes) ->
            return classes.split(' ').indexOf(cls) != -1

    minimize: =>
        return @minimizeButton.click()

    closeMinimized: =>
        return @minimizedCloseButton.click()

    maximize: =>
        return @maximizeButton.click()

    selectParentProject: (index) =>
        return element.all(By.css(".release-project-selector .project-picker li")).get(index).click()

    selectProjectRelease: (index) =>
        return element.all(By.css(".release-project-selector .releases li")).get(index+1).click()

module.exports = StoryEditWindow
