from django.apps import AppConfig
import sys, traceback

import logging

logger = logging.getLogger(__name__)



class ProjectsApp(AppConfig):
    name = 'apps.projects'
    verbose_name = "ScrumDo Projects App"

    def ready(self):
        # so the signal gets hooked up correctly, we need to import this here.
        import signal_handlers


        # Need to force the search analyzer to use whitespace for the text field here,
        # there's a bug in elasticstack preventing it from being set correclty on index creation, so on startup of the
        # app, we'll see if it's set, and if not do it.
        try:
            from haystack import connections
            from django.conf import settings

            backend = connections.all()[0].get_backend()
            connection = backend.conn
            indexname = settings.HAYSTACK_CONNECTIONS['default']['INDEX_NAME']
            mapping = connection.indices.get_mapping(doc_type="modelresult", index=indexname)
            search_analyzer = mapping[indexname]['mappings']['modelresult']['properties']['text'].get('search_analyzer','')
            if search_analyzer != 'whitespace':
                logger.info("Setting search analyzer.")
                body = """{
                    "properties": {
                        "text": {
                            "type":"string",
                            "index_analyzer": "edgengram_analyzer",
                            "search_analyzer": "whitespace"
                            }
                        }
                    }"""
                connection.indices.put_mapping(doc_type="modelresult", index=indexname, body=body)
        except Exception as e:
            logger.error("Could not update index mappings.")
            traceback.print_exc()


