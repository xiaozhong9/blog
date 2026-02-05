"""
搜索模块视图
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from elasticsearch_dsl import Q

from .models import ArticleDocument


class SearchView(APIView):
    """文章搜索视图"""

    @swagger_auto_schema(
        operation_summary='全文搜索',
        operation_description='搜索文章内容，支持高亮显示',
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description='搜索关键词',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description='分类过滤 (slug)',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'tags',
                openapi.IN_QUERY,
                description='标签过滤 (逗号分隔)',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'locale',
                openapi.IN_QUERY,
                description='语言过滤',
                type=openapi.TYPE_STRING,
                enum=['zh', 'en']
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description='页码',
                type=openapi.TYPE_INTEGER,
                default=1
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description='每页数量',
                type=openapi.TYPE_INTEGER,
                default=20
            ),
        ],
        responses={200: openapi.Response(description='搜索成功')}
    )
    def get(self, request):
        """执行搜索"""
        query = request.query_params.get('q', '').strip()
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        if not query:
            return Response({
                'code': 400,
                'message': '请输入搜索关键词',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 构建搜索查询
        search = ArticleDocument.search()

        # 多字段查询 (标题权重最高)
        q = Q(
            'multi_match',
            query=query,
            fields=['title^3', 'description^2', 'content'],
            fuzziness='AUTO'
        )
        search = search.query(q)

        # 过滤条件
        category = request.query_params.get('category')
        if category:
            search = search.filter('term', category_slug=category)

        locale = request.query_params.get('locale')
        if locale:
            search = search.filter('term', locale=locale)

        tags = request.query_params.get('tags')
        if tags:
            tag_list = tags.split(',')
            search = search.filter('terms', tags_names=tag_list)

        # 高亮显示
        search = search.highlight(
            'title',
            'description',
            'content',
            fragment_size=150,
            number_of_fragments=3,
            pre_tags=['<em>'],
            post_tags=['</em>']
        )

        # 排序
        search = search.sort('-published_at')

        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        search = search[start:end]

        # 执行搜索
        try:
            response = search.execute()
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'搜索失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 序列化结果
        results = []
        for hit in response:
            # 将 hit 转换为字典以便更安全地访问字段
            hit_dict = hit.to_dict()

            # 处理可能为数组的字段
            def get_first(value):
                if isinstance(value, list):
                    return value[0] if value else ''
                return value

            # 提取分类
            category_name = get_first(hit_dict.get('category_name'))
            category_slug = get_first(hit_dict.get('category_slug'))

            # 提取标签
            tags_names = hit_dict.get('tags_names', [])
            tags_list = tags_names if isinstance(tags_names, list) else []

            data = {
                'id': hit.id,
                'title': get_first(hit_dict.get('title')),
                'description': get_first(hit_dict.get('description')),
                'slug': get_first(hit_dict.get('slug')),
                'category': {
                    'name': category_name,
                    'slug': category_slug,
                } if category_name else None,
                'tags': [
                    {'name': tag}
                    for tag in tags_list
                ],
                'locale': get_first(hit_dict.get('locale')),
                'reading_time': hit_dict.get('reading_time'),
                'featured': hit_dict.get('featured'),
                'view_count': hit_dict.get('view_count'),
                'published_at': get_first(hit_dict.get('published_at')),
                'highlight': hit.meta.highlight.to_dict() if hasattr(hit.meta, 'highlight') else None
            }
            results.append(data)

        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'items': results,
                'total': response.hits.total.value,
                'page': page,
                'page_size': page_size,
                'query': query
            }
        })


class SearchSuggestView(APIView):
    """搜索建议视图"""

    @swagger_auto_schema(
        operation_summary='搜索建议',
        operation_description='根据输入获取搜索建议',
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description='输入前缀',
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={200: openapi.Response(description='获取成功')}
    )
    def get(self, request):
        """获取搜索建议"""
        query = request.query_params.get('q', '').strip()

        if not query or len(query) < 2:
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'suggestions': []
                }
            })

        # 使用 match_phrase_prefix 查询实现前缀匹配
        search = ArticleDocument.search()
        search = search.query('match_phrase_prefix', title=query)
        search = search[:10]  # 限制结果数量

        response = search.execute()

        # 提取建议
        suggestions = []
        for hit in response:
            hit_dict = hit.to_dict()
            title = hit_dict.get('title', '')
            if isinstance(title, list):
                title = title[0] if title else ''
            suggestions.append(title)

        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'suggestions': suggestions
            }
        })
