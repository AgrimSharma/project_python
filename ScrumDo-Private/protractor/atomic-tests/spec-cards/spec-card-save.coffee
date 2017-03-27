util = require("../util")

describe 'Scrumdo Save Card' , ->

    afterEach () ->
       #util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    it 'Should verify card added without summary', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                    return elem.isDisplayed()
                     .click()
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe false
        return