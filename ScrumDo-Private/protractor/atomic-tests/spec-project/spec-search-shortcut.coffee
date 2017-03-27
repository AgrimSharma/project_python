util = require("../util")

describe 'Scrumdo' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = "#{param.cardName}_to_filter"
    it 'Should add a card to cell', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    element.all(By.css('#ticketMessage')).get(0).sendKeys(param.storyComment).then ->
                        element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                            return elem.isDisplayed()
                        .click()
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return
    
    it 'Should have project search shortcut', ->
        browser.get param.projectUrl
        browser.driver.actions().sendKeys("s").perform().then ->
            browser.waitForAngular()
            browser.driver.actions().sendKeys(cardName).perform()
            element.all(By.css('button[ng-click="ctrl.filter()"]')).filter (elem) ->
                return elem.isDisplayed()
            .click()
            return
        browser.getAllWindowHandles().then (handles) ->
            browser.driver.switchTo().window(handles[1])
            return
        cards = element.all(By.css('.kanban-story-list li.cards'))
        expect(cards.count()).toEqual(1)
        
        browser.getAllWindowHandles().then (handles) ->
            browser.driver.switchTo().window(handles[1])
            browser.driver.close()
            browser.driver.switchTo().window(handles[0])
            return
        return
    return