common = require "../data/data"


exports.config = {
    seleniumAddress: common.param.seleniumAddress
    getPageTimeout: 800000
    allScriptsTimeout: 600000
    jasmineNodeOpts: {
        defaultTimeoutInterval: 60000
        showColors: true
        isVerbose: true
        realtimeFailure: true
        includeStackTrace: true
    }
    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-reports/spec-report-burndown.coffee'
        '../atomic-tests/spec-logout.coffee'
    ]
    capabilities: {
        browserName: 'chrome'
    }
    onPrepare: () ->
        global.select = global.by
        global.disableAnimateCss = common.disableAnimateCss
        global.param = common.param
 
        browser.driver.manage().window().setSize(1200, 1000);
        common.disableAnimate() 
}