util = require("../util")
BetaPage = require("../../pageobjects/beta.coffee")
PortfolioProjectsPage = require("../../pageobjects/portfolioprojects.coffee")

describe 'Scrumdo Portfolio Projects Page', ->
    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    userInfo = {newUserName: param.userName , password: param.password }
    loginUser = if typeof newUser == 'undefined' then userInfo else newUser

    it 'should enable portfolio projects', ->
        page = new BetaPage(param.hostName)
        page.get()
        page.clickPortfolioEnable();

    it 'should display the new portfolio projects page', ->
        page = new PortfolioProjectsPage(param.hostName, param.organizationSlug)
        page.get()
        project = page.project(0,0)
        expect(project.element.isPresent()).toBeTruthy()
        expect(project.rightMenu.exportButton().isPresent()).toBeTruthy()
        expect(project.rightMenu.boardButton().isPresent()).toBeTruthy()
        expect(project.rightMenu.reportsButton().isPresent()).toBeTruthy()

    it 'should create a new portfolio', ->
        # The goal here is to create a 4 level SAFE implementation with
        # 2 value streams,
        # 2 programs
        # 3 teams

        page = new PortfolioProjectsPage(param.hostName, param.organizationSlug)
        page.clickNewPortfolio()
        createWindow = page.createWindow()
        createWindow.clickFourLevelSafeTemplate()

        createWindow.typeTemplateInput(0,'2')
        createWindow.typeTemplateInput(1,'2')
        createWindow.typeTemplateInput(2,'2')
        createWindow.clickNext()

        createWindow.typePortfolioName('Protractor Test Porfolio')

        valuestreams = createWindow.portfolioLevel(0)
        programs = createWindow.portfolioLevel(1)
        teams = createWindow.portfolioLevel(2)

        programs.addProject('test project')
        teams.addProject('test team project')

        programs.removeProject(1)

        createWindow.clickCreate()

        portfolio = page.portfolio(0)
        expect(portfolio.project(0).name()).toBe('Protractor Test Porfolio')
        expect(portfolio.projects().count()).toBe(8)
        expect(portfolio.project(1).name()).toBe('Value Stream 1')
        expect(portfolio.project(2).name()).toBe('Value Stream 2')

        expect(portfolio.project(3).name()).toBe('Program 1')
        expect(portfolio.project(4).name()).toBe('test project')
                
        expect(portfolio.project(5).name()).toBe('Team 1')
        expect(portfolio.project(6).name()).toBe('Team 2')
        expect(portfolio.project(7).name()).toBe('test team project')
    
    it 'should disable portfolio projects', ->
        page = new BetaPage(param.hostName)
        page.get()
        page.clickPortfolioDisable().then ->
            browser.sleep(1000)
    return
