common = require "../data/data"

exports.config = {
    seleniumAddress: common.param.seleniumAddress
    specs: [
        '../atomic-tests/spec-registration.coffee'
    ]
    capabilities: {
        browserName: 'chrome'
    }
    onPrepare: () ->
        global.select = global.by        
        global.param = common.param
        global.newUser =
            fullName: 'Automated Test'
            newUserName: "automated-#{Math.floor(Date.now() / 1000)}"
            password: 'klug'
            email: 'badaddress@scrumdo.com'
        
}