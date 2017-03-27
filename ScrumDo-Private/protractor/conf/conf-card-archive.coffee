common = require "../data/data"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-cards/spec-add-cards.coffee',
        '../atomic-tests/spec-cards/spec-archive-cards.coffee',
        '../atomic-tests/spec-logout.coffee'
    ]
    capabilities: {
        browserName: 'firefox'
    }
    onPrepare: () ->
        global.select = global.by        
        global.param = common.param
}

