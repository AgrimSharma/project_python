
def setup_releases_for_story(story):
    releases = []
    for release in story.projects.releases.all():
        releases.append(release)
    for epic in story.epics.all():
        for release in epic.releases.all():
            releases.append(release)
    releases = set(releases)
    
    prune(list1, unique(list1, list2))
    story.release_tags
    
def prune(L, unique_items):
    """Remove all items in the 'unique_items' list from list L"""
    map(L.remove, unique_items)

def graft(L, unique_items):
    """Add all items in the list 'unique_items' from list L"""
    L.extend(unique_items)

def unique(L1, L2):
    """Return a list containing all items in 'L1' that are not in 'L2'"""
    return [item for item in L1 if item not in L2]