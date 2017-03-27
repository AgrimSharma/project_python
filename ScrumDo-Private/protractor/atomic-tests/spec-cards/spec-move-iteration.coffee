util = require("../util")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
describe 'Scrumdo Move Iteration' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    storyEditWindow = new StoryEditWindow(param.hostName)
    it 'Should add a card to cell (to test move iteration)', ->
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

    it 'Should move card to a different iteration (X)', ->
        card = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards .cards-number')).last()
        expect(card.isPresent()).toBe true
        browser.actions().mouseMove(card).keyDown(protractor.Key.SHIFT).click().perform()
        browser.actions().keyUp(protractor.Key.SHIFT).perform()
        element.all(By.css('button[uib-tooltip="Move selected cards to another workspace or iteration"]')).get(0).click()
        element.all(By.css('.safe-iteration-dropdown-toggle')).get(0).click()
        element.all(By.css('#safe-iteration-select .iteration-name')).then (options) ->
            options[2].click()
            return
        element.all(By.css('button[ng-click="ctrl.ok(selectedProject)"]')).filter (elem) ->
            return elem.isDisplayed()
        .click()
        browser.waitForAngular()
        #check if card was moved successfully
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe false
        return
    return
