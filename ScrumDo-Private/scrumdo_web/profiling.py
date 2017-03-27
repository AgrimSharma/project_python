from django.core.exceptions import MiddlewareNotUsed
from django.conf import settings
import cProfile
import pstats
import marshal
from cStringIO import StringIO

from django.db import connection

import logging

import re

logger = logging.getLogger(__name__)

class SqldumpMiddleware(object):
    def process_response(self, request, response):        
        queries = {}
        for query in connection.queries:
            m = re.search('([A-Z]+).*FROM (\S+).*WHERE(.*)', query["sql"])
            if m:
                # Use this one to group like where clauses
                key = "%s %s %s" % (m.group(1), m.group(2), m.group(3))

                # Use this one to group like tables
                #key = "%s %s" % (m.group(1), m.group(2))

                # Use this one to see everything
                # key = query["sql"]
                
                if key in queries:
                    queries[key]["time"] += float(query["time"])
                    queries[key]["count"] += 1
                else:
                    queries[key] = { "time":float(query["time"]), "count":1 }
        for key in queries:
            q = queries[key]
            logger.debug("%04d %s %s" % (q["count"],q["time"],key) )            
        logger.debug("%04d Total SQL Queries" % len(connection.queries) )
        return response
        
class ProfileMiddleware(object):
    def __init__(self):
        if not settings.DEBUG:
            raise MiddlewareNotUsed()
        self.profiler = None

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG and ('profile' in request.GET
                            or 'profilebin' in request.GET):
            self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def process_response(self, request, response):
        if self.profiler:
            self.profiler.create_stats()
            out = StringIO()
            stats = pstats.Stats(self.profiler, stream=out)
            # Values for stats.sort_stats():
            # - calls           call count
            # - cumulative      cumulative time
            # - file            file name
            # - module          file name
            # - pcalls          primitive call count
            # - line            line number
            # - name            function name
            # - nfl                     name/file/line
            # - stdname         standard name
            # - time            internal time
            stats.sort_stats('time').print_stats(.2)
            print out.getvalue()

        return response