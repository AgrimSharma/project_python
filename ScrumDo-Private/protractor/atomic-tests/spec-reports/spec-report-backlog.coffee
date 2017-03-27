util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")

describe 'Scrumdo Favorite report' , ->
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    storyEditWindow = new StoryEditWindow(param.hostName)
    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
		
    it 'Should navigate to reports page', ->    
        board.gotoReports()
        return
		
    it 'Should select backlog check', ->
        element(By.css('input[ng-model="ctrl.reportOptions.cfd_show_backlog"]')).click().then ->
            element(By.css('button[ng-click="ctrl.refresh()"]')).click().then ->
            return
        browser.waitForAngular()
        backlogCkeckbox = element.all(By.css('input[ng-model="ctrl.reportOptions.cfd_show_backlog"]')).get(0)
        expect(backlogCkeckbox.isSelected()).toBe(true);
        return
								
    it 'Should deselect backlog checkbox ', ->
        backlogText = element.all(By.css('text.avg-values')).get(0).getText()
        element(By.css('input[ng-model="ctrl.reportOptions.cfd_show_backlog"]')).click().then -> browser.sleep(4000).then ->
            element(By.css('button[ng-click="ctrl.refresh()"]')).click().then ->
            return
        browser.waitForAngular()
        newText = element.all(By.css('text.avg-values')).get(0).getText()
        expect(backlogText).not.toEqual(newText)
        return