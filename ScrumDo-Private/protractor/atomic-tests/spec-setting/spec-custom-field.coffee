util = require("../util")

describe 'Scrumdo custom field', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    it 'Should project name', ->
        browser.get param.projectUrl
    
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        browser.waitForAngular()
        expect(element(By.css('input[ng-model="ctrl.project.name"]')).isPresent()).toBe true
        return
		
    it 'should create custom field', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.name('extra_1')).clear().sendKeys('Step to reproduce').then ->
                element(By.name('extra_2')).clear().sendKeys('Environment').then ->
                    element(By.css('button[ng-click="ctrl.save()"]')).click().then ->
                    return
                return
        browser.waitForAngular()
        expect(element(By.css('button[ng-click="ctrl.save()"]')).isPresent()).toBe true 
        return

    it 'Should Archive all cards in a cell', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(4).click().then ->
                element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.css('.kanban-story-list li')).isPresent()).toBe false
        return

    cardName = param.cardName
    it 'Should add card with custum details', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('.scrumdo-mce-editor')).get(2).clear().sendKeys('Click on button').then -> 
                        element.all(By.css('.scrumdo-mce-editor')).get(3).clear().sendKeys('window 7').then ->
                            element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                                return elem.isDisplayed()
                            .click()
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return
