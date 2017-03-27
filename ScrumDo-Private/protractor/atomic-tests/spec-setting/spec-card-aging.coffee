util = require("../util")

describe 'Scrumdo aging', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    it 'Should project name', ->
        browser.get param.projectUrl
    
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        browser.waitForAngular()
        expect(element(By.css('input[ng-model="ctrl.project.name"]')).isPresent()).toBe true
        return
		
    it 'should create aging (in days)', ->
		
        element(By.css('input[ng-model="ctrl.project.warning_threshold"]')).clear().sendKeys('4').then ->
            element(By.css('input[ng-model="ctrl.project.critical_threshold"]')).clear().sendKeys('5').then ->
                element(By.css('button[ng-click="ctrl.save()"]')).click().then ->
                return
            return
        browser.waitForAngular()
        expect(element(By.css('button[ng-click="ctrl.save()"]')).isPresent()).toBe true 
        return

    it 'Should verify days', ->
        browser.waitForAngular()
        expect(element(By.css('input[ng-model="ctrl.project.warning_threshold"]')).isPresent()).toBe true
        return

    it 'Should verify aging checkbox', ->
        browser.get param.projectUrl

        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        aging = element(By.id('showagingdisplay'))
        expect(aging.isSelected()).toBe(true);