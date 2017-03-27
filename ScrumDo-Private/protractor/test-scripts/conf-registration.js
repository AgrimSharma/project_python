// conf.js
exports.config = {
  seleniumAddress: 'http://localhost:4444/wd/hub',
  specs: [
	'../atomic-tests/spec-registration/spec.js',
	'../atomic-tests/spec-logout/spec.js'
	],
  capabilities: {
    browserName: 'firefox'
  },
  onPrepare: function() {
    global.By = global.by;
  }
}