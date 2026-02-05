"""
Elasticsearch 索引重建命令
"""

from django_elasticsearch_dsl.management.commands import search_index


class Command(search_index.Command):
    """重建 Elasticsearch 索引"""

    def handle(self, *args, **options):
        """执行重建"""
        action = options.get('action', None)

        if action == 'delete':
            self.stdout.write(self.style.WARNING('删除旧索引...'))
            super().handle(*args, **options)
            self.stdout.write(self.style.SUCCESS('旧索引已删除'))
            return

        if action == 'rebuild':
            self.stdout.write(self.style.SUCCESS('开始重建索引...'))
            super().handle(*args, **options)
            self.stdout.write(self.style.SUCCESS('索引重建完成!'))
            return

        # 默认行为
        super().handle(*args, **options)
