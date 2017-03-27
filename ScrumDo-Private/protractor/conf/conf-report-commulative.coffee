common = require "../data/data"
#moment = require "moment"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    getPageTimeout: 60000
    allScriptsTimeout: 80000
    jasmineNodeOpts: {
      defaultTimeoutInterval: 60000
      showColors: true
      isVerbose: true
      realtimeFailure: true
  }
	
    specs: [
        '../atomic-tests/spec-reports/spec-report-commulative.coffee',
    ]
    capabilities: {
        browserName: 'chrome'
    }
    onPrepare: () ->
        global.select = global.by
        global.disableAnimateCss = common.disableAnimateCss
        global.param = common.param
 
        browser.driver.manage().window().setSize(1200, 1000);
        common.disableAnimate() 
}