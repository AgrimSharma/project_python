"use strict";

var frisby = require('frisby');
var config = require('./local_config');
var org_path = config.api_root + "/organizations/" + config.org_slug;
var projects_path = org_path + "/projects";

frisby.globalSetup({
  request: {
    headers:{'Accept': 'application/json'},
    inspectOnFailure: true,
  },
  timeout: 30000
});


function deleteProject(project) {
    let project_path = projects_path + "/" + project.slug;
    frisby.create('delete the project')
      .delete(project_path)
      .auth(config.username, config.password)
      .expectStatus(200)
      .toss();
}

function modifyProject(project) {
    let project_path = projects_path + "/" + project.slug;
    frisby.create('modify a project and set work/folder items')
      .put(project_path, {'name': 'Jasmine test Project', work_item_name: 'A', folder_item_name: 'B'}, {json: true})
      .auth(config.username, config.password)
      .expectStatus(200)
      .expectHeaderContains('content-type', 'application/json')
        .expectJSON({
            work_item_name: 'A',
            folder_item_name: 'B',
        })
      .afterJSON(deleteProject)
      .toss();  // the create parent call
}



frisby.create('Create a project to test work/folder items')
  .post(projects_path, {'name': 'Jasmine test Project', folder_item_name: 'Bannana'}, {json: true})
  .auth(config.username, config.password)
  .expectStatus(200)
  .expectHeaderContains('content-type', 'application/json')
    .expectJSON({
        work_item_name: 'Card',
        folder_item_name: 'Bannana',
    })
  .afterJSON(modifyProject)
  .toss();  // the create parent call

