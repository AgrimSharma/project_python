util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")
ProjectApp = require("../../pageobjects/project-app.coffee")
LoginPage = require("../../pageobjects/login-page.coffee")

describe 'Scrumdo Report' , ->
    
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    project = new ProjectApp(param.hostName, param.projectSlug, param.orgSlug)

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
			
		
    cardName = param.cardName
    it 'Should add a card to cell', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                        return elem.isDisplayed()
                    .click()
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('//p[contains(text(),"' + cardName + '")]')).isPresent()).toBe true
        return
			
    realNumberBoard = ''
    it 'should get added card number', ->
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('//p[contains(text(),"' + cardName + '")]')).isPresent()).toBe true
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards .cards-number')).first().getText().then (getNumber) ->
            getNumberString = getNumber.substring(3, 6)
            realNumberBoard = parseInt(getNumberString)
            return
        return
		
    it 'Should move card to last cell', ->
		
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('//p[contains(text(),"' + cardName + '")]')).isPresent()).toBe true
        card = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('//p[contains(text(),"' + cardName + '")]'))
        expect(card.isPresent()).toBe true
        

        browser.actions()
            .mouseMove(card)
            .keyDown(protractor.Key.SHIFT)
            .click()
            .perform();

        browser.actions().keyUp(protractor.Key.SHIFT).perform()

        browser.sleep(100)
        element.all(By.css('button[uib-tooltip="Move selected cards to cell"]')).get(0).click()
        element.all(By.css('.modal-content .move-cell-body button')).get(0).click().then ->
            element.all(By.css('.modal-content svg g g')).get(3).click()
            return
        element.all(By.css('button[ng-click="ctrl.ok()"]')).get(0).click()
        browser.waitForAngular()
        browser.sleep(100)
        #check if card was moved successfully
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(3).element(By.xpath('//p[contains(text(),"' + cardName + '")]')).isPresent()).toBe true
        return

    it 'Should select report lead', ->
        browser.get param.reportUrl
        # Select lead report from report selection
        board.selectReport('Lead Time').then ->
            browser.waitForAngular()
            board.refreshReport().then ->
                browser.waitForAngular()
                return
        return

    realNumberLead = ''
    it 'Should hover the selected bar chart', ->
        bar = element.all(By.css('.lead-bar')).get(0)
        expect(bar.isDisplayed()).toBe(true);
        
        board.hoverElement(bar).then ->
            expect(element(By.css('.tip')).isDisplayed()).toBe(true);
			
            cardNumber = element.all(By.css('.link-card'))
            i = 0
            while i < cardNumber.length
                cardNumber.get(i).getText().then (movedCard) ->
                    getNumberLead = movedCard.substring(1, 4)
                    realNumberLead = parseInt(getNumberLead)
					
                if realNumberLead == realNumberBoard
                    expect(realNumberLead).toEqual(realNumberBoard)
                    break
                else
                    continue
                return
            ++i
			
		
    cardName = param.cardName
    it 'Should add a card to cell', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                        return elem.isDisplayed()
                    .click()
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('//p[contains(text(),"' + cardName + '")]')).isPresent()).toBe true
        return

    realNumberBoard = ''
    it 'should get added card number', ->
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('//p[contains(text(),"' + cardName + '")]')).isPresent()).toBe true
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards .cards-number')).first().getText().then (getNumber) ->
            getNumberString = getNumber.substring(3, 6)
            realNumberBoard = parseInt(getNumberString)
            return
        return
		
    it 'Should move card to second cell', ->
		
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('//p[contains(text(),"' + cardName + '")]')).isPresent()).toBe true
        card = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('//p[contains(text(),"' + cardName + '")]'))
        expect(card.isPresent()).toBe true
        

        browser.actions()
            .mouseMove(card)
            .keyDown(protractor.Key.SHIFT)
            .click()
            .perform();

        browser.actions().keyUp(protractor.Key.SHIFT).perform()

        browser.sleep(100)
        element.all(By.css('button[uib-tooltip="Move selected cards to cell"]')).get(0).click()
        element.all(By.css('.modal-content .move-cell-body button')).get(0).click().then ->
            element.all(By.css('.modal-content svg g g')).get(1).click()
            return
        element.all(By.css('button[ng-click="ctrl.ok()"]')).get(0).click()
        browser.waitForAngular()
        browser.sleep(100)
        #check if card was moved successfully
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).element(By.xpath('//p[contains(text(),"' + cardName + '")]')).isPresent()).toBe true
        return
		
    it 'Should rewind the script', ->
	    #rewind script
        browser.ignoreSynchronization = true;
        browser.get param.rewindUrl
        browser.driver.sleep(2000)
        browser.ignoreSynchronization = false;
		
    it 'Should move card to third cell', ->
        browser.get param.projectUrl
		
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).element(By.xpath('//p[contains(text(),"' + cardName + '")]')).isPresent()).toBe true
        card = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).element(By.xpath('//p[contains(text(),"' + cardName + '")]'))
        expect(card.isPresent()).toBe true
        

        browser.actions()
            .mouseMove(card)
            .keyDown(protractor.Key.SHIFT)
            .click()
            .perform();

        browser.actions().keyUp(protractor.Key.SHIFT).perform()

        browser.sleep(100)
        element.all(By.css('button[uib-tooltip="Move selected cards to cell"]')).get(0).click()
        element.all(By.css('.modal-content .move-cell-body button')).get(0).click().then ->
            element.all(By.css('.modal-content svg g g')).get(2).click()
            return
        element.all(By.css('button[ng-click="ctrl.ok()"]')).get(0).click()
        browser.waitForAngular()
        browser.sleep(100)
        #check if card was moved successfully
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(2).element(By.xpath('//p[contains(text(),"' + cardName + '")]')).isPresent()).toBe true
        return
		
    it 'Should rewind the script', ->
	    #rewind script
        browser.ignoreSynchronization = true;
        browser.get param.rewindUrl
        browser.driver.sleep(2000)
        browser.ignoreSynchronization = false;
		
    it 'Should move card to fourth cell', ->
        browser.get param.projectUrl
		
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(2).element(By.xpath('//p[contains(text(),"' + cardName + '")]')).isPresent()).toBe true
        card = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(2).element(By.xpath('//p[contains(text(),"' + cardName + '")]'))
        expect(card.isPresent()).toBe true
        

        browser.actions()
            .mouseMove(card)
            .keyDown(protractor.Key.SHIFT)
            .click()
            .perform();

        browser.actions().keyUp(protractor.Key.SHIFT).perform()

        browser.sleep(100)
        element.all(By.css('button[uib-tooltip="Move selected cards to cell"]')).get(0).click()
        element.all(By.css('.modal-content .move-cell-body button')).get(0).click().then ->
            element.all(By.css('.modal-content svg g g')).get(3).click()
            return
        element.all(By.css('button[ng-click="ctrl.ok()"]')).get(0).click()
        browser.waitForAngular()
        browser.sleep(100)
        #check if card was moved successfully
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(3).element(By.xpath('//p[contains(text(),"' + cardName + '")]')).isPresent()).toBe true
        return

    it 'Should select report lead', ->
        browser.get param.reportUrl
        # Select lead report from report selection
        board.selectReport('Lead Time').then ->
            browser.sleep(3000)
            element.all(By.css('select[ng-model="ctrl.workflow"]')).get(1).all(By.tagName('option')).get(5).click().then -> browser.sleep(1000).then ->
                browser.waitForAngular()
                board.refreshReport().then ->
                    browser.waitForAngular()
                    return
                return
        return

    realNumberLead = ''
    it 'Should hover the selected bar chart', ->
        bar = element.all(By.css('.lead-bar')).get(2)
        expect(bar.isDisplayed()).toBe(true);
        
        board.hoverElement(bar).then ->
            expect(element(By.css('.tip')).isDisplayed()).toBe(true);
			
            cardNumber = element.all(By.css('.link-card'))
            i = 0
            while i < cardNumber.length
                cardNumber.get(i).getText().then (movedCard) ->
                    getNumberLead = movedCard.substring(1, 4)
                    realNumberLead = parseInt(getNumberLead)
					
                if realNumberLead == realNumberBoard
                    expect(realNumberLead).toEqual(realNumberBoard)
                    break
                else
                    continue
                return
            ++i

    attr1 = ''
    attr2 = ''
    attr3 = ''
    cardNumber = ''
    it 'should verify total cards on Lead-Time report', ->
        bar = element.all(By.css('.lead-bar')).get(2)
        expect(bar.isDisplayed()).toBe(true);
		
        bar.getAttribute('height').then (attr1) ->
            bar.getAttribute('y').then (attr2) ->
                attr3 = attr1/attr2
            return
        
        board.hoverElement(bar).then ->
            expect(element(By.css('.tip')).isDisplayed()).toBe(true);
            cardNumber = element.all(By.css('.link-card')).count()
        expect(attr3).toEqual(cardNumber)
        return
			