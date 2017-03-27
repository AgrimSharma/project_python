class LoginPage
    constructor: (baseUrl) ->
        @loginUrl = "#{baseUrl}/account/login/"
        @loginLink = element(By.id('loginLink'))
        @dropdownMenu = element(By.css('.nav-settings .dropdown-menu li'))

    get: ->
        browser.get(@loginUrl)
        return @

    setUsername: (username) ->
        element(By.name('username')).sendKeys username

    setPassword: (password) ->
        element(By.name('password')).sendKeys password

    clickLogin: ->
        return element.all(By.buttonText('Log In')).click()

module.exports = LoginPage