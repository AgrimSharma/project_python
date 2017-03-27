util = require("../util")

describe 'Scrumdo point scale', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    it 'Should project name', ->
        browser.get param.projectUrl
    
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        browser.waitForAngular()
        expect(element(By.css('input[ng-model="ctrl.project.name"]')).isPresent()).toBe true
        return

    it 'Should select point scale', ->
        #browser.get param.orgSettingUrl

        element.all(By.xpath('//input[@ng-model="ctrl.project.point_scale_type"]')).get(0).click().then ->
            element(By.css('button[ng-click="ctrl.save()"]')).click()
            return
        browser.waitForAngular()
        expect(element.all(By.xpath('//input[@ng-model="ctrl.project.point_scale_type"]')).get(0).isPresent()).toBe true
        return
    
    it 'Should verify point scale', ->
        browser.get param.projectUrl
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element.all(By.css('.dropdown-toggle .scrumdo-btn ')).get(4).click().then ->
                return
            return
        browser.waitForAngular
        expect(element.all(By.css('.dropdown-menu.dropdown-menu-right.scrumdo-dropdown>ul>li>a')).get(1).isPresent()).toBe true
        return