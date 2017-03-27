util = require("../util")

describe 'Scrumdo click permalink' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);


    cardName = param.cardName

    it 'Should add a card to cell', ->
        browser.get param.projectUrl

		
		
		
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


    it 'Should open card', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click()
        return


    it 'Should click permalink', ->
        element.all(By.css('.card-modal-footer>a')).get(0).click()
        browser.waitForAngular()
        expect(element(By.css('.modal-dialog .modal-content button[ng-click="ctrl.deleteCard()"]')).isPresent()).toBe true
        browser.getAllWindowHandles().then (handles) ->
            browser.driver.switchTo().window(handles[1])
            browser.driver.close();
            browser.driver.switchTo().window(handles[0])

        return
