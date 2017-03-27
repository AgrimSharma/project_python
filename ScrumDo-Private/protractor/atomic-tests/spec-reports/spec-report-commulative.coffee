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
        browser.sleep(5000)
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('//p[contains(text(),"' + cardName + '")]')).isPresent()).toBe true
        return
			
    todoEverythingAvgNumber = ''
    it 'should verify comulative report without moving a card', ->
        browser.get param.reportUrl
		
        element.all(By.css('.reports-area svg g text.avg-values')).get(0).getText().then (text) ->
            avgNumberFirstCell = text.substring(13,18)
            todoEverythingAvgNumber = parseFloat(avgNumberFirstCell);
        return
		
    priortizedReportProfileAvgNumber = ''
    it 'should get avg number of report profile without moving card', ->
	
        element.all(By.css('select[ng-model="ctrl.workflow"]')).get(0).all(By.tagName('option')).get(5).click().then ->browser.sleep(1000).then ->
            element(By.css('button[ng-click="ctrl.refresh()"]')).click().then -> browser.sleep(1000).then ->
                element.all(By.css('.reports-area svg g text.avg-values')).get(0).getText().then (report) ->
                    avgNumber_FirstCell = report.substring(25, 30)
                    priortizedReportProfileAvgNumber = parseFloat(avgNumber_FirstCell)
                return
            return
		
    it 'Should move card to second cell', ->
        browser.get param.projectUrl
		
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards .cards-number')).last().isPresent()).toBe true
        card = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards .cards-number')).last()
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
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).all(By.css('li.cards .cards-number')).last().isPresent()).toBe true
        return
		
    it 'Should rewind the script', ->
	    #rewind script
        browser.ignoreSynchronization = true;
        browser.get param.rewindUrl
        browser.driver.sleep(2000)
        browser.ignoreSynchronization = false;
		
    todoEverythingAvgNumberMove1 = ''
    doingEverythingAvgNumber = ''
    it 'should verify comulative report (second cell)', ->
        browser.get param.reportUrl
	
        element.all(By.css('select[ng-model="ctrl.workflow"]')).get(0).all(By.tagName('option')).get(0).click().then ->browser.sleep(1000).then ->
            element(By.css('button[ng-click="ctrl.refresh()"]')).click().then -> browser.sleep(3000).then ->
                element.all(By.css('.reports-area svg g text.avg-values')).get(0).getText().then (text) ->
                    avgNumberAfterMove2 = text.substring(13,18)
                    todoEverythingAvgNumberMove1 = parseFloat(avgNumberAfterMove2)
                return
            return
        browser.sleep(1000)
        expect(todoEverythingAvgNumberMove1).not.toEqual(todoEverythingAvgNumber)
		
        element.all(By.css('.reports-area svg g text.avg-values')).get(1).getText().then (text2) ->
            avgNumberSecondCell = text2.substring(14,19)
            doingEverythingAvgNumber = parseFloat(avgNumberSecondCell)
        return
		
    priortizedReportProfileAvgNumberMove1 = ''
    committedReportProfileAvgNumber = ''
    it 'should verify comulative report with report profile (move to second cell)', ->
	
        element.all(By.css('select[ng-model="ctrl.workflow"]')).get(0).all(By.tagName('option')).get(5).click().then -> browser.sleep(1000).then ->
            element(By.css('button[ng-click="ctrl.refresh()"]')).click().then -> browser.sleep(3000).then ->
                element.all(By.css('.reports-area svg g text.avg-values')).get(0).getText().then (report) ->
                    avgNumber_CellAfterMove1 = report.substring(25, 30)
                    priortizedReportProfileAvgNumberMove1 = parseFloat(avgNumber_CellAfterMove1)
                return
            return
        browser.sleep(1000)
        expect(priortizedReportProfileAvgNumberMove1).not.toEqual(priortizedReportProfileAvgNumber)

			
        element.all(By.css('.reports-area svg g text.avg-values')).get(1).getText().then (reportText2) ->
            reportSecondCell_AvgNumber = reportText2.substring(18,23)
            committedReportProfileAvgNumber = parseFloat(reportSecondCell_AvgNumber)
        return
			
    it 'Should move card to third cell', ->
        browser.get param.projectUrl
		
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).all(By.css('li.cards .cards-number')).last().isPresent()).toBe true
        card = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).all(By.css('li.cards .cards-number')).last()
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
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(2).all(By.css('li.cards .cards-number')).last().isPresent()).toBe true
        return
		
    it 'Should rewind the script', ->
	    #rewind script
        browser.ignoreSynchronization = true;
        browser.get param.rewindUrl
        browser.driver.sleep(2000)
        browser.ignoreSynchronization = false;
		
    doingEverythingAvgNumberMove2 = ''
    reviewingEverythingAvgNumber = ''
    doneEverythingAvgNumber = ''
    it 'should verify comulative report (third cell)', ->
        browser.get param.reportUrl
		
        element.all(By.css('select[ng-model="ctrl.workflow"]')).get(0).all(By.tagName('option')).get(0).click().then -> browser.sleep(2000).then ->
            element(By.css('button[ng-click="ctrl.refresh()"]')).click().then -> browser.sleep(3000).then ->
                element.all(By.css('.reports-area svg g text.avg-values')).get(1).getText().then (text2) ->
                    avgNumberAfterMove3 = text2.substring(14,19)
                    doingEverythingAvgNumberMove2 = parseFloat(avgNumberAfterMove3)
                return
            return
        browser.sleep(2000)
        expect(doingEverythingAvgNumberMove2).not.toEqual(doingEverythingAvgNumber)
		
        element.all(By.css('.reports-area svg g text.avg-values')).get(2).getText().then (text3) ->
            avgNumberThirdCell = text3.substring(18,23)
            reviewingEverythingAvgNumber = parseFloat(avgNumberThirdCell)
		
        element.all(By.css('.reports-area svg g text.avg-values')).get(3).getText().then (averageText) ->
            avgNumberFourthCell = averageText.substring(13,18)
            doneEverythingAvgNumber = parseFloat(avgNumberFourthCell);
        return
		
    committedReportProfileAvgNumberMove2 = ''
    prepareReportProfileAvgNumber = ''
    doneReportProfileAvgNumber = ''
    it 'should verify comulative report with report profile (move to third cell)', ->
	
        element.all(By.css('select[ng-model="ctrl.workflow"]')).get(0).all(By.tagName('option')).get(5).click().then -> browser.sleep(1000).then ->
            element(By.css('button[ng-click="ctrl.refresh()"]')).click().then -> browser.sleep(2000).then ->	
                element.all(By.css('.reports-area svg g text.avg-values')).get(1).getText().then (report) ->
                    avgNumber_CellAfterMove2 = report.substring(18, 23)
                    committedReportProfileAvgNumberMove2 = parseFloat(avgNumber_CellAfterMove2)
                return
            return
        browser.sleep(2000)
        expect(committedReportProfileAvgNumberMove2).not.toEqual(committedReportProfileAvgNumber)
			
        element.all(By.css('.reports-area svg g text.avg-values')).get(2).getText().then (reportText3) ->
            avgNumberThirdCell = reportText3.substring(24, 29)
            prepareReportProfileAvgNumber = parseFloat(avgNumberThirdCell)
		
        element.all(By.css('.reports-area svg g text.avg-values')).get(3).getText().then (report4) ->
            avgNumber_FourthCell = report4.substring(13, 18)
            doneReportProfileAvgNumber = parseFloat(avgNumber_FourthCell)
        return
		
    cardNumberInteger = ''		
    it 'Should move card to fourth cell', ->
        browser.get param.projectUrl
		
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(2).all(By.css('li.cards .cards-number')).last().isPresent()).toBe true
        card = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(2).all(By.css('li.cards .cards-number')).last()	
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
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(3).all(By.css('li.cards .cards-number')).last().isPresent()).toBe true
        return
		
    it 'Should rewind the script', ->
	    #rewind script
        browser.ignoreSynchronization = true;
        browser.get param.rewindUrl
        browser.driver.sleep(2000)
        browser.ignoreSynchronization = false;
		
    reviewingEverythingAvgNumberMove3 = ''
    doneEverythingAvgNumberMove3 = ''
    it 'should verify comulative report (fourth cell) ', ->
        browser.get param.reportUrl
		
        element.all(By.css('select[ng-model="ctrl.workflow"]')).get(0).all(By.tagName('option')).get(0).click().then ->browser.sleep(2000).then ->
            element(By.css('button[ng-click="ctrl.refresh()"]')).click().then -> browser.sleep(3000).then ->
                element.all(By.css('.reports-area svg g text.avg-values')).get(2).getText().then (text3) ->
                    avgNumberAfterMove4 = text3.substring(18,23)
                    reviewingEverythingAvgNumberMove3 = parseFloat(avgNumberAfterMove4)
                return
            return
        browser.sleep(1000)
        expect(reviewingEverythingAvgNumberMove3).not.toEqual(reviewingEverythingAvgNumber)
		
        element.all(By.css('.reports-area svg g text.avg-values')).get(3).getText().then (text4) ->
            avgNumberFourthCell = text4.substring(13,18)
            doneEverythingAvgNumberMove3 = parseFloat(avgNumberFourthCell)
        browser.sleep(1000)
        expect(doneEverythingAvgNumberMove3).not.toEqual(doneEverythingAvgNumber)
        return
		
    prepareReportProfileAvgNumberMove3 = ''
    doneReportProfileAvgNumberMove3 = ''
    it 'should verify comulative report with report profile (move to fourth cell)', ->
		
        element.all(By.css('select[ng-model="ctrl.workflow"]')).get(0).all(By.tagName('option')).get(5).click().then -> browser.sleep(1000).then ->
            element(By.css('button[ng-click="ctrl.refresh()"]')).click().then -> browser.sleep(2000).then ->
                element.all(By.css('.reports-area svg g text.avg-values')).get(2).getText().then (report) ->
                    avgNumber_CellAfterMove3 = report.substring(24, 29)
                    prepareReportProfileAvgNumberMove3 = parseFloat(avgNumber_CellAfterMove3)
                return
            return
        browser.sleep(1000)
        expect(prepareReportProfileAvgNumberMove3).not.toEqual(prepareReportProfileAvgNumber)
			
        element.all(By.css('.reports-area svg g text.avg-values')).get(3).getText().then (report4) ->
            avgNumber_FourthCell = report4.substring(13, 18)
            doneReportProfileAvgNumberMove3 = parseFloat(avgNumber_FourthCell)
        browser.sleep(1000)
        expect(doneReportProfileAvgNumberMove3).not.toEqual(doneReportProfileAvgNumber)
        return
	