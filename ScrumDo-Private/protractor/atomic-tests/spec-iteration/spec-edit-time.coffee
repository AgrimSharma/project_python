util = require("../util")

describe 'Scrumdo Iteration Edit Time' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    iterationName = param.iterationName
    it 'Should edit the Iteration time', ->
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

        element(By.model('iteration.start_date')).element(By.css('button')).click().then ->
            element.all(By.model('date')).get(0).element(By.buttonText("Today")).click()
        element(By.model('iteration.end_date')).element(By.css('button')).click().then ->
            element.all(By.model('date')).get(1).element(By.buttonText("Today")).click()

        element.all(By.css('button[ng-click="ctrl.save()"]')).get(0).click()
        browser.waitForAngular()
        return

    it 'Iteration Should have updated Time', ->
        currentTime = new Date()
        element.all(By.tagName('a')).filter (elem, index)->
            return elem.getText().then (text) ->
                return text == iterationName
        .then (filteredElements) ->
            filteredElements[0].element(By.xpath('..')).element(By.xpath('..')).element(By.css('button')).click()
            return
        element.all(By.css('a[ng-click="ctrl.editIteration()"]')).filter (elem) ->
            return elem.isDisplayed()
        .click()
        D = ("0" + (currentTime.getDate())).slice(-2)
        M = ("0" + (currentTime.getMonth()+1)).slice(-2)
        Y = currentTime.getFullYear()

        expect(element(By.model('iteration.start_date')).element(By.model('ctrl.date')).getText()).toEqual "#{Y}-#{M}-#{D}"
        expect(element(By.model('iteration.end_date')).element(By.model('ctrl.date')).getText()).toEqual "#{Y}-#{M}-#{D}"
        return
    return
