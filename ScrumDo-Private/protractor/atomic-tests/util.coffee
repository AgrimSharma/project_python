fs = require('fs');

module.exports = {
    capture: (spec) ->
        return
        # if spec.results().passed() then return
        # name = spec.description.split(' ').join('_');
        # dir = process.env.CIRCLE_ARTIFACTS || 'tmp';
        #
        # if not fs.existsSync(dir)
        #     fs.mkdirSync(dir)
        #
        # browser.takeScreenshot().then (png) ->
        #     stream = fs.createWriteStream(dir + '/' + name + '.png');
        #     stream.write(new Buffer(png, 'base64'));
        #     stream.end();
}
