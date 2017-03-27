describe 'scrumdo login', () ->
  it 'should log in', () ->
    driver = protractor.getInstance().driver;
    driver.get "#{url}/account/login/"

    findByName = (name) ->
      return driver.findElement(protractor.By.name(name));
    
    findByName("username").sendKeys("mhughes")
    findByName("password").sendKeys("klug")
    findByName("loginButton").click()
