util = require("../util")

describe 'Scrumdo project name', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    it 'Should project name', ->
        browser.get param.projectUrl
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
    
        browser.waitForAngular()
        expect(element(By.css('input[ng-model="ctrl.project.name"]')).isPresent()).toBe true
        return

    it 'Should clear name', ->
        #browser.get param.orgSettingUrl

        element(By.css('input[ng-model="ctrl.project.name"]')).clear()
        browser.waitForAngular()
        return

    it 'Should save workspace with empty field', ->
       	
        element(By.css('button[ng-click="ctrl.save()"]')).click().then ->
        browser.waitForAngular
        expect(element(By.css('button[ng-click="ctrl.save()"]')).isPresent()).toBe true 
        return		