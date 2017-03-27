"use strict";

const frisby = require('frisby');
const config = require('./local_config');
const async = require("async");
const org_path = `${config.api_root}/organizations/${config.org_slug}`;
const projects_path = org_path + "/projects";
const common = require('./project_common');
const story_common = require('./story_common')

const createSampleCard = story_common.createSampleCard
const listCards = story_common.listCards

frisby.globalSetup({
  request: {
    headers:{'Accept': 'application/json'},
    inspectOnFailure: true
  },
  timeout: 30000
});

function deleteDependency(projectBody, cardList, done) {
    let projectSlug = projectBody['slug'];
    let iterationId = projectBody['kanban_iterations']['backlog'];
    let story1 = cardList[0];
    let story2 = cardList[1];
    let story3 = cardList[2];

    let url = `${config.api_root}/dependencies/story/${story1.id}/dependency/${story2.id}`
    let data = {dependencies:[story2, story3]}

    frisby.create('Delete a Dependency')
        .delete(url)
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectMaxResponseTime(500)
        .expectJSONLength('dependent_on', 1)
        .expectJSON('dependent_on.*', {
            project: {
                "slug": projectSlug
            }
        })
        .expectJSON('dependent_on.?', {
            "id": story3.id,
        })
        .after(() => done(null, projectBody, cardList))
        .toss();
}

function readDependencies(projectBody, cardList, done) {
    let projectSlug = projectBody['slug'];
    let iterationId = projectBody['kanban_iterations']['backlog'];
    let story1 = cardList[0];
    let story2 = cardList[1];
    let story3 = cardList[2];

    let url = `${config.api_root}/dependencies/story/${story2.id}/dependency/`
    let data = {dependencies:[story2, story3]}

    frisby.create('Get Dependencies')
        .get(url)
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectMaxResponseTime(500)
        .expectJSONLength('dependent_to', 1)
        .expectJSONLength('dependent_on', 0)
        .expectJSON('dependent_to.*', {
            "project": {
                "slug": projectSlug
            }
        })
        .expectJSON('dependent_to.?', {
            "id": story1.id,
        })
        .toss();

    url = `${config.api_root}/dependencies/story/${story1.id}/dependency/`
    frisby.create('Get Dependencies')
        .get(url)
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectMaxResponseTime(500)
        .expectJSONLength('dependent_to', 0)
        .expectJSONLength('dependent_on', 2)
        .expectJSON('dependent_on.*', {
            "project": {
                "slug": projectSlug
            }
        })
        .expectJSON('dependent_on.?', {
            "id": story2.id,
        })
        .expectJSON('dependent_on.?', {
            "id": story3.id,
        })
        .after(() => done(null, projectBody, cardList))
        .toss();
}

function createDependency(projectBody, cardList, done) {
    let projectSlug = projectBody['slug'];
    let iterationId = projectBody['kanban_iterations']['backlog'];
    let story1 = cardList[0];
    let story2 = cardList[1];
    let story3 = cardList[2];

    let url = `${config.api_root}/dependencies/story/${story1.id}/dependency/`
    let data = {dependencies:[story2, story3]}

    frisby.create('Add Dependency')
        .post(url, data, {json:true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectMaxResponseTime(500)
        .expectJSONLength('dependent_on', 2)
        .expectJSON('dependent_on.*', {
            project: {
                slug: projectSlug,
            }
        })
        .expectJSON('dependent_on.?', {
            "id": story2.id,
        })
        .expectJSON('dependent_on.?', {
            "id": story3.id,
        })
        .after(() => done(null, projectBody, cardList))
        .toss();
}



function createTestProject(done) {
    common.createAndTestProject((body) => done(null, body)).toss();
}

async.waterfall([
    createTestProject,
    createSampleCard({summary:'<p>Sample Card 555 pear grape<br/>Here Staged01.01.2000 is a sentence</p> blerg blarg glarg darg', tags:'banana, peach-cobbler, Normal'}),
    createSampleCard({summary:'Sample Card 555-257-9999 pear123456 Staged01/01/2000 grape-123456', tags:'apple-pear'}),
    createSampleCard({summary:'Sample Card 555-257-1023 grape-123 pear123', extra_1:'fix_link_within_link_invalid_html', tags:'apple'}),
    listCards,
    createDependency,
    readDependencies,
    deleteDependency
]);
