common = require "../data/data"

exports.config = {
  seleniumAddress: common.param.seleniumAddress
  getPageTimeout: 300000
  jasmineNodeOpts: {
      defaultTimeoutInterval: 300000
      showColors: true
      isVerbose: true
      realtimeFailure: true
  }
  specs: [
    '../atomic-tests/spec-login.coffee',
    '../atomic-tests/spec-portfolio/spec-portfolio-project.coffee',
    '../atomic-tests/spec-logout.coffee'
  ]
  capabilities: {
    browserName: 'chrome'
  }
  onPrepare: () ->
        global.select = global.by
        global.disableAnimateCss = common.disableAnimateCss
        global.param = common.param
        global.newUser =
            newUserName: "auto"
            password: 'auto'

        common.disableAnimate()
}
