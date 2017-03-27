util = require("../util")

describe 'Scrumdo velocity calculation', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    it 'Should verify project name on setting page', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
		
        browser.waitForAngular()
        expect(element(By.css('input[ng-model="ctrl.project.name"]')).isPresent()).toBe true
        return	

    it 'Should verify velocity calculation', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element.all(By.css('input[ng-model="ctrl.project.velocity_type"]')).get(0).click().then ->
                element(By.css('button[ng-click="ctrl.save()"]')).click()
                return
            return
        browser.waitForAngular()
        velocity = element.all(By.css('input[ng-model="ctrl.project.velocity_type"]')).get(0)
        expect(velocity.isSelected()).toBe(true);
        return

	