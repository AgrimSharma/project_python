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


from django.contrib import admin
from apps.projects.models import *
from django.conf import settings


class TaskAdmin(admin.ModelAdmin):
    list_display = ('story', 'summary', 'complete')
    search_fields = ('summary',)

class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('organization','name','start_date')

    def get_formset(self, request, obj=None, **kwargs):
        # Hack! Hook parent obj just in time to use in formfield_for_manytomany
        self.parent_obj = obj
        return super(ReleaseAdmin, self).get_formset( request, obj, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'projects':
            kwargs['queryset'] = Project.objects.filter(organization=self.parent_obj)
        return super(ReleaseAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(Release)
admin.site.register(Iteration)
admin.site.register(SiteStats)
admin.site.register(Epic)
admin.site.register(StoryTag)
admin.site.register(Commit)
admin.site.register(Task, TaskAdmin)
