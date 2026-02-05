from django.apps import AppConfig
from django_elasticsearch_dsl.registries import registry


class SearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "search"

    def ready(self):
        """应用启动时建立 Elasticsearch 连接"""
        from elasticsearch_dsl import connections

        # 从 settings 获取配置
        from django.conf import settings

        if hasattr(settings, 'ELASTICSEARCH_DSL'):
            # 创建连接
            connections.configure(**settings.ELASTICSEARCH_DSL)
            self.verbose_name = "Search Module"
