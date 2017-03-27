from haystack.indexes import SearchIndex, CharField, Indexable, IntegerField, MultiValueField, DateField
from elasticstack.fields import EdgeNgramField, CharField as CCharField, MultiValueField as CMultiValueField
from apps.projects.models import Story
from apps.kanban.models import CellMovement
from apps.projects.tasks import queueUpdateSolr

import logging

logger = logging.getLogger(__name__)



class ConfigurableFieldMixin(object):
    """
    A mixin which allows specifying the analyzer on a per field basis.
    """


class StoryIndex(SearchIndex, Indexable):
    # text = EdgeNgramField(document=True, use_template=True, analyzer="SDedgengram_analyzer")
    text = EdgeNgramField(document=True, use_template=True, analyzer="edgengram_analyzer", search_analyzer="whitespace")

    project_id = IntegerField(model_attr='project_id')
    organization_id = IntegerField(null=True)
    iteration_id = IntegerField(model_attr='iteration_id')
    local_id = IntegerField(model_attr='local_id')
    release_prefix = CharField(null=True)
    release_number = IntegerField(null=True)
    epic_number = CCharField(null=True, analyzer='text_ws_analyzer')
    epic_numbers = CMultiValueField(null=True, analyzer='text_ws_analyzer')
    assignee = MultiValueField(faceted=True)
    numeric_points = IntegerField(model_attr='points_value')
    created = DateField(model_attr='created', null=True)
    modified = DateField(model_attr='modified', null=True)
    last_moved = DateField(null=True)
    status = IntegerField(model_attr='status')
    status_text = CharField(model_attr='statusText', null=True)
    rank = IntegerField(model_attr='rank')
    creator = MultiValueField(faceted=True)
    tags = CMultiValueField(null=True, index_fieldname='alt_tag', analyzer="whitespace", search_analyzer="whitespace")

    card_type = CharField(null=True)
    cell_name = CharField(null=True)
    labels = MultiValueField(null=True)

    project_prefix = CharField(null=True)

    def queue_update_object(self, instance, **kwargs):
        if hasattr(instance, "skip_haystack"):
            return False
        queueUpdateSolr(instance.id)

    def read_queryset(self, using=None):
        return self.get_model().objects.select_related("release", "epic", "creator", "project", "cell").prefetch_related('assignee')

    def prepare_last_moved(self, story):
        try:
            return CellMovement.objects.filter(story=story).order_by("-created")[0].created
        except IndexError:
            return None
    
    def prepare_project_prefix(self, story):
        return story.project.prefix

    def prepare_release_number(self, story):
        if story.release:
            return story.release.local_id
        if story.epic and story.epic.release:
            return story.epic.release.local_id
        return None
    
    def prepare_release_prefix(self, story):
        if story.release:
            return str(story.release.project.prefix)
        if story.epic and story.epic.release:
            return str(story.epic.release.project.prefix)
        return None

    def prepare_card_type(self, story):
        return story.cardTypeText()

    def prepare_cell_name(self, story):
        if story.cell is None:
            return None
        return story.cell.full_label

    def prepare_organization_id(self, story):
        try:
            return story.project.organization_id
        except:
            return -1

    def prepare_epic_numbers(self, story):
        epic = story.epic
        rv = []
        while epic is not None:
            rv.append('epic_number_%s' % epic.local_id)
            epic = epic.parent
        return rv

    def prepare_epic_number(self, story):
        if not story.epic:
            return "epic_number_None"
        return 'epic_number_%s' % story.epic.local_id

    def prepare_project_id(self, story):
        try:
            return story.project_id
        except:
            return -1

    def prepare_tags(self, obj):
        return obj.tags.lower().split(",")

    def prepare_labels(self, obj):
        labels = [a.name for a in obj.labels.all()]
        return labels

    def prepare_assignee(self, obj): 
        rv = []
        task_assignees = [str(task.assignee) for task in obj.tasks.all() if task.assignee is not None]
        story_assignees = [str(a) for a in obj.assignee.all()]
        rv = story_assignees + task_assignees
        return rv
    
    def prepare_creator(self, obj): 
        return str(obj.creator)
         
    def get_updated_field(self):
        return "modified"
        
    def should_update(self, instance, **kwargs):
        if hasattr(instance, "skip_haystack"):
            return False
        return super(StoryIndex, self).should_update(instance, **kwargs)

    def get_model(self):
        return Story

    # def update(self):
    #     """Update the entire index"""
    #     self.backend.update(self, self.index_queryset(), commit=False)

    def update_object(self, instance, **kwargs):
        """
        Update the index for a single object. Attached to the class's
        post-save hook.
        """
        # Check to make sure we want to index this first.
        if self.should_update(instance, **kwargs):
            super(StoryIndex, self).update_object(instance, **kwargs)



# class EpicIndex(SearchIndex, Indexable):
#     text = CharField(document=True, use_template=True)
#     local_id = IntegerField(model_attr='local_id')
#     summary = CharField(model_attr='summary')
#     detail = CharField(model_attr='detail', null=True)
#     project_id = IntegerField(model_attr='project_id')
#     parent_id = IntegerField(model_attr='parent_id', null=True)
#     order = IntegerField(model_attr='order')
#     organization_id = IntegerField(null=True)
#     epic_number = CharField()
#
#     def get_model(self):
#         return Epic
#
#     def prepare_organization_id(self, epic):
#         try:
#             organization = epic.project.organization
#             if organization:
#                 return organization.id
#             return None
#         except:
#             return None
#
#     def prepare_epic_number(self, epic):
#         return 'epic_number_%s' % epic.local_id
#
#     def should_update(self, instance, **kwargs):
#         if hasattr(instance, "skip_haystack"):
#             return False
#         return super(EpicIndex, self).should_update(instance, **kwargs)
#
#     def update_object(self, instance, **kwargs):
#         """
#         Update the index for a single object. Attached to the class's
#         post-save hook.
#         """
#         # Check to make sure we want to index this first.
#         if self.should_update(instance, **kwargs):
#             super(EpicIndex, self).update_object(instance, **kwargs)
#             # self.backend.update(self, [instance], commit=False)

