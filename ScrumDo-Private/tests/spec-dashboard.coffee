describe 'scrumdo dashboard', () ->
    it 'should show the dashboard', () ->    
        browser.get "#{url}/organization/scrumdo/dashboard"
        expect(browser.getTitle()).toEqual("ScrumDo ScrumDo LLC")

    it 'should show the news items', () ->
        newslist = element.all By.repeater('newsDay in news')
        expect(newslist.count()).toBeGreaterThan(0)    

    it 'should show the my stories list', () ->        
        myprojects = element.all By.repeater('p in myStories')
        expect(myprojects.count()).toBeGreaterThan(0)

    it 'should show the project list', () ->
        element(By.id('projectsLink')).click()
        projectlist = element.all(By.repeater('project in projects'))
        expect(projectlist.count()).toBeGreaterThan(0)
    
