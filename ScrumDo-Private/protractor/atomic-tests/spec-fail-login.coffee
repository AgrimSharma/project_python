util = require("./util")

describe 'Scrumdo Failed Login', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    userInfo = {newUserName: param.userName , password: param.password }
    loginUser = if typeof newUser == 'undefined' then userInfo else newUser
    it 'should not successfully login with a bad password', ->
        loginUrl = "#{param.hostName}/account/login/"
        browser.driver.manage().deleteAllCookies()
        browser.get(loginUrl)
        element(By.name('username')).sendKeys param.userName
        element(By.name('password')).sendKeys 'ZZZZZBAD PASSWORDZZZZ'

        #element(By.id('loginButton')).click()
        element.all(By.buttonText('Log In')).click()

        errorMessage = element(By.css(".scrumdo-box-modal-content .alert strong")).getText()
        expect(errorMessage).toBe("The username and/or password you specified are not correct.")
