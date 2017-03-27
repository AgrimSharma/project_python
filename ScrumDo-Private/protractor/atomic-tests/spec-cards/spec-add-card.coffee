util = require("../util")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
ProjectBoard = require("../../pageobjects/project-board.coffee")

describe 'Scrumdo add Card' , ->
    storyEditWindow = new StoryEditWindow(param.hostName)
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    
    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    it 'Should Archive all cards in a cell', ->
        board.get()

        board.clickCellActions(0).then ->
            board.archiveAllCardsInCell(0)
        board.confirmOk()
        browser.waitForAngular()
        expect(board.cardFirstCell.isPresent()).toBe false
        return

    it 'Should add a card to cell', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    storyEditWindow.switchToTab(2).then ->
                        element.all(By.css('#ticketMessage')).get(0).sendKeys(param.storyComment).then ->
                            element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                                return elem.isDisplayed()
                            .click()
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return

    it 'Should have comment', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
            expect(element(By.css('.cards-log li')).isPresent()).toBe true
            element(By.css('button[ng-click="ctrl.cancel()"]')).click().then ->
            element.all(By.buttonText('Yes')).filter (elem) ->
                    return elem.isDisplayed()
                .click()


    it 'Should delete a card from cell (after adding)', ->

        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
            element.all(By.css('.modal-dialog .modal-content button[ng-click="ctrl.deleteCard()"]')).get(0).click().then ->
                element.all(By.buttonText('Yes')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
        #check if card was deleted successfully
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe false
        return
    return
