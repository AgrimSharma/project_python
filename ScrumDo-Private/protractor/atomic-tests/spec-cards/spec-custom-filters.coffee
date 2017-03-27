util = require("../util")
ProjectBoard = require("../../pageobjects/project-board.coffee")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")

describe 'Scrumdo Custom Filters' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    userName = param.userName
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    story = new StoryEditWindow(param.hostName)

    it "Should filter lables dropdown", ->
        board.get()
        board.clickCellActions(0)
        board.clickAddCardInCell(0).then ->
            story.setCardSummary(cardName)
            story.labelDropdown.click()
            
            expect(story.labelDropdown.element(By.css(".dropdown-filter-box")).isPresent()).toBe true
            expect(story.labelDropdown.all(By.css("ul li")).count()).toEqual 3
            story.labelDropdown.element(By.css(".dropdown-filter-box input")).sendKeys("Feat")
            expect(story.labelDropdown.all(By.css("ul li")).count()).toEqual 1
            
            story.labelDropdown.element(By.css(".dropdown-filter-box input")).clear().sendKeys("nothing to show")
            expect(story.labelDropdown.all(By.css("ul li")).count()).toEqual 0
            
        return
    
    it "Should filter Assignee dropdown", ->
        board.get()
        board.clickCellActions(0)
        board.clickAddCardInCell(0).then ->
            story.setCardSummary(cardName)
            story.assigneeBox.click()
            
            expect(story.assigneeBox.element(By.css(".dropdown-filter-box")).isPresent()).toBe true
            expect(story.assigneeBox.all(By.css("ul li")).count()).toEqual 1
            story.assigneeBox.element(By.css(".dropdown-filter-box input")).sendKeys("Auto")
            expect(story.assigneeBox.all(By.css("ul li")).count()).toEqual 1
            
            story.assigneeBox.element(By.css(".dropdown-filter-box input")).clear().sendKeys("nothing to show")
            expect(story.assigneeBox.all(By.css("ul li")).count()).toEqual 0
            
        return
    return