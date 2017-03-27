class RightMenu
    constructor: (element) ->
        @element = element

    exportButton: () ->
        return @element.element(By.css('[uib-tooltip="Export"]'))

    boardButton: () ->
        return @element.element(By.css('[uib-tooltip="Kanban Board"]'))

    reportsButton: () ->
        return @element.element(By.css('[uib-tooltip="Reports"]'))

class Portfolio
    constructor: (element) ->
        @element = element

    project: (num) ->
        return new PortfolioProject(@projects().get(num))

    projects: () ->
        return @element.all(By.css('li'));


class PortfolioProject
    constructor: (element) ->
        @element = element
        @rightMenu = new RightMenu(element.element(By.css(".rightmenu")))

    name: () ->
        @element.element(By.css('.project-name')).getText()

class PorfolioEditorLevel
    constructor: (element) ->
        @element = element

    projects: () ->
        return @element.all(By.css('.project'))

    project: (num) ->
        return @projects().get(num)

    addProject: (projectName) ->
        @element.element(By.css('[ng-click="ctrl.addProject(level)"]')).click()
        @element.all(By.model('project.name')).last().sendKeys(projectName)


    removeProject: (num) ->
        return @project(num)
                .element(By.css('.fa-trash'))
                .click()
                .then(() -> element(By.css('[ng-click="ctrl.ok()"]')).click() )


class PortfolioCreateWindow
    constructor: (element) ->
        @element = element

    clickFourLevelSafeTemplate: () ->
        return @element.element(By.css('[ng-click="ctrl.setTemplate(2)"]')).click()

    clickNext: () ->
        return @element.element(By.css('[ng-click="ctrl.buildTemplate()"]')).click()

    clickCreate: () ->
        return @element.element(By.css('.save-button')).click()

    templateInput: (num) ->
        return @element.all(By.css('[ng-model="templateLevel.value"]')).get(num)

    typeTemplateInput: (num, input) ->
        # input.sendKeys(protractor.Key.BACK_SPACE)
        return @templateInput(num).clear().sendKeys(input)

    typePortfolioName: (name) ->
        return @element.element(By.css('[ng-model="ctrl.portfolio.root.name"]')).clear().sendKeys(name)

    portfolioLevel: (num) ->
        return new PorfolioEditorLevel(@element.all(By.css('.portfolio-level')).get(num))


class PortfolioProjectsPage
    constructor: (baseUrl, organizationSlug) ->
        @url = "#{baseUrl}/organization/#{organizationSlug}/dashboard#/portfolioprojects"

    get: ->
        browser.get(@url)
        return @

    clickNewPortfolio: () ->
        return element(By.css('[ng-click="ctrl.createPortfolio()"]')).click()

    createWindow: () ->
        # Returns the new portfolio window
        return new PortfolioCreateWindow(element(By.css(".portfolio-window")))

    projectCategoryGroup: (number=0) ->
        # Returns the element representing a project group in the top simple-projects section
        return element.all(By.css('[ng-repeat="group in projectByCategory"]')).get(number)

    project: (groupNumber, projectNumber) ->
        # Returns a PorfolioProject object representing a project in a project group in the top simple-projects section
        return new PortfolioProject(@projectCategoryGroup(groupNumber)
                    .all(By.css('[ng-controller="DashboardPortfolioProjectController as dpctrl"]'))
                    .get(projectNumber))

    portfolios: () ->
        return element.all(By.css('.portfolio-wrapper'))

    portfolio: (num) ->
        return new Portfolio(@portfolios().get(num))

module.exports = PortfolioProjectsPage
