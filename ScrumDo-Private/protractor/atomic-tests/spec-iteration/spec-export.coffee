util = require("../util")

ProjectBoard = require("../../pageobjects/project-board.coffee")
ProjectApp = require("../../pageobjects/project-app.coffee")
EC = protractor.ExpectedConditions;

describe "Scrumdo export iteration", ->
    projectApp = new ProjectApp(param.hostName, param.projectSlug)
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it "should export the iteration", ->
        board.get()
        projectApp.gotoTabs("cardlist")
        element.all(By.css('button[ng-click="ctrl.export($event)"]')).get(0).click().then ->
            element.all(By.css('.modal-body button[ng-click="ctrl.export()"]')).get(0).click().then ->
                downloadButton = EC.textToBePresentInElement($(".modal-dialog .modal-body a"), "Download File")
                browser.wait(downloadButton, 10000);

                expect(element.all(By.css(".modal-body a")).get(0).getText()).toEqual "Download File"
            return
        return
    return
