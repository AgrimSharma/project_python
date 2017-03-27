"use strict";

var frisby = require('frisby');
var config = require('./local_config');
var org_path = config.api_root + "/organizations/" + config.org_slug;
var projects_path = org_path + "/projects";
var exports = module.exports = {};

// Helper function that creates a project and runs testFunction in it's afterJSON event
exports.createAndTestProject = function(testFunction) {
    return frisby.create('Create a project')
        .post(projects_path, {'name': 'Jasmine Test Project'})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectHeaderContains('content-type', 'application/json')
        .expectJSON({
            'name': 'Jasmine Test Project',
            'slug': function(val){ expect(val).toContain('jasmine-test-project') },
            'use_time_crit': false,
            'use_risk_reduction': false,
            'use_points': true,
            'use_time_estimate': true,
            'use_due_date': true,
            'business_value_mode': 0
        })
        .afterJSON(testFunction);
}
