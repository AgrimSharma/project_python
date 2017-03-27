util = require("../util")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
describe 'Scrumdo Add Time' , ->
    storyEditWindow = new StoryEditWindow(param.hostName)
    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardTime = param.storyTime
    cardName = param.cardName
    it 'Should add a card to cell (to test time estimate)', ->
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

    it 'Should add time estimate to story', ->
        # browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.css('li.cards div.cards-header span.pull-right')).click().then ->
            inputTag = element.all(By.css('.modal-content input[placeholder="Estimate (hh:mm)"]')).filter (elem) ->
                return elem.isDisplayed()
            inputTag.clear().then ->
                inputTag.sendKeys(cardTime)
                return
            element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                return elem.isDisplayed()
            .click()
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-details ul.cards-information li')).get(0).element(By.css('span')).getText()).toEqual cardTime
        return
    return
