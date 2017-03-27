// conf.js
exports.config = {
  seleniumAddress: 'http://localhost:4444/wd/hub',
  specs: [
	'../atomic-tests/spec-login/spec.js',
	'../atomic-tests/spec-iteration/spec.add.js'
	],
  capabilities: {
    browserName: 'firefox'
  },
  onPrepare: function() {
    global.By = global.by;
  }
}