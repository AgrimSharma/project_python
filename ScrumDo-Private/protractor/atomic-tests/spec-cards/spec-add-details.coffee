util = require("../util")

describe 'Scrumdo add details' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    
    
   
    cardName = param.cardName
	
	
    it 'Should add a card to cell', ->
	       browser.get param.projectUrl
		
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('.scrumdo-mce-editor')).get(1).sendKeys('Enter details here').then ->
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

    it 'Should have details and update', ->
         element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).first().click().then -> 
           element.all(By.css('.scrumdo-mce-editor')).get(1).click().then -> 
             element.all(By.css('.scrumdo-mce-editor')).get(1).clear().then -> 
               element.all(By.css('.scrumdo-mce-editor')).get(1).sendKeys('deatails updated').then ->
                    element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                      return elem.isDisplayed()
                    .click()