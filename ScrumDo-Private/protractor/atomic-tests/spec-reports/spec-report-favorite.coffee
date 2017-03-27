util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")

describe 'Scrumdo Favorite report' , ->
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    storyEditWindow = new StoryEditWindow(param.hostName)
    afterEach () ->
        #util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    it 'Should create card with point',->
        browser.get param.projectUrl
        
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
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
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return
								
    it 'Should navigate to reports page', ->    
        board.gotoReports()
        return

    it 'Should select report burndown', ->
        # Select Burn down report from report selection
        board.selectReport('Burn Down').then ->
            browser.waitForAngular()
            iteration = element(By.xpath('(//select[@ng-model="ctrl.reportOptions.iteration"])[2]'))
            
            board.selectDropdownbyNum(iteration, 1).then ->
                board.refreshReport().then ->
                    browser.waitForAngular()
                    return
        return

    it 'Should create favorite report', ->

        element(By.css('button[ng-click="ctrl.saveReportSettings()"]')).click().then ->
            element(By.css('#reportName')).sendKeys('burnDown').then -> 
                element(By.buttonText('Save')).click().then ->
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//a[contains(text(),"burnDown")]')).isPresent()).toBe true
        return

    it 'Should open favorite report of burn down', ->
        browser.get param.projectUrl

        element(By.css('button[ng-click="ctrl.loadSavedReports()"]')).click().then ->
            element(By.xpath('//a[contains(text(),"burnDown")]')).click().then -> browser.sleep(3000).then ->
                element(By.buttonText('Close')).click().then ->
                return
            return
        browser.waitForAngular()
        return

    it 'Should delete favorite report', ->
        board.gotoReports()

        element(By.css('i[ng-click="ctrl.deleteSavedReport(report.id)"]')).click().then ->
            element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                return elem.isDisplayed()
            .click()
            return
        browser.waitForAngular()
        expect(element(By.xpath('//a[contains(text(),"burnDown")]')).isPresent()).toBe false
        return
								
    it 'Should create commulative favorite report', ->
        board.gotoReports()
								
        element(By.css('button[ng-click="ctrl.saveReportSettings()"]')).click().then ->
            element(By.css('#reportName')).sendKeys('commulative').then -> 
                element(By.buttonText('Save')).click().then ->
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//a[contains(text(),"commulative")]')).isPresent()).toBe true
        return
								
    it 'Should open favorite report of commulative', ->
        browser.get param.projectUrl

        element(By.css('button[ng-click="ctrl.loadSavedReports()"]')).click().then ->
            element(By.xpath('//a[contains(text(),"commulative")]')).click().then -> browser.sleep(3000).then ->
                element(By.buttonText('Close')).click().then ->
                return
            return
        browser.waitForAngular()
        return

    it 'Should delete favorite report', ->
        board.gotoReports()

        element(By.css('i[ng-click="ctrl.deleteSavedReport(report.id)"]')).click().then ->
            element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                return elem.isDisplayed()
            .click()
            return
        browser.waitForAngular()
        expect(element(By.xpath('//a[contains(text(),"commulative")]')).isPresent()).toBe false
        return