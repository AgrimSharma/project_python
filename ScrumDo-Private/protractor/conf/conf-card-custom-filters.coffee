common = require "../data/data"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    getPageTimeout: 30000
    allScriptsTimeout: 30000
    jasmineNodeOpts: {defaultTimeoutInterval: 30000}
    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-cards/spec-custom-filters.coffee',
        '../atomic-tests/spec-logout.coffee'
    ]
    capabilities: {
        browserName: 'chrome'
    }
    onPrepare: () ->
        global.select = global.by        
        global.param = common.param
}

