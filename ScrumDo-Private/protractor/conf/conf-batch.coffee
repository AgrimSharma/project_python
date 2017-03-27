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
    '../atomic-tests/spec-registration.coffee',
    '../atomic-tests/spec-project/spec-add.coffee',
    '../atomic-tests/spec-intercom-close.coffee',
    '../atomic-tests/spec-cards/spec-custom-filters.coffee',
    '../atomic-tests/spec-login.coffee',
    #'../atomic-tests/spec-cards/spec-card-issue.coffee', 
    '../atomic-tests/spec-cards/spec-add-details.coffee',
    '../atomic-tests/spec-cards/spec-add-label.coffee', 
    '../atomic-tests/spec-cards/spec-add-multilabel.coffee', 
    '../atomic-tests/spec-cards/Spec-card-assignee.coffee', 
    #'../atomic-tests/spec-cards/spec-card-attachment.coffee', 
    #'../atomic-tests/spec-cards/spec-card-epic.coffee', 
    '../atomic-tests/spec-cards/spec-card-history.coffee', 
    #'../atomic-tests/spec-cards/spec-card-new-task.coffee', 
    '../atomic-tests/spec-cards/spec-card-playpoker.coffee', 
    '../atomic-tests/spec-cards/spec-card-duplicate.coffee', 
    '../atomic-tests/spec-cards/spec-card-fields.coffee',
    '../atomic-tests/spec-cards/spec-card-save.coffee',
    '../atomic-tests/spec-cards/spec-card-close.coffee',
    '../atomic-tests/spec-cards/spec-card-permalink.coffee',
    '../atomic-tests/spec-cards/spec-comment-update.coffee', 
    '../atomic-tests/spec-cards/spec-edit-card.coffee', 
    #'../atomic-tests/spec-cards/spec-epic-icon.coffee', 
    #'../atomic-tests/spec-cards/spec-file-attachment-local.coffee', 
    '../atomic-tests/spec-cards/spec-permalink-minimize-card.coffee', 
    '../atomic-tests/spec-cards/spec-add-card.coffee',
    '../atomic-tests/spec-cards/spec-due-date-card.coffee',
    '../atomic-tests/spec-cards/spec-add-time.coffee',
    '../atomic-tests/spec-cards/spec-track-time.coffee',
    '../atomic-tests/spec-cards/spec-add-tag.coffee',
    #'../atomic-tests/spec-cards/spec-card-blocked.coffee',
    '../atomic-tests/spec-cards/spec-card-minimize.coffee',
    '../atomic-tests/spec-project/spec-tags.coffee',
    '../atomic-tests/spec-project/spec-custom-point-scale.coffee',
    '../atomic-tests/spec-project/spec-card-wip.coffee',
    '../atomic-tests/spec-project/spec-point-wip.coffee',
    '../atomic-tests/spec-cards/spec-comment-card.coffee',
    '../atomic-tests/spec-cards/spec-archive-cards.coffee',
    '../atomic-tests/spec-cards/spec-business-value.coffee',
    '../atomic-tests/spec-cards/spec-move-card.coffee',
    '../atomic-tests/spec-cards/spec-move-multiple.coffee',
    # TODO: '../atomic-tests/spec-cards/spec-move-iteration.coffee',
    '../atomic-tests/spec-report/spec-report.coffee'
    '../atomic-tests/spec-cards/spec-board-sort.coffee',
    '../atomic-tests/spec-cards/spec-iteration-sort.coffee',
    '../atomic-tests/spec-iteration/spec-export.coffee',
    #'../atomic-tests/spec-cards/spec-delete-card.coffee',  - Don't need this one because add-card does it too
    '../atomic-tests/spec-backlog/spec.coffee',
    #'../atomic-tests/spec-iteration/spec-add.coffee',
    # TODO: '../atomic-tests/spec-cards/spec-move-project.coffee',
    # TODO: '../atomic-tests/spec-iteration/spec-edit-time.coffee',
    # TODO: '../atomic-tests/spec-iteration/spec-delete.coffee',
    # TODO: '../atomic-tests/spec-iteration/spec-show-hide-all.coffee',

    # These two are being replaced by portfolios:
    #'../atomic-tests/spec-planning/spec-release.coffee',
    #'../atomic-tests/spec-planning/spec-valuestream.coffee',
	
    # Setting script
    '../atomic-tests/spec-setting/spec-project-name.coffee',
    '../atomic-tests/spec-setting/spec-point-scale.coffee',
    '../atomic-tests/spec-setting/spec-create-point-scale.coffee',
    '../atomic-tests/spec-setting/spec-rendor.coffee',
    '../atomic-tests/spec-setting/spec-card-aging.coffee',
    '../atomic-tests/spec-setting/spec-velocity-calculation.coffee',
    '../atomic-tests/spec-setting/spec-project-category.coffee',
    '../atomic-tests/spec-setting/spec-add-label.coffee',
    #'../atomic-tests/spec-setting/spec-add-tag.coffee',
    #'../atomic-tests/spec-setting/spec-board-editor.coffee', #script issue (mouse action)
    '../atomic-tests/spec-setting/spec-card-setting.coffee',
    #'../atomic-tests/spec-setting/spec-custom-field.coffee', #Custom field is not present on the site
    #'../atomic-tests/spec-setting/spec-report-profile.coffee',
    #'../atomic-tests/spec-setting/spec-sharing-setting.coffee', #broken Url
    '../atomic-tests/spec-setting/spec-task-status.coffee',
    #'../atomic-tests/spec-setting/spec-default-cell.coffee', #Options are not present in default cell dropdown
    #'../atomic-tests/spec-setting/spec-admin-archive.coffee', 
	
    '../atomic-tests/spec-context-menu/spec-context-menu.coffee',
    '../atomic-tests/spec-organization/spec-timezone.coffee',
    '../atomic-tests/spec-cards/spec-stress-add-card.coffee',
    '../atomic-tests/spec-project/spec-export.coffee',
    '../atomic-tests/spec-project/spec-delete.coffee',
    '../atomic-tests/spec-login.coffee'
    '../atomic-tests/spec-logout.coffee'
    '../atomic-tests/spec-fail-login.coffee'
    '../atomic-tests/spec-login.coffee'
    '../atomic-tests/spec-organization/spec-delete.coffee',
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
    global.param.planningUrl = "#{common.param.hostName}/projects/project-#{common.param.timeCode}/planning"
    global.param.orgPlanningUrl = "#{common.param.hostName}/organization/automated-org-#{common.param.timeCode}/planning"
    global.param.projectMilestoneUrl = "#{common.param.hostName}/projects/project-#{common.param.timeCode}/milestones/#/list"
    global.param.orgEditUrl = "#{common.param.hostName}/organization/automated-org-#{common.param.timeCode}/edit"
    global.moment = moment
    console.log global.param

    global.param.projectName = global.projectName = "Project #{common.param.timeCode}"
    
    global.newUser =
        fullName: 'Automated Test'
        newUserName: "automated-#{common.param.timeCode}"
        password: 'klug'
        email: 'badaddress@scrumdo.com'
        
    browser.driver.manage().window().setSize(1200, 1000);
    common.disableAnimate() 
}
