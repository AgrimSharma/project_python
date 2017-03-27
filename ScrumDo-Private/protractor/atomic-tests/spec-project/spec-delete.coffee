util = require("../util")

ProjectBoard = require("../../pageobjects/project-board.coffee")
ProjectApp = require("../../pageobjects/project-app.coffee")

describe 'Scrumdo Delete Project' , ->
    board = new ProjectBoard(param.hostName, param.projectSlug, param.orgSlug)
    projectApp = new ProjectApp(param.hostName, param.projectSlug)

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'Should delete the Project', ->
        board.get()
        projectApp.gotoSettings("admin")
        element.all(By.buttonText('Delete Workspace')).filter (elem) ->
            return elem.isDisplayed()
        .click()
        element.all(By.css('.modal-dialog .modal-content .modal-footer button')).get(0).click()
        element.all(By.css('.modal-dialog .modal-body input[name="projectname"]')).get(0).sendKeys(projectName).then ->
            element.all(By.css('.modal-dialog .modal-body')).get(0).element(By.buttonText('
                    I understand the consequences, delete this workspace')).click()
        expect(element(By.xpath('.//*[normalize-space(text())=normalize-space("' + projectName + '")]')).isPresent()).toBe false
        return
