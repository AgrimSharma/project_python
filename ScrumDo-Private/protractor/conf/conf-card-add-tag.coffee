common = require "../data/data"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-cards/spec-add-tag.coffee',
        '../atomic-tests/spec-logout.coffee'
    ]
    capabilities: {
        browserName: 'chrome'
    }
    onPrepare: () ->
        global.select = global.by        
        global.param = common.param
}

