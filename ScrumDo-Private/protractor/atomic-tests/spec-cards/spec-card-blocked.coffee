util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")

describe 'Scrumdo Card Block/Unblock' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    story = new StoryEditWindow(param.hostName)
    internalReason = "testing blocker feature..."
    externalReason = "testing external blocker feature..."

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

    it "Should add an internal blocker", ->
        board.editCardInCell(0,0).then ->
            story.addBlocker(internalReason)
            story.close()

        expect(story.hasClass(board.getCardInCell(0, 0), 'card-blocked')).toBe true

        board.editCardInCell(0,0).then ->
            story.switchToTab(3)
            expect(element.all(By.css('.blockers-box .scrumdo-text.block')).get(0).getText()).toEqual internalReason
            story.close()
        return

    it "Should resolve the blocker", ->
        board.editCardInCell(0,0).then ->
            story.switchToTab(3)
            story.resolveBlocker("Resolved the blocker...")
            story.close()

        board.editCardInCell(0,0).then ->
            story.switchToTab(3)
            expect(story.hasClass(element.all(By.css('.blockers-box .scrumdo-text.block')).get(0), 'strike')).toBe true
            story.close()

        expect(story.hasClass(board.getCardInCell(0, 0), 'card-blocked')).toBe false
        return

    it "Should add an external blocker", ->
        board.editCardInCell(0,0).then ->
            story.addBlocker(internalReason, true)
            story.close()

        expect(story.hasClass(board.getCardInCell(0, 0), 'card-blocked')).toBe true
        board.editCardInCell(0,0).then ->
            story.switchToTab(3)
            expect(element.all(By.css('.blockers-box .external-icon')).get(0).isPresent()).toBe true
            story.close()
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
