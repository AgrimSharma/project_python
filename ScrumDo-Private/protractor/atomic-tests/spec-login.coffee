util = require("./util")
LoginPage = require("../pageobjects/login-page.coffee")

describe 'Scrumdo Login', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    userInfo = {newUserName: param.userName , password: param.password }
    loginUser = if typeof newUser == 'undefined' then userInfo else newUser


    it 'should successfully login', ->
        browser.driver.manage().deleteAllCookies()

        page = new LoginPage(param.hostName)
        page.get()

        page.setUsername(loginUser.newUserName);
        page.setPassword(loginUser.password)

        page.clickLogin().then ->
            browser.get(param.hostName)
            expect(page.dropdownMenu.isPresent()).toBe true

        # Check that the username is in the logout link, but we have to open that menu first
        element(By.css('.nav-settings-link')).click().then ->
            #check for help/support link
            helpLink = element(By.css('a[href="http://help.scrumdo.com/"]'))
            expect(helpLink.isPresent()).toBe true
            
            logoutText = element(By.css('#logoutlink')).getText()
            expect(logoutText).toBe( "Log Out - #{loginUser.newUserName}" )
    return
