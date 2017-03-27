util = require("../util")

describe "Scrumdo card lebal", ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
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
    
    it "Should add card to cell with a labels", ->
        browser.get param.projectUrl
        
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('.scrumdo-btn.dropdown-main-button.primary.extended.scrumdo-select-button')).get(0).click().then -> element.all(By.css('.labels')).get(0).click().then ->
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
    
    it "Should have label on card", ->
        browser.get param.projectUrl
        expect(element(By.css('.kanban-cell .scrumdo-boards-column .cards-tag>li')).isPresent()).toBe true
    
    return
	
    cardName = param.cardName
    it "Should add card to cell with a feature labels", ->
        browser.get param.projectUrl
        
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('.scrumdo-btn.dropdown-main-button.primary.extended.scrumdo-select-button')).get(0).click().then -> element.all(By.css('.labels')).get(1).click().then ->
                        #element.all(By.css('#ticketMessage')).get(0).sendKeys(param.storyComment).then ->
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
    
    it "Should have label on card", ->
        browser.get param.projectUrl
        expect(element(By.css('.kanban-cell .scrumdo-boards-column .cards-tag>li')).isPresent()).toBe true
    
    return
	
	