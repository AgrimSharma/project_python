# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


import django.dispatch


project_created = django.dispatch.Signal(providing_args=["project","user"])

# Signal dispatched when a story is edited. (Not including status changes, see next signal)
# user = who did it, story = the story that changed, diffs=dict of what fields changed
story_updated = django.dispatch.Signal(providing_args=["story","user","diffs"])

# Signal dispatched when a story's status is changed.
# user = who did it, story = the story that changed.
story_status_changed = django.dispatch.Signal(providing_args=["story","user"])

# Signal dispatched when a story is deleted
# user = who did it, story = the story that changed.
story_deleted = django.dispatch.Signal(providing_args=["story","user"])

# Signal dispatched when a story is created
# user = who did it, story = the story that changed.
story_created = django.dispatch.Signal(providing_args=["story","user"])

# Signal dispatched when a story is moved into a different iteration.
story_moved = django.dispatch.Signal(providing_args=["story", "user"])

# Disabling mentions for now, they don't work right.
# story_mention = django.dispatch.Signal(providing_args=["story","user"])

# Dispatched when an epic is created
epic_created = django.dispatch.Signal(providing_args=["epic","user"])

# Dispatched when an epic is created
epic_updated = django.dispatch.Signal(providing_args=["epic","user","diffs"])

# Dispatched when an epic is created
epic_deleted = django.dispatch.Signal(providing_args=["epic","user"])


# Signal dispatched when a new task is created.
task_created = django.dispatch.Signal(providing_args=["task","user"])

# Signal dispatched when the status (done/not done) of a task changed.
task_status_changed = django.dispatch.Signal(providing_args=["task","user"])

# Signal dispatched when a task is edited
task_updated = django.dispatch.Signal(providing_args=["task","user"])

# Signal dispatched when a task is deleted.
# Note: it's already been deleted when this is dispatched.
task_deleted = django.dispatch.Signal(providing_args=["task","user"])

# Dispatched when an iteration is created.
iteration_created = django.dispatch.Signal(providing_args=["iteration","user"])
# Dispatched when an iteration hidden status changed.
iteration_updated = django.dispatch.Signal(providing_args=["iteration","user","hidden"])
# Dispatched when an iteration is deleted.
iteration_deleted = django.dispatch.Signal(providing_args=["iteration","user"])

# Dispatched when a news item is posted
news_posted = django.dispatch.Signal(providing_args=["news_item"])

# Dispatched when a attachment added
attachment_added = django.dispatch.Signal(providing_args=["story","user","fileData"])

#Dispatched when a note created
note_created = django.dispatch.Signal(providing_args=["note","user"])

#Dispatched when a note updated
note_updated = django.dispatch.Signal(providing_args=["note","user","diffs"])

#Dispatched when a note deleted
note_deleted = django.dispatch.Signal(providing_args=["note","user"])

#Dispatched when a attachment added to note
note_attachment_added = django.dispatch.Signal(providing_args=["note","user","fileData"])
