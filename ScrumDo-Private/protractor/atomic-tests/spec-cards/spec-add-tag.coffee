util = require("../util")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
describe "Scrumdo card Tag", ->
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

    it "Should add card to cell with a tag", ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('.modal-body input.tags-input')).get(0).sendKeys("scrumDo").then ->
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
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return

    it "Should have tag on card", ->
        browser.get param.projectUrl
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css("li.cards")).get(0).all(By.css(".cards-badges-wrapper span")).get(0).getText()).toEqual "#scrumDo"

    return
