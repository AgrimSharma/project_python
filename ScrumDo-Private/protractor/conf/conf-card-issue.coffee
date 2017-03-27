common = require "../data/data"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    getPageTimeout: 800000
    allScriptsTimeout: 600000
    jasmineNodeOpts: {
      defaultTimeoutInterval: 60000
      showColors: true
      isVerbose: true
      realtimeFailure: true
  }
    specs: [
        '../atomic-tests/spec-login.coffee',
        '../atomic-tests/spec-cards/spec-card-issue.coffee',
        '../atomic-tests/spec-logout.coffee'
    ]
    capabilities: {
        browserName: 'firefox'
    }
    onPrepare: () ->
        global.select = global.by        
        global.param = common.param
}