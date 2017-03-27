util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")

describe 'Scrumdo Report' , ->
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    
    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'Should navigate to reports page', ->    
        board.gotoReports()
        return

    it 'Should select assignees from dropdown selection', ->

        selectAssigneeMenu = element(By.css('div[ng-click="ctrl.toggleMenu($event)"]'))
        ngAssignee = element(By.css('.scrumdo-select-button'))

        selectAssigneeMenu.click().then ->
            option = element(By.css('div[uib-dropdown-menu]')).all(By.css('ul li a'))
            expect(selectAssigneeMenu.isDisplayed()).toBe(true)
            expect(option.count()).toBeGreaterThan(0)

            option.get(0).click().then ->
                expect(ngAssignee.getText()).not.toBe('Anyone')                
                board.refreshReport().then ->
                    browser.waitForAngular()
                    return
        return