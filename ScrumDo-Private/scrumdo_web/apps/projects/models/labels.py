from django.db import models
from django.db.models.signals import post_save


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

    class Meta:
        app_label = 'projects'
        ordering = ["name"]
        db_table = "v2_projects_labels"

    def __unicode__(self):
        return "Label: %s/%s" % (self.project.name, self.name)

