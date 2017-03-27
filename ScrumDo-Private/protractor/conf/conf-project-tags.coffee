common = require "../data/data"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    jasmineNodeOpts:
          defaultTimeoutInterval: 60000
          showColors: true
          isVerbose: true
          realtimeFailure: true
    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-project/spec-tags.coffee',
        '../atomic-tests/spec-logout.coffee'
    ]
    capabilities: {
        browserName: 'chrome'
    }
    onPrepare: () ->
        global.select = global.by
        global.param = common.param

        browser.driver.manage().window().setSize(1200, 1000);

        common.disableAnimate()
}
