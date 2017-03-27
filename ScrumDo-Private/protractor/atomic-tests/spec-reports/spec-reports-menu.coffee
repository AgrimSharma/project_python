util = require("../util")
ProjectApp = require("../../pageobjects/project-app.coffee")

describe 'Scrumdo Projects Menu' , ->

    app = new ProjectApp(param.hostName, param.projectSlug)

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'Should go to the reports page.', ->
        app.get()
        app.clickReportsButton()
