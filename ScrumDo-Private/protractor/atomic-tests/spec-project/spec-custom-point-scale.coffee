util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
ProjectApp = require("../../pageobjects/project-app.coffee")

describe 'Scrumdo Project Custom Point Scale' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    story = new StoryEditWindow(param.hostName)
    projectApp = new ProjectApp(param.hostName, param.projectSlug)


    it "Should add new point scale", ->
        projectApp.gotoSettings("project")
        browser.waitForAngular()
        lastInput = element.all(By.css(".scale-values .custom-point")).last().element(By.css('input[name="point-value"]'))
        firstInput = element.all(By.css(".scale-values .custom-point")).first().element(By.css('input[name="point-value"]'))
        savePintScale = element(By.css('button[ng-click="ctrl.savePointScale(scale)"]'))

        #check for the button to add new point scale
        expect(board.newPointScaleBtn.getText()).toEqual "Add New Point Scale"
        board.newPointScaleBtn.click()
        expect(element.all(By.css(".scale-values .custom-point")).count()).toEqual 14

        #check max point value
        firstInput.clear().sendKeys(9999999999)
        lastInput.click()
        expect(firstInput.getAttribute('value')).toEqual "9999999"

        #check invalid input value
        lastInput.sendKeys("invalid value")
        expect(story.hasClass(element(By.css(".alert.alert-info")), 'alert-danger')).toBe true
        lastInput.click()
        i = 0
        for count in [0..24]
            val = parseInt(Math.random() * (1111 - 11) + 11)
            if i == 24
                val = 9999999
            element.all(By.css(".scale-values .custom-point")).get(i).element(By.css('input[name="point-value"]')).clear().sendKeys(val)
            i++

        expect(lastInput.getAttribute('value')).toEqual "9999999"
        savePintScale.click()
        browser.waitForAngular()
        board.get()

        projectApp.gotoSettings("project")
        expect(element.all(By.css(".custom-point-scales .form-group")).count()).toEqual 7
        return

    it "Should be available for story", ->
        board.get()

        board.clickCellActions(0).then ->
            board.archiveAllCardsInCell(0)
        board.confirmOk()
        browser.waitForAngular()
        expect(board.cardFirstCell.isPresent()).toBe false

        board.clickCellActions(0)
        board.clickAddCardInCell(0).then ->
            story.setCardSummary(cardName)
            story.setPoints(24)
            story.clickSave()
        browser.waitForAngular()
        expect(board.getCardByNameInCell(0, cardName).isPresent()).toBe true

        #check for the point
        board.togglePriorityView()
        card1 = board.getCardInCell(0,0).all(By.css('.points-value span')).get(0)
        expect(card1.getText()).toBe('9999999')

        board.clickCellActions(0).then ->
            board.archiveAllCardsInCell(0)
        board.confirmOk()
        browser.waitForAngular()
        expect(board.cardFirstCell.isPresent()).toBe false
        return

    it "Should delete the added point scale", ->
        delPointScale = element(By.css('button[ng-click="ctrl.deletePointScale(scale)"]'))
        board.get()
        projectApp.gotoSettings("project")
        browser.waitForAngular()

        element.all(By.model("ctrl.project.point_scale_type")).get(1).click()
        browser.waitForAngular()
        delPointScale.click().then ->
            board.confirmOk()

        browser.waitForAngular()
        expect(element.all(By.css(".custom-point-scales .form-group")).count()).toEqual 6
        return

    return
