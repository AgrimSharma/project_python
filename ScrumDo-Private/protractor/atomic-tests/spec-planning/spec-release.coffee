util = require("../util")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")

describe 'Scrumdo Release' , ->

    storyEditWindow = new StoryEditWindow(param.hostName)

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'Should setup org to release planning', ->
        browser.get "#{param.orgPlanningUrl}#/setup"
        element(By.buttonText("Enable Releases")).click()
        return

    it 'Shoud create new release', ->
        element(By.css('button[ng-click="releasesCtrl.newRelease()"]')).click().then ->
            element.all(By.css('div.scrumdo-mce-editor')).get(0).sendKeys(param.releaseName).then ->
                element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
        return

    it 'Should add card to Release planning', ->
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

    it 'Should add card to Release planning with points', ->
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
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
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

    it 'Should updated the release stats', ->
        browser.sleep(30000)
        browser.get param.orgPlanningUrl
        browser.waitForAngular()
        expect(element.all(By.css('.scrumdo-project-boxes-content.upper')).get(0).all(By.css('.col-xs-4 h3')).get(0).getText()).toEqual '2'
        expect(element.all(By.css('.scrumdo-project-boxes-content.lower')).get(0).all(By.css('.col-xs-4 h4')).get(0).getText()).toEqual '1'
        return

    it 'Should delete the release', ->
        element.all(By.css('button[ng-click="releaseCtrl.deleteRelease(releasesCtrl.currentRelease)"]')).click().then ->
            element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                return elem.isDisplayed()
            .click()
            return
        browser.waitForAngular()
        return
    return