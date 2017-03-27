util = require('../util')
describe 'Scrumdo attachment from dropbox', ->

    afterEach ->
        util.capture(jasmine.getEnv().currentSpec);
        
  
    it 'Should Archive all cards in a cell', ->
        browser.get param.projectUrl
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(4).click().then ->
                element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.css('.kanban-story-list li')).isPresent()).toBe false
        return
  
    cardName = param.cardName
  
    it 'Should attached a file', ->
        browser.ignoreSynchronization = true
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then -> browser.sleep(3000).then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then -> browser.sleep(3000).then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then -> browser.sleep(3000).then ->
                    element(By.css('input[value="Attach File"]')).click().then -> browser.sleep(3000).then ->
                        element.all(By.css('.nav-link>uib-tab-heading')).get(1).click().then -> browser.sleep(3000).then ->
                            element(By.css('.dropbox-dropin-btn')).click().then -> browser.sleep(3000).then ->
                
                            browser.getAllWindowHandles().then (handles) ->
                                browser.switchTo().window(handles[1]).then ->
                                    element(By.css('input[name="login_email"]')).sendKeys('jatin@codegenesys.com')
                                    element(By.css('input[name="login_password"]')).sendKeys('sachin2727').then -> browser.sleep(3000).then ->
                                            element(By.xpath('(//button[@type="submit"])[1]')).click().then -> browser.sleep(10000).then -> element(By.css('input[type="text"]')).sendKeys('scrumDo').then -> browser.sleep(5000).then -> element(By.xpath('//span[contains(text(),"scrumDo")]')).click().then -> browser.sleep(5000).then -> element(By.css('#select-btn')).click().then -> browser.sleep(5000).then -> browser.getAllWindowHandles().then (handles) -> browser.switchTo().window(handles[0]).then -> element(By.buttonText('OK')).click().then -> browser.sleep(3000).then -> element(By.xpath('(//button[@type="button"])[3]')).click().then -> browser.sleep(3000)
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).isPresent()).toBe true
        return