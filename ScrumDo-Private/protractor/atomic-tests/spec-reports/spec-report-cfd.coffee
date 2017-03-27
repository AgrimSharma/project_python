util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")


describe 'Scrumdo Report' , ->
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    
    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'Should navigate to reports page', ->    
        # Goto project reports url
        board.gotoReports()
        browser.waitForAngular()
        return

    it 'Should hover the selected circle points on the chart', ->

        iterationSelect = element(By.css('select[ng-change="ctrl.iterationChanged()"]'))
        board.selectDropdownbyNum(iterationSelect, 1)
        
        element.all(By.css('button[ng-click="ctrl.refresh()"]')).get(0).click().then ->
            browser.waitForAngular()

        circle_point = element.all(By.css('.point-circles circle[visibility="inherit"]')).get(0)
        expect(circle_point.isDisplayed()).toBe(true);

        board.hoverElement(circle_point).then ->
            browser.sleep(1000)
            expect(element(By.css('.tip')).isDisplayed()).toBe(true);
        return

    it 'Should view the detail of the card number', ->
        element.all(By.css('.link-card')).get(0).click().then ->
            browser.waitForAngular()
            expect(element(By.css('.card-modal')).isDisplayed()).toBe(true);
        return