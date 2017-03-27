common = require "../data/data"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    getPageTimeout: 300000
    jasmineNodeOpts: {
      defaultTimeoutInterval: 60000
      showColors: true
      isVerbose: true
      realtimeFailure: true
      includeStackTrace: true
    }
    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-iteration/spec-show-hide-all.coffee',
        '../atomic-tests/spec-logout.coffee'
    ]
    capabilities: {
        browserName: 'chrome'
    }
    onPrepare: () ->
        global.select = global.by        
        global.param = common.param
        common.disableAnimate()
}

