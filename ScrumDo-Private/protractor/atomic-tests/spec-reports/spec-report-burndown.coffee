util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")

describe 'Scrumdo Burn down report' , ->
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    storyEditWindow = new StoryEditWindow(param.hostName)
    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName + "Sort Test"

    it 'Should Archive all cards in first cell', ->
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
								
    it 'Should Archive all cards in done cell', ->

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(1).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(1).all(By.css('.dropdown-menu li a')).get(4).click().then ->
                element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).element(By.css('.kanban-story-list li')).isPresent()).toBe false
        return

    it 'should reset burn-up data', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Admin Options")]')).click().then ->
                element.all(By.css('.scrumdo-btn.secondary')).get(3).click().then ->
                return
            return
        browser.waitForAngular()
        expect(element(By.css('.fa.fa-gears')).isPresent()).toBe true
        return

    thiscardName = "#{cardName} - 1"
    it 'Should create card with point',->

        browser.get param.projectUrl
        
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(thiscardName).then ->
                    storyEditWindow.switchToTab(2).then ->
                        element.all(By.css('#ticketMessage')).get(0).sendKeys(param.storyComment).then ->
                            storyEditWindow.pointsDropDown.element(By.css(".dropdown-toggle")).click().then ->
                                storyEditWindow.pointsDropDown.element(By.css(".dropdown-menu")).all(By.css('li')).get(3).click().then ->
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
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + thiscardName + '")]')).isPresent()).toBe true
        return
								
    it 'Should select report burndown', ->
				    board.gotoReports()
        # Select Burn down report from report selection
        board.selectReport('Burn Down').then ->
            browser.waitForAngular()
            iteration = element(By.xpath('(//select[@ng-model="ctrl.reportOptions.iteration"])[2]'))
            
            board.selectDropdownbyNum(iteration, 1).then ->
                board.refreshReport().then ->
                    browser.waitForAngular()
                    return
        return
								
    it 'Should verify point value on graph', ->
        pointtext = element.all(By.css('.y .tick text'))
				
        browser.waitForAngular()
        expect(pointtext.get(10).getText()).toEqual('1.0')
        return
																
    it 'Should move card to done', ->
        browser.get param.projectUrl
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
            element.all(By.css('.scrumdo-modal-card-buttons .form-group')).get(1).element(By.css('button.scrumdo-select-button')).click().then ->
                element.all(By.css('.cell-picker svg g g')).get(3).click()
                element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
        #check if card was moved successfully
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + thiscardName + '")]')).isPresent()).toBe true
        return
								
    it 'Should select report burndown', ->
				    board.gotoReports()
        # Select Burn down report from report selection
        board.selectReport('Burn Down').then ->
            browser.waitForAngular()
            iteration = element(By.xpath('(//select[@ng-model="ctrl.reportOptions.iteration"])[2]'))
            
            board.selectDropdownbyNum(iteration, 1).then ->
                board.refreshReport().then ->
                    browser.waitForAngular()
                    return
        return
								
    it 'Should verify burn down graph when card in done state', ->
				
        pointtext = element(By.css('.area-band'))
				
        browser.waitForAngular()
        expect(pointtext.isDisplayed()).toBe true
        return