# Helper functions for managing the organization wide backlog.
from django.core.exceptions import ValidationError


def remove_project_parent(child, parent):
    if child.stories.filter(release__project=parent).count() > 0:
        raise ValidationError('Can not clear project parent because cards within the '
                              'project point to an existing release')

    if child.epics.filter(release__project=parent).count() > 0:
        raise ValidationError('Can not clear project parent because epics within the project '
                              'point to an existing release')

    child.parents.remove(parent)


def has_child(parent, child):
    """ Return strue if parent has child as a child project, or as any grand-child project"""
    for c in parent.children.all():
        if c == child:
            return True
        if has_child(c, child):
            return True
    return False


def add_project_parent(child, parent):
    if parent.organization_id != child.organization_id:
        raise ValidationError('Can not set project parent in a different organization')

    if child == parent:
        raise ValidationError('Can not set project as it\'s own parent')

    if child.personal or parent.personal:
        raise ValidationError('Personal projects can not participate in a project hierarchy.')

    if has_child(child, parent):
        # Make sure the parent isn't one of child's children for a circlular reference
        raise ValidationError('Can not set project as it\'s own ancester')

    child.parents.add(parent)


def clear_project_parents(project):
    """Removed the parent project from this one.  Raises an exception if doing so would invalidate
       a parent/child work relationship."""
    for parent in project.parents.all():
        remove_project_parent(project, parent)


def set_project_parents(child, parents):
    """Sets the parent of a child project.  Raises exception if the child already has a parent that it can't clear.
    """
    current = set(child.parents.all())
    desired = set(parents)

    to_add = desired - current
    to_remove = current - desired

    for parent in to_remove:
        remove_project_parent(child, parent)

    for parent in to_add:
        add_project_parent(child, parent)

