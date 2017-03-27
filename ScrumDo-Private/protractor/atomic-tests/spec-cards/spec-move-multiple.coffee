util = require("../util")

describe 'Scrumdo Move Multiple' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    it 'Should add a card to cell (to test move multiple)', ->
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

    it 'Should move Multiple cards to cell', ->

        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        card = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards .cards-number')).last()
        expect(card.isPresent()).toBe true

        browser.actions()
            .mouseMove(card)
            .keyDown(protractor.Key.SHIFT)
            .click()
            .perform();

        browser.actions().keyUp(protractor.Key.SHIFT).perform()

        browser.sleep(100)
        element.all(By.css('button[uib-tooltip="Move selected cards to cell"]')).get(0).click()
        element.all(By.css('.modal-content .move-cell-body button')).get(0).click().then ->
            element.all(By.css('.modal-content svg g g')).get(2).click()
            return
        element.all(By.css('button[ng-click="ctrl.ok()"]')).get(0).click()
        browser.waitForAngular()
        browser.sleep(100)
        #check if card was moved successfully
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(2).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return
    return
