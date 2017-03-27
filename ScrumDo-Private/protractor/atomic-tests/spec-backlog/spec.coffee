util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
describe 'Scrumdo Backlog' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = "Backlog Card-#{Math.floor(Date.now() / 1000)}"
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    story = new StoryEditWindow(param.hostName)

    it 'Should Add a Cards to Backlog', ->
        board.get()
        board.toggleBacklog()

        element.all(By.css('div.summary-editor')).get(0).click()
        browser.actions().sendKeys(cardName).perform().then ->
            browser.sleep(1000)
            element.all(By.css('.scrumdo-backlog-add .row .col-sm-3 button')).get(0).click()
            return
        browser.waitForAngular()
        #check if card was successfully added with card name
        expect(element.all(By.css('.scrumdo-backlog-scroll-reset')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return

    it 'Should Add Comment to a Backlog Card', ->
        element.all(By.css('.scrumdo-backlog-scroll-reset li.cards div.cards-header span.pull-right')).get(0).click()
        story.switchToTab(2)
        element(By.css('#ticketMessage')).sendKeys(param.storyComment).then ->
            element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.addComment()"]')).get(0).click()
            return
        browser.sleep(2000)
        element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.save($event)')).get(0).click()
        browser.waitForAngular()
        element.all(By.css('.scrumdo-backlog-scroll-reset li.cards div.cards-header span.pull-right')).get(0).click()
        story.switchToTab(2)
        el = element.all(By.css('div.cards-message-response')).get(0)
        expect(el.getText()).toContain(param.storyComment);
        return

    it 'Should add a Tag to Backlog Card', ->
        story.switchToTab(0)
        element.all(By.css('.scrumdo-tags-box input[placeholder="Add a tag..."]')).filter (elem) ->
            return elem.isDisplayed()
        .sendKeys(param.storyTag)
        element.all(By.css('span[ng-click="ctrl.addTag()"]')).filter (elem) ->
            return elem.isDisplayed()
        .click()
        element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.save($event)"]')).get(0).click()
        browser.waitForAngular()
        element.all(By.css('.scrumdo-backlog-scroll-reset li.cards div.cards-header span.pull-right')).get(0).click()
        expect(element.all(By.css('.scrumdo-tags-box .tags-list span.scrumdo-tags')).get(0).isPresent()).toBe true
        element(By.css('button[ng-click="ctrl.cancel()"]')).click().then ->
            element.all(By.buttonText('Yes')).filter (elem) ->
                    return elem.isDisplayed()
                .click()

        return

    it 'Should add a task to Backlog card', ->
        element.all(By.css('.scrumdo-backlog-scroll-reset li.cards div.cards-header span.pull-right')).get(0).click()
        story.switchToTab(4)
        element.all(By.css('button[ng-click="ctrl.newTask()"]')).get(0).click()
        element.all(By.css('input[ng-model="task.summary"]')).get(0).sendKeys(param.taskSummery)
        element.all(By.css('select#assignee')).get(0).all(By.tagName('option')).then (options) ->
            options[1].click()
            return
        element.all(By.css('button[ng-click="ctrl.save($event)"]')).get(0).click()
        browser.waitForAngular()
        element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.save($event)"]')).get(0).click()
        browser.waitForAngular()
        return

    it 'Should delete task from card', ->
        element.all(By.css('.scrumdo-backlog-scroll-reset li.cards div.cards-header span.pull-right')).get(0).click()
        story.switchToTab(4)
        element.all(By.css('.task-list span[ng-click="ctrl.edit()"]')).get(0).click()
        element.all(By.css('button[ng-click="ctrl.confirmDelete()"]')).get(0).click().then ->
            element.all(By.buttonText('Yes')).filter (elem) ->
                return elem.isDisplayed()
            .click()
            return
        element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.cancel()"]')).get(0).click()
        browser.waitForAngular()
        return

    it 'Should confirm the deletion of a card', ->
        element.all(By.css('.scrumdo-backlog-scroll-reset li.cards div.cards-header span.pull-right')).get(0).click()
        element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.deleteCard()"]')).get(0).click().then ->
            element.all(By.buttonText('Yes')).filter (elem) ->
                return elem.isDisplayed()
            .click()
            return
        browser.waitForAngular()
        #check if card was deleted successfully
        expect(element.all(By.css('.scrumdo-backlog-scroll-reset')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe false
        return

    it 'Should Add a Cards to Backlog', ->
        element.all(By.css('div.summary-editor')).get(0).click()
        browser.actions().sendKeys(cardName).perform().then ->
            browser.sleep(1000)
            element.all(By.css('.scrumdo-backlog-add .row .col-sm-3 button')).get(0).click()
            return
        browser.waitForAngular()
        #check if card was successfully added with card name
        expect(element.all(By.css('.scrumdo-backlog-scroll-reset')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return

    it 'Should Select all cards to Backlog', ->
        element.all(By.css('.scrumdo-backlog-cards .dropdown-toggle')).last().click()
        element(By.css('a[ng-click="ctrl.selectAll($event)"]')).click().then ->
            browser.sleep(1000)
            element.all(By.css('.kanban-story-list .cards.story-list-style')).each (elem) ->
                expect(elem.getAttribute('class')).toMatch('selected')
        return

    it 'Should have No-Epic section', ->
        board.toggleBacklogView("epic")
        element.all(By.css("sd-backlog-no-epics .scrumdo-panel-title a")).last().click().then ->
            expect(element.all(By.css("sd-backlog-no-epics li.cards")).count()).toEqual 1

        return

    it "Should retain the epic view", ->
        board.get()
        board.toggleBacklog()
        element.all(By.css("sd-backlog-no-epics .scrumdo-panel-title a")).last().click().then ->
            expect(element.all(By.css("sd-backlog-no-epics li.cards")).count()).toEqual 1
        board.toggleBacklogView("list")
        return
    
    it "Shoud cancel the creation of backlog story", ->
        element.all(By.css('div.summary-editor')).get(0).click()
        browser.actions().sendKeys(cardName).perform().then ->
            browser.sleep(1000)
            element.all(By.css('.scrumdo-backlog-add .row .col-sm-3 button')).get(1).click().then ->
                browser.sleep(1000)
                expect(element(By.css('.scrumdo-backlog-add-container')).getAttribute('class')).toBe 'scrumdo-backlog-add-container'
            return
        return
    return