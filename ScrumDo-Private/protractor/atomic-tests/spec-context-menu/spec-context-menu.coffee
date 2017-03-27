util = require("../util")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
describe 'Scrumdo Context Menu' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    story = new StoryEditWindow(param.hostName)

    it 'Should add a card to cell', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    story.switchToTab(2).then ->
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
    it 'Should open the edit card window', ->
        browser.get param.projectUrl
        elementToRightClick = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards')).get(0)
        browser.driver.actions().click(elementToRightClick,protractor.Button.RIGHT).perform().then ->
            element.all(By.css('.custom-context-menu a')).get(0).click().then ->
                story.switchToTab(2).then ->
                    element.all(By.css('#ticketMessage')).get(0).sendKeys(param.storyComment).then ->
                        element.all(By.css('button[ng-click="ctrl.addComment()"]')).filter (elem) ->
                             return elem.isDisplayed()
                        .click()
                        element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                            return elem.isDisplayed()
                        .click()
                        browser.waitForAngular()
                        return
                    return
                return
            return
        return

    it 'Should Assign Card', ->
        browser.get param.projectUrl
        elementToRightClick = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards')).get(0)
        browser.driver.actions().click(elementToRightClick,protractor.Button.RIGHT).perform().then ->
            element.all(By.css('.custom-context-menu a')).get(1).click().then ->
                element.all(By.css('input[ng-click="$select.activate()"]')).get(0).click().then ->
                    element.all(By.css('.ui-select-choices-content .ui-select-choices-row a')).get(0).click().then ->
                        element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                            return elem.isDisplayed()
                        .click()
                        browser.waitForAngular()
                        return
                    return
                return
            return
        return

    it 'Should Add tasks to card', ->
        browser.get param.projectUrl
        elementToRightClick = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards')).get(0)
        browser.driver.actions().click(elementToRightClick,protractor.Button.RIGHT).perform().then ->
            element.all(By.css('.custom-context-menu a')).get(3).click().then ->
                element.all(By.css('button[ng-click="ctrl.newTask()"]')).get(0).click()
                element.all(By.css('input[ng-model="task.summary"]')).get(0).sendKeys(param.taskSummery)
                element.all(By.css('select#assignee')).get(0).all(By.tagName('option')).then (options) ->
                    options[1].click()
                    return
                element.all(By.css('button[ng-click="ctrl.save($event)"]')).get(0).click()
                browser.waitForAngular()
                element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.save($event)"]')).get(0).click()
                browser.waitForAngular()
            return
        return

    it 'Should add time to Card', ->
        browser.get param.projectUrl
        elementToRightClick = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards')).get(0)
        browser.driver.actions().click(elementToRightClick,protractor.Button.RIGHT).perform().then ->
            element.all(By.css('.custom-context-menu a')).get(5).click().then ->
                element(By.css('.modal-dialog .modal-content input[ng-model="ctrl.currentValue"]')).sendKeys(param.storyTime).then ->
                    element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.enterTime()"]')).get(0).click()
                browser.waitForAngular()
            return
        return

    it 'Should duplicate the Card', ->
        browser.get param.projectUrl
        elementToRightClick = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards')).get(0)
        browser.driver.actions().click(elementToRightClick,protractor.Button.RIGHT).perform().then ->
            element.all(By.css('.custom-context-menu a')).get(6).click().then ->
                element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.ok()"]')).get(0).click()
            browser.waitForAngular()
            return
        return

    it 'Should delete the Card', ->
        browser.get param.projectUrl
        elementToRightClick = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards')).get(0)
        browser.driver.actions().click(elementToRightClick,protractor.Button.RIGHT).perform().then ->
            element.all(By.css('.custom-context-menu a')).get(10).click().then ->
                element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.ok()"]')).get(0).click()
            browser.waitForAngular()
            return
        return

    it 'Should move card to another cell', ->
        browser.get param.projectUrl
        elementToRightClick = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards')).get(0)
        browser.driver.actions().click(elementToRightClick,protractor.Button.RIGHT).perform().then ->
            element.all(By.css('.custom-context-menu a')).get(7).click().then ->
                element.all(By.css('.modal-content .dropdown-toggle')).get(0).click().then ->
                element.all(By.css('.cell-picker svg g g')).get(1).click()
                element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
    return
