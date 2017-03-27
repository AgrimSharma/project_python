# -*- coding: utf-8 -*-

from django.template.loader import render_to_string
import apps.kanban.managers as kanban_managers
import random
from apps.activities.models import NewsItem
from apps.kanban.tasks import scheduleRebuildStepMovements
import django.template.defaultfilters as defaultfilters

from apps.organizations.models import *
from apps.projects.models import *
from apps.favorites.models import Favorite
from apps.inbox import tasks as inbox_tasks
from apps.projects.util import generateProjectPrefix

import datetime

def _generateSlug(projectName):
    slug = defaultfilters.slugify( projectName )[:45]
    c = 1
    while True:
        try:
            Project.objects.get(slug=slug)
            c += 1
            slug = "%s%d" % (defaultfilters.slugify(projectName)[:45], c)
        except Project.DoesNotExist:
            return slug  # finally found a slug that doesn't exist

def createTutorialProject(organization, user):
    project = Project(name="Sample Workspace", slug=_generateSlug("training%d" % random.randint(0, 50000)), creator=user, organization=organization)
    project.prefix = generateProjectPrefix(project)
    project.save()
    (backlog, current, archive) = kanban_managers.initKanbanProject(project)

    current.start_date = datetime.date.today() - datetime.timedelta(2)
    current.save()

    e1 = Epic(order=5000, local_id=1, summary="Using ScrumDo", project=project)
    e1.save()
    e2 = Epic(order=10000, local_id=2, summary="Working on a Workspace", project=project, parent=e1)
    e2.save()
    e3 = Epic(order=15000, local_id=3, summary="Administration Functions", project=project, parent=e1)
    e3.save()
    epics = {'e1': e1, 'e2': e2, 'e3': e3}


    rows = [{'name':''}]
    columns = [ {'name': 'Todo', 'color': "#747E89", 'style': 0, 'sub': ['Doing', 'Done']},
                {'name': 'Doing', 'color': "#3898DB", 'style': 0, 'sub': ['Doing', 'Done']},
                {'name': 'Reviewing', 'color': "#F5764E", 'style': 0, 'sub': ['Doing', 'Done']},
                {'name': 'Done', 'color': "#34CC73", 'style': 0, 'sub': ['Doing', 'Done']}]
    kanban_managers.wizard(project, {'rows': rows, 'columns': columns}, True)

    for team in organization.teams.all():
        team.projects.add(project)


    # item = NewsItem(user=None, project=project, icon='server_add' )
    # item.text = render_to_string("activities/project_created.txt", {'user':user,'project':project} )
    # item.save()
    cards = [
        {'summary': '<h1>Start Here!</h1><p>This is a sample card in a Sample Workspace for you.  Click it to go to the workspace and open it.</p>',
         'cell': 'Todo',
         'backlog': False,
         'assign': True,
         'points': '2',
         'inbox': True,
         'detail': "<h1>Good Job!</h1><p>You just navigated to your workspace board and opened this card!  Check out the other cards on the board for more info.</p>"},

        {'summary': '<h1>Edit/View a card</h1><p>Click the pencil icon <span class="glyphicon glyphicon-pencil cards-edit"></span> in the upper right hand of this card.</p>',
         'cell': 'Todo',
         'backlog': False,
         'assign': False,
         'points': '2',
         'inbox': True,
         'detail': "<h1>Good Job!</h1><p>You just opened the detail window for this card. From here you can see everything about it. If you click around on it, you could edit it, go ahead and explore it a bit.</p><p>A card represents a unit of work in ScrumDo.  For teams doing Scrum, they are usually User Stories. <span>If you are brand new to Scrum, take a look at our </span><a href=\"http://help.scrumdo.com/beginners/scrum.html\">Beginners Guide.</a></p><p>All of the cards in this tutorial workspace have more information if you open them.</p><p>When you're done with this card, feel free to close or save this window with the buttons in the upper right.</p>"},

        {'summary': '<h1>Move Cards</h1><p>You can drag these cards into the columns on the right to track what is happening with them.</p>',
         'detail': "<p>There are a couple other ways to move cards:</p><ul><li>The dropdown on the right of this window.</li><li>By shift-clicking several cards on the board and then using the move-card button in the toolbar (the grid of squares).</li></ul>",
         'backlog': False,
         'assign': False,
         'inbox': True,
         'points': '3',
         'epic': 'e2',
         'cell': 'Todo'},

        {'summary': "<h1>Sub Tasks</h1><p>A lot of teams will create Sub Tasks on their user stories.  Open this card to see how.</p>",
         'cell': 'Todo',
         'tasks': True,
         'backlog': False,
         'assign': False,
         'inbox': True,
         'epic': 'e2',
         'points': '5',
         'detail': "<p>See the &#34;Tasks&#34; tab at the top of this window?  That will open a mini-board where you can create and manage the sub tasks for this card.</p><p>If you want to see your sub tasks on your main board, open up the board editor (see the next card) and make one of the columns a Task Column.</p><p>You can set up your task statuses in your workspace settings.</p>"},

        {'summary': "<h1>Customize your workspace</h1><p>Click the &#34;Settings&#34; button from the top right navbar bar to customize all aspects of your workspace.  </p>",
         'cell': 'Todo',
         'backlog': False,
         'assign': False,
         'inbox': True,
         'epic': 'e3',
         'points': '5',
         'detail': "<p>Within that, you can find the &#34;Board Editor&#34; that lets you change how this board looks to match your team's workflow.</p><p>When you're done with this tutorial workspace, you'll also find the Delete option in there under Admin Options</p>"},

        {'summary': "<h1>Create a card</h1><p>There are several ways to create a card, the easiest is the dropdown menu at the top of each column on your board.</p>",
         'cell': 'Todo',
         'inbox': False,
         'epic': 'e2',
         'detail': '<div>Some other ways:</div><ul><li>Open your backlog panel on the left and use the quick-add form at the top.</li><li>Open the card-list view of an iteration from the &#34;Card List&#34; tab and use the quick-add form at the top of that page.</li><li>Create a new card from the Planning tool</li><li>Import cards via Excel</li><li>Import GitHub issues via our integration</li></ul>'},

        {'summary': "<h1>Backlog</h1><p>Your backlog is where future work not currently being worked on goes.</p>",
         'cell': 'Todo',
         'backlog': False,
         'assign': False,
         'inbox': False,
         'points': '3',
         'detail': "<p>Open the panel on the left to get a miniature view of your backlog right from your board.</p><p>Or you can click on &#34;Backlog&#34; in the right navigation panel to go to your full backlog.</p>"},

        {'summary': "<h1>Getting Help</h1><p>Click the Gear menu in the upper right corner and choose Help/Support to ask us anything.</p>",
         'cell': 'Doing',
         'backlog': False,
         'assign': False,
         'inbox': False,
         'points': '2',
         'detail': '<p>We have some guides available at: <a href="http://help.scrumdo.com/help/">http://help.scrumdo.com/help/</a></p><p>You can also email us: <a href="mailto:support@scrumdo.com">support@scrumdo.com</a></p>'},


        {'summary': "<h1>Create an Iteration</h1><p>You're looking at a default iteration we made for you. You can create a new one from Workspace Summary page by clicking the &#34;New Iteration&#34; button.</p>",
         'cell': '',
         'backlog': True,
         'assign': False,
         'inbox': False,
         'epic': 'e3',
         'points': '2',
         'detail': "<p>If you're doing Scrumban or Kanban with continuous flow, leave the dates blank.  As cards are completed and no longer needed, you can archive them to keep things tidy.</p>"},

        {'summary': "<h1>Planning Tool</h1><p>The planning tool lets you create Collections to categorize your cards, and to plan out your iterations.</p>",
         'cell': '',
         'backlog': True,
         'assign': False,
         'inbox': False,
         'epic': 'e2',
         'points': '8',
         'detail': "<p>Click on Planning in the top right navbar to get to it.</p>"},

        {'summary': "<h1>Invite Other People</h1><p>You can invite other people via 'Teams' from your organization dashboard.</p>",
         'cell': '',
         'backlog': True,
         'assign': False,
         'inbox': False,
         'epic': 'e3',
         'points': '5',
         'detail': "<p>Teams also define the access people have and what workspaces they can access.</p>"},

        {'summary': 'Create a ScrumDo Trial',
         'cell': 'Done',
         'inbox': False,
         'points': '5',
         'detail': 'Since you\'re seeing this, you have already completed this one!',
         'label': 'Feature'},


        {'summary': "<h1>Reports</h1><p>Track your progress in your workspace with reports.</p>",
         'cell': '',
         'backlog': True,
         'inbox': False,
         'assign': False,
         'detail': "<p>Click the Reports link in the top right navbar.  There are a couple days of sample data in this workspace.</p>"},

        {'summary': "<h1>Edit Iteration</h1><p>You can change the name or dates of an iteration by going into the Workspace Summary view <span class='glyphicon glyphicon-align-justify'></span> and clicking specific Iteration Settings.</p>",
         'cell': '',
         'backlog': True,
         'assign': False,
         'inbox': False,
         'detail': "<p>That is also where you can delete or archive iterations.</p>"},

        {'summary': "<h1>Integrations</h1><p>Find integrations with GitHub, Hipchat, Flowdock, and Slack in the Settings link from the top right navbar.</p>",
         'cell': '',
         'backlog': True,
         'assign': False,
         'detail': "<p>For more information, see <a href='http://help.scrumdo.com/help/integrations.html'>http://help.scrumdo.com/help/integrations.html</a></p>"},

        {'summary': "<h1>Priortize Cards</h1><p>You can prioritze cards by business value, points, or dragging them up or down in the list.</p>",
         'cell': '',
         'backlog': True,
         'inbox': False,
         'assign': False,
         'value': True,
         'detail': "<p>You can also enter a time estimate and see value/time.</p>  <p>Change how you sort cards with the <i class='fa fa-sort-alpha-asc'></i> button.  Click the <i class='fa fa-unsorted'></i> priority button to toggle priority mode.</p>"},

        {'summary': "<h1>Planning Poker</h1><p>Use planning poker to estimate cards with your team.</p>",
         'cell': '',
         'backlog': True,
         'inbox': False,
         'assign': False,
         'value': False,
         'detail': "<p>Click the Planning Poker button at the top of the card edit window.</p>"},

    ]
    order = 10000
    label = project.labels.get(name='Feature')
    num = 1
    todoCell = project.boardCells.get(label='Todo')
    stories = []
    for card in cards:
        story = Story(project=project)
        story.summary = card['summary']
        story.local_id = num
        story.creator = user
        num += 1
        story.detail = card['detail']
        story.points = card.get('points', '?')
        story.rank = order
        story.epic_rank = order
        story.tags = "tutorial"
        order += 10000

        if card.get("value"):
            story.business_value = 2500
            story.estimated_minutes = 240

        if card.get("epic") in epics:
            story.epic = epics[card.get("epic")]

        if card.get('backlog'):
            story.iteration = backlog
        else:
            # story.cell =
            story.iteration = current
            story.save()
            # Move ever card into the Todo Cell
            movement = kanban_managers.moveStoryOntoCell(story, todoCell, user)
            movement.created += datetime.timedelta(days=-2)
            movement.save()
            if card['cell'] != 'Todo':
                # But some cards get moved into another later
                cell = project.boardCells.get(label=card['cell'])
                movement = kanban_managers.moveStoryOntoCell(story, cell, user)
                movement.created += datetime.timedelta(days=-1)
                movement.save()


        story.save()
        story.labels.add(label)
        if card.get('assign'):
            story.assignee.add(user)
        if card.get('tasks', False):
            Task(story=story, summary='Create your first task', order=10, status=1).save()
            Task(story=story, summary='Move a sub task', order=20, status=1).save()
            Task(story=story, summary='Open the sub task window', order=50, status=10).save()
        story.resetCounts()
        if card.get('inbox'):
            stories.append(story)

    stories.reverse()
    for story in stories:
        # For the tutorial, we want that card #1 at the top of the newsfeed.
        inbox_tasks.on_story_created(story.id, user.id)


    PointsLog(date=datetime.date.today() - datetime.timedelta(days=2),
              points_status1=40,
              points_status2=0,
              points_status3=0,
              points_status4=0,
              points_status5=0,
              points_status6=0,
              points_status7=0,
              points_status8=0,
              points_status9=0,
              points_status10=0,
              time_estimated=0,
              time_estimated_completed=0,
              points_total=40,
              project=project).save()

    PointsLog(date=datetime.date.today() - datetime.timedelta(days=1),
              points_status1=37,
              points_status2=0,
              points_status3=0,
              points_status4=0,
              points_status5=0,
              points_status6=0,
              points_status7=0,
              points_status8=0,
              points_status9=0,
              points_status10=3,
              time_estimated=0,
              time_estimated_completed=0,
              points_total=40,
              project=project).save()

    PointsLog(date=datetime.date.today() - datetime.timedelta(days=2),
              points_status1=25,
              points_status2=0,
              points_status3=0,
              points_status4=0,
              points_status5=0,
              points_status6=0,
              points_status7=0,
              points_status8=0,
              points_status9=0,
              points_status10=0,
              time_estimated=0,
              time_estimated_completed=0,
              points_total=25,
              iteration=current).save()

    PointsLog(date=datetime.date.today() - datetime.timedelta(days=1),
              points_status1=15,
              points_status2=0,
              points_status3=0,
              points_status4=10,
              points_status5=0,
              points_status6=0,
              points_status7=0,
              points_status8=0,
              points_status9=0,
              points_status10=0,
              time_estimated=0,
              time_estimated_completed=0,
              points_total=25,
              iteration=current).save()

    Favorite.setFavorite(1, project.id, user, True)


    scheduleRebuildStepMovements(project)
    return project

