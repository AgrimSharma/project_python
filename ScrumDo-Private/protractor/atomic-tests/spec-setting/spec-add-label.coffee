util = require("../util")

describe 'Scrumdo Label&Tag', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    it 'Should create label', ->
        browser.get param.projectUrl
        
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Tags & Labels")]')).click().then -> browser.sleep(3000).then ->
                element(By.css('a[ng-click="ctrl.addLabel($event)"]')).click().then ->
                    element(By.css('input[ng-model="label.name"]')).clear().sendKeys('Epic').then ->
                        element(By.css('.sp-replacer.sp-light')).click().then ->
                            element.all(By.css('.sp-thumb-inner')).get(9).click().then ->
                                element(By.xpath('//button[contains(text(),"Save")]')).click().then ->
                                return
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.css('button[ng-click="ctrl.deleteLabel(label)"]')).isPresent()).toBe true
        return

    it 'Should edit label', ->

        element.all(By.xpath('//button[@ng-click="ctrl.editLabel(label)"]')).last().click().then ->
            element(By.css('input[ng-model="label.name"]')).clear().sendKeys('Improvement').then ->
                element(By.css('.sp-replacer.sp-light')).click().then ->
                    element.all(By.css('.sp-thumb-inner')).get(12).click().then ->
                        element(By.xpath('//button[contains(text(),"Save")]')).click().then ->
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.css('button[ng-click="ctrl.deleteLabel(label)"]')).isPresent()).toBe true
        return

    it 'Should delete label', ->
        element.all(By.css('button[ng-click="ctrl.deleteLabel(label)"]')).last().click().then ->
            element.all(By.buttonText('Yes')).filter (elem) ->
                return elem.isDisplayed()
            .click()
            return
        browser.waitForAngular()
        expect(element(By.xpath('//span[contains(text(),"Improvement")]')).isPresent()).toBe false
        return
		
    it 'Should scrape a label', ->

        browser.get param.projectUrl
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Tags & Labels")]')).click().then -> browser.sleep(3000).then ->
                element.all(By.css('button[ng-click="ctrl.deleteLabel(label)"]')).first().click().then ->
                    element.all(By.buttonText('Yes')).filter (elem) ->
                        return elem.isDisplayed()
                    .click()
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//span[contains(text(),"Bug")]')).isPresent()).toBe false
        return
	
    it 'Should verify in backlog slider', ->

        browser.get param.projectUrl
		
        element(By.xpath('//a[contains(text(),"Backlog")]')).click().then ->
            element(By.css('select[ng-model="ctrl.viewType"]')).all(By.tagName('option')).get(2).click().then -> browser.sleep(1000).then ->
            return
        browser.waitForAngular()
        expect(element(By.xpath('//span[contains(text(),"Bug")]')).isPresent()).toBe false
        return

    it 'Should open new card to verify delete label', ->
        browser.get param.projectUrl
		
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element.all(By.css('.scrumdo-btn.dropdown-main-button.primary.extended.scrumdo-select-button')).get(0).click().then ->
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.labels')).get(0).element(By.xpath('//span[contains(text(),"Bug")]')).isPresent()).toBe false
        return

    it 'Should create label on setting page', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Tags & Labels")]')).click().then -> browser.sleep(3000).then ->
                element(By.css('a[ng-click="ctrl.addLabel($event)"]')).click().then ->
                    element(By.css('input[ng-model="label.name"]')).clear().sendKeys('Bug').then ->
                        element(By.css('.sp-replacer.sp-light')).click().then ->
                            element.all(By.css('.sp-thumb-inner')).get(5).click().then ->
                                element(By.xpath('//button[contains(text(),"Save")]')).click().then ->
                                return
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//span[contains(text(),"Bug")]')).isPresent()).toBe true
        return
