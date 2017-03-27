common = require "../data/data"
moment = require "moment"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    getPageTimeout: 300000
    allScriptsTimeout: 300000
    jasmineNodeOpts: {
        defaultTimeoutInterval: 30000
        showColors: true
        isVerbose: true
        realtimeFailure: true
        includeStackTrace: true
    }
    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-reports/spec-report.coffee'
        '../atomic-tests/spec-logout.coffee'
    ]
    capabilities: {
        browserName: 'chrome'
    }
    onPrepare: () ->
        baseUrl = 'http://local.scrumdo.com:8000'

        global.select = global.by
        global.disableAnimateCss = common.disableAnimateCss
        global.param = common.param      
    
        browser.driver.manage().window().setSize(1200, 1000);
        common.disableAnimate() 
}