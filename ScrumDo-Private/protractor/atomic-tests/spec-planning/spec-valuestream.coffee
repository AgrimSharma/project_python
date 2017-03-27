util = require("../util")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")

EC = protractor.ExpectedConditions


describe 'Scrumdo Valuestream' , ->
    storyEditWindow = new StoryEditWindow(param.hostName)

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'Should setup org to value stream planning', ->
        browser.get "#{param.orgPlanningUrl}#/setup"
        element(By.buttonText("Enable Value Stream Planning")).click()

        # In single-tests, the board is often set up and this button doesn't exist, so only click it if it's there.
        element(By.buttonText("Use Default Board")).isPresent().then (result) ->
            if result
                element(By.buttonText("Use Default Board")).click()


        return browser.driver.wait( (() ->
            return browser.driver.getCurrentUrl().then( (url) ->
                return /board/.test(url)
                )
            ), 10000);

    it 'Shoud create new value stream release', ->
        browser.sleep(4000)
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(1).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(1).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(param.releaseName)
                element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()

        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).all(By.css('li.cards div.cards-header span.pull-right')).get(1).click().then ->
            element.all(By.css('.assignment-checkbox-list li')).then (checkboxes) ->
                checkboxes.forEach (elem, i) ->
                    elem.all(By.css('input[type="checkbox"]')).get(0).click()
            element.all(By.css('button[ng-click="ctrl.save()"]')).filter (elem) ->
                return elem.isDisplayed()
            .click()
            return
        return
    it 'Should add card to value stream Release planning', ->
        browser.get param.projectUrl
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(param.cardName).then ->
                    storyEditWindow.releaseDropDown.element(By.css(".dropdown-toggle")).click().then ->
                        storyEditWindow.releaseDropDown.element(By.css(".dropdown-menu")).all(By.css('li')).get(1).click().then ->
                            element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                                return elem.isDisplayed()
                            .click()
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        return

    it 'Should add card to value stream Release planning with points', ->
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(param.cardName).then ->
                    storyEditWindow.releaseDropDown.element(By.css(".dropdown-toggle")).click().then ->
                        storyEditWindow.releaseDropDown.element(By.css(".dropdown-menu")).all(By.css('li')).get(1).click().then ->
                            storyEditWindow.pointsDropDown.element(By.css(".dropdown-toggle")).click().then ->
                                storyEditWindow.pointsDropDown.element(By.css(".dropdown-menu")).all(By.css('li')).get(3).click().then ->
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
        browser.waitForAngular()
        return

    #let's add some delay here by adding card, while celery does its job
    it 'Should add card', ->
        e = element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button'))
        browser.wait(EC.visibilityOf(e), 10000);
        e.click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(param.cardName).then ->
                    element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                        return elem.isDisplayed()
                    .click()
                    return
                return
            return
        browser.waitForAngular()
        return

    # it 'Should updated the value stream release stats', ->
    #     browser.get param.projectMilestoneUrl
    #     element(By.css('.milestones-navigation')).all(By.css('a')).get(0).click().then ->
    #         browser.waitForAngular()
    #         e = element.all(By.css('.scrumdo-project-boxes-content.upper')).get(0).all(By.css('.col-xs-4 h3')).get(0)
    #         browser.wait(EC.textToBePresentInElement(e, '2'), 45000)
    #         expect(e.getText()).toEqual '2'
    #
    #         e = element.all(By.css('.scrumdo-project-boxes-content.lower')).get(0).all(By.css('.col-xs-4 h4')).get(0)
    #         browser.wait(EC.textToBePresentInElement(e, '1'), 45000)
    #         expect(e.getText()).toEqual '1'
    #
    # return
