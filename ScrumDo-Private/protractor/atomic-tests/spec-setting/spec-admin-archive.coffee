util = require("../util")

describe 'Scrumdo Admin access', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    newOrgName = "Org#{param.timeCode}"
    newProjectName = "Automated Proj #{param.timeCode}"
	
    it 'Should verify Admin setting page', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Admin Options")]')).click().then ->
            return
		
        browser.waitForAngular()
        expect(element(By.xpath('//h2[contains(text(), "Archive Workspace")]')).isPresent()).toBe true
        return
		
    it 'Should archive whole project', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Admin Options")]')).click().then ->
                element(By.xpath('.//*[@id="archiveFormButton"]')).click().then ->
                    element(By.css('button[ng-click="ctrl.ok()"]')).click().then -> browser.sleep(3000).then ->
                        element(By.xpath('//input[@value="Reactivate Workspace"]')).click().then ->
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.css('.fa.fa-gears')).isPresent()).toBe true
        return
		
    it 'should update project', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Admin Options")]')).click().then ->
                element(By.css('button[ng-click="settingsCtrl.updateIndexes()"]')).click().then ->
                return
            return
        browser.waitForAngular()
        expect(element(By.css('.fa.fa-gears')).isPresent()).toBe true
        return
		
    it 'should reset burn-up data', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Admin Options")]')).click().then ->
                element.all(By.css('.scrumdo-btn.secondary')).get(3).click().then ->
                return
            return
        browser.waitForAngular()
        expect(element(By.css('.fa.fa-gears')).isPresent()).toBe true
        return
		
    it 'should rebuild a report', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Admin Options")]')).click().then ->
                element.all(By.css('.scrumdo-btn.secondary')).get(2).click().then ->
                return
            return
        browser.waitForAngular()
        expect(element(By.css('.fa.fa-gears')).isPresent()).toBe true
        return
		
    it 'should create project/workspace', ->
        browser.get param.dashboardUrl
		
        browser.sleep(3000)
        element(By.css('a[href="#/projects"]')).click().then ->browser.sleep(3000).then ->
            element.all(By.css('.scrumdo-btn.secondary.text-left')).get(0).click().then ->browser.sleep(3000).then ->
                element(By.css('input[id="id_name"]')).sendKeys(newProjectName).then ->
                    element(By.buttonText("Create New Workspace")).click().then -> browser.sleep(3000).then ->
                        element(By.buttonText("Use Default Board")).click().then ->
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//span[contains(text(),"' + newProjectName + '")]')).isPresent()).toBe true
        return
		
    it 'Should delete a workspace', ->
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Admin Options")]')).click().then ->
                element(By.css('.scrumdo-btn.tertiary')).click().then ->
                    element(By.css('button[ng-click="ctrl.ok()"]')).click().then ->
                        element(By.css('input[ng-model="ctrl.projectname"]')).sendKeys(newProjectName).then -> browser.sleep(3000).then ->
                            element(By.css('button[ng-click="ctrl.confirmDeleteProject()"]')).click().then ->
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        browser.sleep(5000)
        expect(element(By.xpath('//a[@href="/subscription/register"]')).isPresent()).toBe true
        return
		
    it 'should create new organization', ->
        browser.get param.projectUrl
		
        element(By.css('.nav-settings-link')).click().then -> browser.sleep(2000).then ->
            element(By.xpath('//a[@href="/?force_org_view=1"]')).click().then -> element(By.xpath('//a[@href="/subscription/register"]')).click().then ->
                element(By.name('organization_name')).sendKeys(newOrgName).then ->
                    element(By.css('button[ng-click="ctrl.step2()"]')).click().then ->
                        element(By.name('project_name')).sendKeys(newProjectName).then ->
                            element(By.id('createFirstProjectButton')).click().then ->
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//a[contains(text(),"' + newOrgName + '")]')).isPresent()).toBe true
        return

    it 'should move organization', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[contains(text(),"Admin Options")]')).click().then ->
                element(By.css('select[ng-model="orgtomove"]')).all(By.xpath('//option[contains(text(),"' + newOrgName + '")]')).click().then ->
                    element.all(By.css('.scrumdo-btn.secondary')).get(1).click().then ->
                        element(By.css('button[ng-click="ctrl.ok()"]')).click().then -> browser.sleep(3000).then ->
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//a[contains(text(),"' + newOrgName + '")]')).isPresent()).toBe true
        return
