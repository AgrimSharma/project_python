common = require "../data/data"
moment = require "moment"



exports.config = {
  seleniumAddress: common.param.seleniumAddress
  getPageTimeout: 45000
  allScriptsTimeout: 60000
  jasmineNodeOpts: {
      defaultTimeoutInterval: 60000
      showColors: true
      isVerbose: true
      realtimeFailure: true
  }
  specs: [      
    '../atomic-tests/spec-login.coffee'
    '../atomic-tests/spec-organization/spec-setup-new.coffee'
    '../atomic-tests/spec-project/spec-add.coffee'
    '../atomic-tests/spec-intercom-close.coffee'
    # '../atomic-tests/spec-reports/spec-favorite-report.coffee'
    # '../atomic-tests/spec-reports/spec-burndown-report.coffee'
    # '../atomic-tests/spec-reports/spec-backlog-report.coffee'
    # '../atomic-tests/spec-reports/spec-reports-menu.coffee'
    # '../atomic-tests/spec-reports/spec-report-cfd.coffee'
    # '../atomic-tests/spec-report/spec-report.coffee' 
    # '../atomic-tests/spec-reports/spec-report-cfd.coffee' // need to update
    # '../atomic-tests/spec-report/spec-report.coffee' // need to update
    # '../atomic-tests/spec-reports/spec-report-commulative.coffee' 
    # '../atomic-tests/spec-reports/spec-report-leadtime.coffee' 
    # '../atomic-tests/spec-project/spec-delete.coffee'
    '../atomic-tests/spec-logout.coffee'
    '../atomic-tests/spec-fail-login.coffee'
    '../atomic-tests/spec-login.coffee'
    '../atomic-tests/spec-organization/spec-delete.coffee'
  ]

  capabilities: {
    browserName: 'chrome'
  }

  onPrepare: () ->
    global.select = global.by
    global.disableAnimateCss = common.disableAnimateCss
    global.param = common.param
    global.param.projectSlug = "project-#{common.param.timeCode}"
    global.param.orgSlug = "automated-org-#{common.param.timeCode}"
    global.param.dashboardUrl = "#{common.param.hostName}/organization/automated-org-#{common.param.timeCode}/dashboard"
    global.param.projectUrl = "#{common.param.hostName}/projects/project-#{common.param.timeCode}/board#/view"
    global.param.rewindUrl = "#{common.param.hostName}/projects/project-#{common.param.timeCode}/debug/rewind"
    global.param.reportUrl = "#{common.param.hostName}/projects/project-#{common.param.timeCode}/#/reports/cfd"
    global.param.planningUrl = "#{common.param.hostName}/projects/project-#{common.param.timeCode}/planning"
    global.param.orgPlanningUrl = "#{common.param.hostName}/organization/automated-org-#{common.param.timeCode}/planning"
    global.param.projectMilestoneUrl = "#{common.param.hostName}/projects/project-#{common.param.timeCode}/milestones/#/list"
    global.param.orgEditUrl = "#{common.param.hostName}/organization/automated-org-#{common.param.timeCode}/edit"
    global.moment = moment
    console.log global.param

    global.param.projectName = global.projectName = "Project #{common.param.timeCode}"
        
    global.newUser =
        fullName: 'Report User'
        newUserName: "reporttestuser"
        password: 'reporttestuser@123'
        email: 'badaddress@scrumdo.com'

    browser.driver.manage().window().setSize(1200, 1000);

    common.disableAnimate()
}
