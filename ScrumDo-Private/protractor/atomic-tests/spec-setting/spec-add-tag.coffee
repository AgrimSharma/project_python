util = require("../util")

describe 'Scrumdo workspace tags', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    it 'Should verify project name on setting page', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Tags & Labels")]')).click().then -> browser.sleep(3000).then ->
            return
		
        browser.waitForAngular()
        expect(element(By.xpath('//h2[contains(text(),"Card Labels")]')).isPresent()).toBe true
        return
		
    tagName=param.categoryName
    it 'Should create a new tag', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Tags & Labels")]')).click().then -> browser.sleep(3000).then ->
                element(By.xpath('//a[@ng-click="ctrl.addTag($event)"]')).click().then ->
                    element(By.xpath('//input[@ng-model="tag.name"]')).sendKeys(tagName).then ->
                        element(By.xpath('//button[@ng-click="ctrl.saveTag(tag)"]')).click()
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//span[contains(text(),"' +tagName+ '")]')).isPresent()).toBe true
        return

    tagNameEdit=param.tagName		
    it 'should edit existing Tag', ->
        browser.get param.projectUrl

        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Tags & Labels")]')).click().then -> browser.sleep(3000).then ->
                element(By.xpath('//button[@ng-click="ctrl.editTag(tag)"]')).click().then ->
                    element(By.xpath('//input[@ng-model="tag.name"]')).clear().sendKeys(tagNameEdit).then ->
                        element(By.xpath('//button[@ng-click="ctrl.saveTag(tag)"]')).click()
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//span[contains(text(),"' +tagNameEdit+ '")]')).isPresent()).toBe true
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
    it 'should create a card with tag', ->
        browser.get param.projectUrl
		
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('.modal-body input.tags-input')).get(0).sendKeys(tagNameEdit).then ->
                        element.all(By.css('button[ng-click="ctrl.save($event)"]')).click().then ->
                        return
                    return
                return
            return
        browser.waitForAngular()
        browser.sleep(3000).then ->
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return
		
    it 'should search a card with same tag', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Tags & Labels")]')).click().then -> browser.sleep(3000).then ->
                element(By.xpath('//button[@ng-click="ctrl.searchByTag(tag)"]')).click().then -> browser.getAllWindowHandles().then (handles) -> browser.switchTo().window(handles[1]).then ->
        browser.waitForAngular()
        expect(element(By.css('.cards-text>p')).isPresent()).toBe true
								browser.getAllWindowHandles().then (handles) -> browser.switchTo().window(handles[0])
        return
				
    it 'should delete a tag', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Tags & Labels")]')).click().then -> browser.sleep(3000).then ->
                element(By.xpath('//button[@ng-click="ctrl.deleteTag(tag)"]')).click().then ->
                    element.all(By.buttonText('Yes')).filter (elem) ->
                        return elem.isDisplayed()
                    .click()
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//span[contains(text(),"' +tagNameEdit+ '")]')).isPresent()).toBe false
        return