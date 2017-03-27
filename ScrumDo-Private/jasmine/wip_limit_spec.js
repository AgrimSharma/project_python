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


function createTestProject(done) {
    common.createAndTestProject((body) => done(null, body)).toss();
}

function testCreateLimit(featureLimit,featurePointLimit,cardLimit,cardPointLimit) {
    return function (project, cb) {
        const projectSlug = project.slug;
        const iterationId = project.kanban_iterations.backlog;
        const data = {
            featureLimit: featureLimit,
            featurePointLimit: featurePointLimit,
            cardLimit: cardLimit,
            cardPointLimit: cardPointLimit
        };

        let path = `${projects_path}/${projectSlug}/iterations/${iterationId}/wiplimit/`;
        frisby.create('Create a wip limit')
            .post(path, data, {json: true})
            .auth(config.username, config.password)
            .expectStatus(200)
            .expectJSON(data)
            .after(()=>cb(null, project))
            .toss();
    }
}

function testReadLimit(project, cb) {
    const projectSlug = project.slug;
    const iterationId = project.kanban_iterations.backlog;
    const data = {
        featureLimit: 1,
        featurePointLimit: 10,
        cardLimit: 1000,
        cardPointLimit: 0
    };

    let path = `${projects_path}/${projectSlug}/iterations/${iterationId}/wiplimit/`;
    frisby.create('Read a wip limit')
        .get(path)
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectJSON(data)
        .after(()=>cb(null, project))
        .toss();
}

function testUpdateLimit(project, cb) {
    const projectSlug = project.slug;
    const iterationId = project.kanban_iterations.backlog;
    const data = {
        featureLimit: 2,
        featurePointLimit: 20,
        cardLimit: 2000,
        cardPointLimit: 2
    };

    let path = `${projects_path}/${projectSlug}/iterations/${iterationId}/wiplimit/`;
    frisby.create('Update a wip limit')
        .put(path, data, {json: true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectJSON(data)
        .after(()=>cb(null, project))
        .toss();
}
function testDeleteLimit(project, cb) {
    const projectSlug = project.slug;
    const iterationId = project.kanban_iterations.backlog;


    let path = `${projects_path}/${projectSlug}/iterations/${iterationId}/wiplimit/`;
    frisby.create('Update a wip limit')
        .delete(path)
        .auth(config.username, config.password)
        .expectStatus(200)
        .after(()=>cb(null, project))
        .toss();
}


async.waterfall([
    createTestProject,
    testCreateLimit(5,5,5,5),
    testCreateLimit(1,0,0,0),
    testCreateLimit(0,1,0,0),
    testCreateLimit(0,0,1,0),
    testCreateLimit(0,0,0,1),    
    testCreateLimit(1,10,1000,0),
    testReadLimit,
    testUpdateLimit,
    testDeleteLimit
]);
