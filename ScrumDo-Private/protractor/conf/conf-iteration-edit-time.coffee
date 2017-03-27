common = require "../data/data"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    getPageTimeout: 300000
    jasmineNodeOpts: {defaultTimeoutInterval: 300000}
    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-iteration/spec-add.coffee',
        '../atomic-tests/spec-iteration/spec-edit-time.coffee',
        '../atomic-tests/spec-iteration/spec-delete.coffee',
        '../atomic-tests/spec-logout.coffee'
    ]
    capabilities: {
        browserName: 'chrome'
    }
    onPrepare: () ->
        global.select = global.by
        global.param = common.param
        console.log(global.param)
}
