util = require("../util")

describe 'Scrumdo card setting', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    it 'Should project name', ->
        browser.get param.projectUrl
    
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        browser.waitForAngular()
        expect(element(By.css('input[ng-model="ctrl.project.name"]')).isPresent()).toBe true
        return

    it 'Should verify popup (Run board wizard)', ->
        element(By.xpath('//a[contains(text(),"Board Editor")]')).click().then ->
            element(By.css('button[ng-click="ctrl.wizard()"]')).click().then ->
                element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                    return elem.isDisplayed()
                return
            return
        browser.waitForAngular()
        return
		
    it 'Should verify (Reset board and Run wizard functinality)', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Board Editor")]')).click().then ->
                element(By.css('button[ng-click="ctrl.wizard()"]')).click().then ->
                    element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                        return elem.isDisplayed()
                    .click()
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.css('button[ng-click="ctrl.buildBoard()"]')).isPresent()).toBe true
        element(By.css('button[ng-click="ctrl.buildBoard()"]')).click().then -> browser.sleep(5000).then ->
        browser.waitForAngular()
        expect(element(By.xpath('//a[contains(text(),"Done Editing")]')).isPresent()).toBe true
        return
	
    it 'Should verify done editing functinality', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Board Editor")]')).click().then ->
                element(By.xpath('//a[contains(text(),"Done Editing")]')).click().then ->
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.app-right-tabs>a')).get(3).isPresent()).toBe true
        return
		

    cellname = param.cellName
    it 'Should create new cell', ->
        browser.get param.projectUrl
		
        elem = element.all(By.css('#kanbanboardeditor  svg .vline')).get(49)
        target = element.all(By.css('#kanbanboardeditor  svg .hline')).get(0)
	
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->	
        element(By.xpath('//a[contains(text(),"Board Editor")]')).click().then ->
            browser.driver.actions()
                .mouseDown(elem)
                .mouseMove(target)
                .mouseUp()
                .perform();
            browser.sleep(3000);
            element(By.css('input[ng-model="editingCell.label"]')).clear().sendKeys(cellname).then ->
            element(By.css('button[ng-click="ctrl.onSave()"]')).click()
        browser.waitForAngular()
        browser.get param.projectUrl
        browser.waitForAngular()
        expect(element(By.xpath('//h2[contains(text(),"'+cellname+'")]')).isPresent()).toBe true
        return

    it 'Should delete a created cell', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Board Editor")]')).click().then -> browser.sleep(2000).then ->
                browser.actions().mouseMove(element.all(By.css('#kanbanboardeditor svg g g')).get(4)).perform();
                element.all(By.css('#kanbanboardeditor svg g g')).get(4).click().then -> browser.sleep(2000).then ->
                    element(By.css('button[ng-click="ctrl.onDelete()"]')).click().then -> browser.sleep(2000).then ->
                        element.all(By.buttonText('Delete')).filter (elem) ->
                            return elem.isDisplayed()
                        .click()
                        return
                    return
                return
            return
        browser.waitForAngular()
        browser.get param.projectUrl
        browser.waitForAngular()
        expect(element(By.xpath('//h2[contains(text(),"'+cellname+'")]')).isPresent()).toBe false
        return
		
    headername = param.cellName
    it 'Should create new header cell', ->
        browser.get param.projectUrl
        elem = element.all(By.css('#kanbanboardeditor  svg .hline')).get(16)
        target = element.all(By.css('#kanbanboardeditor  svg .hline')).get(2)
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        element(By.xpath('//a[contains(text(),"Board Editor")]')).click().then ->
            browser.driver.actions()
                .mouseDown(elem)
                .mouseMove(target)
                .mouseUp()
                .perform();
            browser.sleep(3000);
            element(By.css('input[ng-model="editingHeader.label"]')).clear().sendKeys(headername).then ->
            element(By.css('a[ng-click="ctrl.onSave()"]')).click()
        browser.waitForAngular()
        browser.get param.projectUrl
        browser.waitForAngular()
        expect(element(By.xpath('//h2[contains(text(),"'+headername+'")]')).isPresent()).toBe true
        return
		
    headername = param.cellName
    it 'Should edit header cell', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        element(By.xpath('//a[contains(text(),"Board Editor")]')).click().then -> browser.sleep(2000).then ->
            browser.actions().mouseMove(element.all(By.css('#kanbanboardeditor svg g g')).get(4)).perform();
            element.all(By.css('#kanbanboardeditor svg g g')).get(4).click().then -> browser.sleep(2000).then ->
                element(By.css('input[ng-model="editingHeader.label"]')).clear().sendKeys(headername).then ->
                    element.all(By.css('.sp-replacer.sp-light')).get(0).click().then ->
                        element.all(By.css('.sp-thumb-el.sp-thumb-light')).get(5).click().then -> browser.sleep(2000).then ->
                             element(By.css('a[ng-click="ctrl.selectHeaderCells()"]')).click().then -> browser.sleep(2000).then ->
                                element.all(By.css('#kanbanboardeditor svg g g')).get(0).click().then -> element(By.css('a[ng-click="ctrl.doneSelecting()"]')).click().then ->
                                    element.all(By.css('input[type="number"]')).get(0).click().then -> browser.sleep(2000).then ->
                                        element.all(By.css('input[type="number"]')).get(0).clear().sendKeys('1').then -> browser.sleep(2000).then ->
                                            element.all(By.css('input[type="number"]')).get(1).click().then -> browser.sleep(2000).then ->
                                                element.all(By.css('input[type="number"]')).get(1).clear().sendKeys('10').then -> browser.sleep(2000).then -> 
                                                    element(By.css('textarea[ng-model="editingHeader.policy_text"]')).clear().sendKeys('Policy Text').then ->
                                                        element(By.css('a[ng-click="ctrl.onSave()"]')).click().then ->
                                                        return
                                                    return
                                                return
                                            return
                                        return
                                    return
                                return
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        browser.get param.projectUrl
        browser.waitForAngular()
        expect(element(By.xpath('//h2[contains(text(),"'+headername+'")]')).isPresent()).toBe true
        return

    it 'Should move to other place', ->
        browser.get param.projectUrl
        elem = element.all(By.css('#kanbanboardeditor svg g g')).get(4)
        target = element.all(By.css('#kanbanboardeditor  svg .hline')).get(18)

        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        element(By.xpath('//a[contains(text(),"Board Editor")]')).click().then -> browser.sleep(2000).then ->
            browser.actions().mouseMove(element.all(By.css('#kanbanboardeditor svg g g')).get(4)).perform();
            element.all(By.css('#kanbanboardeditor svg g g')).get(4).click().then -> browser.sleep(2000).then ->
                browser.driver.actions()
                .mouseDown(elem)
                .mouseMove(target)
                .mouseUp()
                .perform();
                browser.sleep(3000);
                #element.all(By.css('#kanbanboardeditor svg g g')).get(4).click().then -> browser.sleep(5000).then ->
                element(By.css('a[ng-click="ctrl.onSave()"]')).click().then -> browser.sleep(5000).then ->
                return
            return
        browser.waitForAngular()
        browser.get param.projectUrl
        browser.waitForAngular()
        expect(element(By.xpath('//h2[contains(text(),"'+headername+'")]')).isPresent()).toBe true
        return

    it 'Should resize cell', ->
        browser.get param.projectUrl
        elem = element.all(By.css('#kanbanboardeditor  svg .hline')).get(18)
        target = element.all(By.css('#kanbanboardeditor  svg .hline')).get(2)

        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        element(By.xpath('//a[contains(text(),"Board Editor")]')).click().then -> browser.sleep(2000).then ->
            browser.actions().mouseMove(element.all(By.css('#kanbanboardeditor svg g g')).get(4)).perform();
            element.all(By.css('#kanbanboardeditor svg g g')).get(4).click().then -> browser.sleep(2000).then ->
                browser.driver.actions()
                .mouseDown(elem)
                .mouseMove(target)
                .mouseUp()
                .perform();
                browser.sleep(5000);
                element(By.css('a[ng-click="ctrl.onSave()"]')).click().then ->
                return
            return
        browser.waitForAngular()
        browser.get param.projectUrl
        browser.waitForAngular()
        expect(element(By.xpath('//h2[contains(text(),"'+headername+'")]')).isPresent()).toBe true
        return

    it 'Should delete a created header cell', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        element(By.xpath('//a[contains(text(),"Board Editor")]')).click().then -> browser.sleep(2000).then ->
            browser.actions().mouseMove(element.all(By.css('#kanbanboardeditor svg g g')).get(4)).perform();
            element.all(By.css('#kanbanboardeditor svg g g')).get(4).click().then -> browser.sleep(2000).then ->
                element(By.css('a[ng-click="ctrl.deleteHeader()"]')).click().then -> browser.sleep(2000).then ->
                    element(By.css('button[ng-click="ctrl.ok()"]')).click().then ->
                    return
                return
            return
        browser.waitForAngular()
        browser.get param.projectUrl
        browser.waitForAngular()
        expect(element(By.xpath('//h2[contains(text(),"'+headername+'")]')).isPresent()).toBe false
        return
		
    it 'Should edit cell', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        element(By.xpath('//a[contains(text(),"Board Editor")]')).click().then ->		
            element.all(By.css('#kanbanboardeditor svg g g')).get(0).click().then ->
                element(By.css('input[ng-model="editingCell.label"]')).clear().sendKeys('New Issue').then -> browser.sleep(2000).then ->
                    element(By.css('select[ng-model="editingCell.layout"]')).all(By.tagName('option')).get(0).click().then -> browser.sleep(2000).then ->
                        element(By.css('select[ng-model="editingCell.time_type"]')).all(By.tagName('option')).get(1).click().then -> browser.sleep(2000).then ->
                            element.all(By.css('.sp-replacer.sp-light')).get(0).click().then -> 
                                element.all(By.css('.sp-thumb-el.sp-thumb-light')).get(12).click().then -> browser.sleep(2000).then ->
                                    element.all(By.css('input[type="number"]')).get(0).click().then -> browser.sleep(2000).then ->
                                        element.all(By.css('input[type="number"]')).get(0).clear().sendKeys('1').then ->
                                            element.all(By.css('input[type="number"]')).get(1).click().then -> browser.sleep(2000).then ->
                                                element.all(By.css('input[type="number"]')).get(1).clear().sendKeys('50').then ->
                                                    element.all(By.css('input[type="number"]')).get(2).click().then -> browser.sleep(2000).then ->
                                                        element.all(By.css('input[type="number"]')).get(2).clear().sendKeys('10').then ->
                                                            element.all(By.css('input[type="number"]')).get(3).click().then -> browser.sleep(2000).then ->
                                                                element.all(By.css('input[type="number"]')).get(3).clear().sendKeys('100').then -> browser.sleep(2000).then ->
                                                                    element(By.css('textarea[ng-model="editingCell.policy_text"]')).clear().sendKeys('Policy Text').then ->
                                                                        element(By.css('button[ng-click="ctrl.onSave()"]')).click().then ->
                                                                        return
                                                                    return
                                                                return
                                                            return
                                                        return
                                                    return
                                                return
                                            return
                                        return
                                    return
                                return
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//a[contains(text(),"Board Editor")]')).isPresent()).toBe true
        return
		
    it 'Should verify changes on board', ->
        browser.get param.projectUrl
		
        browser.waitForAngular()
        expect(element(By.xpath('//h2[contains(text(),"New Issue")]')).isPresent()).toBe true
        return