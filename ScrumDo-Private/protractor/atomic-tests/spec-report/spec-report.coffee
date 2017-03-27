util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")
ProjectApp = require("../../pageobjects/project-app.coffee")

describe 'Scrumdo Report' , ->
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    project = new ProjectApp(param.hostName, param.projectSlug, param.orgSlug)

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'Should navigate to reports page', ->    
        # Goto project reports url
        project.gotoReports()
        return

    it 'Should select report lead', ->
        # Select lead report from report selection
        board.selectReport('Lead Time').then ->
            browser.waitForAngular()
            endStep = element(By.css('select[ng-model="ctrl.reportOptions.lead_end_step"]'))
            
            board.selectDropdownbyNum(endStep, 2).then ->
                board.refreshReport().then ->
                    browser.waitForAngular()
                    return
        return

    it 'Should hover the selected bar chart', ->
        bar = element.all(By.css('.lead-bar')).get(0)
        expect(bar.isDisplayed()).toBe(true);
        
        board.hoverElement(bar).then ->
            expect(element(By.css('.tip')).isDisplayed()).toBe(true);
        return