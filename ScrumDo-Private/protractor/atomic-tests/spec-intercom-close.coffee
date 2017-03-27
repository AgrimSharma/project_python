ProjectBoard = require("../pageobjects/project-board.coffee")
util = require("./util")

# Depending on external causes, the intercom window might be open and obscuring items.  We should close it.
describe 'Scrumdo Intercom Close', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);


    it 'should close window if open', ->
        board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
        board.get()

        button = element(By.css('.intercom-sheet-header-close-button'))
        return button.isPresent().then (result) ->
            if result
                return button.isDisplayed.then (result) ->
                    element(By.css('.intercom-sheet-header-close-button')).click()
