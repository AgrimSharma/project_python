// conf.js
exports.config = {
  seleniumAddress: 'http://localhost:4444/wd/hub',
  specs: [
	'../atomic-tests/spec-login/spec.js',
	'../atomic-tests/spec-cards/spec.add.js',
	'../atomic-tests/spec-cards/spec.archive.js'
	],
  capabilities: {
    browserName: 'firefox'
  },
  onPrepare: function() {
    global.By = global.by;
  }
}