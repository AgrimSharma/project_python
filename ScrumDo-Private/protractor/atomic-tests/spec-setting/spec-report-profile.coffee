util = require("../util")

describe 'Scrumdo Report profile', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
		
    cardName = param.cardName
    it 'Should create new profile', ->
        browser.get param.projectUrl
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        element(By.xpath('//a[contains(text(),"Report Profiles")]')).click().then ->
            element(By.css('a[ng-click="ctrl.closeWorkflowHelp()"]')).click().then ->
                element(By.css('a[ng-click="ctrl.newWorkflow()"]')).click().then ->
                    element(By.css('input[ng-model="promptText"]')).clear().sendKeys(cardName).then ->
                        element.all(By.buttonText('Ok')).filter (elem) ->
                            return elem.isDisplayed()
                        .click()
                        return
                    return
                return
            return
        browser.waitForAngular()
		      expect(element(By.css('a[ng-click="ctrl.newWorkflow()"]')).isPresent()).toBe true
        return
		
    cardName = param.cardName
    it 'Should change name', ->
	       element(By.css('button[ng-click="ctrl.changeWorkflowName()"]')).click().then ->
            element(By.css('input[ng-model="promptText"]')).clear().sendKeys(cardName).then ->
                element.all(By.buttonText('Ok')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
		      expect(element(By.css('a[ng-click="ctrl.newWorkflow()"]')).isPresent()).toBe true
        return
		
    it 'Should verify Add step functinality', ->
        
        element(By.css('a[ng-click="ctrl.addWorkflowStep()"]')).click().then ->
            element(By.css('.sp-replacer.sp-light')).click().then ->
                element.all(By.css('.sp-thumb-inner')).get(15).click().then ->
                    element(By.css('input[ng-model="step.name"]')).click().then ->
                        element(By.css('input[ng-model="step.name"]')).clear().sendKeys('Step1').then ->
                            element(By.css('button[ng-click="ctrl.pickCellsForStep(step)"]')).click().then ->
                                element.all(By.css('#kanbanboardeditor svg g g')).get(0).click().then ->
                                    element(By.css('a[ng-click="ctrl.doneSelecting()"]')).click().then ->
                                    return
                                return
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('#kanbanboardeditor svg g')).get(0).isPresent()).toBe true
        return
		
    it 'Should Delete step functinality', ->
        browser.sleep(3000)
        element(By.css('.glyphicon.glyphicon-remove')).click().then ->
            element(By.css('button[ng-click="ctrl.ok()"]')).click().then ->
            return
        browser.waitForAngular()
        expect(element(By.css('.glyphicon.glyphicon-remove')).isPresent()).toBe false
        return
		
    it 'Should delete profile', ->
        browser.sleep(3000)
        element(By.xpath('//a[contains(text(),"Delete Profile")]')).click().then ->
            element(By.css('button[ng-click="ctrl.ok()"]')).click().then ->
            return
        browser.waitForAngular()
        expect(element.all(By.css('.scrumdo-btn.extended.primary')).get(1).isPresent()).toBe true
        return
        