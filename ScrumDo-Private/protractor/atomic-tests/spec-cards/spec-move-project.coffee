util = require("../util")

describe 'Scrumdo Move Project' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);


    cardName = param.cardName + " MOVE TEST"

    it 'Should add a card to cell (to test move project)', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(1).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(1).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('#ticketMessage')).get(0).sendKeys(param.storyComment).then ->
                        element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                            return elem.isDisplayed()
                        .click()
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return


    it 'Should move card to another Iteration', ->
        card = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]'))
        browser.actions().mouseMove(card).keyDown(protractor.Key.SHIFT).click().perform()
        browser.actions().keyUp(protractor.Key.SHIFT).perform()
        element.all(By.css('button[uib-tooltip="Move selected cards to another project or iteration"]')).get(0).click()

        element(By.cssContainingText('option', param.iterationName)).click();

        element(By.css('button[ng-click="ctrl.ok(selectedProject)"]')).click();

        browser.waitForAngular()

        #check if card was moved out successfully
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe(false);


        expect(element.all(By.repeater("iteration in filteredIterations")).all(By.cssContainingText('label', param.iterationName)).get(0).isPresent()).toBe(true)

        #now switch to that iteration
        element.all(By.repeater("iteration in filteredIterations")).all(By.cssContainingText('label', param.iterationName)).get(0).click()

        #Make sure it's in the right column.
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe(true)


        return


    it 'Should move card to another Project', ->
        card = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]'))
        browser.actions().mouseMove(card).keyDown(protractor.Key.SHIFT).click().perform()
        browser.actions().keyUp(protractor.Key.SHIFT).perform()
        element.all(By.css('button[uib-tooltip="Move selected cards to another project or iteration"]')).get(0).click()
        
        element(By.css('#safe-project-select .dropdown-toggle')).click().then ->
            element.all(By.css('#safe-project-select .dropdown-menu ul ul li a')).get(0).click()

        element.all(By.css('select[ng-options="iteration.id as iteration.name for iteration in iterations"]')).get(0).all(By.tagName('option')).then (options) ->
            options[2].click()
            return
        element.all(By.css('button[ng-click="ctrl.ok(selectedProject)"]')).filter (elem) ->
            return elem.isDisplayed()
        .click()
        browser.waitForAngular()
        #check if card was moved successfully
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe false
        return
    return
