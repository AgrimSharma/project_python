Models
======

The models are used to design the database structure in the project. 
They are scattered around but the main tables are located in the projects and kanban applications.

Projects Models
***************

Models related to the projects specifics and storing most of the information for Tasks/Story, Releases, Iterations.

TimeEntry
----------

Model **TimeEntry** is storing the time spent on each card/task.
The data is stored in the db table **v2_projects_timeentry**

.. code-block:: python

    class TimeEntry(models.Model):
        user = models.ForeignKey(User, related_name="time_entries", verbose_name='user')
        organization = models.ForeignKey(Organization)
        project = models.ForeignKey("projects.Project", null=True)
        iteration = models.ForeignKey(Iteration, null=True)
        story = models.ForeignKey(Story, null=True, on_delete=models.SET_NULL, related_name="time_entries")
        task = models.ForeignKey(Task, null=True, on_delete=models.SET_NULL)
        minutes_spent = models.PositiveIntegerField()
        notes = models.TextField()
        date = models.DateField()

        def timestamp(self):
            return int((time.mktime(self.date.timetuple()) - time.timezone)*1000)

        class Meta:
            app_label = 'projects'
            db_table = "v2_projects_timeentry"

**Fields**:

* **minutes_spent** - Integer field storing the time spent on the pointed Story
* **notes** - Text field containing the leaved notes about why and how the time is spent
* **date** - Date field containing the date that the task was apointed/started to work on

Related classes: Story_, Task_, Iteration_, Project_, Organization_, **User**

The class is located in **apps/projects/models/timeentry.py**


TimeAllocation
---------------

Model **TimeAllocation** used to assigned time per iteration on a project. Its used to set the deadlines/milestones for each Iteration
The data is stored in the db table **v2_projects_timeallocation**

.. code-block:: python

    class TimeAllocation(models.Model):
        project = models.ForeignKey("projects.Project")
        iteration = models.ForeignKey(Iteration, null=True)
        user = models.ForeignKey(User)
        minutes_allocated = models.IntegerField(default=0)

        class Meta:
            app_label = 'projects'
            db_table = "v2_projects_timeallocation"

**Fields**:

* **minutes_allocated** - Integer field that stores the allocated minutes

Related classes: Project_, Iteration_, **User**

The class is located in apps/projects/models/timeallocation.py


TaskTagging
------------

Model **TaskTagging** is used to store the tags used in the task/card.
The data is stored in the db table **v2_projects_tasktagging**

.. code-block:: python

    class TaskTagging(models.Model):
        tag = models.ForeignKey(StoryTag, related_name="tasks")
        task = models.ForeignKey(Task, related_name="task_tags")

        @property
        def name(self):
            return self.tag.name

        class Meta:
            app_label = 'projects'
            db_table = "v2_projects_tasktagging"

Related classes: StoryTag_, Task_
s
The class is located in apps/projects/models/tasktagging.py


Task
----

Model **Task** stores the information about each card.
The data is stored in the db table **v2_projects_task**

.. code-block:: python

    class Task(models.Model):
        story = models.ForeignKey("projects.Story", related_name="tasks")
        summary = models.TextField(blank=True)
        assignee = models.ForeignKey(User, related_name="assigned_tasks", verbose_name='assignee', null=True, blank=True)
        order = models.PositiveIntegerField( default=0 )
        tags_cache = models.CharField(max_length=512, blank=True, null=True, default=None)
        estimated_minutes = models.IntegerField(default=0)
        status = models.IntegerField(default=1, validators=[validators.MinValueValidator(1), validators.MaxValueValidator(10)])
        modified = models.DateTimeField('modified', auto_now=True)
        tags_to_delete = []
        tags_to_add = []


**Fields**:

* **summary** - detailed description/summary of the task, allowed to be blank (*blank=True*)
* **order** - task order
* **tags_cache** - tag cache - a long string, that is splited and used for filtering
* **estimated_minutes** - a assumption for the time the task will take to complete
* **status** - status of the card, that is calculated by a strange logic of slicing some strings in projects(Todo, .... or similar custom ones)
* **modified** - Date and time of each modification of the task (its auto_now on every save of the object)


**Functions**:

* **status_text** - gets the current status of the task, accordingly to the defined statuses per the project
* **task_tags_array** - builds the current task tags
* **task_tags_full** - Helper function to return an querySet with the tag objec preloaded
* **resetTagsCache** - resets the tags_cache value
* **complete (property)** - this property marks the task as completed (backward compatibility)
* **complete (complete.setter)** - this property marks the task as completed
* **tags (property)** - resets the cache if its empty
* **tags (tags.setter)** - manage and maintain tag cache
* **export_value** - <returns the summary> + [assignee.username] + <status>, where assignee.username is optional if the task is assigned to someone

Related classes: Story_, **User**

The class is located in apps/projects/models/tasks.py


StoryTagging
-------------

Model **StoryTagging** maintains the information about each tag for the stories.
The data is stored in the db table **v2_projects_storytagging**

.. code-block:: python

    class StoryTagging(models.Model):
        tag = models.ForeignKey("projects.StoryTag", related_name="stories")
        story = models.ForeignKey("projects.Story", related_name="story_tags")


**Funtions**:

* **name (property)** - returns the current tag name

Related classes: StoryTag_, Story_

The class is located in apps/projects/models/storytagging.py


StoryTag
--------

Model **StoryTag** contains the information about each tag for the stories.
The data is stored in the db table **v2_projects_storytag**

.. code-block:: python

    class StoryTag(models.Model):
        project = models.ForeignKey("projects.Project", related_name="tags")
        name = models.CharField('name', max_length=32)

**Fields**:

* **name** - char field containing the project tag

Related classes: Project_

The class is located in apps/projects/models/storytag.py


StoryAttributes
---------------
Model **StoryAttributes** stores some additional information about each Story_ object.
The data is stored in the db table **v2_projects_storyattributes**



.. code-block:: python

    class StoryAttributes( models.Model ):
        story = models.ForeignKey( Story, related_name="extra_attributes")
        context = models.CharField(max_length=6)
        key = models.CharField(max_length=4)
        value = models.CharField(max_length=10)

**Fields**:

* **context** - char field containing some context value    ... (**what is the use of this ?**)
* **key** - char field containing some key (max 4 chars)    ... (**what is the use of this ?**)
* **value** - char field containing some value(max 10 chars)... (**what is the use of this ?**)
    
Related classes: Story_

The class is located in apps/projects/models/storyattributes.py


Story
-----
Model **Story** stores the information each Story/Card and its one of the main data holder tables in the project.

Need a lot of help with this one ...

.. code-block:: python

    class Story(models.Model):
        # Why are these 4 statuses duplicated from the module level?
        STATUS_TODO = 1
        STATUS_DOING = 4
        STATUS_REVIEWING = 7
        STATUS_DONE = 10
        business_value = models.PositiveIntegerField(default=0)
        rank = models.IntegerField(default=500000)
        epic_rank = models.IntegerField(default=500000)  # Rank of this card inside epic views
        release_rank = models.IntegerField(default=500000)  # Rank of this card inside release views
        summary = models.TextField()
        local_id = models.IntegerField()
        detail = models.TextField(blank=True)
        creator = models.ForeignKey(User, related_name="created_stories", verbose_name=_('creator'))
        created = models.DateTimeField(_('created'), auto_now_add=True)
        modified = models.DateTimeField(_('modified'), auto_now=True)
        assignee = models.ManyToManyField(User,
                                          blank=True,
                                          verbose_name=_('assignees'),
                                          db_table='v2_projects_story_assignee_m2m',
                                          related_name="assigned_stories")

        points = models.CharField('points', max_length=4, default="?", blank=True)
        iteration = models.ForeignKey("projects.Iteration", related_name="stories")
        project = models.ForeignKey("projects.Project", related_name="stories")
        status = models.IntegerField(default=1, validators=[validators.MinValueValidator(1), validators.MaxValueValidator(10)])
        card_type = models.IntegerField(default=1, validators=[validators.MinValueValidator(1), validators.MaxValueValidator(10)])
        category = models.CharField(max_length=25, blank=True, null=True)
        extra_1 = models.TextField(blank=True, null=True)
        extra_2 = models.TextField(blank=True, null=True)
        extra_3 = models.TextField(blank=True, null=True)
        epic = models.ForeignKey("projects.Epic", null=True, blank=True, related_name="stories")

        # These next 5 fields are added in to cache some values so we can
        # reduce the number of queries when displaying long lists of stories.
        # They are updated through signals and can be reset with self.resetCounts()

        task_counts = models.CommaSeparatedIntegerField(max_length=44, default="0,0,0,0,0,0,0,0,0,0")
        comment_count = models.IntegerField(default=0)
        has_external_links = models.BooleanField(default=False)
        has_attachment = models.BooleanField(default=False)
        has_commits = models.BooleanField(default=False)
        tags_cache = models.CharField(max_length=512, blank=True, null=True, default=None)
        epic_label = models.CharField(max_length=32, blank=True, null=True, default=None)
        assignees_cache = models.CharField(max_length=512, blank=True, null=True, default=None)

        estimated_minutes = models.IntegerField(default=0)
        task_minutes = models.IntegerField(default=0)

        cell = models.ForeignKey("kanban.BoardCell", on_delete=models.SET_NULL, null=True, default=None, related_name="stories", blank=True)

        due_date = models.DateTimeField(null=True, blank=True)
        
        release = models.ForeignKey('projects.Story',
                                      null=True,
                                      blank=True,
                                      on_delete=models.SET_NULL,
                                      default=None)

        tags_to_delete = []
        tags_to_add = []

        tasks_to_export = []

        tracker = FieldTracker(fields=['tags_cache', 'cell_id'])


**Predefined Values**:

* **STATUS_TODO** - initial default value for TODO status = 1
* **STATUS_DOING** - initial default value for DOING status = 4
* **STATUS_REVIEWING** - initial default value for REVIEWING status = 7
* **STATUS_DONE** - initial default value for DONE status = 10



**Fields**:

* **business_value** - **UNKNOWN MEANING**
* **rank** - **UNKNOWN MEANING**
* **epic_rank** -  **UNKNOWN MEANING**
* **release_rank** - **UNKNOWN MEANING** (i suppose all ranks represent the card type - normal, epic or otherwise)
* **summary** - short description/headline of the story/card
* **local_id** - current number of the story for the project (i.e. card number #CARD <ID>)
* **detail** - full description of the story/card
* **created** - date of creating (Note: Automatically gets current date on creation)
* **modified** - date of modifying (Note: Automatically changes when saving the object)
* **assignee** - stores all assignees that are on this task
* **points** - **UNKNOWN MEANING**
* **status** - integer representation of the status
* **card_type** - integer representation of the card type
* **category** - name of the category the card is in
* **extra_1 - extra_3** - extra custom text fields
* **task_counts** - **UNKNOWN MEANING**
* **comment_count** - stores the comment counts
* **has_external_links** - stores if there is an external link (**UNKNOWN MEANING**)
* **has_attachment** - stores if there is an attachment
* **has_commits** - shows if there are commits in github (true/false)
* **tags_cache** - contains the tags for the task
* **epic_label** - epic label title if the story is epic
* **assignees_cache** - stores a cache of known assignees
* **estimated_minutes** - an assumption for time need to do the story
* **task_minutes** - actual time needed to complete the task
* **cell** - foreign key that shows in which cell in the board is the story currently in
* **due_date** - deadline date
* **release** - **UNKNOWN MEANING**
* **tags_to_delete - tags_to_add** - used for tagging changes
* **tracker** - **UNKNOWN MEANING**

**Funtions**:

* **clean_fields** - status field validation
* **full_epic_label** - gets the full epic label if one exists
* **resetCounts and all resets what and why ?** - **UNKNOWN MEANING**


.. code-block:: python

    def resetTaskCount(self):
        counts = [0] * 10
        for task in self.tasks.all():
            counts[task.status-1] += 1
        self.task_counts = ",".join([str(c) for c in counts])

*From where do we get tasks (and tasks.all() alternatively) in the Story class ?* UNKNOWN MEANING


Related classes: **User**, Iteration_, Project_, Epic_, BoardCell_, Story_

The class is located in apps/projects/models/story.py



SiteStats
----------
Model **SiteStats** is a statistical data container that stores the current users, project and story counts. The date field updates automatic on every save of the object.

.. code-block:: python

    class SiteStats(models.Model):
        user_count = models.IntegerField()
        project_count = models.IntegerField()
        story_count = models.IntegerField()
        date = models.DateField(auto_now=True)

Related classes: None

The class is located in apps/projects/models/sitestats.py


SavedQuery
----------
Model **SavedQuery** used to store custom queries *(SQL queries for the DB or in-app client queries? unknown meaning)*

.. code-block:: python

    class SavedQuery(models.Model):
        creator = models.ForeignKey(User)
        name = models.CharField(max_length=100)
        query = models.CharField(max_length=255)


Related classes: **User**

The class is located in apps/projects/models/savedquery.py


ReleaseStat
------------
Model **ReleaseStat** is a statistical data container similar to SiteStats_ in this case it stores the information about each release.
How many are the total cards, the completed ones and those still in progress.

.. code-block:: python

    class ReleaseStat(models.Model):
        release = models.ForeignKey("projects.Story", related_name='stats')

        date = models.DateField()

        cards_total = models.IntegerField(default=0)
        cards_completed = models.IntegerField(default=0)
        cards_in_progress = models.IntegerField(default=0)

        points_total = models.IntegerField(default=0)
        points_completed = models.IntegerField(default=0)
        points_in_progress = models.IntegerField(default=0)

Related classes: Story_

The class is located in apps/projects/models/releasestat.py


ReleaseLog
----------
Model **ReleaseLog** is a log data container that stores the **points** and **stories** statuses and some counters and time trackers.

.. code-block:: python

    class ReleaseLog(models.Model):
        release = models.ForeignKey(Release, related_name="points_log")
        date = models.DateTimeField()
        points_status1 = models.IntegerField(default=0)
        points_status2 = models.IntegerField(default=0)
        points_status3 = models.IntegerField(default=0)
        points_status4 = models.IntegerField(default=0)
        points_status5 = models.IntegerField(default=0)
        points_status6 = models.IntegerField(default=0)
        points_status7 = models.IntegerField(default=0)
        points_status8 = models.IntegerField(default=0)
        points_status9 = models.IntegerField(default=0)
        points_status10 = models.IntegerField(default=0)

        stories_status1 = models.IntegerField(default=0)
        stories_status2 = models.IntegerField(default=0)
        stories_status3 = models.IntegerField(default=0)
        stories_status4 = models.IntegerField(default=0)
        stories_status5 = models.IntegerField(default=0)
        stories_status6 = models.IntegerField(default=0)
        stories_status7 = models.IntegerField(default=0)
        stories_status8 = models.IntegerField(default=0)
        stories_status9 = models.IntegerField(default=0)
        stories_status10 = models.IntegerField(default=0)

        points_total = models.IntegerField()
        story_count = models.IntegerField()
        total_time_spent = models.IntegerField()
        time_estimated = models.IntegerField(default=0)  # total of time of stories estimated.
        time_estimated_completed = models.IntegerField(default=0)  # total of estimates from compelted stories

Related classes: Release_

The class is located in apps/projects/models/releaselog.py


Release
-------

Model **Release** is a container that enwraps data about the projects, stories and epics for a statistical and functionality features


.. code-block:: python

    class Release(models.Model):
        name = models.CharField(max_length=128)
        start_date = models.DateField(help_text="Date that work on this release is planned to start.")
        delivery_date = models.DateField(help_text="Date that this release is expected to be delivered/completed.")
        organization = models.ForeignKey(Organization, related_name="releases")
        projects = models.ManyToManyField(Project, related_name="releases")
        stories = models.ManyToManyField(Story, related_name="releases")
        epics = models.ManyToManyField(Epic, related_name="releases")
        shared = models.BooleanField(default=False, help_text="Should a public page about this release be created?")
        key = models.CharField(max_length=32)
        calculating = models.BooleanField(default=False)
        order = models.IntegerField(default=1)

Related classes: Organization_, Project_, Story_, Epic_

The class is located in apps/projects/models/release.py


PullRequest
-----------

Model **PullRequest** is a feature class that ensures the connection with the Github features.

.. code-block:: python

    class PullRequest(models.Model):
        STATUS = Choices((0, 'open', 'Open'), (1, 'closed', 'Closed'))
        state = models.IntegerField(choices=STATUS, default=STATUS.open)
        stories = models.ManyToManyField(Story, related_name="pull_requests")
        created = models.DateTimeField(auto_now_add=True)
        name = models.CharField(max_length=64, default="")
        full_text = models.TextField()
        link = models.CharField(max_length=200, unique=True)

Related classes: Story_

The class is located in apps/projects/models/pullrequest.py


ProjectShare
------------

Model **ProjectShare** is related to the feature of sharing a project and this class specifies what exactly to be shared (with the boolean fields)

.. code-block:: python

    class ProjectShare(models.Model):
        project = models.ForeignKey("projects.Project")
        iteration = models.ForeignKey("projects.Iteration")
        enabled = models.BooleanField(default=False)
        all_cards = models.BooleanField(default=False)
        tag = models.CharField(default='public', max_length=64)
        key = models.CharField(max_length=16)
        assignee = models.BooleanField( default=True )
        summary = models.BooleanField( default=True )
        detail = models.BooleanField( default=True )
        custom1 = models.BooleanField( default=True )
        custom2 = models.BooleanField( default=True )
        custom3 = models.BooleanField( default=True )
        time_estimates = models.BooleanField( default=True )
        points = models.BooleanField( default=True )
        epic = models.BooleanField( default=True )
        business_value = models.BooleanField( default=True )
        comments = models.BooleanField( default=True )
        tasks = models.BooleanField( default=True )

Related classes: Project_, Iteration_

The class is located in apps/projects/models/projectshare.py


Project
-------

Model **Project** is one of the major classes with a lot of information stored in it, there are a lot of other classes that are dependent 
on this one and its acting for them as their linking point.


.. code-block:: python

    class Project(models.Model):
        POINT_CHOICES_FIBO = ( ('?', '?'), ('0', '0'), ('0.5','0.5'), ('1', '1'),  ('2', '2'),  ('3', '3'),  ('5', '5'), ('8', '8'), ('13', '13'), ('20', '20'), ('40', '40'), ('100', '100'), ('Inf', 'Infinite') )
        POINT_CHOICES_MINIMAL = ( ('?', '?'), ('0', '0'),  ('1', '1'),  ('2', '2'),  ('3', '3'),  ('4', '4'), ('5', '5') )
        POINT_CHOICES_MAX = ( ('?', '?'), ('0', '0'), ('0.25', '0.25'), ('0.5','0.5'), ('1', '1'),  ('2', '2'),  ('3', '3'),   ('4', '4'), ('5', '5'),  ('6', '6'),  ('7', '7'), ('8', '8'),  ('9', '9'),  ('10', '10'), ('15', '15'), ('25', '25'), ('50', '50'), ('100', '100'), ('Inf', 'Infinite') )
        POINT_CHOICES_SIZES = ( ('?', '?'), ('1', 'XS'), ('5', 'S'), ('10','M'), ('15', 'L'),  ('25', 'XL')  )
        POINT_CHOICES_FIBO_BIG = ( ('?', '?'), ('0', '0'), ('1', '1'),  ('2', '2'),  ('3', '3'),  ('5', '5'), ('8', '8'), ('13', '13'), ('21', '21'), ('34', '34'), ('55', '55'), ('89','89'), ('144','144'), ('Inf', 'Infinite') )
        POINT_CHOICES_EXPO = (('1', '1'), ('2', '2'), ('4', '4'), ('8', '8'), ('16', '16'), ('32', '32'), ('64', '64') )
        POINT_RANGES = [POINT_CHOICES_FIBO, POINT_CHOICES_MINIMAL, POINT_CHOICES_MAX, POINT_CHOICES_SIZES, POINT_CHOICES_FIBO_BIG, POINT_CHOICES_EXPO]

        VELOCITY_TYPE_AVERAGE = 0
        VELOCITY_TYPE_AVERAGE_5 = 1
        VELOCITY_TYPE_MEDIAN = 2
        VELOCITY_TYPE_AVERAGE_3 = 3

        PROJECT_TYPE_SCRUM = 0
        PROJECT_TYPE_KANBAN = 1
        PROJECT_TYPE_PORTFOLIO = 2


        RENDER_MODE_RESIZE = 0
        RENDER_MODE_FIXED = 1
        
        TIME_TRACKING_TYPES_CHOICES = (('scrumdo', 'ScrumDo'),('harvest', 'Harvest'))

        # PROJECT_TYPE_CHOICES = ((PROJECT_TYPE_SCRUM, "Scrum"), (PROJECT_TYPE_KANBAN, "Scrumban"), (PROJECT_TYPE_PORTFOLIO, "Portfolio Planning"))
        PROJECT_TYPE_CHOICES = ((PROJECT_TYPE_SCRUM, "Scrum"), (PROJECT_TYPE_KANBAN, "Scrumban"), (PROJECT_TYPE_PORTFOLIO, "Portfolio Planning"))

        project_type = models.SmallIntegerField(default=PROJECT_TYPE_SCRUM, choices=PROJECT_TYPE_CHOICES )

        slug = models.SlugField(_('slug'), unique=True)
        name = models.CharField(_('name'), max_length=80 )
        creator = models.ForeignKey(User, verbose_name=_('creator'), related_name="projects_created")
        created = models.DateTimeField(_('created'), default=datetime.now)
        description = models.TextField(_('description'), blank=True, null=True, default="")

        parent = models.ForeignKey("projects.Project", default=None, null=True, related_name="children", blank=True)

        personal = models.BooleanField(default=False)

        color = models.IntegerField(default=0xf6764e)

        active = models.BooleanField( default=True)
        # private means only members can see the project
        private = models.BooleanField(_('private'), default=True)
        current_iterations = None
        default_iteration = None
        use_assignee = models.BooleanField( default=True )
        use_tasks = models.BooleanField( default=True )
        use_extra_1 = models.BooleanField( default=False )
        use_extra_2 = models.BooleanField( default=False )
        use_extra_3 = models.BooleanField( default=False )
        extra_1_label = models.CharField(  max_length=25, blank=True, null=True)
        extra_2_label = models.CharField(  max_length=25, blank=True, null=True)
        extra_3_label = models.CharField(  max_length=25, blank=True, null=True)

        status_names = models.CharField(max_length=100, default="Todo                          Doing                         Reviewing                     Done      ")
        task_status_names = models.CharField( max_length=100, default = "Todo                          Doing                                                       Done      ")

        card_types = models.CharField(max_length=100, default="User Story          Feature                                           Bug                           ")

        velocity_type = models.PositiveIntegerField( default=1 )
        point_scale_type = models.PositiveIntegerField( default=0 )
        velocity = models.PositiveIntegerField(null=True, blank=True)
        velocity_iteration_span = models.PositiveIntegerField( null=True, blank=True)
        iterations_left = models.PositiveIntegerField(null=True, blank=True)
        organization = models.ForeignKey(Organization,related_name="projects", null=True, blank=True)
        category = models.CharField( max_length=25, blank=True, null=True, default="")
        categories = models.CharField(max_length=1024, blank=True, null=True)
        token = models.CharField(max_length=7, default=_default_token)
        burnup_reset = models.IntegerField(default=0)
        burnup_reset_date = models.DateField(null=True, default=None, blank=True)
        has_iterations_hidden = models.BooleanField(default=False)
        abandoned = models.BooleanField(default=False) # has this project languished for far to long with no activity?
        live_updates = models.BooleanField(default=False)

        shared = models.CharField( max_length=25, blank=True, null=True, default=None)

        story_minutes = models.IntegerField(default=0)

        render_mode = models.IntegerField(default=RENDER_MODE_RESIZE)

        default_cell = models.ForeignKey("kanban.BoardCell", blank=True, null=True, on_delete=models.SET_NULL, related_name="+")

        release_project = models.ForeignKey("projects.Project", blank=True, null=True, default=None, on_delete=models.SET_NULL)
        time_tracking_mode = models.CharField(max_length=50, choices=TIME_TRACKING_TYPES_CHOICES, default='scrumdo')

        work_item_name = models.CharField(max_length=32, default="Card")
        folder_item_name = models.CharField(max_length=32, default="Epic")


Related classes: **User**, Project_, Organization_, BoardCell_

The class is located in apps/projects/models/project.py


PortfolioStoryMapping
---------------------

Model **PortfolioStoryMapping** is used to link/map a Story_ to the Project_ / Epic_ . 

**Unknown meaning**

.. code-block:: python

    class PortfolioStoryMapping(models.Model):
        story = models.ForeignKey("projects.Story", related_name="portfolio_mappings")
        target_project = models.ForeignKey("projects.Project", related_name="portfolio_mappings")
        target_epic = models.ForeignKey("projects.Epic")


Related classes: Project_, Story_, Epic_

The class is located in apps/projects/models/portfoliostorymapping.py


PointsLog
---------

Model **PointsLog** is used the keep the points statuses and some time tracking. 

Unknown meaning

.. code-block:: python

    class PointsLog(models.Model):
        date = models.DateField()
        points_status1 = models.IntegerField(default=0)
        points_status2 = models.IntegerField(default=0)
        points_status3 = models.IntegerField(default=0)
        points_status4 = models.IntegerField(default=0)
        points_status5 = models.IntegerField(default=0)
        points_status6 = models.IntegerField(default=0)
        points_status7 = models.IntegerField(default=0)
        points_status8 = models.IntegerField(default=0)
        points_status9 = models.IntegerField(default=0)
        points_status10 = models.IntegerField(default=0)

        time_estimated = models.IntegerField(default=0)  # total of time of stories estimated.
        time_estimated_completed = models.IntegerField(default=0)  # total of estimates from compelted stories

        points_total = models.IntegerField()

        # content_type = models.ForeignKey(ContentType)
        # object_id = models.PositiveIntegerField()
        # related_object = generic.GenericForeignKey('content_type', 'object_id')
        iteration = models.ForeignKey("projects.Iteration", null=True, related_name='points_log')
        project = models.ForeignKey("projects.Project", null=True, related_name='points_log')


Related classes: Iteration_, Project_

The class is located in apps/projects/models/pointslog.py


OfflineJob
----------

Model **OfflineJob** is a class that is responsible for tracking the offline jobs (async tasks).

.. code-block:: python

    class OfflineJob(models.Model):
        organization = models.ForeignKey(Organization, related_name="offlineJobs")
        request_date = models.DateField(auto_now=True)
        owner = models.ForeignKey(User)
        completed = models.BooleanField(default=False)
        job_type = models.CharField(max_length=32)
        result = models.CharField(max_length=255, default='', blank=True, null=True)

Related classes: **User**, Organization_

The class is located in apps/projects/models/offlinejob.py



MilestoneAssignment
-------------------

Model **MilestoneAssignment** is a class obligated with storing information about when, who and what Story/Project have to be done in a certain deadline/milestone.
It keeps track of the different kind of cards (closed, in progress and total) and points.

.. code-block:: python


    class MilestoneAssignment(models.Model):
        assigned_project = models.ForeignKey("projects.Project")
        milestone = models.ForeignKey("projects.Story")
        active = models.BooleanField(default=True)
        assigned_date = models.DateTimeField(auto_now_add=True)

        STATUS = model_utils.Choices(
            (0, 'Assigned'),
            (1, 'Scoped'),
            (2, 'Sized'),
            (3, 'Developing'),
            (4, 'Verification'),
            (5, 'Completed'))

        status = models.SmallIntegerField(default=0, choices=STATUS)

        cards_total = models.IntegerField(default=0)
        cards_completed = models.IntegerField(default=0)
        cards_in_progress = models.IntegerField(default=0)

        points_total = models.IntegerField(default=0)
        points_completed = models.IntegerField(default=0)
        points_in_progress = models.IntegerField(default=0)


Related classes: Project_, Story_

The class is located in apps/projects/models/milestoneassignment.py


Label
-----

Model **Label** is a an class storing the data about labels for the different stories.


.. code-block:: python

    class Label(models.Model):
        name = models.CharField("name", max_length=150)
        color = models.IntegerField()
        project = models.ForeignKey("projects.Project", related_name="labels")
        stories = models.ManyToManyField("projects.Story",
                                         db_table="v2_projects_label_stories",
                                         related_name="labels")

        # This is a temporary field that we'll be using while both www and beta are running
        # different branches.  It tells us what category on www maps to this label
        mapped_category = models.CharField(max_length=100, default=None, blank=True, null=True)

        # This is a temporary field that we'll be using while both www and beta are running
        # different branches.  It tells us what card type (scrumban projects) on www maps to this label
        mapped_card_type = models.IntegerField(default=None, null=True)


**Legacy code**

    mapped_category - temporary field, to be removed in future releases
    map_card_type - temporary field, to be removed in future releases

Related classes: Project_, Story_

The class is located in apps/projects/models/label.py


Iteration
---------

Model **Iteration** a basic functionality class describing the Iterations information for a project.

.. code-block:: python

    class Iteration(models.Model):
        ITERATION_BACKLOG = 0
        ITERATION_WORK = 1
        ITERATION_ARCHIVE = 2
        name = models.CharField("name", max_length=100)
        detail = models.TextField('detail', blank=True)
        start_date = models.DateField(blank=True, null=True)
        end_date = models.DateField(blank=True, null=True)
        project = models.ForeignKey("projects.Project", related_name="iterations")
        default_iteration = models.BooleanField( default=False )
        locked = models.BooleanField(default=False)

        iteration_type = models.SmallIntegerField(default=ITERATION_WORK)

        include_in_velocity = models.BooleanField('include_in_velocity', default=True)
        hidden = models.BooleanField(default=False)

Related classes: Project_

The class is located in apps/projects/models/iteration.py


FileJob
-------

Model **FileJob** class storing the information for uploaded files as an attachments.

.. code-block:: python

    class FileJob(models.Model):
        attachment_file = models.FileField('attachment', upload_to=attachment_upload, null=True)
        organization = models.ForeignKey(Organization, related_name="generatedFiles")
        file_type = models.CharField(max_length=100)
        request_date = models.DateField(auto_now=True)
        owner = models.ForeignKey(User)
        completed = models.BooleanField(default=False)

Related classes: Organization_, **User**

The class is located in apps/projects/models/filejob.py

ExtraUserInfo
-------------

Model **ExtraUserInfo** is a class used to artificially extend the django default User class.


class ExtraUserInfo(models.Model):
    """We're going to keep a reference to a user's full name so we can do fast lookups on it."""
    user = models.ForeignKey(User)
    full_name = models.CharField(max_length=128, blank=True)

Related classes: **User**

The class is located in apps/projects/models/extrauserinfo.py


Epic
----

Model **Epic** is a class representing the more sophisticated type of cards/tasks. 
This class is used to keep track of the cards/tasks that are within the Epic card.


.. code-block:: python

    class Epic(models.Model):
        STATUS_INITIAL = 0
        STATUS_WRITTEN = 1
        STATUS_BLOCKED = 2
        STATUS_COMPLETED = 3
        STATUS_CHOICES = (
            (STATUS_INITIAL, 'Initial'),
            (STATUS_WRITTEN, 'Stories Written'),
            (STATUS_BLOCKED, 'Blocked'),
            (STATUS_COMPLETED, 'Completed'),
        )
        local_id = models.IntegerField()
        summary = models.TextField()
        parent = models.ForeignKey('self', related_name="children", on_delete=models.SET_NULL, null=True, verbose_name="Parent Epic", help_text="What epic does this one belong within?", )
        detail = models.TextField(blank=True)
        points = models.CharField('points',
                                  max_length=4,
                                  default="?",
                                  blank=True,
                                  help_text="Rough size of this epic (including size of sub-epics or stories).  Enter ? to specify no sizing.")
        project = models.ForeignKey("projects.Project", related_name="epics")
        order = models.IntegerField(default=5000)
        archived = models.BooleanField(default=False,
                                       help_text="Archived epics are generally hidden and their points don't count towards the project.")
        status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_INITIAL)

        cards_total = models.IntegerField(default=0)
        cards_completed = models.IntegerField(default=0)
        cards_in_progress = models.IntegerField(default=0)

        points_total = models.IntegerField(default=0)
        points_completed = models.IntegerField(default=0)
        points_in_progress = models.IntegerField(default=0)

        release = models.ForeignKey('projects.Story',
                                    related_name='+',
                                    null=True,
                                    blank=True,
                                    on_delete=models.SET_NULL,
                                    default=None)

Related classes: Epic_, Project_, Story_

The class is located in apps/projects/models/epic.py


Commit
------

Model **Commit** is a simple data container for the Commit history and its used for the Github interactions.

.. code-block:: python

    class Commit(models.Model):
        story = models.ForeignKey(Story, related_name="commits")
        created = models.DateTimeField(auto_now_add=True)
        name = models.CharField(max_length=24, default="")
        full_text = models.TextField()
        link = models.CharField(max_length=200)

Related classes: Story_

The class is located in apps/projects/models/commit.py



Comment
-------

Model **Comment** is a data container that stores the comments on each story as well as when and who made it.

.. code-block:: python

    class StoryComment(models.Model):
        story = models.ForeignKey("projects.Story", related_name='comments')
        date_submitted = models.DateTimeField(auto_now_add=True)
        comment = models.TextField()
        user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, default=None)

Related classes: Story_, **User**

The class is located in apps/projects/models/comment.py


BoardAttributes
---------------

Model **BoardAttributes** is a class that extends the Project information with some additional information.

.. code-block:: python

    class BoardAttributes(models.Model):
        project = models.ForeignKey("projects.Project", related_name="extra_attributes")
        context = models.CharField(max_length=6)
        key = models.CharField(max_length=4)
        value = models.TextField()

Related classes: Project_

The class is located in apps/projects/models/boardattributes.py


Kanban Models
***************

Kanban models are related to functionality and feature-specific usability. All of those class definitions are located in apps/kanban/models.py


Policy
------

Model **Policy** A policy represents a rule on a workflow step. For instance, it could be a WIP Limit.

.. code-block:: python

    class Policy(models.Model):
        POLICY_TYPE_STORY_WIP = 0   # The maximum number of stories allowed
        POLICY_TYPE_POINTS_WIP = 1  # The maximum number of points allowed
        POLICY_TYPE_MAX_AGE = 2     # The maximum age of a story in hours
        policy_type = models.SmallIntegerField(default=POLICY_TYPE_STORY_WIP)
        user_defined = models.BooleanField(default=False)
        name = models.CharField(max_length=128)
        related_value = models.IntegerField()  # for age records, max minutes the card can be.
                                               # otherwise # of cards or points.
        project = models.ForeignKey("projects.Project", related_name="policies", null=True)

Related classes: Project_


Workflow
--------

Model **Workflow** represents a series of steps a story can go through.  Those steps may or may not be displayed linearly on a board. 
Workflow is the logical progression, BoardGroups are the visual representation. Graphs/reports/etc are made on Workflows
In the UI, we call these report profile now.

.. code-block:: python

    class Workflow(models.Model):
        WORK_FLOW_TYPES = Choices((0, 'user', 'User Defined'), (1, 'generated', 'System Generated'))
        project = models.ForeignKey("projects.Project", related_name="workflows")
        name = models.CharField(max_length=128, blank=False)
        default = models.BooleanField(default=False)
        flow_type = models.SmallIntegerField(choices=WORK_FLOW_TYPES, default=WORK_FLOW_TYPES.user)

Related classes: Project_



WorkflowStep
------------

Model **WorkflowStep** stores the information about each step in a workflow. In the UI, we call these report profile steps now

.. code-block:: python

    class WorkflowStep(models.Model):
        order = models.IntegerField(default=0)
        workflow = models.ForeignKey(Workflow, related_name="steps")
        name = models.CharField(max_length=128)    
        report_color = models.IntegerField(default=0x448cca, null=True)
        mapped_status = models.SmallIntegerField(default=-1)

**Field Info**

**mapped_status** -    this field is for scrum projects that were converted to scrumban.
we remember the status of the cells that were created.  This way, we can still generate the stacked charts for these projects.
Over time, we should push users towards the real CFD (Cumulative Flow Diagram), once we do that we can retire this.


Related classes: Workflow_


BoardImage
----------

Model **BoardImage** stores the image for the board for each project.

.. code-block:: python

    class BoardImage(models.Model):
        sx = models.IntegerField()
        sy = models.IntegerField()
        ex = models.IntegerField()
        ey = models.IntegerField()
        project = models.ForeignKey("projects.Project", related_name="images")
        image_file = models.ImageField(upload_to=board_image_attachment_upload, height_field="image_height", width_field="image_width")
        image_height = models.IntegerField(default=0)
        image_width = models.IntegerField(default=0)

Related classes: Project_


BoardGraphic
------------

Model **BoardGraphic** stores the graphic elements for the board for each project

.. code-block:: python

    class BoardGraphic(models.Model):
        GRAPHIC_TYPE_LABEL = 0
        GRAPHIC_TYPE_ARROW = 1
        GRAPHIC_TYPE_RECTANGLE = 2
        GRAPHIC_TYPE_CIRCLE = 3

        graphic_type = models.IntegerField(default=GRAPHIC_TYPE_LABEL)
        label = models.CharField(max_length=128)

        project = models.ForeignKey("projects.Project", related_name="graphics")

        # Position...
        sx = models.IntegerField()
        sy = models.IntegerField()
        ex = models.IntegerField()
        ey = models.IntegerField()

        foreground = models.IntegerField(default=0xaaaaaa)
        background = models.IntegerField(default=0xaaaaaa)
        policy = models.ForeignKey(Policy, null=True, default=None)

Related classes: Project_, Policy_


BoardCell
---------
Model **BoardCell** defines a single location on a board where a story can be placed.


.. code-block:: python

    class BoardCell(models.Model):
        CELL_TYPE_STANDARD = 0
        CELL_TYPE_SPLIT = 1

        LAYOUT_NORMAL = 0
        LAYOUT_COMPACT = 1
        LAYOUT_LIST = 2
        LAYOUT_GRID = 3
        LAYOUT_COMPACT_GRID = 4
        LAYOUT_POKER = 5
        LAYOUT_FULL_WIDTH = 6
        LAYOUT_SEARCH = 7
        LAYOUT_TASKS = 8
        LAYOUT_TEAM = 9

        WAIT_TIME = 0
        SETUP_TIME = 1
        WORK_TIME = 2
        DONE_TIME = 3    
        
        
        # group = models.ForeignKey(BoardGroup, related_name="cells")
        # Note: There is a ForeignKey on projects.Story to BoardCell with a related_name of stories
        steps = models.ManyToManyField(WorkflowStep,
                                       db_table="v2_kanban_boardcell_steps",
                                       related_name="cells")
        project = models.ForeignKey("projects.Project", related_name="boardCells")  # duplicating this, so we can get all cells for a project in a single query
        cellType = models.SmallIntegerField(default=CELL_TYPE_STANDARD)
        label = models.CharField(max_length=100, null=True)

        full_label = models.CharField(max_length=100, null=True)

        layout = models.PositiveSmallIntegerField(default=LAYOUT_NORMAL)
        
        headerColor = models.IntegerField(default=0xaaaaaa)
        backgroundColor = models.IntegerField(default=0xfafafa)

        wip_policy = models.ForeignKey(Policy, null=True, default=None)

        wipLimit = models.IntegerField(default=-1)
        pointLimit = models.IntegerField(default=-1)

        x = models.IntegerField(default=0)
        y = models.IntegerField(default=0)
        width = models.IntegerField(default=200)
        height = models.IntegerField(default=200)

        policy_text = models.TextField(blank=True, default="")

        time_type = models.PositiveSmallIntegerField(default=WORK_TIME)

        leadTime = models.BooleanField(default=True)

        policies = models.ManyToManyField(Policy,
                                          related_name="cells",
                                          db_table="v2_kanban_boardcell_policies")

Related classes: WorkflowStep_, Project_, Policy_

CellMovementLog
---------------
Model **CellMovementLog** stores the last place that we saved to S3 for a given project.
We're going to save cell movements in S3 as flat files so that we can do faster reporting without hitting the database.


.. code-block:: python

    class CellMovementLog(models.Model):
        project = models.ForeignKey("projects.Project")
        workflow = models.ForeignKey(Workflow)
        last_cell_movement = models.IntegerField(null=True, default=0)

Related classes: Project_, Workflow_


TagMovementLog
--------------
Model **TagMovementLog** stores the last place that we saved to S3 for a given project identical to CellMovementLog_.s
We're going to save cell movements in S3 as flat files so that we can do faster reporting without hitting the database.


.. code-block:: python

    class TagMovementLog(models.Model):
        project = models.OneToOneField("projects.Project")
        last_tag_movement = models.IntegerField(null=True, default=0)

Related classes: Project_

TagMovement
-----------

Model **TagMovement** stores information for the story tags.

.. code-block:: python

    class TagMovement(models.Model):
        story = models.ForeignKey("projects.story")
        tags_cache = models.CharField(max_length=512)
        created = models.DateTimeField(auto_now_add=True)


        # These next five fields cache some values as of the tag movement record's creation
        # These are used in the filtering of reports.
        related_iteration = models.ForeignKey(Iteration, null=True, on_delete=models.SET_NULL, related_name='+')
        epic_id = models.IntegerField(default=0)
        label_ids = models.CharField(max_length=72, default='')
        assignee_ids = models.CharField(max_length=72, default='')
        points_value = models.DecimalField(max_digits=6, decimal_places=1, default="0.0")

Related classes: Story_, Iteration_


CellMovement
------------

Model **CellMovement** identical to TagMovement_ this class stores the information about the cards moves between cells.

.. code-block:: python

    class CellMovement(models.Model):
        user = models.ForeignKey(User, related_name='+', default=None, null=True)
        story = models.ForeignKey("projects.story")
        cell_to = models.ForeignKey(BoardCell, null=True, on_delete=models.SET_NULL, related_name='+')    
        created = models.DateTimeField(auto_now_add=True)    
        related_iteration = models.ForeignKey(Iteration, null=True, on_delete=models.SET_NULL, related_name='+')

        # These next four fields cache some values as of the cell movement record's creation
        # These are used in the filtering of reports.
        epic_id = models.IntegerField(default=0)
        label_ids = models.CharField(max_length=72, default='')
        tags = models.CharField(max_length=256, default='')
        assignee_ids = models.CharField(max_length=72, default='')
        points_value = models.DecimalField(max_digits=6, decimal_places=1)

Related classes: **User**, Story_, Iteration_


StepMovement
------------

Model **StepMovement** records when a story goes from one step in a workflow to another.  
            
.. note::

    1. Either side of that could be null if the boardCell isn't associated with a step
    2. A single move on a board, could produce multiple StepMovement records if cells are associated with more than one step
    3. The to/from should always be within the same workflow.


.. code-block:: python

    class StepMovement(models.Model):
        user = models.ForeignKey(User, related_name='+', default=None, null=True)
        story = models.ForeignKey("projects.story")
        step_from = models.ForeignKey(WorkflowStep, null=True, on_delete=models.SET_NULL, related_name='+')
        step_to = models.ForeignKey(WorkflowStep,   null=True, on_delete=models.SET_NULL, related_name='+')
        workflow = models.ForeignKey(Workflow)
        created = models.DateTimeField(auto_now_add=True)
        related_iteration = models.ForeignKey(Iteration, null=True, on_delete=models.SET_NULL, related_name='+')

Related classes: **User**, Story_, Workflowstep_, Workflow_, Iteration_


BacklogHistorySnapshot
----------------------
Model **BacklogHistorySnapshot** is a simple container for making Iteration snapshots/backlogs.

.. code-block:: python

    class BacklogHistorySnapshot(models.Model):
        created = models.DateTimeField(auto_now_add=True)
        backlog = models.ForeignKey("projects.iteration")

Related classes: Iteration_


BacklogHistoryStories
----------------------
Model **BacklogHistorySnapshot** is identical to BacklogHistorySnapshot_ with the difference that it makes a snapshot on a Story_ and links them with the Iteration_ from the previous snapshot.

.. code-block:: python

    class BacklogHistoryStories(models.Model):
        snapshot = models.ForeignKey(BacklogHistorySnapshot, related_name="stories")
        story = models.ForeignKey("projects.story")

Related classes: Story_, BacklogHistorySnapshot_


PolicyAge
---------
Model **PoliciAge** is used to calculate the age of stories in a policy.We need to keep this table around.  
You get one record with an entered date when a story enters a policy.When it exits that policy, you get an 
exited value filled in. If a story re-enters a new record is created.  You can find the age of a story in a 
policy by getting the record with that story/policy and a null exited. Records with an exited filled in are 
for historical & charting purposes

.. code-block:: python

    class PolicyAge(models.Model):
        story = models.ForeignKey("projects.story")
        policy = models.ForeignKey(Policy)
        entered = models.DateTimeField(auto_now_add=True)
        exited = models.DateTimeField(default=None, null=True)

Related classes: Story_, Policy_


StepStat
--------
Model **StepStat** stores daily data.

.. code-block:: python

    class StepStat(models.Model):
        created = models.DateField(auto_now_add=True)
        stories = models.IntegerField()
        points = models.IntegerField()

Related classes: **None**

RebuildMovementJob
------------------

Model **RebuildMovementJob** stores information about the rebuilding of project. **UNKNOWN MEANING**

.. code-block:: python

    class RebuildMovementJob(models.Model):
        initiator = models.ForeignKey(User, related_name='+', default=None, null=True)
        project = models.ForeignKey("projects.project",related_name='+')
        created = models.DateTimeField(auto_now_add=True)

Related classes: **User**, Project_

KanbanizeJob
------------

Model **KanbanizeJob** is responsible for maitaining the information for any transfering to Kanban methodology. **Unknown meaning**

.. code-block:: python

    class KanbanizeJob(models.Model):
        initiator = models.ForeignKey(User, related_name='+', default=None, null=True)
        source = models.ForeignKey("projects.project",related_name='+')
        destination = models.ForeignKey("projects.project", null=True,related_name='+')
        complete = models.BooleanField(default=False)
        config = models.TextField()
        created = models.DateTimeField(auto_now_add=True)

Related classes: **User**, Project_


BoardHeader
-----------

Model **BoardHeader** is a container for the heading information and specific settings on the board.


.. code-block:: python

    class BoardHeader(models.Model):
        project = models.ForeignKey("projects.project", related_name='headers')
        sx = models.IntegerField()
        sy = models.IntegerField()
        ex = models.IntegerField()    
        ey = models.IntegerField()
        background = models.IntegerField(default=0x444444)
        label = models.CharField(max_length=128)
        policy = models.ForeignKey(Policy, null=True, default=None)    
        policy_text = models.TextField(blank=True, default="")

Related classes: Project_, Policy_


KanbanStat
----------

Model **KanbanStat** is a model that stores statistical data.

.. code-block:: python

    class KanbanStat(models.Model):
        project = models.ForeignKey("projects.project")    
        daily_lead_time = models.IntegerField()  # in minutes
        daily_flow_efficiency = models.IntegerField()
        system_lead_time = models.IntegerField()  # in minutes
        system_flow_efficiency = models.IntegerField()
        cards_claimed = models.IntegerField(default=0)
        points_claimed = models.IntegerField(default=0)
        created = models.DateField(auto_now_add=True)

Related classes: Project_


SavedReport
-----------

Model **SavedReport** is a container that stores data about the auto and manualy generated reports.

.. code-block:: python

    class SavedReport(models.Model):
        DATE_FORMAT_TYPES = Choices((0, 'fixed', 'Fixed Dates'),
                                    (2, 'relative', 'Relative Dates'))

        name = models.CharField(max_length=60)
        project = models.ForeignKey("projects.Project")
        creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
        workflow = models.ForeignKey(Workflow)

        date_format = models.SmallIntegerField(choices=DATE_FORMAT_TYPES, default=DATE_FORMAT_TYPES.fixed)

        # Have to add these when we start caching aging report:
        # agingData=step
        # agingSteps=142937,142938,142939,142940,142942,142944,142945
        # agingTags=\
        # agingType=1
        startdate = models.DateField(null=True, default=None)
        enddate = models.DateField(null=True, default=None)

        # General report options
        report_type = models.CharField(max_length=5)  # cfd or lead for now, will expand later.
        burn_type = models.IntegerField(default=0)  # 0-3 for burn types
        y_axis = models.SmallIntegerField(default=1)
        lead_start_step = models.ForeignKey(WorkflowStep, null=True, related_name="+")
        lead_end_step = models.ForeignKey(WorkflowStep, null=True, related_name="+")
        cfd_show_backlog = models.BooleanField(default=False)
        interval = models.SmallIntegerField(default=-1)

        iteration = models.ForeignKey("projects.Iteration", default=None, null=True, on_delete=models.SET_NULL, related_name="+")

        # Filter options:
        assignee = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL, related_name="+")
        epic = models.ForeignKey("projects.Epic", null=True, default=None, on_delete=models.SET_NULL, related_name="+")
        label = models.ForeignKey("projects.Label", null=True, default=None, on_delete=models.SET_NULL, related_name="+")
        tag = models.CharField(max_length=255, null=True, default=None)

        aging_type = models.SmallIntegerField(default=0, choices=((0,'Step'),(1,'Tag')))
        aging_by = models.SmallIntegerField(default=0)
        aging_steps = models.CommaSeparatedIntegerField(max_length=255, null=True, default=None)
        aging_tags = models.CharField(max_length=255, default=None, null=True)

        # these next few entries will be used to help determine which saved reports to automatically run

        # The last time we automatically generated this report.
        last_generated = models.DateTimeField(null=True)

        # The last time this saved report was manually viewed via the reports interface
        last_manual_view = models.DateField(null=True)

        # The last time this saved report was viewed via an automatic means
        last_auto_view = models.DateField(null=True)

        # How many times has this saved report been viewed
        views = models.IntegerField(default=0)

        created = models.DateField(auto_now_add=True)

        # Was this saved report auto-generated by the system?
        generated = models.BooleanField(default=False)


Related classes: WorkflowStep_, Iteration_, **User**, Epic_, Label_


OrganizationVelocityLog
-----------------------

Model **OrganizationVelocityLog** - unknown meaning

.. code-block:: python

    class OrganizationVelocityLog(models.Model):
        organization = models.ForeignKey(Organization, related_name="velocity_log")
        created = models.DateTimeField(_('created'), default=datetime.datetime.now)
        velocity = models.IntegerField()

Related classes: Organization_

Organizations Models
********************

In this section are present the models related to the organizations functionality.


Team
----

Model **Team** is a wrapper that links members to a team that relates to specific Project_ and Organization_.

.. code-block:: python

    class Team(models.Model):
        ACCESS_CHOICES = [
            ('read', 'Read Only'),
            ('write', 'Read / Write'),
            ('admin', 'Administrator'),
            ('staff', 'Staff Member'),]
        members = models.ManyToManyField(User, verbose_name=_('members'), related_name="teams")

        projects = models.ManyToManyField("projects.Project",
                                          db_table="v2_organizations_team_projects",
                                          verbose_name=_('projects'),
                                          related_name="teams")

        organization = models.ForeignKey('Organization', related_name="teams")
        assignable = models.BooleanField(default=True)

        name = models.CharField( max_length=65 )
        access_type = models.CharField( max_length=25 , default="read", choices=ACCESS_CHOICES)

Related classes: **User**, Organization_, Project_

TeamInvite
----------

Model **TeamInvite** is used to manage the feature of inviting users to Team_.

.. code-block:: python

    class TeamInvite(models.Model):
        email_address = models.CharField(max_length=60)
        team = models.ForeignKey(Team, related_name="invites")
        key = models.CharField(max_length=8)

Related classes: Team_


Organization
------------

Model **Organization**  is used to storage container with descriptive fields regarding the Organizations.

.. code-block:: python

    class Organization(models.Model):
        name = models.CharField( max_length=65 )
        slug = models.SlugField(_('slug'), unique=True)
        creator = models.ForeignKey(User, verbose_name=_('creator'), related_name="organizations_created", null=False, blank=False)
        created = models.DateTimeField(_('created'), default=datetime.datetime.now)
        description = models.TextField(_('description'),  null=True, blank=True, default="")
        source = models.CharField(max_length=100, default="", blank=True)
        bill_to = models.TextField(null=True, blank=True, default="", help_text="Bill To address to put on invoices.")
        timezone = models.CharField(max_length=32, default="US/Eastern")
        end_of_week = models.PositiveSmallIntegerField(default=6, choices=( (0,'Monday'),(1,'Tuesday'),(2,'Wednesday'),(3,'Thursday'),(4,'Friday'),(5,'Saturday'),(6,'Sunday')) )
        allow_personal = models.BooleanField(default=True, help_text="Allow users to create personal projects.")
        active = models.BooleanField(default=True)

        PLANNING_MODES = Choices('unset', 'release', 'portfolio')
        planning_mode = models.CharField(choices=PLANNING_MODES, default=PLANNING_MODES.unset, max_length=10)

        CLASSIC_MODE_CLASSIC = 0
        CLASSIC_MODE_MIXED = 1
        CLASSIC_MODE_NEW = 2
        classic_mode = models.SmallIntegerField(default=CLASSIC_MODE_NEW)

Related classes: **User**