common = require "../data/data"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    getPageTimeout: 300000
    allScriptsTimeout: 300000
    jasmineNodeOpts: {defaultTimeoutInterval: 300000}
    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-cards/spec-stress-add-card.coffee',
        '../atomic-tests/spec-logout.coffee'
    ]

    capabilities: {
        'browserName': 'chrome'
    },

    onPrepare: () ->
        global.select = global.by
        global.param = common.param
        browser.driver.manage().window().setSize(1200, 1000);
        common.disableAnimate()
}
