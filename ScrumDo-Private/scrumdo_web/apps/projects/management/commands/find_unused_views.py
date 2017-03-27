#!/usr/bin/env python

# Script to scan a set of ELB based logs, match them against our URLS, and figure out which
# views are or aren't used anymore.

from django.core.management.base import BaseCommand
from django.core.urlresolvers import get_resolver
import os

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.views_left = get_resolver(None).reverse_dict.keys()
        logger.info("%d views to check" % (len(self.views_left)) )
        for logfilename in os.listdir("/Users/mhughes/Downloads/logs"):
            self.check_log_file("/Users/mhughes/Downloads/logs/" + logfilename)
            logger.info("Processed %s %d left" % (logfilename, len(self.views_left)) )


        for view in self.views_left:
            try:
                if hasattr(view, "api_name"):
                    logger.info(": %s %s" % (view.api_name.handler.__module__, view.api_name.handler) )
                elif hasattr(view, '__call__'):
                    logger.info("> %s %s" % (view.__module__, view) )
                else:
                    logger.info(view)
            except:
                logger.info(view)

    def check_log_file(self, logfilename):
        # Example log line:
        # 2015-11-25T22:59:37.218222Z app-scrumdo 116.58.10.24:54332 10.178.170.86:83 0.000061 0.049362 0.000041 200 200 0 543 "GET https://app.scrumdo.com:443/api/v3/organizations/motorcycle-house/projects/data-entry/stories/301390/news HTTP/1.1" "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2
        # date/time elb client_ip host_ip t1 t2 t3 status1 status2 ? ? "Request" ...
        with open(logfilename, 'r') as f:
            for line in f:
                request = line.split(" ")[12].split("?")[0]
                request = request.replace('https://app.scrumdo.com:443', '')

                try:
                    view = get_resolver(None).resolve(request).__dict__['func']
                    if view in self.views_left:
                        self.views_left.remove(view)
                except:
                    pass



