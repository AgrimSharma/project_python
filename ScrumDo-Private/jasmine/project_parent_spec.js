"use strict";

var frisby = require('frisby');
var config = require('./local_config');
var org_path = config.api_root + "/organizations/" + config.org_slug;
var projects_path = org_path + "/projects";

// Create parent -> create child -> create grandchild ->

frisby.globalSetup({
  request: {
    headers:{'Accept': 'application/json'},
    inspectOnFailure: false,
  },
  timeout: 30000
});


function testParenting(child) {
    let child_path = projects_path + "/" + child.slug;
    frisby.create('Unset a child project')
        .put(child_path, {'parents':[]}, {json: true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectHeaderContains('content-type', 'application/json')
        .expectJSON({
            'parents': []
        })
        .after(function(err,res,body){
            frisby.create('Fail to set self as child')
                .put(child_path, {'parents':[{'id':child.id}]}, {json: true})
                .auth(config.username, config.password)
                .expectStatus(400)
                .toss();
        })
        .toss(); // Unset child call
}

function createGrandChild(parent) {
    frisby.create('Create a grand child project')
        .post(projects_path, {'name': 'Jasmine Grand Child Project', 'parents':[{'id':parent.id}]}, {json: true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectHeaderContains('content-type', 'application/json')
        .expectJSON({
            'parents': [{
                'id': parent.id
            }]
        })
        .afterJSON(testParenting)
        .toss(); // create child call
}

function createChild(parent) {
      frisby.create('Create a child project')
          .post(projects_path, {'name': 'Jasmine Child Project', 'parents':[{'id':parent.id}]}, {json: true})
          .auth(config.username, config.password)
          .expectStatus(200)
          .expectHeaderContains('content-type', 'application/json')
          .expectJSON({
              'parents': [{
                  'id': parent.id
              }]
          })
          .afterJSON(createGrandChild)
          .toss(); // create child call
}

// Test parenting
frisby.create('Create a parent project')
  .post(projects_path, {'name': 'Jasmine Parent Project'}, {json: true})
  .auth(config.username, config.password)
  .expectStatus(200)
  .expectHeaderContains('content-type', 'application/json')
  .afterJSON(createChild)
  .toss();  // the create parent call
