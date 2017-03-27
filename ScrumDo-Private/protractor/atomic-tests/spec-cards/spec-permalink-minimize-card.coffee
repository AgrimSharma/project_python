util = require("../util")

describe 'Scrumdo Minimize (permalink)' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec)
		
    cardName = param.cardName
		
    it 'Should add a card to cell', ->
        browser.get param.projectUrl
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
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return
  
    it 'Should card minimize (permalink)', ->
        browser.get param.projectUrl
		
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
                element.all(By.css('button[ng-click="ctrl.minimize()"]')).click().then -> 
                    element(By.css('.card-modal-footer>a')).click().then -> browser.getAllWindowHandles().then (handles) -> browser.switchTo().window(handles[1]).then ->    