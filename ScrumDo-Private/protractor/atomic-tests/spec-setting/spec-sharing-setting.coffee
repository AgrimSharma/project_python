util = require("../util")
#Data = require("../data/data.coffee")

describe 'Scrumdo Sharing settings', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
		
    it 'Should verify sharing setting page', ->
        browser.get param.sharingUrl
		
        browser.waitForAngular()
        expect(element(By.xpath('//h2[contains(text(),"Sharing")]')).isPresent()).toBe true
        return
	
    it 'should share iteration', ->
		
        element(By.css('select[ng-model="sharectrl.selectedIteration"]')).all(By.tagName('option')).get(1).click().then ->
            element(By.css('.scrumdo-btn.secondary')).click().then ->
                element.all(By.css('.col-md-10>a')).get(0).click().then -> browser.getAllWindowHandles().then (handles) -> browser.switchTo().window(handles[1]).then ->
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//a[contains(text(),"Log In")]')).isPresent()).toBe true
        return
        str = browser.getCurrentUrl
        res = str.replace("https://app.scrumdo.com", "https://qa.scrumdo.com").then ->
            browser.get res
            browser.sleep(5000)
		
    it 'Should share project', ->
        browser.get param.sharingUrl
        browser.sleep(5000)
        element(By.name('username')).sendKeys("jayTest").then ->
            element(By.name('password')).sendKeys("sachin2727").then ->
                element.all(By.buttonText('Log In')).click()
                return
            return
        browser.get param.sharingUrl
        browser.sleep(2000).then ->	
		
        if element(By.css('input[id="SharedProject"]')).isSelected()
            element.all(By.css('.col-sm-5>p>a')).click()
            return
        else
            element(By.css('input[id="SharedProject"]')).click().then -> browser.sleep(10000).then ->
                element.all(By.css('.col-sm-5>p>a')).click().then -> browser.getAllWindowHandles().then (handles) -> browser.switchTo().window(handles[1]).then ->
                return
        browser.waitForAngular()
        expect(element(By.xpath('//a[contains(text(),"Log In")]')).isPresent()).toBe true
        return
		
    it 'Should share all cards', ->
        browser.get param.sharingUrl
        browser.sleep(5000)
        element(By.name('username')).sendKeys("jayTest").then ->
            element(By.name('password')).sendKeys("sachin2727").then ->
                element.all(By.buttonText('Log In')).click()
                return
            return
        browser.get param.sharingUrl
        browser.sleep(2000).then ->	
		
        if element.all(By.css('.ng-pristine.ng-untouched.ng-valid.ng-empty')).get(1).isSelected()
            element.all(By.css('.col-md-10>a')).get(0).click()
            return
        else
            element.all(By.css('.ng-pristine.ng-untouched.ng-valid.ng-empty')).get(1).click().then -> browser.sleep(5000).then ->
                element.all(By.css('.col-md-10>a')).get(0).click().then ->browser.getAllWindowHandles().then (handles) -> browser.switchTo().window(handles[1]).then ->
                return
        browser.waitForAngular()
        expect(element(By.xpath('//a[contains(text(),"Log In")]')).isPresent()).toBe true
        return
		
    it 'should verify cards field', ->
        browser.get param.sharingUrl
		
        element.all(By.css('.scrumdo-backlog-form.navigation>label>span')).get(1).click().then ->
            element.all(By.css('.scrumdo-btn.secondary')).get(1).click().then ->
                element.all(By.css('.col-md-10>a')).get(0).click().then ->browser.getAllWindowHandles().then (handles) -> browser.switchTo().window(handles[1]).then ->
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//a[contains(text(),"Log In")]')).isPresent()).toBe true
        return
		
    it 'should verify default tag', ->
        browser.get param.sharingUrl
		
        element.all(By.css('.col-md-10>a')).get(0).click().then ->browser.getAllWindowHandles().then (handles) -> browser.switchTo().window(handles[1]).then ->
        browser.waitForAngular()
        expect(element(By.xpath('//a[contains(text(),"Log In")]')).isPresent()).toBe true
        return