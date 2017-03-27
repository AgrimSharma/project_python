util = require("../util")

describe "Scrumdo export project", ->
    EC = protractor.ExpectedConditions;
    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);


    it "should export the project", ->
        browser.get param.dashboardUrl+"#/projects"

        param.closeIntercom()

        browser.actions().mouseMove(element.all(By.css(".projects-list li")).get(0)).perform();

        element.all(By.css(".projects-list li")).get(0).all(By.css('button[ng-click="ctrl.exportProject(project)"]')).get(0).click().then ->
            element.all(By.css('.modal-body button[ng-click="ctrl.export()"]')).get(0).click().then ->

                downloadButton = EC.textToBePresentInElement($(".modal-dialog .modal-body a"), "Download File")
                browser.wait(downloadButton, 30000);

                expect(element.all(By.css(".modal-body a")).get(0).getText()).toEqual "Download File"
            return
        return
    return
