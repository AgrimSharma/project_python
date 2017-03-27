util = require("../util")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
ProjectBoard = require("../../pageobjects/project-board.coffee")
ProjectApp = require("../../pageobjects/project-app.coffee")

EC = protractor.ExpectedConditions


describe 'Scrumdo card fields' , ->
    cardName = param.cardName + "Sort Test"
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    story = new StoryEditWindow(param.hostName)
    projectApp = new ProjectApp(param.hostName, param.projectSlug)

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'Should Archive all cards in a cell', ->
        board.get()

        board.clickCellActions(0).then ->
            board.archiveAllCardsInCell(0)
        board.confirmOk()
        browser.waitForAngular()
        expect(board.cardFirstCell.isPresent()).toBe false
        return

    it "Should disable all fields and add card to cell", ->
        projectApp.gotoCardSetting()
        element(By.css('input[name="use_points"]')).click().then ->
            element(By.css('input[name="use_time_estimate"]')).click().then ->
                element(By.css('input[name="use_due_date"]')).click().then ->
                    board.saveSettings()
        browser.waitForAngular()

        board.get()
        board.clickCellActions(0)
        board.clickAddCardInCell(0).then ->
            expect(story.pointsDropDown.isPresent()).toBe false
            expect(story.estimateTime.isPresent()).toBe false
            expect(element(By.model('story.due_date')).isPresent()).toBe false

            story.setCardSummary(cardName)
            story.clickSave()

        browser.waitForAngular()
        expect(board.getCardByNameInCell(0, cardName).isPresent()).toBe true
        return

    it "Should enable criticality and resk-reduction and add card to cell", ->
        newCard = "#{cardName}_more_filelds"
        projectApp.gotoCardSetting()
        element(By.css('input[name="use_time_crit"]')).click().then ->
            element(By.css('input[name="use_risk_reduction"]')).click().then ->
                board.saveSettings()
        browser.waitForAngular()

        board.get()
        board.clickCellActions(0)
        board.clickAddCardInCell(0).then ->
            expect(story.timeCriticality.isPresent()).toBe true
            expect(story.riskReduction.isPresent()).toBe true

            story.setCardSummary(newCard)
            story.setTimeCriticality(4)
            story.setRiskReduction(2)
            story.clickSave()

        browser.waitForAngular()
        expect(board.getCardByNameInCell(0, newCard).isPresent()).toBe true
        return

    it "Should reset the card fields", ->
        projectApp.gotoCardSetting()
        element(By.css('input[name="use_points"]')).click().then ->
            element(By.css('input[name="use_time_estimate"]')).click().then ->
                element(By.css('input[name="use_due_date"]')).click().then ->
                    element(By.css('input[name="use_time_crit"]')).click().then ->
                        element(By.css('input[name="use_risk_reduction"]')).click().then ->
                            board.saveSettings()
        browser.waitForAngular()

        board.get()
        return

    it 'Should Archive all cards in a cell', ->
        board.get()

        board.clickCellActions(0).then ->
            board.archiveAllCardsInCell(0)
        board.confirmOk()
        browser.waitForAngular()
        expect(board.cardFirstCell.isPresent()).toBe false
        return

    return
