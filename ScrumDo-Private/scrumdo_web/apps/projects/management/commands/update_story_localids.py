from django.core.management import BaseCommand
from apps.projects.models import Project, Story
from django.db.models import Count, Max

class Command(BaseCommand):
  
  def handle(self, *args, **options):
    #loop in projects to find duplicate stories
    for project in Project.objects.all().order_by("id"):
      unique_fields = ['local_id']
      duplicates = (Story.objects.values(*unique_fields)
                             .order_by()
                             .annotate(count_id=Count('id'))
                             .filter(count_id__gt=1, project=project))
      
      for duplicate in duplicates:
        print "For Project %s, found %s stories duplicate with local_id %s" % (project.id, duplicate["count_id"], duplicate["local_id"])
        maxlocal_id = Story.objects.filter(project=project).aggregate(Max("local_id"))
        next_local_id = maxlocal_id["local_id__max"]
        counter = 0
        for story in Story.objects.filter(project=project, local_id=duplicate["local_id"]).order_by("id"):
          counter += 1
          #skip first story wuth duplicate local_id
          if counter >1:
            next_local_id += 1
            print "    Story id %d with local_id %d has been updated to local_id %d" % (story.id, story.local_id, next_local_id)
            story.local_id = next_local_id
            story.save()
      