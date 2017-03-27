util = require("../util")

describe 'Scrumdo Delete Card' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'Should delete a card from cell', ->
        cardName = param.cardName
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
            element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.deleteCard()"]')).get(0).click().then ->
                element.all(By.buttonText('Yes')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
        #check if card was deleted successfully
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe false
        return
    return
