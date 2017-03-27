util = require("../util")

describe 'Scrumdo Stress Test Add Card' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName

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

    it "Should navigate to project page", ->
        browser.get(param.projectUrl)
    #
    # afterEach () ->
    #     browser.manage().logs().getAvailableLogTypes().then (types) ->
    #         console.log(types)
    #     browser.manage().logs().get('browser').then (browserLog) ->
    #         for message in browserLog
    #             console.log(message.message)

    for count in [0..5]
        it "Should create a card and delete it. ##{count}", ->
            element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
                element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                    element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                        element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                            return elem.isDisplayed()
                        .click()
                        return
                    return
                return

            expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
            element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
                element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.deleteCard()"]')).get(0).click().then ->
                    element.all(By.buttonText('Yes')).filter (elem) ->
                        return elem.isDisplayed()
                    .click()
                    return
                return
            expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe false
            return
