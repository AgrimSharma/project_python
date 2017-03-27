util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
ProjectApp = require("../../pageobjects/project-app.coffee")

describe "Scrumdo Card Change business value type", ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    story = new StoryEditWindow(param.hostName)
    projectApp = new ProjectApp(param.hostName, param.projectSlug)

    it "Should select dollar business mode", ->
        projectApp.gotoCardSetting()
        browser.waitForAngular()
        dollar = element.all(By.css('input[name="optionsBusinessMode"]')).get(1)
        dollar.click()
        element(By.css('button[ng-click="ctrl.save()"]')).click()

    it 'Should Archive all cards in a cell', ->
        board.get()
        board.clickCellActions(0).then ->
            board.archiveAllCardsInCell(0)
        board.confirmOk()
        browser.waitForAngular()
        expect(board.cardFirstCell.isPresent()).toBe false
        return

    it "Should add card to cell", ->
        board.get()
        browser.waitForAngular()
        board.clickCellActions(0)
        board.clickAddCardInCell(0)
        story.setCardSummary(cardName)
        story.setBusinessValue('10')
        story.clickSave()
        browser.waitForAngular()
        expect(board.getCardByNameInCell(0, cardName).isPresent()).toBe true
        return

    it "Should select point scale business mode", ->
        projectApp.gotoCardSetting()
        browser.waitForAngular()
        pointScale = element.all(By.css('input[name="optionsBusinessMode"]')).get(2)
        pointScale.click()
        element(By.css('button[ng-click="ctrl.save()"]')).click()

    it "Should have initial business value", ->
        board.get()
        card = board.editCardInCell(0,0)
        businessValue = element.all(By.css('.card-modal sd-story-fields .business-input button'))
        expect(businessValue.get(0).getText()).toEqual "10 Points"
        story.close()

    it "Should have point scale in planning poker", ->
        board.get()
        card = board.editCardInCell(0,0)
        story.playPoker()
        pointsFirst = element.all(By.css('.modal-body .scrumdo-planning-poker-points span')).first()
        pointsLast = element.all(By.css('.modal-body .scrumdo-planning-poker-points span')).last()
        expect(pointsFirst.getText()).toEqual "?"
        expect(pointsLast.getText()).toEqual "Infinite"

    it 'Should Archive all cards in a cell', ->
        board.get()
        board.clickCellActions(0).then ->
            board.archiveAllCardsInCell(0)
        board.confirmOk()
        browser.waitForAngular()
        expect(board.cardFirstCell.isPresent()).toBe false
        return

    it "Should select dollar business mode", ->
        projectApp.gotoCardSetting()
        browser.waitForAngular()
        dollar = element.all(By.css('input[name="optionsBusinessMode"]')).get(1)
        dollar.click()
        element(By.css('button[ng-click="ctrl.save()"]')).click()
