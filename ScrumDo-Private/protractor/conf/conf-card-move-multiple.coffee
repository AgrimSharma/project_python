common = require "../data/data"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    jasmineNodeOpts: {
        defaultTimeoutInterval: 30000
        showColors: true
        isVerbose: true
        realtimeFailure: true
        includeStackTrace: true
    }
    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-cards/spec-move-multiple.coffee',
        '../atomic-tests/spec-logout.coffee'
    ]
    capabilities: {
        browserName: 'firefox'
    }
    onPrepare: () ->
        global.select = global.by
        global.param = common.param
}
