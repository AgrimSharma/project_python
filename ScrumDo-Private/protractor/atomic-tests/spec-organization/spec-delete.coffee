util = require("../util")

describe 'Scrumdo Org Delete', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    orgName = "Automated Org #{param.timeCode}"
    userInfo = {newUserName: param.userName , password: param.password }
    loginUser = if typeof newUser == 'undefined' then userInfo else newUser
    it 'should successfully login', ->
        loginUrl = "#{param.hostName}/account/login/"
        browser.driver.manage().deleteAllCookies()
        browser.get(loginUrl)
        element(By.name('username')).sendKeys loginUser.newUserName
        element(By.name('password')).sendKeys loginUser.password

        #element(By.id('loginButton')).click().then ->
        element.all(By.buttonText('Log In')).click().then ->
            expect(element(By.css('.nav-settings .dropdown-menu li')).isPresent()).toBe true

        browser.get param.dashboardUrl
        # Check that the username is in the logout link, but we have to open that menu first
        element(By.css('.nav-settings-link')).click().then ->
            logoutText = element(By.css('#logoutlink')).getText()
            expect(logoutText).toBe( "Log Out - #{loginUser.newUserName}" )
            return
        return

    it 'Should have organization in list', ->
        browser.get param.hostName + "/?force_org_view=1"
        expect(element.all(By.cssContainingText('.organisations td a', orgName)).count()).toBe(1)
        return

    it 'Should delete the organization', ->
        browser.get param.orgEditUrl
        element.all(By.css('#deleteForm button')).get(0).click().then ->
            element(By.css('.modal-content')).all(By.buttonText('Delete Organization')).filter (elem) ->
                return elem.isDisplayed()
            .click()
            return
        browser.get param.hostName + "/?force_org_view=1"
        expect(element.all(By.cssContainingText('.organisations td a', orgName)).count()).toBe(0)
        return
    return
