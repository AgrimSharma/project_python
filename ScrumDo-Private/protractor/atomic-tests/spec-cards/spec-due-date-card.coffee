util = require("../util")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
describe 'Scrumdo Due Date' , ->
    storyEditWindow = new StoryEditWindow(param.hostName)
    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    it 'Should add a card to cell', ->
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

    it 'Should have red calendar icon', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
            element(By.model('story.due_date')).element(By.css('button')).click().then ->
                element.all(By.css('.uib-datepicker-popup')).get(0).element(By.css('button[ng-click="move(-1)"]')).click().then ->
                    element.all(By.css('.uib-datepicker-popup')).get(0).element(By.css('table tbody tr:nth-child(2) td:nth-child(3) button')).click().then ->
                        element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                            return elem.isDisplayed()
                        .click()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards')).last().element(By.css('li.due-date .past-due')).isPresent()).toBe true

    it 'Should have yellow calendar icon', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
            element(By.model('story.due_date')).element(By.css('button')).click().then ->
                element.all(By.css('.uib-datepicker-popup')).get(0).element(By.buttonText("Today")).click()
            element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                return elem.isDisplayed()
            .click()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards')).last().element(By.css('li.due-date .due-soon')).isPresent()).toBe true

    it 'Should have grey calendar icon', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
            element(By.model('story.due_date')).element(By.css('button')).click().then ->
                element.all(By.css('.uib-datepicker-popup')).get(0).element(By.css('button[ng-click="move(1)"]')).click().then ->
                    element.all(By.css('.uib-datepicker-popup')).get(0).element(By.css('table tbody tr:nth-child(2) td:nth-child(3) button')).click().then ->
                        element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                            return elem.isDisplayed()
                        .click()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards')).last().element(By.css('li.due-date')).isPresent()).toBe true

    it 'Should not have calendar icon', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
            element(By.model('story.due_date')).element(By.css('button')).click().then ->
                element.all(By.css('.uib-datepicker-popup')).get(0).element(By.buttonText("Clear")).click().then ->
                    element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                        return elem.isDisplayed()
                    .click()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards')).last().element(By.css('li.due-date')).isPresent()).toBe false

    it 'Should delete a card from cell (after adding)', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
            element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.deleteCard()"]')).get(0).click().then ->
                element.all(By.buttonText('Yes')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
        #check if card was deleted successfully
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe false
        return
    return
