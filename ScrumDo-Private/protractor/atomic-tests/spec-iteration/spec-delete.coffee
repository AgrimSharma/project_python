util = require("../util")

describe 'Scrumdo Iteration Delete' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'Should delete the Iteration', ->
        iterationName = param.iterationName

        browser.get param.planningUrl


        element.all(By.tagName('a')).filter (elem, index)->
            return elem.getText().then (text) ->
                return text == iterationName
        .then (filteredElements) ->
            filteredElements[0].element(By.xpath('..')).element(By.xpath('..')).element(By.css('button')).click()
            return
        element.all(By.css('a[ng-click="ctrl.editIteration()"]')).filter (elem) ->
            return elem.isDisplayed()
        .click()
        element.all(By.css('button[ng-click="ctrl.deleteIteration()"]')).filter (elem) ->
            return elem.isDisplayed()
        .click()
        element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
            return elem.isDisplayed()
        .click()

        browser.get param.projectUrl

        #check if Iteration was deleted successfully
        expect(element(By.css("label.iteration-name[title='#{iterationName}']")).isPresent()).toBe false
        return
    return
