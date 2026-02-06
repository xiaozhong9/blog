"""
搜索模块视图

优化要点：
1. 添加详细的错误处理和日志
2. 限制查询复杂度防止 ES 过载
3. 添加查询结果缓存
4. 优化分页和排序
5. 支持更多搜索选项
"""

import logging
from typing import Optional, List, Dict, Any

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from elasticsearch_dsl import Q
from elasticsearch.exceptions import ApiError, TransportError

from .models import ArticleDocument
from utils.cache_utils import CacheKeyBuilder, get_or_set

logger = logging.getLogger(__name__)


# 搜索配置常量
MAX_PAGE_SIZE = 100  # 最大每页数量
DEFAULT_PAGE_SIZE = 20
DEFAULT_SEARCH_TIMEOUT = 3  # ES 查询超时（秒）
MIN_QUERY_LENGTH = 2  # 最小查询长度


class SearchView(APIView):
    """文章搜索视图

    支持全文搜索、分类过滤、标签过滤、高亮显示等功能
    """
    permission_classes = [AllowAny]  # 允许匿名访问

    @swagger_auto_schema(
        operation_summary='全文搜索',
        operation_description='搜索文章内容，支持高亮显示、多字段搜索',
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
            openapi.Parameter(
                'sort',
                openapi.IN_QUERY,
                description='排序方式',
                type=openapi.TYPE_STRING,
                enum=['published_at', 'view_count', 'like_count', '-published_at', '-view_count', '-like_count'],
                default='-published_at'
            ),
        ],
        responses={200: openapi.Response(description='搜索成功')}
    )
    def get(self, request):
        """执行搜索"""
        query = self._get_query_param(request)
        page, page_size = self._get_pagination_params(request)
        sort_by = request.query_params.get('sort', '-published_at')

        # 参数验证
        if not query:
            return self._error_response('请输入搜索关键词', status.HTTP_400_BAD_REQUEST)

        if len(query) < MIN_QUERY_LENGTH:
            return self._error_response(
                f'搜索关键词至少需要 {MIN_QUERY_LENGTH} 个字符',
                status.HTTP_400_BAD_REQUEST
            )

        try:
            # 暂时禁用缓存，直接执行搜索
            result = self._perform_search(query, request, page, page_size, sort_by)

            return Response({
                'code': 200,
                'message': 'success',
                'data': result
            })

        except (ApiError, TransportError) as e:
            logger.error(f"Elasticsearch 搜索失败: {e}, 查询: {query}")
            return self._error_response(
                '搜索服务暂时不可用，请稍后重试',
                status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.exception(f"搜索处理异常: {e}")
            return self._error_response(
                '搜索失败，请检查参数',
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_query_param(self, request) -> str:
        """获取并清理查询参数"""
        return request.query_params.get('q', '').strip()

    def _get_pagination_params(self, request) -> tuple[int, int]:
        """获取并验证分页参数"""
        page = max(1, int(request.query_params.get('page', 1)))
        page_size = min(
            MAX_PAGE_SIZE,
            max(1, int(request.query_params.get('page_size', DEFAULT_PAGE_SIZE)))
        )
        return page, page_size

    def _perform_search(
        self,
        query: str,
        request,
        page: int,
        page_size: int,
        sort_by: str
    ) -> Dict[str, Any]:
        """执行实际的搜索操作"""

        # 构建搜索查询
        search = ArticleDocument.search()

        # 设置超时和最大结果窗口
        search = search.params(request_timeout=DEFAULT_SEARCH_TIMEOUT)
        search = search.params(size=page_size, from_=(page - 1) * page_size)

        # 构建多字段查询
        should_queries = [
            # 精确匹配标题（最高权重）
            Q('match', title={'query': query, 'boost': 5}),
            # 标题模糊匹配
            Q('match_phrase', title={'query': query, 'boost': 3}),
            # 描述匹配
            Q('match', description={'query': query, 'boost': 2}),
            # 内容匹配
            Q('match', content=query),
        ]

        # 添加模糊匹配（仅对较长的查询）
        if len(query) >= 3:
            should_queries.append(
                Q('multi_match',
                  query=query,
                  fields=['title^3', 'description^2', 'content'],
                  fuzziness='AUTO',
                  prefix_length=1)
            )

        q = Q('bool', should=should_queries, minimum_should_match=1)
        search = search.query(q)

        # 应用过滤器
        search = self._apply_filters(search, request.query_params)

        # 配置高亮
        search = search.highlight(
            'title',
            'description',
            'content',
            fragment_size=150,
            number_of_fragments=3,
            pre_tags=['<mark>'],
            post_tags=['</mark>'],
            no_match_size=150
        )

        # 排序
        search = search.sort(sort_by)

        # 执行搜索
        response = search.execute()

        # 序列化结果
        results = [self._serialize_hit(hit) for hit in response]

        # 获取总数（兼容不同版本的 elasticsearch-dsl）
        total = response.hits.total.value if hasattr(response.hits.total, 'value') else response.hits.total

        return {
            'items': results,
            'total': total,
            'page': page,
            'page_size': page_size,
            'query': query,
            'max_score': response.hits.max_score
        }

    def _apply_filters(self, search, params: Dict[str, str]):
        """应用搜索过滤器"""
        # 分类过滤
        category = params.get('category')
        if category:
            search = search.filter('term', category_slug=category)

        # 语言过滤
        locale = params.get('locale')
        if locale:
            search = search.filter('term', locale=locale)

        # 标签过滤（支持多个）
        tags = params.get('tags')
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            if tag_list:
                search = search.filter('terms', tags_names=tag_list)

        # 精选过滤
        featured = params.get('featured')
        if featured and featured.lower() in ('true', '1'):
            search = search.filter('term', featured=True)

        return search

    def _serialize_hit(self, hit) -> Dict[str, Any]:
        """序列化搜索结果"""
        hit_dict = hit.to_dict()

        def get_first(value):
            """获取字段值（处理数组情况）"""
            if isinstance(value, list):
                return value[0] if value else ''
            return value

        # 提取分类信息
        category_name = get_first(hit_dict.get('category_name'))
        category_slug = get_first(hit_dict.get('category_slug'))

        # 提取标签
        tags_names = hit_dict.get('tags_names', [])
        tags_list = tags_names if isinstance(tags_names, list) else []

        # 构建结果
        result = {
            'id': hit.id,
            'title': get_first(hit_dict.get('title')),
            'description': get_first(hit_dict.get('description')),
            'slug': get_first(hit_dict.get('slug')),
            'category': {
                'name': category_name,
                'slug': category_slug,
            } if category_name else None,
            'tags': [{'name': tag} for tag in tags_list],
            'locale': get_first(hit_dict.get('locale')),
            'reading_time': hit_dict.get('reading_time'),
            'featured': hit_dict.get('featured'),
            'view_count': hit_dict.get('view_count', 0),
            'like_count': hit_dict.get('like_count', 0),
            'comment_count': hit_dict.get('comment_count', 0),
            'published_at': get_first(hit_dict.get('published_at')),
            'score': hit.meta.score,
        }

        # 添加高亮结果
        if hasattr(hit.meta, 'highlight') and hit.meta.highlight:
            highlight_dict = hit.meta.highlight.to_dict()
            result['highlight'] = {
                'title': highlight_dict.get('title', []),
                'description': highlight_dict.get('description', []),
                'content': highlight_dict.get('content', []),
            }

        return result

    def _error_response(self, message: str, status_code: int) -> Response:
        """返回错误响应"""
        return Response({
            'code': status_code,
            'message': message,
            'data': None
        }, status=status_code)


class SearchSuggestView(APIView):
    """搜索建议视图

    提供基于前缀的搜索建议
    """
    permission_classes = [AllowAny]  # 允许匿名访问

    @swagger_auto_schema(
        operation_summary='搜索建议',
        operation_description='根据输入获取搜索建议（支持中文拼音）',
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description='输入前缀',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'size',
                openapi.IN_QUERY,
                description='返回数量',
                type=openapi.TYPE_INTEGER,
                default=10
            ),
        ],
        responses={200: openapi.Response(description='获取成功')}
    )
    def get(self, request):
        """获取搜索建议"""
        query = request.query_params.get('q', '').strip()
        size = min(20, int(request.query_params.get('size', 10)))

        if not query or len(query) < 1:
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'suggestions': []
                }
            })

        try:
            # 缓存建议结果（缓存 10 分钟）
            cache_key = CacheKeyBuilder.build('search_suggest', query, size)

            suggestions = get_or_set(
                cache_key,
                lambda: self._get_suggestions(query, size),
                ttl=600
            )

            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'suggestions': suggestions
                }
            })

        except ElasticsearchException as e:
            logger.error(f"Elasticsearch 建议查询失败: {e}")
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'suggestions': []  # 失败时返回空列表
                }
            })
        except Exception as e:
            logger.exception(f"搜索建议异常: {e}")
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'suggestions': []
                }
            })

    def _get_suggestions(self, query: str, size: int) -> List[str]:
        """获取搜索建议列表"""
        search = ArticleDocument.search()

        # 使用 completion suggester 或 match_phrase_prefix
        # 这里使用 match_phrase_prefix 支持前缀匹配
        search = search.query('match_phrase_prefix', title={'query': query, 'boost': 2})

        # 限制结果数量
        search = search[:size]

        response = search.execute()

        # 提取建议标题
        suggestions = set()  # 使用集合去重
        for hit in response:
            title = self._extract_title(hit)
            if title:
                suggestions.add(title)

        return list(suggestions)[:size]

    def _extract_title(self, hit) -> Optional[str]:
        """从搜索结果中提取标题"""
        hit_dict = hit.to_dict()
        title = hit_dict.get('title', '')
        if isinstance(title, list):
            title = title[0] if title else ''
        return title.strip() if title else None
