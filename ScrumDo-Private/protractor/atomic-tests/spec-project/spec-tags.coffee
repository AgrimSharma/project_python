util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")
ProjectApp = require("../../pageobjects/project-app.coffee")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")

describe 'Scrumdo Project Tags' , ->

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

    it "Should add card to cell with a tag", ->
        board.clickCellActions(0)
        board.clickAddCardInCell(0).then ->
            story.setCardSummary(cardName)
            story.setTag("#scrumDo")
            story.clickSave()
        browser.waitForAngular()
        return

    it "Should add card to cell with a tag", ->
        board.clickCellActions(0)
        board.clickAddCardInCell(0).then ->
            story.setCardSummary(cardName)
            story.setTag("#CodeGenesys")
            story.clickSave()
        browser.waitForAngular()
        return

    it "Should have card's tags on Setting page", ->
        projectApp.gotoTagSetting()
        tag1 = board.getTag(0)
        tag2 = board.getTag(1)
        expect(tag1.getText()).toBe("scrumDo")
        expect(tag2.getText()).toBe("CodeGenesys")
        return

    it "Should not have duplicate tags after renaming", ->
        board.getTagEditButton(0).click().then ->
            board.getTagInputBox(0).clear().sendKeys("CodeGenesys").then ->
                board.saveTag(0)
        browser.waitForAngular()
        tag1 = board.getTag(0)
        allTags = board.getAllTags()
        expect(tag1.getText()).toBe("CodeGenesys")
        expect(allTags.count()).toEqual(1)
        return

    # it "Should add card to cell", ->
    #     #wait for some time while tags get updated
    #
    #     board.clickCellActions(1)
    #     board.clickAddCardInCell(1).then ->
    #         story.setCardSummary("wait for some time")
    #         story.clickSave()
    #     browser.waitForAngular()
    #     board.clickCellActions(1)
    #     board.clickAddCardInCell(1).then ->
    #         story.setCardSummary("wait for some time")
    #         story.clickSave()
    #     browser.waitForAngular()
    #     return

    it "Should update the cards tag", ->
        # Since this comes over the realtime chanel, it can take some time for it to happen.
        EC = protractor.ExpectedConditions;
        board.get()
        browser.sleep(30000)
        board.editCardInCell(0,0)
        browser.sleep(1000)
        story.close()
        browser.sleep(1000)
        card = board.getCardInCell(0,0)
        tagElement = card.all(By.css(".cards-badges-wrapper span")).get(0)
        browser.wait(EC.textToBePresentInElement(tagElement, '#CodeGenesys'), 10000);

        expect(tagElement.getText()).toEqual "#CodeGenesys"

    it 'Should Archive all cards in a cell', ->
        board.clickCellActions(0).then ->
            board.archiveAllCardsInCell(0)
        board.confirmOk()
        browser.waitForAngular()
        board.clickCellActions(1).then ->
            board.archiveAllCardsInCell(1)
        board.confirmOk()
        browser.waitForAngular()
        return

    it "Should add new tag on Project Tags Page", ->
        projectApp.gotoTagSetting()
        board.addNewTag("Agile")
        browser.waitForAngular()
        tag = board.getTag(1)
        expect(tag.getText()).toBe("Agile")
        return

    it "Should delete tag on Project Tags Page", ->
        board.getTagDeleteButton(0).click().then ->
            board.confirmOk()
        browser.waitForAngular()
        tag1 = board.getTag(0)
        allTags = board.getAllTags()
        expect(tag1.getText()).toBe("Agile")
        expect(allTags.count()).toEqual(1)
        return
    return
