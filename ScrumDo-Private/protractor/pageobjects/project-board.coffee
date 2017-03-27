class ProjectBoard
    constructor: (baseUrl, projectSlug, orgSlug) ->
        @boardUrl = "#{baseUrl}/projects/#{projectSlug}/#defaultboard"
        @dashboardUrl = "#{baseUrl}/organization/#{orgSlug}/dashboard"
        @reportUrl = "#{baseUrl}/projects/#{projectSlug}/#/reports/cfd"
        @settingsProjectUrl = "#{baseUrl}/projects/#{projectSlug}/board#/settings/settings/project"
        @settingsBoardEditorUrl = "#{baseUrl}/projects/#{projectSlug}/board#/settings/settings/board"
        @settingsTagsUrl = "#{baseUrl}/projects/#{projectSlug}/board#/settings/settings/labeltags"
        @settingsCardUrl = "#{baseUrl}/projects/#{projectSlug}/board#/settings/settings/card"
        @cardFirstCell = element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.css('.kanban-story-list li'))
        @sortDropdown = element.all(By.css('.board-sub-nav .action-5 button[uib-tooltip="Sort Cards"]')).get(0)
        @saveButton = element.all(By.buttonText('Save'))
        @backlogViewSelect = element(By.css('select[ng-change="ctrl.viewChange()"]'))
        @newPointScaleBtn = element(By.css('.custom-point-scales a[ng-click="ctrl.addPointScale()"]'))

    get: ->
        browser.get(@boardUrl)
        return @
    
    gotoCardSetting: ->
        browser.get(@settingsCardUrl)
        return @
    
    gotoTagSetting: ->
        browser.get(@settingsTagsUrl)
        return @
    
    gotoSettings: (section) =>
        switch section
            when "project" then url = @settingsProjectUrl
            when "board" then url = @settingsBoardEditorUrl
            
        browser.get(url)
        return @
            
    gotoReports: ->
        
        browser.get(@reportUrl)
        return @            

    clickCellActions: (index) ->
        return element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(index).element(By.tagName('button')).click()
    
    archiveAllCardsInCell: (index)->
        return element.all(By.css('.scrumdo-column-title')).get(index).all(By.css('.dropdown-menu li a')).get(4).click()
    
    clickAddCardInCell: (index)->
        return element.all(By.css('.scrumdo-column-title')).get(index).all(By.css('.dropdown-menu li a')).get(0).click()
    
    confirmOk: ->
        return  element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
    
    getCardInCell: (call, card) ->
        return element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(call).all(By.css("li.cards")).get(card)
    
    getTag: (index) ->
        return element.all(By.css("span.tag")).get(index)
    
    getAllTags: ->
        return element.all(By.css("span.tag"))
    
    getTagDeleteButton: (index) ->
        return element.all(By.css('button[ng-click="ctrl.deleteTag(tag)"]')).get(index)
    
    getTagEditButton: (index) ->
        return element.all(By.css('button[ng-click="ctrl.editTag(tag)"]')).get(index)
    
    getTagInputBox: (index) ->
        return element.all(By.css('input[sd-enter="ctrl.saveTag(tag)"')).get(index)
    
    saveTag: (index) ->
        return element.all(By.css('button[ng-click="ctrl.saveTag(tag)"')).get(index).click()
    
    addNewTag: (tag) ->
        return  element(By.css('a[ng-click="ctrl.addTag($event)"]')).click().then =>
                    @getTagInputBox(0).sendKeys(tag).then =>
                        @saveTag(0)
    
    togglePriorityView: ->
        return element.all(By.css('.board-sub-nav .action-5 button[uib-tooltip="Toggle Priority/WSJF Card View"]')).get(0).click()
    
    sortCardBy: (option) =>
        switch option
            when "points" then index = 3
            when "business_value" then index = 4
            when "estimate_time" then index = 5
            when "due_date" then index = 8
            when "wsjf" then index = 9
        return  @sortDropdown.click().then ->
                    element.all(By.css('.board-sub-nav .action-5 ul li')).get(index).click()
            
    getCardByNameInCell: (index, cardName) ->
        return element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(index).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]'))
    
    editCardInCell: (cell, card) =>
        return @getCardInCell(cell, card).element(By.css('span[ng-click="ctrl.onEdit()"]')).click()
    
    saveSettings: =>
        return @saveButton.click()
    
    toggleBacklog: ->
        return element.all(By.css('.backlog-pull')).get(0).click()
    
    toggleBacklogView: (type) =>
        switch type
            when "list" then index = 0
            when "epic" then index = 1
            when "label" then index = 2
            
        return @selectDropdownbyNum(@backlogViewSelect, index)
            
    selectDropdownbyNum: ( select, index = 0 ) ->
        return  select.all(By.tagName('option')).then (options) ->
                    return options[index].click()
        browser.sleep(1000)
        
    editBoardCell: (index) ->
        return element.all(By.css('sd-board-preview g')).get(1).all(By.css("g")).get(index).click()
    
    setCardWip: (limit, type='min', cell=0) ->
        if type=='min'
            return element(By.model("editingCell.minWipLimit")).clear().sendKeys(limit)
        else
            return element(By.model("editingCell.wipLimit")).clear().sendKeys(limit)
        
    setPointWip: (limit, type='min', cell=0) ->
        if type=='min'
            return element(By.model("editingCell.minPointLimit")).clear().sendKeys(limit)
        else
            return element(By.model("editingCell.pointLimit")).clear().sendKeys(limit)
    
    saveBoardCell: ->
        return element(By.css('form[name="cellForm"] button[ng-click="ctrl.onSave()"]')).click()
    
    cellWipHolder: (index) ->
        return element.all(By.css('.scrumdo-column-title')).get(index).element(By.css(".wip-limit-holder"))
    
    cellMinWip: (index) ->
        return element.all(By.css('.scrumdo-column-title .wip-limit-holder')).get(index).all(By.css(".wip-min small")).get(0).text()
    
    cellMaxWip: (index) ->
        return element.all(By.css('.scrumdo-column-title .wip-limit-holder')).get(index).all(By.css(".wip-max small")).get(0).text()
    
    cellWipValue: (index) ->
        return element.all(By.css('.scrumdo-column-title .wip-limit-holder')).get(index).all(By.css(".wip-value")).get(0).text()
            
    selectReport: (option) ->
        return element(By.cssContainingText('option', option)).click()

    hoverElement: (elem) ->
        return browser.actions().mouseMove(elem).perform()

    refreshReport: ->
        return element(By.css('button[ng-click="ctrl.refresh()"]')).click()

module.exports = ProjectBoard
