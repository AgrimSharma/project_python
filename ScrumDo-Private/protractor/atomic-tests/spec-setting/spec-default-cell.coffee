util = require("../util")

describe 'Scrumdo default cell', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    it 'Should project name', ->
        browser.get param.orgSettingUrl
    
        browser.waitForAngular()
        expect(element(By.css('input[ng-model="ctrl.project.name"]')).isPresent()).toBe true
        return
		
    it 'Should select cell', ->
        browser.get param.orgSettingUrl
		
        element.all(By.css('.scrumdo-btn .glyphicon')).get(2).click().then -> browser.sleep(2000).then ->
            element.all(By.css('.dropdown-menu  sd-cell-picker .cell-picker .picker-content sd-board-preview svg g g')).get(0).all(By.css('g[id="cell_5191"] rect')).get(0).click().then ->
                element(By.css('button[ng-click="ctrl.save()"]')).click().then ->
                return
            return
        browser.waitForAngular()
        expect(element(By.css('button[ng-click="ctrl.save()"]')).isPresent()).toBe true 
        return
		
    cardName = param.cardName
    it 'Should add default card ', ->
        browser.get param.projectUrl
        browser.waitForAngular()
        element(By.css('.app-cardlist-tab')).click().then ->
            element(By.name('addStorySummary')).sendKeys(cardName).then ->
                element(By.css('button[ng-click="ctrl.addCard()"]')).click().then ->
                return
            return
        browser.waitForAngular()
        browser.get param.projectUrl
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return