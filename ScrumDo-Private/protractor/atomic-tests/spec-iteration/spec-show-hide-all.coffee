util = require("../util")

describe 'Scrumdo Iteration Show-Hide All' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);


    it "Should navigate to planning page", ->
        browser.get param.planningUrl
    
    it 'Should have link to show all Iterations after adding an hidden Iteration', ->
        iterationName = "#{param.iterationName}"
        planningHeader = element.all(By.css(".scrumdo-planning-container .planning-column-header")).get(1)
        planningHeader.all(By.css(".table-cell")).get(3).element(By.css("button")).click().then ->
            planningHeader.all(By.css(".table-cell")).get(3).element(By.css('ul a[ng-click="planningCtrl.addIteration()"]')).click()
            element.all(By.css('.modal-content input[ng-model="iteration.name"]')).get(0).sendKeys(iterationName)
            element.all(By.css('.modal-content input[ng-model="iteration.hidden"]')).get(0).click()
            element.all(By.css('.modal-content button[ng-click="ctrl.save()"]')).get(0).click()
        browser.waitForAngular()
        #check link to show all iterations
        browser.get param.projectUrl
        expect(element(By.css(".scrumdo-navigation a.scrumdo-navigation-link")).isPresent()).toBe true
        return
        
    it 'Should not have link to show all Iterations after deleting the hidden Iteration', ->
        iterationName = "#{param.iterationName}"
        browser.get param.planningUrl
        planningHeader = element.all(By.css(".scrumdo-planning-container .planning-column-header")).get(1)
        planningHeader.all(By.css(".table-cell")).get(3).element(By.css("button")).click().then ->
            planningHeader.all(By.css(".table-cell")).get(3).all(By.css('ul li')).get(1).element(By.css('a')).click()
            
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
        expect(element(By.css(".scrumdo-navigation a.scrumdo-navigation-link")).isPresent()).toBe false
        return
    
    it "Should navigate to planning page", ->
        browser.get param.planningUrl
    
    for count in [0..15]
        it 'Should add an Iteration', ->
            iterationName = "#{param.iterationName}"
            planningHeader = element.all(By.css(".scrumdo-planning-container .planning-column-header")).get(1)
            planningHeader.all(By.css(".table-cell")).get(3).element(By.css("button")).click().then ->
                planningHeader.all(By.css(".table-cell")).get(3).element(By.css('ul a[ng-click="planningCtrl.addIteration()"]')).click()
                element.all(By.css('.modal-content input[ng-model="iteration.name"]')).get(0).sendKeys(iterationName)
                element.all(By.css('.modal-content button[ng-click="ctrl.save()"]')).get(0).click()
            browser.waitForAngular()
            return
    
    it 'Should not have link to show all Iterations after adding 15 without end-date Iteration', ->
        #check link to show all iterations
        browser.get param.projectUrl
        expect(element(By.css(".scrumdo-navigation a.scrumdo-navigation-link")).isPresent()).toBe false
        
    it 'Should have link to show all Iterations after adding an future Iteration', ->
        browser.get param.planningUrl
        iterationName = "#{param.iterationName}"
        planningHeader = element.all(By.css(".scrumdo-planning-container .planning-column-header")).get(1)
        planningHeader.all(By.css(".table-cell")).get(3).element(By.css("button")).click().then ->
            planningHeader.all(By.css(".table-cell")).get(3).element(By.css('ul a[ng-click="planningCtrl.addIteration()"]')).click()
            element.all(By.css('.modal-content input[ng-model="iteration.name"]')).get(0).sendKeys(iterationName)
            
            element(By.model('iteration.start_date')).element(By.css('button')).click().then ->
                element.all(By.model('date')).get(0).element(By.css('button[ng-click="move(1)"]')).click().then ->
                    element.all(By.model('date')).get(0).element(By.css('table tbody tr:nth-child(2) td:nth-child(3) button')).click()
            
            element(By.model('iteration.end_date')).element(By.css('button')).click().then ->
                element.all(By.model('date')).get(1).element(By.css('button[ng-click="move(1)"]')).click().then ->
                    element.all(By.model('date')).get(1).element(By.css('table tbody tr:nth-child(3) td:nth-child(3) button')).click()
                        
            element.all(By.css('.modal-content button[ng-click="ctrl.save()"]')).get(0).click()
        browser.waitForAngular()
        
        #add one more iteration
        browser.get param.planningUrl
        planningHeader = element.all(By.css(".scrumdo-planning-container .planning-column-header")).get(1)
        planningHeader.all(By.css(".table-cell")).get(3).element(By.css("button")).click().then ->
            planningHeader.all(By.css(".table-cell")).get(3).element(By.css('ul a[ng-click="planningCtrl.addIteration()"]')).click()
            element.all(By.css('.modal-content input[ng-model="iteration.name"]')).get(0).sendKeys(iterationName)
            element.all(By.css('.modal-content button[ng-click="ctrl.save()"]')).get(0).click()
        browser.waitForAngular()
    
        #check link to show all iterations
        browser.get param.projectUrl
        expect(element(By.css(".scrumdo-navigation a.scrumdo-navigation-link")).isPresent()).toBe true
        return