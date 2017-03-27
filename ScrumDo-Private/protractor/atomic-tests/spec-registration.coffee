util = require("./util")

describe 'Scrumdo Register', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    existingUser = {
        'name': 'mhughes',
        'email': 'marc.hughes@scrumdo.com'
    }

    newOrgName = "Automated Org #{param.timeCode}"
    newOrgSlug = "automated-org-#{param.timeCode}"
    newProjectName = "Automated Proj #{param.timeCode}"
    param.organizationSlug = newOrgSlug

    it 'should fail to request a registration key for registered email', ->
        registrationUrl = "#{param.hostName}/account/signup/"
        browser.get(registrationUrl)
        element(By.name('email')).sendKeys existingUser.email
        element(By.id('signupForm')).submit()
        return

    it 'should request a registration key for a new user', ->
        registrationUrl = "#{param.hostName}/account/signup/"
        browser.get(registrationUrl)
        element(By.name('email')).sendKeys newUser.email
        element(By.id('signupForm')).submit()
        registerMessage = element(By.css('.scrumdo-box-modal-content p')).getText()
        expect(registerMessage).toContain("If you did not receive this email, please check your junk/spam folder.")
        return

    it 'should successfully register a new user', ->
        registrationUrl = "#{param.hostName}/account/signup/#{param.registrationKey}/"
        browser.get(registrationUrl)
        element(By.name('username')).sendKeys newUser.newUserName
        element(By.name('fullname')).sendKeys newUser.fullName
        element(By.name('password')).sendKeys newUser.password
        element(By.name('company')).sendKeys newOrgName
        element(By.id('signupForm')).submit()
        successUrl = "#{param.hostName}/organization/#{newOrgSlug}/dashboard#/overview"
        expect(browser.getCurrentUrl()).toBe(successUrl)
        return
    