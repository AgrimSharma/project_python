util = require('../util')
path = require('path')

describe 'Scrumdo attachment form local', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);  
  
  
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
	
    it 'Should attached a file', ->
    
        absolutePath = path.resolve('../file/scrumDo.png')
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then -> 
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then -> 
                 element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then -> 
                    element(By.css('input[value="Attach File"]')).click().then -> element(By.xpath('//input[@type="file"]')).sendKeys(absolutePath).then -> browser.sleep(5000).then -> element(By.buttonText('OK')).click().then -> browser.sleep(4000).then -> element(By.xpath('(//button[@type="button"])[3]')).click().then -> browser.sleep(3000).then ->
                    return
                return
            return
       
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return	
		
    it 'Should open card and delete image', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
            element(By.css('a[ng-click="ctrl.deleteAttachment(attachment)"]')).click().then -> 
                element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
        expect(element(By.css('a[ng-click="ctrl.deleteAttachment(attachment)"]')).isPresent()).toBe false
        return	