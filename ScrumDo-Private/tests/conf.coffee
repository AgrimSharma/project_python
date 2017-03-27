exports.config = {
  seleniumAddress: 'http://localhost:4444/wd/hub'
  specs: ['spec-login.coffee', 'spec-dashboard.coffee']
  onPrepare: () ->
        global.select = global.by;
        global.url = "http://192.168.1.125:8000"
}