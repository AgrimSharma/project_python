util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")

describe 'Scrumdo Card Minimize/Maximize' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    secondCardName = "Card-Minimize-Test"
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    story = new StoryEditWindow(param.hostName)

    it 'Should Archive all cards in a cell', ->
        board.get()

        board.clickCellActions(0).then ->
            board.archiveAllCardsInCell(0)
        board.confirmOk()
        browser.waitForAngular()
        expect(board.cardFirstCell.isPresent()).toBe false
        return

    it "Should add card to cell", ->
        board.clickCellActions(0)
        board.clickAddCardInCell(0)
        story.setCardSummary(cardName)
        story.clickSave()
        browser.waitForAngular()
        expect(board.getCardByNameInCell(0, cardName).isPresent()).toBe true
        return

    it "Should minimize card", ->
        board.editCardInCell(0,0).then ->
            story.minimize();
            expect(story.maximizeButton.isPresent()).toBe true
            story.closeMinimized();
            board.confirmOk();
        return

    it "Should maximize card", ->
        board.editCardInCell(0,0).then ->
            story.minimize();
            story.maximize();
            story.close();
        return

    it "Should Add new card when one card is minimized", ->
        board.editCardInCell(0,0).then ->
            story.minimize();
            board.clickCellActions(0)
            board.clickAddCardInCell(0)
            story.setCardSummary(secondCardName)
            story.clickSave();
            browser.waitForAngular()
            expect(board.getCardByNameInCell(0, secondCardName).isPresent()).toBe true
            story.closeMinimized();
            board.confirmOk();
            board.get()

            board.clickCellActions(0).then ->
                board.archiveAllCardsInCell(0)
                board.confirmOk()
                browser.waitForAngular()
       return