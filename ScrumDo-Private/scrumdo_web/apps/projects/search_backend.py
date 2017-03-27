from haystack.backends.elasticsearch_backend import ElasticsearchSearchEngine
from elasticstack.backends import ConfigurableElasticBackend


class ScrumDoConfigurableElasticBackend(ConfigurableElasticBackend):

    def __init__(self, connection_alias, **connection_options):
        super(ScrumDoConfigurableElasticBackend, self).__init__(connection_alias, **connection_options)

    def build_schema(self, fields):
        content_field_name, mapping = super(ScrumDoConfigurableElasticBackend, self).build_schema(fields)

        for field_name, field_class in fields.items():
            field_mapping = mapping[field_class.index_fieldname]

            if "search_analyzer" in field_mapping and "analyzer" in field_mapping:
                field_mapping['index_analyzer'] = field_mapping['analyzer']
                del field_mapping['analyzer']
                mapping.update({field_class.index_fieldname: field_mapping})

        return (content_field_name, mapping)



class ScrumDoConfigurableElasticSearchEngine(ElasticsearchSearchEngine):
    backend = ScrumDoConfigurableElasticBackend
