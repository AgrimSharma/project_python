util = require("../util")

describe 'Scrumdo render mode', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    it 'Should project name', ->
        browser.get param.projectUrl
    
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->	
        browser.waitForAngular()
        expect(element(By.css('input[ng-model="ctrl.project.name"]')).isPresent()).toBe true
        return
		
    it 'should select render mode', ->
        browser.get param.projectUrl
 
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element.all(By.css('input[ng-model="ctrl.project.render_mode"]')).get(1).click().then -> browser.sleep(2000).then ->
                element(By.css('button[ng-click="ctrl.save()"]')).click().then ->
                return
            return
        browser.waitForAngular()
        expect(element(By.css('button[ng-click="ctrl.save()"]')).isPresent()).toBe true 
        return
		
    #First Archive all cell cards
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
    it "Should add card to cell", ->
        
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                        return elem.isDisplayed()
                    .click()
                    return  
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return
		
    cardName = param.cardName
    it "Should add card to cell", ->
        
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                        return elem.isDisplayed()
                    .click()
                    return  
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return
		
    cardName = param.cardName
    it "Should add card to cell", ->
        
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                        return elem.isDisplayed()
                    .click()
                    return  
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return
		
    cardName = param.cardName
    it "Should add card to cell", ->
        
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                        return elem.isDisplayed()
                    .click()
                    return  
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return

    it 'Should verify render is selected', ->
        browser.get param.projectUrl

        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        rendor = element.all(By.css('input[ng-model="ctrl.project.render_mode"]')).get(1)
        browser.waitForAngular()
        expect(rendor.isSelected()).toBe(true);
        return