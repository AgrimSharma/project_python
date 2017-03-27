"use strict";

const frisby = require('frisby');
const config = require('./local_config');
const org_path = config.api_root + "/organizations/" + config.org_slug;
const projects_path = org_path + "/projects";

const portfolio_path = org_path + "/portfolio";
const portfolio_build_path = portfolio_path + "/build";

const common = require('./project_common');
const async = require("async");

frisby.globalSetup({
  request: {
    headers:{'Accept': 'application/json'},
    inspectOnFailure: true
  },
  timeout: 30000
});


// {"levels": [{"id": 5, "level_number": 1, "name": "Programs", "projects": [{"work_item_name": "Feature", "name": "Program 1", "color": 3709147, "id": 23, "parents": [{"id": 22, "slug": "new-portfolio2", "name": "New Portfolio"}], "slug": "program-12", "icon": "fa-bullseye"}, {"work_item_name": "Feature", "name": "Program 2", "color": 3709147, "id": 24, "parents": [{"id": 22, "slug": "new-portfolio2", "name": "New Portfolio"}], "slug": "program-22", "icon": "fa-bullseye"}], "icon": "fa-bullseye"}, {"id": 6, "level_number": 2, "name": "Teams", "projects": [{"work_item_name": "User Story", "name": "Team 1", "color": 10115509, "id": 25, "parents": [{"id": 23, "slug": "program-12", "name": "Program 1"}, {"id": 24, "slug": "program-22", "name": "Program 2"}], "slug": "team-12", "icon": "fa-users"}, {"work_item_name": "User Story", "name": "Team 2", "color": 10115509, "id": 26, "parents": [{"id": 23, "slug": "program-12", "name": "Program 1"}, {"id": 24, "slug": "program-22", "name": "Program 2"}], "slug": "team-22", "icon": "fa-users"}, {"work_item_name": "User Story", "name": "Team 3", "color": 10115509, "id": 27, "parents": [{"id": 23, "slug": "program-12", "name": "Program 1"}, {"id": 24, "slug": "program-22", "name": "Program 2"}], "slug": "team-32", "icon": "fa-users"}], "icon": "fa-users"}], "root": {"use_time_estimate": true, "extra_2_label": null, "milestone_counts": {"active": 0, "inactive": 0}, "work_item_name": "Portfolio Epic", "color": 16152142, "labels": [], "project_type": 2, "use_extra_1": false, "use_extra_2": false, "use_extra_3": false, "category": "", "use_risk_reduction": false, "extra_3_label": null, "render_mode": 0, "aging_display": true, "personal": false, "use_time_crit": false, "id": 22, "time_tracking_mode": "scrumdo", "parents": [], "statuses": ["Todo", "", "", "Doing", "", "", "Reviewing", "", "", "Done"], "business_value_mode": 0, "warning_threshold": null, "use_points": true, "portfolio_id": null, "description": "", "releases": [], "tags": [], "story_queue_count": 0, "use_due_date": true, "card_types": ["User Story", "", "Feature", "", "", "", "", "Bug", "", ""], "default_cell_id": null, "members": [{"username": "mhughes", "first_name": "", "last_name": "", "email": "support@scrumdo.com", "id": 2}], "shared": null, "active": true, "folder_item_name": "Epic", "iterations_left": null, "slug": "new-portfolio2", "icon": "fa-folder", "critical_threshold": null, "point_scale_type": 0, "name": "New Portfolio", "created": "2016-07-19T13:02:02", "url": "/projects/project/new-portfolio2/", "velocity_type": 1, "burnup_reset_date": null, "burnup_reset": 0, "kanban_iterations": {"archive": 66, "backlog": 64}, "creator_id": 2, "extra_1_label": null, "alltags": [], "task_statuses": ["Todo", "", "", "Doing", "", "", "", "", "", "Done"], "velocity": null, "point_scale": [["?", "?"], ["0", "0"], ["0.5", "0.5"], ["1", "1"], ["2", "2"], ["3", "3"], ["5", "5"], ["8", "8"], ["13", "13"], ["20", "20"], ["40", "40"], ["100", "100"], ["Inf", "Infinite"]]}, "id": 3}

function buildPortfolio(cb) {
    let portfolio_input = {
        "number":null,
        "root":{"name":"New Portfolio","work_item_name":"Portfolio Epic","parents":[],"color":"#000000","icon":"fa-folder","uid":"root"},
        "levels":[
            {"name":"Programs","projects":[{"name":"Program 1","color":"#3898DB","icon":"fa-bullseye","work_item_name":"Feature","parents":[{"name":"New Portfolio","work_item_name":"Portfolio Epic","parents":[],"color":"#000000","icon":"fa-folder","uid":"root"}],"uid":"60840c12-d2d2-4d6b-95a9-492d5fdb86cc","id":-10000},{"name":"Program 2","color":"#3898DB","icon":"fa-bullseye","work_item_name":"Feature","parents":[{"name":"New Portfolio","work_item_name":"Portfolio Epic","parents":[],"color":"#000000","icon":"fa-folder","uid":"root"}],"uid":"06f41993-755e-47bd-b5c5-3e3b293fcf36","id":-9999}],"level_number":1,"defaultWorkItem":"Feature","icon":"fa-bullseye"},{"name":"Teams","projects":[{"name":"Team 1","color":"#9A59B5","icon":"fa-users","work_item_name":"User Story","parents":[{"name":"Program 1","color":"#3898DB","icon":"fa-bullseye","work_item_name":"Feature","parents":[{"name":"New Portfolio","work_item_name":"Portfolio Epic","parents":[],"color":"#000000","icon":"fa-folder","uid":"root"}],"uid":"60840c12-d2d2-4d6b-95a9-492d5fdb86cc","id":-10000},{"name":"Program 2","color":"#3898DB","icon":"fa-bullseye","work_item_name":"Feature","parents":[{"name":"New Portfolio","work_item_name":"Portfolio Epic","parents":[],"color":"#000000","icon":"fa-folder","uid":"root"}],"uid":"06f41993-755e-47bd-b5c5-3e3b293fcf36","id":-9999}],"uid":"c24ad2e6-3c77-4004-9906-f4a0e6fc01cf","id":-9998},{"name":"Team 2","color":"#9A59B5","icon":"fa-users","work_item_name":"User Story","parents":[{"name":"Program 1","color":"#3898DB","icon":"fa-bullseye","work_item_name":"Feature","parents":[{"name":"New Portfolio","work_item_name":"Portfolio Epic","parents":[],"color":"#000000","icon":"fa-folder","uid":"root"}],"uid":"60840c12-d2d2-4d6b-95a9-492d5fdb86cc","id":-10000},{"name":"Program 2","color":"#3898DB","icon":"fa-bullseye","work_item_name":"Feature","parents":[{"name":"New Portfolio","work_item_name":"Portfolio Epic","parents":[],"color":"#000000","icon":"fa-folder","uid":"root"}],"uid":"06f41993-755e-47bd-b5c5-3e3b293fcf36","id":-9999}],"uid":"63c55f3c-21d7-4ef9-bc0d-90f8a71bedaf","id":-9997},{"name":"Team 3","color":"#9A59B5","icon":"fa-users","work_item_name":"User Story","parents":[{"name":"Program 1","color":"#3898DB","icon":"fa-bullseye","work_item_name":"Feature","parents":[{"name":"New Portfolio","work_item_name":"Portfolio Epic","parents":[],"color":"#000000","icon":"fa-folder","uid":"root"}],"uid":"60840c12-d2d2-4d6b-95a9-492d5fdb86cc","id":-10000},{"name":"Program 2","color":"#3898DB","icon":"fa-bullseye","work_item_name":"Feature","parents":[{"name":"New Portfolio","work_item_name":"Portfolio Epic","parents":[],"color":"#000000","icon":"fa-folder","uid":"root"}],"uid":"06f41993-755e-47bd-b5c5-3e3b293fcf36","id":-9999}],"uid":"4dc57c5f-0706-4bfb-9ee2-2464c001ae54","id":-9996}],"level_number":2,"defaultWorkItem":"User Story","icon":"fa-users"}]}
    frisby.create('Build a portfolio')
        .post(portfolio_build_path, portfolio_input, {json: true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectHeaderContains('content-type', 'application/json')
        .expectJSONTypes({
            levels: Array,
            id: Number,
            root: {
                id: Number
            }
        })
        .expectJSONLength('levels', 2)  // TODO: Let's add a bit more validation in here...
        .afterJSON(function(body){
            cb(null, body)
        }).toss();
}

function addPortfolioLevel(portfolioBody, cb) {
    let existing_project = portfolioBody.levels[0].projects.shift()  // going to move one project to a new level

    portfolioBody.levels.push({name: "created level",
                               level_number: 3,
                               work_item_name:"widgets",
                               color:"#123456",
                               icon:"fa-new",
                               uid:"new!",
                               projects: [
                                   existing_project,
                                   {name:'New with level', work_item_name:'flimflam', parents:[]},
                               ]
                           });

    frisby.create('Add a level with two projects in it (one new, one existing)')
        .put(portfolio_path + `/${portfolioBody.id}`, portfolioBody, {json: true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectHeaderContains('content-type', 'application/json')
        .expectJSONTypes({
            levels: Array,
            id: Number,
            root: {
                id: Number
            }
        })
        .expectJSONLength('levels', 3)
        .afterJSON(function(body){
            cb(null, body)
        }).toss();
}


function removePortfolioLevel(portfolioBody, cb) {
    portfolioBody.levels.shift();
    frisby.create('Remove a portfolio level')
        .put(portfolio_path + `/${portfolioBody.id}`, portfolioBody, {json: true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectHeaderContains('content-type', 'application/json')
        .expectJSONTypes({
            levels: Array,
            id: Number,
            root: {
                id: Number
            }
        })
        .expectJSONLength('levels', 2)
        .afterJSON(function(body){
            cb(null, portfolioBody)
        }).toss();
}


function updatePorfolioAttributes(portfolioBody, cb) {
    portfolioBody.root.name = 'changed name';
    portfolioBody.levels[0].projects[0].name = 'Changed project name';

    frisby.create('Modify portfolio attributes')
        .put(portfolio_path + `/${portfolioBody.id}`, portfolioBody, {json: true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectHeaderContains('content-type', 'application/json')
        .expectJSONTypes({
            levels: Array,
            id: Number,
            root: {
                id: Number
            }
        })
        .expectJSONLength('levels', 2)
        .expectJSON({
            root: {
                name: 'changed name'
            }
        })
        .afterJSON(function(body){
            cb(null, body)
        }).toss();
}


function createIncrement(portfolioBody, cb) {
    let increment_url = `${projects_path}/${portfolioBody.root.slug}/increment/`;
    // console.log(increment_url);

    let body = {
        name: 'Program Increment #1',
        start_date: '2016-01-01',
        end_date: '2016-04-01',
        schedule: [
            {
                start_date: '2016-01-01',
                end_date: '2016-02-01',
                default_name: 'Iteration #1.1'
            },
            {
                start_date: '2016-02-01',
                end_date: '2016-03-01',
                default_name: 'Iteration #1.2'
            },
            {
                start_date: '2016-03-01',
                end_date: '2016-04-01',
                default_name: 'Iteration #1.3'
            }
        ]
    };


    frisby.create('Create a program increment')
        .post(increment_url, body, {json: true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectHeaderContains('content-type', 'application/json')
        .expectJSONTypes({
            id: Number,
            project_slug: String
        })
        .expectJSONTypes('schedule.*', {
            default_name:String,
            id : Number,
            iterations:Array
        })
        .expectJSON({
                name: 'Program Increment #1',
                start_date: '2016-01-01',
                end_date: '2016-04-01',
                schedule: [
                    {
                        start_date: '2016-01-01',
                        end_date: '2016-02-01',
                        default_name: 'Iteration #1.1',
                        iterations: [{
                                project_name: 'Changed project name',
                                cards_in_progress: 0,
                                cards_total: 0,
                                iteration_name: 'Iteration #1.1'
                        }]
                    },
                    {
                        start_date: '2016-02-01',
                        end_date: '2016-03-01',
                        default_name: 'Iteration #1.2',
                        iterations: [{
                                project_name: 'Changed project name',
                                cards_in_progress: 0,
                                cards_total: 0,
                                iteration_name: 'Iteration #1.2'
                        }]
                    },
                    {
                        start_date: '2016-03-01',
                        end_date: '2016-04-01',
                        default_name: 'Iteration #1.3',
                        iterations: [{
                                project_name: 'Changed project name',
                                cards_in_progress: 0,
                                cards_total: 0,
                                iteration_name: 'Iteration #1.3'
                        }]
                    }
                ]
        })
        .afterJSON(function(body){

            cb(null, [portfolioBody, body])
        }).toss();
}



function modifyIncrement(results, cb) {
    let portfolioBody = results[0];
    let incrementBody = results[1];
    let increment_url = `${projects_path}/${portfolioBody.root.slug}/increment/${incrementBody.id}/`;
    incrementBody.name = "Modified Increment";
    incrementBody.start_date = "2016-01-02";
    incrementBody.end_date = "2016-02-02";

    frisby.create('Modify a program increment')
        .put(increment_url, incrementBody, {json: true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectHeaderContains('content-type', 'application/json')
        .expectJSONTypes({
            id: Number
        })
        .expectJSONTypes('schedule.*', {
            default_name:String,
            id : Number,
            iterations:Array
        })
        .expectJSON({
                name: 'Modified Increment',
                start_date: '2016-01-02',
                end_date: '2016-02-02',
                schedule: [
                    {
                        start_date: '2016-01-01',
                        end_date: '2016-02-01',
                        default_name: 'Iteration #1.1',
                        iterations: [{
                                project_name: 'Changed project name',
                                cards_in_progress: 0,
                                cards_total: 0,
                                iteration_name: 'Iteration #1.1'
                        }]
                    },
                    {
                        start_date: '2016-02-01',
                        end_date: '2016-03-01',
                        default_name: 'Iteration #1.2',
                        iterations: [{
                                project_name: 'Changed project name',
                                cards_in_progress: 0,
                                cards_total: 0,
                                iteration_name: 'Iteration #1.2'
                        }]
                    },
                    {
                        start_date: '2016-03-01',
                        end_date: '2016-04-01',
                        default_name: 'Iteration #1.3',
                        iterations: [{
                                project_name: 'Changed project name',
                                cards_in_progress: 0,
                                cards_total: 0,
                                iteration_name: 'Iteration #1.3'
                        }]
                    }
                ]
        })
        .afterJSON(function(body){

            cb(null, [portfolioBody, body])
        }).toss();
}

function modifyIncrementLevel(results, cb) {
    let portfolioBody = results[0];
    let incrementBody = results[1];
    let scheduleBody = incrementBody.schedule[0]
    let url = `${projects_path}/${portfolioBody.root.slug}/increment/${incrementBody.id}/schedule/${scheduleBody.id}/`;
    scheduleBody.default_name = "Modified Increment";
    scheduleBody.start_date = "2016-01-02";
    scheduleBody.end_date = "2016-02-02";

    frisby.create('Modify a program increment schedule')
        .put(url, scheduleBody, {json: true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectHeaderContains('content-type', 'application/json')
        .expectJSONTypes({
            id: Number
        })
        .expectJSON({
                default_name: 'Modified Increment',
                start_date: '2016-01-02',
                end_date: '2016-02-02',
        })
        .afterJSON(function(body){

            cb(null, [portfolioBody, incrementBody, body])
        }).toss();
}

function deleteIncrementLevel(results, cb) {
    let portfolioBody = results[0];
    let incrementBody = results[1];
    let scheduleBody = results[2];
    let url = `${projects_path}/${portfolioBody.root.slug}/increment/${incrementBody.id}/schedule/${scheduleBody.id}/`;

    frisby.create('Delete a program increment schedule')
        .delete(url, {json: true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectHeaderContains('content-type', 'application/json')
        .after(function(body){
            cb(null, [portfolioBody, incrementBody])
        }).toss();
}

function verifyIncrementLevel(results, cb) {
    let portfolioBody = results[0];
    let incrementBody = results[1];
    let url = `${projects_path}/${portfolioBody.root.slug}/increment/${incrementBody.id}/`;


    frisby.create('Get a program increment (after a delete)')
        .get(url)
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectHeaderContains('content-type', 'application/json')
        .expectJSONLength('schedule', 2)
        .expectJSON({
                name: 'Modified Increment',
                start_date: '2016-01-02',
                end_date: '2016-02-02',
                schedule: [
                    {
                        start_date: '2016-02-01',
                        end_date: '2016-03-01',
                        default_name: 'Iteration #1.2',
                        iterations: [{
                                project_name: 'Changed project name',
                                cards_in_progress: 0,
                                cards_total: 0,
                                iteration_name: 'Iteration #1.2'
                        }]
                    },
                    {
                        start_date: '2016-03-01',
                        end_date: '2016-04-01',
                        default_name: 'Iteration #1.3',
                        iterations: [{
                                project_name: 'Changed project name',
                                cards_in_progress: 0,
                                cards_total: 0,
                                iteration_name: 'Iteration #1.3'
                        }]
                    }
                ]
        })
        .afterJSON(function(body){
            cb(null, [portfolioBody, incrementBody])
        }).toss();
}



function addIncrementLevel(results, cb) {
    let portfolioBody = results[0];
    let incrementBody = results[1];
    let url = `${projects_path}/${portfolioBody.root.slug}/increment/${incrementBody.id}/schedule/`;

    let body = {
        default_name: 'Added Level',
        start_date: '2017-01-01',
        end_date: '2017-02-01',
    }


    frisby.create('Create a program increment schedule')
        .post(url, body, {json: true})
        .auth(config.username, config.password)
        .expectStatus(200)
        .expectHeaderContains('content-type', 'application/json')
        .expectJSON({
            iterations: [
                {
                    project_name: 'Changed project name',
                    cards_completed: 0,
                    cards_in_progress: 0,
                    cards_total: 0,
                    iteration_name: 'Added Level'
                }],
                default_name: 'Added Level',
                start_date: '2017-01-01',
                end_date: '2017-02-01'
            })
        .afterJSON(function(body){
            cb(null, [portfolioBody, incrementBody])
        }).toss();
}

function createSampleCard() {

}

async.waterfall([
    buildPortfolio,
    updatePorfolioAttributes,
    addPortfolioLevel,
    removePortfolioLevel,
    createIncrement,
    // createSampleCard(0, 'Test card 1'),
    // createSampleCard(0, 'Test card 2'),
    // createSampleCard(0, 'Test card 3'),
    modifyIncrement,
    modifyIncrementLevel,
    deleteIncrementLevel,
    verifyIncrementLevel,
    addIncrementLevel
]);
