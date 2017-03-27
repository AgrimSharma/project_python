class BetaPage
    constructor: (baseUrl) ->
        @betaUrl = "#{baseUrl}/beta"
        @enablePortfolioButton = element(By.css('[ng-click="ctrl.setOption(\'portfolio\',\'enabled\')"]'))
        @disablePortfolioButton = element(By.css('[ng-click="ctrl.setOption(\'portfolio\',\'disabled\')"]'))

    get: ->
        browser.get(@betaUrl)
        return @

    clickPortfolioEnable: ->
        return @enablePortfolioButton.click()

    clickPortfolioDisable: ->
        return @disablePortfolioButton.click()

module.exports = BetaPage
