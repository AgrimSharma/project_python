util = require("../util")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
describe "Scrumdo track time", ->
    storyEditWindow = new StoryEditWindow(param.hostName)
    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    #First Archive all cell cards
    it 'Should Archive all cards in a cell', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(4).click().then ->
                element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.css('.kanban-story-list li')).isPresent()).toBe false
        return

    it "Should add card to cell", ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    storyEditWindow.switchToTab(2).then ->
                        element.all(By.css('#ticketMessage')).get(0).sendKeys(param.storyComment).then ->
                            element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                                return elem.isDisplayed()
                            .click()
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return

    it "Should add time to card", ->
        elementToRightClick = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards')).get(0)
        browser.driver.actions().click(elementToRightClick,protractor.Button.RIGHT).perform().then ->
            element.all(By.css('.custom-context-menu a')).get(5).click().then ->
                element(By.css('.modal-dialog .modal-content input[ng-model="ctrl.currentValue"]')).sendKeys(param.storyTime).then ->
                    element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.enterTime()"]')).get(0).click()
                browser.waitForAngular()
            return
        return

    it "Should have added time to card", ->
        browser.get param.projectUrl
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
            expect(element.all(By.css("table.time-table tr")).last().all(By.css("td.ng-binding")).last().getText()).toEqual param.storyTime
            element(By.css('button[ng-click="ctrl.cancel()"]')).click()
        return

    return
