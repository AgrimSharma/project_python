


baseUrl = 'http://localhost:8000'


process.argv.forEach (v) ->
    if v.slice(0, 7) == "--host="
        baseUrl = v.split("=")[1]

console.log "Testing #{baseUrl}"

# baseUrl = 'http://marc.scrumdo.com'
# baseUrl = 'https://app-dev.scrumdo.com'
# baseUrl = 'https://app.scrumdo.com'

timeCode = Math.floor(Date.now() / 1000)

module.exports =
    param:
        seleniumAddress: 'http://localhost:4444/wd/hub'
        hostName: baseUrl
        userName: 'auto'
        password: 'auto'
        cardName: "Story Card-#{Math.floor(Date.now() / 1000)}"
        categoryName: "Scrum-#{Math.floor(Date.now() / 1000)}"
        tagName: "Scrum-#{Math.floor(Date.now() / 1000)}"
        cellName: "Cell-#{Math.floor(Date.now() / 1000)}"
        storySummery: 'This is a Story'
        storyDetails: 'This is details about the story'
        storyComment: 'This is a test comment on story'
        storyTag: 'tag1'
        storyTime: '0:30'
        taskSummery: 'this is a task'
        iterationName: "I#{Math.floor(Date.now() / 1000)}"
        iterationStartDate: '2015-06-10'
        iterationEndDate: '2015-06-21'
        iterationStartDateNew: '2015-06-15'
        iterationEndDateNew: '2015-06-25'
        timeCode: timeCode
        projectSlug: "auto2"
        orgSlug: "auto1"
        releaseName: "Release-#{Math.floor(Date.now() / 1000)}"

        organizationSlug: "auto1",
        projectSlug: "auto2",
        registrationKey: "eeeee764a1c04c15877d796e7b464532",

        dashboardUrl: "#{baseUrl}/organization/auto1/dashboard"
        projectUrl: "#{baseUrl}/projects/auto2/board#/view"
        rewindUrl: "#{baseUrl}/projects/auto2/debug/rewind"
        reportUrl: "#{baseUrl}/projects/auto2/#/reports/cfd"
        projectMilestoneUrl: "#{baseUrl}/projects/auto2/milestones/#/list"
        planningUrl: "#{baseUrl}/projects/auto2/planning"
        orgPlanningUrl: "#{baseUrl}/organization/auto1/planning"
        orgEditUrl: "#{baseUrl}/organization/auto1/edit"
        projectReportUrl: "#{baseUrl}/projects/auto2/reports#/cfd"
        orgSettingUrl: "#{baseUrl}/projects/auto2/#/settings/project"
        adminArchiveUrl: "#{baseUrl}/projects/auto2/#/settings/admin"
        sharingUrl: "#{baseUrl}/projects/auto2/#/settings/sharing"
        tagLabelUrl: "#{baseUrl}/projects/auto2/#/settings/labeltags"
        closeIntercom: () ->
            button = element(By.css('.intercom-sheet-header-close-button'))
            return button.isPresent().then (result) ->
                browser.executeScript('window.Intercom && Intercom(\'shutdown\');');
                if result
                    return button.isDisplayed.then (result) ->
                        button.click()

    disableAnimateCss: () ->
        browser.executeScript('sheet = document.createElement("style");
            sheet.innerHTML = ".modal.fade { opacity: 1; } .modal.fade .modal-dialog, .modal.in .modal-dialog { -webkit-transform: translate(0, 0); -ms-transform: translate(0, 0); transform: translate(0, 0); } .scrumdo-boards-wrapper, .navbar-open, .scrumdo-navigation-sidebar, .scrumdo-backlog-sidebar { -webkit-transition: none; -moz-transition: none; -o-transition: none; transition: none; }";
            document.body.appendChild(sheet);')

    disableAnimate: () ->
        browser.get(baseUrl).then () ->
            browser.executeScript('window.localStorage.setItem("disableanimate", true);');
            browser.executeScript('window.localStorage.setItem("ngStorage-betaOptions", "{\\"textEditor\\":\\"tinymce\\",\\"animations\\":false,\\"dashboard\\":\\"dashboard\\",\\"dropbox\\":\\"enabled\\",\\"portfolio\\":\\"disabled\\"}");');
            browser.executeScript('window.Intercom && window.Intercom(\'shutdown\')');
            browser.executeScript('sheet = document.createElement("style");
            sheet.innerHTML = ".modal.fade { opacity: 1; } .modal.fade .modal-dialog, .modal.in .modal-dialog { -webkit-transform: translate(0, 0); -ms-transform: translate(0, 0); transform: translate(0, 0); } .scrumdo-boards-wrapper, .navbar-open, .scrumdo-navigation-sidebar, .scrumdo-backlog-sidebar { -webkit-transition: none; -moz-transition: none; -o-transition: none; transition: none; }";
            document.body.appendChild(sheet);')

            console.log("Animation disabled")

    enableAnimate: () ->
        browser.executeScript('window.localStorage.clear();');
