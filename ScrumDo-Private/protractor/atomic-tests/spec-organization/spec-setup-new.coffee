util = require("../util")

describe 'Scrumdo Org Setup', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    orgName = "Automated Org #{param.timeCode}"
    userInfo = {newUserName: param.userName , password: param.password }
    
    newOrgName = "Automated Org #{param.timeCode}"
    newOrgSlug = "automated-org-#{param.timeCode}"
    newProjectName = "Automated Proj #{param.timeCode}"

    it 'shoud set up a new organization', ->
        setupUrl = "#{param.hostName}/subscription/register"
        browser.get(setupUrl)
        
        element(By.name('organization_name')).sendKeys newOrgName
        element(By.css('button[ng-click="ctrl.step2()"]')).click()
        element(By.name('project_name')).sendKeys newProjectName
        element(By.id('createFirstProjectButton')).click()

        browser.waitForAngular()
        browser.sleep(1500);

        news = element.all(By.css(".news-text"))

        projectMessage = news.get(1).getText()
        orgMessage = news.get(2).getText()

    return