util = require("../util")

describe 'Scrumdo Iteration Add' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'Should Add an Iteration', ->
        iterationName = param.iterationName
        browser.get param.projectUrl

        element.all(By.css('button[ng-click="ctrl.addIteration()"]')).get(0).click()
        element.all(By.css('input[ng-model="iteration.name"]')).get(0).sendKeys(iterationName)
        # element.all(By.css('input[ng-model="iteration.start_date"]')).get(0).sendKeys(param.iterationStartDate)
        # element.all(By.css('input[ng-model="iteration.end_date"]')).get(0).sendKeys(param.iterationEndDate)
        element.all(By.css('button[ng-click="ctrl.save()"]')).get(0).click()
        browser.waitForAngular()
        #check if Iteration added successfully
        expect(element.all(By.css("label.iteration-name[title='#{iterationName}']")).get(0).isPresent()).toBe true
        return
    return
