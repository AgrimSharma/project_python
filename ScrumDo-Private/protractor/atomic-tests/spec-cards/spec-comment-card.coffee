util = require("../util")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
describe 'Scrumdo add comment to Card' , ->
    story = new StoryEditWindow(param.hostName)
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

    it 'Should add a card to cell', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    story.switchToTab(2).then ->
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

    it 'Should have comment', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
            story.switchToTab(2)
            expect(element(By.css('.cards-log li')).isPresent()).toBe true
            element(By.css('button[ng-click="ctrl.cancel()"]')).click().then ->
            element.all(By.buttonText('Yes')).filter (elem) ->
                    return elem.isDisplayed()
                .click()


    it 'Should add 2 more comment to card', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click()
        story.switchToTab(2)
        element(By.css('#ticketMessage')).sendKeys(param.storyComment).then ->
            element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.addComment()"]')).get(0).click()
            return
        element(By.css('#ticketMessage')).sendKeys(param.storyComment).then ->
            element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.addComment()"]')).get(0).click()
            return
        element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
            return elem.isDisplayed()
        .click()
        browser.waitForAngular()

        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css("li.cards")).get(0).all(By.css(".cards-details .cards-information li")).get(1).element(By.css(".cards-comments-info span")).getText()).toEqual "3"
        return

    it 'Should delete comment from card', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click()
        story.switchToTab(2)
        element.all(By.css('.cards-log li')).get(0).element(By.css("span.comment-delete")).click().then ->
            element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.ok()"]')).get(0).click().then ->
                element.all(By.buttonText('Yes')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
            return elem.isDisplayed()
        .click()
        browser.waitForAngular()

        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css("li.cards")).get(0).all(By.css(".cards-details .cards-information li")).get(1).element(By.css(".cards-comments-info span")).getText()).toEqual "2"
        return

    it 'Should update comment count with cancel button', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click()
        story.switchToTab(2)
        element.all(By.css('.cards-log li')).get(0).element(By.css("span.comment-delete")).click().then ->
            element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.ok()"]')).get(0).click().then ->
                element.all(By.buttonText('Yes')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        element.all(By.css('button[ng-click="ctrl.cancel()"]')).filter (elem) ->
            return elem.isDisplayed()
        .click().then ->
            element.all(By.buttonText('Yes')).filter (elem) ->
                    return elem.isDisplayed()
                .click()

        browser.waitForAngular()

        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css("li.cards")).get(0).all(By.css(".cards-details .cards-information li")).get(1).element(By.css(".cards-comments-info span")).getText()).toEqual "1"
        return

    it 'Should have updated comment count on page reload', ->
        browser.get param.projectUrl
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css("li.cards")).get(0).all(By.css(".cards-details .cards-information li")).get(1).element(By.css(".cards-comments-info span")).getText()).toEqual "1"
        return

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
