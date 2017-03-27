common = require "../data/data"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    getPageTimeout: 45000
    allScriptsTimeout: 60000
    jasmineNodeOpts:
        defaultTimeoutInterval: 60000
        showColors: true
        isVerbose: true
        realtimeFailure: true

    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-project/spec-add.coffee',
        '../atomic-tests/spec-logout.coffee'
    ]
    capabilities: {
        browserName: 'chrome'
    }
    onPrepare: () ->
        global.select = global.by
        global.param = common.param
        global.projectName = "Project #{Math.floor(Date.now() / 1000)}"

        browser.driver.manage().window().setSize(1200, 1000);
        common.disableAnimate()

}
