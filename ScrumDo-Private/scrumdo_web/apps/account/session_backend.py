from django.contrib.sessions.backends.db import SessionStore as DBSessionStore

import base64
from django.contrib.sessions.exceptions import SuspiciousSession, SuspiciousOperation
from django.utils.crypto import constant_time_compare, salted_hmac
try:
    import cPickle as pickle
except ImportError:
    import pickle

import json

import logging


class SessionStore(DBSessionStore):
    """ We need a session store compatible with django 1.4 so we can share sessions with
        classic scrumdo.
    """

    def __init__(self, session_key=None):
        super(DBSessionStore, self).__init__(session_key)

    def _hash(self, value):
        key_salt = "django.contrib.sessions" + self.__class__.__name__
        return salted_hmac(key_salt, value).hexdigest()

    def encode(self, session_dict):
        "Returns the given session dictionary pickled and encoded as a string."
        pickled = pickle.dumps(session_dict, pickle.HIGHEST_PROTOCOL)
        hash = self._hash(pickled)
        return base64.encodestring(hash + ":" + pickled)

    def decode(self, session_data):
        encoded_data = base64.decodestring(session_data)
        try:
            # could produce ValueError if there is no ':'
            hash, pickled = encoded_data.split(':', 1)
            # expected_hash = self._hash(pickled)
            try:
                return pickle.loads(pickled)
            except:
                self.modified = True  # so we save it pickled...
                return json.loads(pickled)  # WE ONLY NEED THIS TEMPORARILY TODAY SINCE THERE ARE SOME ACTIVE JSON SESSIONS IN PRODUCTION RIGHT NOW


            # if not constant_time_compare(hash, expected_hash):
            #     raise SuspiciousOperation("Session data corrupted")
            # else:

        except Exception:
            # ValueError, SuspiciousOperation, unpickling exceptions. If any of
            # these happen, just return an empty dictionary (an empty session).
            return {}
