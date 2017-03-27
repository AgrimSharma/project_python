util = require("./util")

describe 'Scrumdo Logout', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    it 'should successfully log out', ->
        browser.get param.dashboardUrl
        element(By.css('.nav-settings-link')).click()
        element(By.css('.nav-settings a[href="/account/logout/"]')).click()
        expect(element(By.css('.nav-settings .dropdown-menu li')).isPresent()).toBe false
    return
