from django.db.models import fields

def model_differences(m1, m2, excludes = [], dicts=False):
    """ this function takes two models and compares them.
    optionally takes two dicts created by running model_instance.__dict__ """
    changes = {}
    if not dicts:
        m1 = m1.__dict__
        m2 = m2.__dict__
    for k in m1:
        if _different(m1[k], m2[k]) and (not k in excludes):
            changes[k] = (m1[k], m2[k])
    return changes

def _different(v1, v2):
    if v1 == v2:
        return False

    # We're going to treat None and the empty string as the same here.
    if (v1 == None) and (v2 == ""):
        return False

    if (v2 == None) and (v1 == ""):
        return False

    return True

def instanceof(obj, classes):
    for cl in classes:
        if isinstance(obj, cl):
            return True
    return False

def allinstances(objs, cl):
    for obj in objs:
        if not isinstance(obj, cl):
            return False
    return True
