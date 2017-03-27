util = require("../util")

describe 'Scrumdo card setting', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    it 'Should project name', ->
        browser.get param.projectUrl
    
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        browser.waitForAngular()
        expect(element(By.css('input[ng-model="ctrl.project.name"]')).isPresent()).toBe true
        return

    it 'Should optional field', ->
        element(By.xpath('//a[contains(text(),"Card Settings")]')).click().then ->
            element(By.css('input[ng-model="ctrl.project.use_time_crit"]')).click().then ->
                element(By.css('button[ng-click="ctrl.save()"]')).click().then ->
                return
            return
        browser.waitForAngular()
        expect(element(By.css('button[ng-click="ctrl.save()"]')).isPresent()).toBe true
        return

    it 'Should select business mode', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Card Settings")]')).click().then ->
                element.all(By.css('input[type="radio"]')).get(0).click().then -> browser.sleep(2000).then ->
                    element(By.css('button[ng-click="ctrl.save()"]')).click().then ->
                    return
                return
            return
        businessMode = element.all(By.css('input[type="radio"]')).get(0)
        browser.waitForAngular()
        expect(businessMode.isSelected()).toBe(true);
        return

    it 'Should verify business mode on card', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
            return
        browser.waitForAngular()
        expect(element(By.xpath('//span[contains(text(),"$")]')).isPresent()).toBe false
        return

    it 'should custom field on card setting', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Card Settings")]')).click().then ->
                element.all(By.css('input[type="radio"]')).get(1).click().then -> browser.sleep(2000).then ->
                    element(By.name('extra_1')).clear().sendKeys('Operating system').then ->
                        element(By.name('extra_2')).clear().sendKeys('Version').then ->
                            element(By.css('button[ng-click="ctrl.save()"]')).click().then ->
                            return
                        return
                    return
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
    it 'Should add card with custom details', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                   element.all(By.css('.scrumdo-mce-editor')).get(2).clear().sendKeys('window 7').then -> 
                    element.all(By.css('.scrumdo-mce-editor')).get(3).clear().sendKeys('64 bit').then ->
                        element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                            return elem.isDisplayed()
                        .click()
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return