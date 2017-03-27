util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")

describe 'Scrumdo Add Project' , ->
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'Should create a new Project', ->
        browser.get param.dashboardUrl

        element.all(By.css('a[href="#/projects"]')).click()
        element(By.css('#boardTable .scrumdo-wrapper-navigation .col-md-12 .scrumdo-btn')).click()
        element(By.css('#id_name')).sendKeys projectName
        element.all(By.buttonText('Create New Workspace')).filter (elem) ->
            return elem.isDisplayed()
        .click()
        browser.waitForAngular()
        expect(browser.getTitle()).toEqual('ScrumDo - ' + projectName);
        return

    it 'Should setup the new Project', ->
        browser.get param.dashboardUrl

        #check if the project was added successfully
        expect(element.all(By.xpath('.//*[normalize-space(text())=normalize-space("' + projectName + '")]')).get(0).isPresent()).toBe true

        #now setup the project with Wizard
        browser.get param.projectUrl

        element.all(By.buttonText('Customize Board')).filter (elem) ->
            return elem.isDisplayed()
        .click()
        
        element.all(By.buttonText('Next')).filter (elem) ->
            return elem.isDisplayed()
        .click()
            
        board.selectDropdownbyNum(element.all(By.css('.step-container select[ng-model="step.style"]')).get(1), 0)
        
        element.all(By.buttonText('Next')).filter (elem) ->
            return elem.isDisplayed()
        .click()
        element.all(By.buttonText('Done')).filter (elem) ->
            return elem.isDisplayed()
        .click();

        browser.waitForAngular()
        return
