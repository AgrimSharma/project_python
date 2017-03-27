util = require("../util")

StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
ProjectBoard = require("../../pageobjects/project-board.coffee")
ProjectApp = require("../../pageobjects/project-app.coffee")

describe 'Scrumdo Iteration Sort', ->

    storyEditWindow = new StoryEditWindow(param.hostName)
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    projectApp = new ProjectApp(param.hostName, param.projectSlug)

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName + "Sort Test"

    #First Archive all cell cards
    it 'Should Archive all cards in all cell', ->
        board.get()

        element.all(By.css('.kanban-cell')).get(0).all(By.css('.scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(4).click().then ->
                element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
        element.all(By.css('.kanban-cell')).get(1).all(By.css('.scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(1).all(By.css('.dropdown-menu li a')).get(4).click().then ->
                element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
        element.all(By.css('.kanban-cell')).get(2).all(By.css('.scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(2).all(By.css('.dropdown-menu li a')).get(4).click().then ->
                element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.css('.kanban-story-list li')).isPresent()).toBe false
        return

    it 'Should add a card to cell with point 1 & business val 10 & estimate time 4', ->
        thiscardName = "#{cardName} - 1"
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(thiscardName).then ->
                    storyEditWindow.switchToTab(2).then ->
                        element.all(By.css('#ticketMessage')).get(0).sendKeys(param.storyComment).then ->
                            storyEditWindow.pointsDropDown.element(By.css(".dropdown-toggle")).click().then ->
                                storyEditWindow.pointsDropDown.element(By.css(".dropdown-menu")).all(By.css('li')).get(3).click().then ->
                                    storyEditWindow.businessValue.element(By.css('input[type="text"]')).sendKeys(10).then ->
                                        storyEditWindow.estimateTime.element(By.css('input[type="text"]')).sendKeys(4).then ->
                                            element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                                                return elem.isDisplayed()
                                            .click()
                                            return
                                        return
                                    return
                                return
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + thiscardName + '")]')).isPresent()).toBe true
        return

    it 'Should add a card to cell  with point 2 & business val 20 & estimate time 6', ->
        thiscardName = "#{cardName} - 2"
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(thiscardName).then ->
                    storyEditWindow.switchToTab(2).then ->
                        element.all(By.css('#ticketMessage')).get(0).sendKeys(param.storyComment).then ->
                            storyEditWindow.pointsDropDown.element(By.css(".dropdown-toggle")).click().then ->
                                storyEditWindow.pointsDropDown.element(By.css(".dropdown-menu")).all(By.css('li')).get(4).click().then ->
                                    storyEditWindow.businessValue.element(By.css('input[type="text"]')).sendKeys(20).then ->
                                        storyEditWindow.estimateTime.element(By.css('input[type="text"]')).sendKeys(6).then ->
                                            element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                                                return elem.isDisplayed()
                                            .click()
                                            return
                                        return
                                    return
                                return
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + thiscardName + '")]')).isPresent()).toBe true
        return

    it 'Should add a card to cell  with point 3 & business val 30 & estimate time 1', ->
        thiscardName = "#{cardName} - 3"
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(thiscardName).then ->
                    storyEditWindow.switchToTab(2).then ->
                        element.all(By.css('#ticketMessage')).get(0).sendKeys(param.storyComment).then ->
                            storyEditWindow.pointsDropDown.element(By.css(".dropdown-toggle")).click().then ->
                                storyEditWindow.pointsDropDown.element(By.css(".dropdown-menu")).all(By.css('li')).get(5).click().then ->
                                    storyEditWindow.businessValue.element(By.css('input[type="text"]')).sendKeys(30).then ->
                                        storyEditWindow.estimateTime.element(By.css('input[type="text"]')).sendKeys(1).then ->
                                            element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                                                return elem.isDisplayed()
                                            .click()
                                            return
                                        return
                                    return
                                return
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + thiscardName + '")]')).isPresent()).toBe true
        return

    it 'Should sort cards with point value', ->
        projectApp.gotoTabs("cardlist")
        #toggle to priority mode
        element.all(By.css('.backlog-container-tools button[uib-tooltip="Toggle Priority/WSJF View"]')).get(0).click()
        #sort with point value
        element.all(By.css('.backlog-container-tools button[uib-tooltip="Sort"]')).get(0).click().then ->
            element.all(By.css('.backlog-container-tools ul.dropdown-menu li')).get(3).click()

        card1 = element.all(By.css('.story-list')).get(0).all(By.css('li.backlog-container-card')).get(0).all(By.css('.points-value span')).get(0)
        card2 = element.all(By.css('.story-list')).get(0).all(By.css('li.backlog-container-card')).get(1).all(By.css('.points-value span')).get(0)
        card3 = element.all(By.css('.story-list')).get(0).all(By.css('li.backlog-container-card')).get(2).all(By.css('.points-value span')).get(0)
        expect(card1.getText()).toBe('1')
        expect(card2.getText()).toBe('2')
        expect(card3.getText()).toBe('3')
        return

    it 'Should sort cards with business value', ->
        #sort with business value
        element.all(By.css('.backlog-container-tools button[uib-tooltip="Sort"]')).get(0).click().then ->
            element.all(By.css('.backlog-container-tools ul.dropdown-menu li')).get(4).click()
        card1 = element.all(By.css('.story-list')).get(0).all(By.css('li.backlog-container-card')).get(0).all(By.css('.value span')).get(2)
        card2 = element.all(By.css('.story-list')).get(0).all(By.css('li.backlog-container-card')).get(1).all(By.css('.value span')).get(2)
        card3 = element.all(By.css('.story-list')).get(0).all(By.css('li.backlog-container-card')).get(2).all(By.css('.value span')).get(2)
        expect(card1.getText()).toBe('30')
        expect(card2.getText()).toBe('20')
        expect(card3.getText()).toBe('10')
        return

    it 'Should sort cards with estimate time', ->
        #sort with estimate time
        element.all(By.css('.backlog-container-tools button[uib-tooltip="Sort"]')).get(0).click().then ->
            element.all(By.css('.backlog-container-tools ul.dropdown-menu li')).get(5).click()
        card1 = element.all(By.css('.story-list')).get(0).all(By.css('li.backlog-container-card')).get(0).all(By.css('.estimate-value span')).get(0)
        card2 = element.all(By.css('.story-list')).get(0).all(By.css('li.backlog-container-card')).get(1).all(By.css('.estimate-value span')).get(0)
        card3 = element.all(By.css('.story-list')).get(0).all(By.css('li.backlog-container-card')).get(2).all(By.css('.estimate-value span')).get(0)
        expect(card1.getText()).toBe('1:00')
        expect(card2.getText()).toBe('4:00')
        expect(card3.getText()).toBe('6:00')
        return

    return
