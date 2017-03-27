"use strict";

// Clean up old projects...

var frisby = require('frisby');
var config = require('./local_config');
var org_path = config.api_root + "/organizations/" + config.org_slug;
var projects_path = org_path + "/projects";

var project_count = 0;

frisby.globalSetup({
  request: {
    headers:{'Accept': 'application/json'},
    inspectOnFailure: true,
  },
  timeout: 60000
});

function deleteAll(list) {
    for(var project of list) {
        if(project.slug.indexOf('jasmine') == 0) {  // let's make sure to never accidently delete a project not named jasmine
            frisby.create('Delete all projects')
                .delete(projects_path + "/" + project.slug)
                .auth(config.username, config.password)
                .expectStatus(200)
                .toss()
        }

    }
}

frisby.create('Delete all jasmine created projects')
    .get(projects_path)
    .auth(config.username, config.password)
    .expectStatus(200)
    .afterJSON(deleteAll)
    .toss();
