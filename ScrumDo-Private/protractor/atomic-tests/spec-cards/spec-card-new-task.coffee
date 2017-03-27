util = require("../util")

describe 'Scrumdo new task Card' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec)

    
	
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
    
    it 'Should add a card to cell', ->
		
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                   element.all(By.css('.nav-link')).get(1).click().then -> 
                       element.all(By.css('#ticketMessage')).get(0).sendKeys(param.storyComment).then ->
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
    
    it 'Should click tasks tab', ->
	       element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
            element.all(By.css('.nav-link')).get(4).click().then ->
								    return
						  browser.waitForAngular()
        expect(element(By.css('button[ng-click="ctrl.newTask()"]')).isPresent()).toBe true
								return
           
    it 'Should create new task', ->
	
	       element(By.css('button[ng-click="ctrl.newTask()"]')).click().then ->
		          element(By.css('#summary')).sendKeys('New task').then ->
                element(By.xpath('//*[@id="assignee"]')).click().then ->
                    element(By.xpath('//*[@id="assignee"]/option[2]')).click().then ->	
					                   element.all(By.css('input[sd-enter="ctrl.addTag()"]')).get(0).sendKeys('#scrumDo').then ->
                            element(By.xpath('//span[@ng-click="ctrl.addTag()"]')).click().then ->	
                                element(By.xpath('//input[@ng-model="ctrl.currentValue"]')).sendKeys('00:50').then -> 
                                    element.all(By.css('button[ng-click="ctrl.save($event)"]')).click().then ->
                                        element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                                            return elem.isDisplayed()
                                        .click()
                                        return   
                                    return	
                                return
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        #expect(element.all(By.css('.cards-badges-wrapper>span')).get(0).isPresent()).toBe true	
								expect(element.all(By.css('.kanban-cell .scrumdo-boards-column .labels')).get(0).isPresent()).toBe true
        return