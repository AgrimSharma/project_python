common = require "../data/data"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    getPageTimeout: 30000
    allScriptsTimeout: 30000
    jasmineNodeOpts: {
        defaultTimeoutInterval: 30000
        showColors: true
        isVerbose: true
        realtimeFailure: true
        includeStackTrace: true
    }
    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-iteration/spec-add.coffee',  # Need another iteration
        '../atomic-tests/spec-cards/spec-move-project.coffee',
        '../atomic-tests/spec-iteration/spec-delete.coffee',
        '../atomic-tests/spec-logout.coffee'
    ]
    capabilities: {
        browserName: 'chrome'
    }
    onPrepare: () ->
        global.select = global.by
        global.disableAnimateCss = common.disableAnimateCss
        global.param = common.param
        global.projectName = "Project #{Math.floor(Date.now() / 1000)}"
}
