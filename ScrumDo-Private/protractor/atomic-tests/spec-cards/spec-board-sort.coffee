util = require("../util")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
ProjectBoard = require("../../pageobjects/project-board.coffee")
ProjectApp = require("../../pageobjects/project-app.coffee")

EC = protractor.ExpectedConditions


describe 'Scrumdo sort board cards' , ->
    cardName = param.cardName + "Sort Test"
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    storyEditWindow = new StoryEditWindow(param.hostName)
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

    it "Should enable time criticality card filed", ->
        projectApp.gotoCardSetting()

        element(By.css('input[name="use_time_crit"]')).click().then ->
            board.saveSettings()
        browser.waitForAngular()

    it 'Should add a card to cell with point 1 & business val 10 & estimate time 4', ->
        board.get()
        thiscardName = "#{cardName} - 1"
        board.clickCellActions(0)
        e = element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0);
        browser.wait(EC.visibilityOf(e), 10000);
        e.click().then ->
            storyEditWindow.setCardSummary(thiscardName).then ->
                storyEditWindow.switchToTab(2).then ->
                    storyEditWindow.setComment(param.storyComment).then ->
                        storyEditWindow.setPoints(3).then ->
                            storyEditWindow.setBusinessValue(10).then ->
                                storyEditWindow.setEstimateTime(4).then ->
                                    storyEditWindow.setTimeCriticality(4).then ->
                                        storyEditWindow.setDate("future")
                                        storyEditWindow.clickSave()
                                    return
                                return
                            return
                        return
                    return
                return
            return
        return
        browser.waitForAngular()
        expect(board.getCardByNameInCell(0, thiscardName).isPresent()).toBe true
        return

    it 'Should add a card to cell  with point 2 & business val 20 & estimate time 6', ->
        thiscardName = "#{cardName} - 2"
        board.clickCellActions(0)
        board.clickAddCardInCell(0).then ->
            storyEditWindow.setCardSummary(thiscardName).then ->
                storyEditWindow.switchToTab(2).then ->
                    storyEditWindow.setComment(param.storyComment).then ->
                        storyEditWindow.setPoints(4).then ->
                            storyEditWindow.setBusinessValue(20).then ->
                                storyEditWindow.setEstimateTime(6).then ->
                                    storyEditWindow.setTimeCriticality(2).then ->
                                        storyEditWindow.setDate("past")
                                        storyEditWindow.clickSave()
                                    return
                                return
                            return
                        return
                    return
                return
            return
        return
        browser.waitForAngular()
        expect(board.getCardByNameInCell(0, thiscardName).isPresent()).toBe true
        return

    it 'Should add a card to cell  with point 3 & business val 30 & estimate time 1', ->
        thiscardName = "#{cardName} - 3"
        board.clickCellActions(0)
        board.clickAddCardInCell(0).then ->
            storyEditWindow.setCardSummary(thiscardName).then ->
                storyEditWindow.switchToTab(2).then ->
                    storyEditWindow.setComment(param.storyComment).then ->
                        storyEditWindow.setPoints(5).then ->
                            storyEditWindow.setBusinessValue(30).then ->
                                storyEditWindow.setEstimateTime(1).then ->
                                    storyEditWindow.setTimeCriticality(6).then ->
                                        storyEditWindow.setDate("today")
                                        storyEditWindow.clickSave()
                                    return
                                return
                            return
                        return
                    return
                return
            return
        return
        browser.waitForAngular()
        expect(board.getCardByNameInCell(0, thiscardName).isPresent()).toBe true
        return

    it 'Should sort cards with point value', ->
        board.get()
        board.togglePriorityView()
        board.sortCardBy("points")

        card1 = board.getCardInCell(0,0).all(By.css('.points-value span')).get(0)
        card2 = board.getCardInCell(0,1).all(By.css('.points-value span')).get(0)
        card3 = board.getCardInCell(0,2).all(By.css('.points-value span')).get(0)

        expect(card1.getText()).toBe('1')
        expect(card2.getText()).toBe('2')
        expect(card3.getText()).toBe('3')
        return

    it 'Should sort cards with business value', ->
        board.get()
        board.togglePriorityView()
        board.sortCardBy("business_value")

        card1 = board.getCardInCell(0,0).all(By.css('.value span')).get(2)
        card2 = board.getCardInCell(0,1).all(By.css('.value span')).get(2)
        card3 = board.getCardInCell(0,2).all(By.css('.value span')).get(2)

        expect(card1.getText()).toBe('30')
        expect(card2.getText()).toBe('20')
        expect(card3.getText()).toBe('10')
        return

    it 'Should sort cards with estimate time', ->
        board.get()
        board.togglePriorityView()
        board.sortCardBy("estimate_time")

        card1 = board.getCardInCell(0,0).all(By.css('.estimate-value span')).get(0)
        card2 = board.getCardInCell(0,1).all(By.css('.estimate-value span')).get(0)
        card3 = board.getCardInCell(0,2).all(By.css('.estimate-value span')).get(0)

        expect(card1.getText()).toBe('1:00')
        expect(card2.getText()).toBe('4:00')
        expect(card3.getText()).toBe('6:00')
        return

    it 'Should sort cards with Due Date', ->
        board.get()
        board.sortCardBy("due_date")

        card1 = board.getCardInCell(0,0).element(By.css('li.due-date .past-due'))
        card2 = board.getCardInCell(0,1).element(By.css('li.due-date .due-soon'))
        card3 = board.getCardInCell(0,2).element(By.css('li.due-date'))

        expect(card1.isPresent()).toBe true
        expect(card2.isPresent()).toBe true
        expect(card3.isPresent()).toBe true
        return

    it 'Should sort cards with WSJF Value', ->
        board.get()
        board.togglePriorityView()
        board.sortCardBy("wsjf")

        card1 = board.getCardInCell(0,0).all(By.css('.value span')).get(5)
        card2 = board.getCardInCell(0,1).all(By.css('.value span')).get(5)
        card3 = board.getCardInCell(0,2).all(By.css('.value span')).get(5)

        expect(card1.getText()).toBe('12')
        expect(card2.getText()).toBe('11.67')
        expect(card3.getText()).toBe('10.25')
        return

    it "Should disable time criticality card filed", ->
        projectApp.gotoCardSetting()

        element(By.css('input[name="use_time_crit"]')).click().then ->
            board.saveSettings()
        browser.waitForAngular()

    return
