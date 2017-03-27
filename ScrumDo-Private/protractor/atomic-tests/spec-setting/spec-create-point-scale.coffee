util = require("../util")

describe 'Scrumdo point scale (Add, Edit,Delete)', ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec);
	
    it 'Should project name', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        browser.waitForAngular()
        expect(element(By.css('input[ng-model="ctrl.project.name"]')).isPresent()).toBe true
        return

    it 'Should select point scale', ->
        browser.get param.projectUrl
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element.all(By.xpath('//input[@ng-model="ctrl.project.point_scale_type"]')).get(0).click().then ->
                element(By.css('button[ng-click="ctrl.save()"]')).click()
                return
            return
            browser.waitForAngular()
            expect(element.all(By.xpath('//input[@ng-model="ctrl.project.point_scale_type"]')).get(0).isPresent()).toBe true
            return

    it 'Should add point scale', ->
        browser.get param.projectUrl
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.xpath('//a[@ng-click="ctrl.addPointScale()"]')).click().then ->
                element.all(By.xpath('//input[@name="point-value"]')).get(1).clear().sendKeys('1').then ->
                    element.all(By.xpath('//input[@name="point-value"]')).get(2).clear().sendKeys('1.1').then ->
                        element.all(By.xpath('//input[@name="point-value"]')).get(3).clear().sendKeys('1.2').then ->
                            element.all(By.xpath('//input[@name="point-value"]')).get(4).clear().sendKeys('1.3').then ->
                                element.all(By.xpath('//input[@name="point-value"]')).get(5).clear().sendKeys('1.4').then ->
                                    element.all(By.xpath('//input[@name="point-value"]')).get(6).clear().sendKeys('1.5').then ->
                                        element.all(By.xpath('//input[@name="point-value"]')).get(7).clear().sendKeys('1.6').then ->
                                            element.all(By.xpath('//input[@name="point-value"]')).get(8).clear().sendKeys('2.5').then ->
                                                element.all(By.xpath('//input[@name="point-value"]')).get(9).clear().sendKeys('50').then ->
                                                    element.all(By.xpath('//input[@name="point-value"]')).get(10).clear().sendKeys('80').then ->
                                                        element.all(By.xpath('//input[@name="point-value"]')).get(11).clear().sendKeys('100').then ->
                                                            element.all(By.xpath('//input[@name="point-value"]')).get(12).clear().sendKeys('end').then ->
                                                                element(By.css('button[ng-click="ctrl.savePointScale(scale)"]')).click().then ->
                                                                return
                                                            return
                                                        return
                                                    return
                                                return
                                            return
                                        return
                                    return
                                return
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.css('button[ng-click="ctrl.editPointScale(scale)"]')).isPresent()).toBe true
        return

    it 'Should edit point scale', ->

        element(By.css('button[ng-click="ctrl.editPointScale(scale)"]')).click().then ->
            element.all(By.xpath('//input[@name="point-value"]')).get(1).clear().sendKeys('1').then ->
                element.all(By.xpath('//input[@name="point-value"]')).get(2).clear().sendKeys('10').then ->
                    element.all(By.xpath('//input[@name="point-value"]')).get(3).clear().sendKeys('20').then ->
                        element.all(By.xpath('//input[@name="point-value"]')).get(4).clear().sendKeys('30').then ->
                            element.all(By.xpath('//input[@name="point-value"]')).get(5).clear().sendKeys('40').then ->
                                element.all(By.xpath('//input[@name="point-value"]')).get(6).clear().sendKeys('50').then ->
                                    element.all(By.xpath('//input[@name="point-value"]')).get(7).clear().sendKeys('60').then ->
                                        element.all(By.xpath('//input[@name="point-value"]')).get(8).clear().sendKeys('70').then ->
                                            element.all(By.xpath('//input[@name="point-value"]')).get(9).clear().sendKeys('80').then ->
                                                element.all(By.xpath('//input[@name="point-value"]')).get(10).clear().sendKeys('90').then ->
                                                    element.all(By.xpath('//input[@name="point-value"]')).get(11).clear().sendKeys('100').then ->
                                                        element.all(By.xpath('//input[@name="point-value"]')).get(12).clear().sendKeys('max').then ->
                                                            element(By.css('button[ng-click="ctrl.savePointScale(scale)"]')).click().then ->
                                                            return
                                                        return
                                                    return
                                                return
                                            return
                                        return
                                    return
                                return
                            return
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element(By.css('button[ng-click="ctrl.editPointScale(scale)"]')).isPresent()).toBe true
        return
	
    it 'Should select point scale', ->
        browser.get param.projectUrl
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
        element.all(By.xpath('//input[@ng-model="ctrl.project.point_scale_type"]')).get(0).click().then ->
            element(By.css('button[ng-click="ctrl.save()"]')).click()
            return
        browser.waitForAngular()
        expect(element.all(By.xpath('//input[@ng-model="ctrl.project.point_scale_type"]')).get(0).isPresent()).toBe true
        return

    it 'Should delete point scale', ->
        browser.get param.projectUrl
		
        element(By.css('.fa.fa-gears')).click().then -> browser.sleep(3000).then ->
            element(By.css('button[ng-click="ctrl.deletePointScale(scale)"]')).click().then ->
                element(By.css('button[ng-click="ctrl.ok()"]')).click().then ->
                return
            return
        browser.waitForAngular()
        expect(element(By.xpath('//a[@ng-click="ctrl.addPointScale()"]')).isPresent()).toBe true
        return