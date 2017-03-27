"use strict";

var frisby = require('frisby');
var config = require('./local_config');
var org_path = config.api_root + "/organizations/" + config.org_slug;
var projects_path = org_path + "/projects";
var exports = module.exports = {};


// Helper function that creates a project and runs testFunction in it's afterJSON event
exports.createSampleCard = function(data) {
    return function(projectBody, cb) {
        let projectSlug = projectBody['slug'];
        let iterationId = projectBody['kanban_iterations']['backlog'];
        let storyPath = `${projects_path}/${projectSlug}/iterations/${iterationId}/stories`;
        frisby.create('Create sample card')
            .post(storyPath, data, {json: true})
            .auth(config.username, config.password)
            .expectStatus(200)
            .expectJSON({
                'summary': data.summary,
                'tags': data.tags
            })
            .after(()=>cb(null, projectBody))
            .toss();
    }
}

exports.listCards = function(projectBody, cb) {
    let projectSlug = projectBody['slug'];
    let iterationId = projectBody['kanban_iterations']['backlog'];
    let storyPath = `${projects_path}/${projectSlug}/iterations/${iterationId}/stories`;
    frisby.create('Get card list')
        .get(storyPath)
        .auth(config.username, config.password)
        .expectStatus(200)
        .afterJSON((cardBody)=>cb(null, projectBody, cardBody))
        .toss();
}
