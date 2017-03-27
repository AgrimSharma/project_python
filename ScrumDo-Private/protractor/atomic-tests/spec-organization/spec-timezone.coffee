util = require("../util")
StoryEditWindow = require("../../pageobjects/storyeditwindow.coffee")
describe 'Scrumdo Timezone' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);

    cardName = param.cardName
    cardTime = ''
    cardTzTime = ''
    story = new StoryEditWindow(param.hostName)
    it 'Should set Timezone to UTC: +00:00', ->
        browser.get param.orgEditUrl
        # first set org timezone to UTC: +00:00
        element(By.css('#id_timezone')).element(By.cssContainingText('option', 'Africa/Accra')).click().then ->
            element(By.buttonText('Update Organization')).click()

        #now add card a card with timezone UTC: +00:00
        browser.get param.projectUrl
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                    story.switchToTab(2).then ->
                        element.all(By.css('#ticketMessage')).get(0).sendKeys(param.storyComment).then ->
                            element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                                return elem.isDisplayed()
                            .click()
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true

        browser.get param.dashboardUrl
        element.all(By.css('.scrumdo-overview-logs')).first().element(By.css('.scrumdo-overview-time')).getText().then (text) ->
            cardTime = text
        return

    it 'Should set Timezone to UTC: +5:30', ->
        browser.get param.orgEditUrl
        # first set org timezone to UTC: +5:30
        element(By.css('#id_timezone')).element(By.cssContainingText('option', 'Asia/Kolkata')).click().then ->
            element(By.buttonText('Update Organization')).click()

        # now check the time log on dashboard
        browser.get param.dashboardUrl
        element.all(By.css('.scrumdo-overview-logs')).first().element(By.css('.scrumdo-overview-time')).getText().then (text) ->
            cardTzTime = text
        .then ->
            cardTimeNew = moment("#{cardTime.slice(0,-2)} #{cardTime.slice(-2)}", 'h:mm A').add(330, "minutes").format('h:mm A')
            cardTzTimeNew = moment("#{cardTzTime.slice(0,-2)} #{cardTzTime.slice(-2)}", 'h:mm A').format('h:mm A')
            expect(cardTzTimeNew).toEqual cardTzTimeNew
            cardTime = cardTzTime
        return

    it 'Should set Timezone to UTC: +10:00', ->
        browser.get param.orgEditUrl
        # first set org timezone to UTC: +10:00
        element(By.css('#id_timezone')).element(By.cssContainingText('option', 'Australia/Sydney')).click().then ->
            element(By.buttonText('Update Organization')).click()

        # now check the time log on dashboard
        browser.get param.dashboardUrl
        element.all(By.css('.scrumdo-overview-logs')).first().element(By.css('.scrumdo-overview-time')).getText().then (text) ->
            cardTzTime = text
        .then ->
            cardTimeNew = moment("#{cardTime.slice(0,-2)} #{cardTime.slice(-2)}", 'h:mm A').add(600, "minutes").format('h:mm A')
            cardTzTimeNew = moment("#{cardTzTime.slice(0,-2)} #{cardTzTime.slice(-2)}", 'h:mm A').format('h:mm A')
            expect(cardTzTimeNew).toEqual cardTzTimeNew
            cardTime = cardTzTime
        return

    return
