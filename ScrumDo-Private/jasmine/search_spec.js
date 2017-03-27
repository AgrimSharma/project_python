"use strict";

const frisby = require('frisby');
const config = require('./local_config');
const async = require("async");
const org_path = `${config.api_root}/organizations/${config.org_slug}`;
const projects_path = org_path + "/projects";
const common = require('./project_common');
const createSampleCard = require('./story_common').createSampleCard


frisby.globalSetup({
  request: {
    headers:{'Accept': 'application/json'},
    inspectOnFailure: false
  },
  timeout: 30000
});



// Returns a test function for a single query/expected that async.watefall can deal with
function testSearch(query, expected, projectBody, done) {
    let projectSlug = projectBody['slug'];
    let iterationId = projectBody['kanban_iterations']['backlog'];
    let searchPath = `${projects_path}/${projectSlug}/iterations/${iterationId}/search?q=`;

    let test = frisby.create('Search for ' + query)
        .get(searchPath + query)
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectMaxResponseTime(500)
        .expectJSON('*', {
            "project_slug": projectSlug,
        })
        .expectJSONLength('', expected.length)
        .after(() => done(null, projectBody))

    for(let e of expected) {
        test = test.expectJSON('?', {   // The '?' path means it has to match any one of the returned elements.
            'number': e
        })
    }
    test.toss();
}



function createTestProject(done) {
    common.createAndTestProject((body) => done(null, body)).toss();
}

async.waterfall([
    createTestProject,
    createSampleCard({summary:'<p>Sample Card 555 pear grape<br/>Here Staged01.01.2000 is a sentence</p> blerg blarg glarg darg', tags:'banana, peach-cobbler, Normal'}),
    createSampleCard({summary:'Sample Card 555-257-9999 pear123456 Staged01/01/2000 grape-123456', tags:'apple-pear'}),
    createSampleCard({summary:'Sample Card 555-257-1023 grape-123 pear123', extra_1:'fix_link_within_link_invalid_html', tags:'apple'}),
    testSearch.bind(null, 'Staged01/01/2000', [2]),
    testSearch.bind(null, 'Staged01.01.2000', [1]),
    testSearch.bind(null, 'Staged01', [1,2]),
    testSearch.bind(null, 'Staged', [1,2]),
    testSearch.bind(null, 'sample', [1,2,3]),
    testSearch.bind(null, 'pear', [1,2,3]),
    testSearch.bind(null, 'grape', [1,2,3]),
    testSearch.bind(null, 'grape-123', [3,2]),
    testSearch.bind(null, 'samp', [1,2,3]),
    testSearch.bind(null, 'sample card', [1,2,3]),
    testSearch.bind(null, 'Sample Card', [1,2,3]),
    testSearch.bind(null, 'SAMPLE CARD', [1,2,3]),
    testSearch.bind(null, 'blerg blarg glarg darg', [1]),
    testSearch.bind(null, 'Here is a sentence', [1]),
    testSearch.bind(null, 'Here is sentence', [1]),
    testSearch.bind(null, 'Here a sentence', [1]),
    testSearch.bind(null, 'here sentence', [1]),
    testSearch.bind(null, 'here', [1]),
    testSearch.bind(null, 'HERE', [1]),
    testSearch.bind(null, 'sentence', [1]),
    testSearch.bind(null, 'card', [1,2,3]),
    testSearch.bind(null, '555', [1,2,3]),
    testSearch.bind(null, '555-257', [2,3]),
    testSearch.bind(null, '555-257-1023', [3]),
    testSearch.bind(null, '555-257-1024', []),
    testSearch.bind(null, 'apple', [2, 3]),
    testSearch.bind(null, 'tag: NORMAL', [1]),
    testSearch.bind(null, 'tag: Normal', [1]),
    testSearch.bind(null, 'tag: normal', [1]),
    testSearch.bind(null, 'tag: apple', [3]),
    testSearch.bind(null, 'tag: apple-pear', [2]),
    testSearch.bind(null, 'tag: banana', [1]),
    testSearch.bind(null, 'tag: peach-cobbler', [1]),
    testSearch.bind(null, 'zoinks', []),
    testSearch.bind(null, '555-333', []),
    testSearch.bind(null, '553', []),
    testSearch.bind(null, '5', [1,2,3]),
    testSearch.bind(null, 'bl', [1]),
    testSearch.bind(null, 's', [1,2,3]),
    testSearch.bind(null, 'z', []),
    testSearch.bind(null, 'fix_link_within_link_invalid_html', [3]),
]);
