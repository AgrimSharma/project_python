util = require("../util")

describe 'Scrum close card', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'Close open card', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.xpath('(//button[@ng-click="ctrl.cancel()"])[1]')).click().then ->
                    element.all(By.buttonText('Yes')).click()
                    return
                return
            return
        browser.waitForAngular()
