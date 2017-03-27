"use strict";

var frisby = require('frisby');
var config = require('./local_config');
var org_path = config.api_root + "/organizations/" + config.org_slug;
var projects_path = org_path + "/projects";
var common = require('./project_common');

var project_count = 0;

frisby.globalSetup({
  request: {
    headers:{'Accept': 'application/json'},
    inspectOnFailure: true
  },
  timeout: 30000
});

// Try doing a listing without credentials
frisby.create('Check permissions')
  .get(projects_path)
  .auth('Bad', 'User')
  .expectStatus(401)
  .toss();


frisby.create('List projects')
    .get(projects_path)
    .auth(config.username, config.password)
    .expectStatus(200)
    .afterJSON(function(body) {
        project_count = body.length;
    })
    .toss();


// let's try modifying the color and optional fields
common.createAndTestProject(function(body){
    let slug = body['slug'];

    frisby.create('Change color of project')
        .put(projects_path + "/" + slug,
                {
                    'color':0xFF00FF,
                    'use_time_crit': true,
                    'use_risk_reduction': true,
                    'use_points': false,
                    'use_time_estimate': false,
                    'use_due_date': false,
                    'business_value_mode': 2
                },
                {json: true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectJSON({
            'color': 0xFF00FF,
            'use_time_crit': true,
            'use_risk_reduction': true,
            'use_points': false,
            'use_time_estimate': false,
            'use_due_date': false,
            'business_value_mode': 2
        })
        .toss();

}).toss();


common.createAndTestProject(function(body) {
      let slug = body['slug'];

      // After creating a project, try deleting it without credentials
      frisby.create('Anon can not delete')
        .delete(projects_path + "/" + slug)
        .auth('BAD','USER')
        .expectStatus(401)
        .toss();

      // Now delete it for real
      frisby.create('Delete a project')
        .delete(projects_path + "/" + slug)
        .auth(config.username, config.password)
        .expectStatus(200)
        .after(function(){

            // Finally, do a listing and make sure the project count is right
            frisby.create('Check project was removed')
              .get(projects_path)
              .auth(config.username, config.password)
              .expectStatus(200)
              .afterJSON(function(body){
                  let slugs = body.map(function(p){return p.slug});
                  expect(slugs).not.toContain(slug);
              })
              .toss();
        })
        .toss();
    })
    .toss();
