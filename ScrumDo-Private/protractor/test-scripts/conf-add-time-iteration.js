// conf.js
exports.config = {
  seleniumAddress: 'http://localhost:4444/wd/hub',
  specs: [
	'../atomic-tests/spec-login/spec.js',
	'../atomic-tests/spec-iteration/spec.edit.time.js'
	],
  capabilities: {
    browserName: 'firefox'
  },
  onPrepare: function() {
    global.By = global.by;
	global.clearValue = function(elem){
		elem.getAttribute('value').then(function (text) {
			var len = text.length
			var backspaceSeries = Array(len+1).join(protractor.Key.BACK_SPACE);
			elem.sendKeys(backspaceSeries);
		})
	}
  }
}