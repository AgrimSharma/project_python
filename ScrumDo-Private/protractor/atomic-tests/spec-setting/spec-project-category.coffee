util = require("../util")

describe 'Scrumdo category', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    it 'Should verify project name on setting page', ->
        browser.get param.projectUrl

        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
		
        browser.waitForAngular()
        expect(element(By.css('input[ng-model="ctrl.project.name"]')).isPresent()).toBe true
        return
		
    categoryName=param.categoryName
    it 'Should enter project category', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.css('input[ng-model="ctrl.project.category"]')).clear().sendKeys(categoryName).then ->
                element(By.css('button[ng-click="ctrl.save()"]')).click()
                return
            return
        browser.waitForAngular()
        expect(element(By.css('input[ng-model="ctrl.project.category"]')).isPresent()).toBe true
        return
		
    it 'Should verify new category', ->
        browser.get param.dashboardUrl
		
        browser.waitForAngular()
        expect(element(By.css(".project-category>span")).isPresent()).toBe true
        return
		