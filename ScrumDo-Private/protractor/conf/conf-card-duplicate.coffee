common = require "../data/data"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    getPageTimeout: 300000
    allScriptsTimeout: 300000
    jasmineNodeOpts: {defaultTimeoutInterval: 300000}
    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-cards/spec-card-duplicate.coffee',
        '../atomic-tests/spec-logout.coffee'
    ]
    capabilities: {
        browserName: 'firefox'
    }
    onPrepare: () ->
        global.select = global.by        
        global.param = common.param
}