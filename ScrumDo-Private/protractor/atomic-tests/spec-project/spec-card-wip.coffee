util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
ProjectApp = require("../../pageobjects/project-app.coffee")

describe 'Scrumdo Board Cards WIP' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    story = new StoryEditWindow(param.hostName)
    projectApp = new ProjectApp(param.hostName, param.projectSlug)

    it 'Should Archive all cards in a cell', ->
        board.get()

        board.clickCellActions(0).then ->
            board.archiveAllCardsInCell(0)
        board.confirmOk()
        browser.waitForAngular()
        expect(board.cardFirstCell.isPresent()).toBe false
        return

    it "Should add WIP limits to cell", ->
        board.get()
        projectApp.gotoSettings("board")
        board.editBoardCell(0)
        board.setCardWip(2).then ->
            board.setCardWip(4, "max")

        board.saveBoardCell()
        browser.waitForAngular()
        board.get()

        expect(story.hasClass(board.cellWipHolder(0), 'over-wip')).toBe true
        return

    for count in [0..2]
        it "Should add cards to cell", ->
            board.clickCellActions(0)
            board.clickAddCardInCell(0).then ->
                story.setCardSummary(cardName)
                story.clickSave()
            browser.waitForAngular()
            return

    it "Should not have over wip", ->
        expect(story.hasClass(board.cellWipHolder(0), 'over-wip')).toBe false

    for count in [0..1]
        it "Should add cards to cell", ->
            board.clickCellActions(0)
            board.clickAddCardInCell(0).then ->
                story.setCardSummary(cardName)
                story.clickSave()
            browser.waitForAngular()
            return

    it "Should have over wip", ->
        expect(story.hasClass(board.cellWipHolder(0), 'over-wip')).toBe true

    it 'Should Archive all cards in a cell', ->
        board.get()

        board.clickCellActions(0).then ->
            board.archiveAllCardsInCell(0)
        board.confirmOk()
        browser.waitForAngular()
        expect(board.cardFirstCell.isPresent()).toBe false
        return

    it "Should remove WIP limit", ->
        board.get()
        projectApp.gotoSettings("board")
        board.editBoardCell(0)
        board.setCardWip(0).then ->
            board.setCardWip(0, "max")

        board.saveBoardCell()
        browser.waitForAngular()
        board.get()

        expect(board.cellWipHolder(0).isPresent()).toBe false

    return
