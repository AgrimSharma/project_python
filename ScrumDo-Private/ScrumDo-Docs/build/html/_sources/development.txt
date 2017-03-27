Development process
===================
Being a remote team has certain challenges in managing and organizing. 
This tutorial describes the nominal way the engineering team will work at Codegenesys

Daily updates
-----------------------

Instead of a daily phone checkin, we're using Slack. Every day, at a convenient time for you, please give the team an update of what's going on. Please start it with 'Daily Update:' to make it easy to identify. Here's some examples:

.. note::    Daily Update: Today I worked on some bugs related to shortcut keys for card, planning poker and project drop-down. and also worked on my cards section to show Help Topic with empty cards. Will start work on new Blocked feature for cards.

.. note::    Daily update: Over the weekend I deployed the elasticsearch cluster into production, ran into a lot of problems. Everything seems to be going really well with it now, no customer complaints, CPU usage way down and creating cards feels faster. I've cleared out my backlog of code to review and deployed all that. Today I'll be working on writing up specifications for new work and then digging into some myself.

Branches
--------


    * development
    * production

These two branches are for the classic version of ScrumDo. You should only touch them with explicit orders and they can generally be ignored.

    * production-v2

This represents the version of ScrumDo that runs on app.scrumdo.com and is live for our customers. We have jobs which automatically deploy this branch to the servers. Only Marc should ever push to this branch, so you can probably ignore it.

    * development-v2

This is the main development branch for ScrumDo. We merge all our features into it and test before deploying to production-v2. However, you should not be directly committing changes to it. We use a feature branch and pull request mechanism to review all code first.

    * feature/**<feature name>**

These are all the branches we use to develop new features, fix bugs, or do just about any work. Most of your development time will be spent in here.

    * beta

This branch represents the version that is live on beta.scrumdo.com You can push changes here if you want someone else to view them

git checkout beta

git pull

git merge feature/my-feature

git push

Doing that will cause it to automatically be deployed to beta.scrumdo.com, so give a warning in the development slack channel so everyone knows.

When we get a QA person, we'll be doing this a lot.

.. warning:: beta runs on the production database. So that's real live data and you have to be careful not to mess up any customer data. Database migrations are not automatically run. If you need a migration, talk with Marc, we need to make sure it'll be backward compatible and it needs to be manually run.


Merging
-------

Any time you do a git pull, you might have to manually merge changes from other people. Watch for this. This can get tricky. Here is some help:

General method via command line: https://githowto.com/resolving_conflicts

I use p4merge as a visual merge tool, here is how to set that up: https://gist.github.com/tony4d/3454372

Here is how to use p4merge: http://naleid.com/blog/2013/10/29/how-to-use-p4merge-as-a-3-way-merge-tool-with-git-and-tower-dot-app

If you skip to 2:00 in this video (ignore the perforce parts before that and everything after 3:00) you can see how to use it: https://www.perforce.com/resources/tutorials/resolving-conflicts

It's important to do the merges correctly so you don't lose the other persons changes, ask if you have questions.