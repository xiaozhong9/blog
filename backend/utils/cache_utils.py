"""
统一缓存工具模块

提供缓存键管理、缓存穿透/击穿防护、批量操作等工具
"""

from typing import Any, Callable, Optional, Union, List, Dict
from functools import wraps
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


# ============================================
# 缓存键前缀和版本管理
# ============================================

class CacheKeyPrefix:
    """缓存键前缀常量"""

    # 文章相关
    ARTICLE_STATS = "article_stats"
    ARTICLE_DETAIL = "article_detail"
    ARTICLE_LIST = "article_list"
    ARTICLE_RELATED = "article_related"

    # 用户相关
    USER_PROFILE = "user_profile"
    USER_PERMISSIONS = "user_permissions"

    # 统计相关
    STATS_OVERVIEW = "stats_overview"
    STATS_POPULAR = "stats_popular"

    # 分类和标签
    CATEGORY_LIST = "category_list"
    TAG_LIST = "tag_list"

    # 搜索相关
    SEARCH_RESULTS = "search_results"
    SEARCH_SUGGEST = "search_suggest"

    # 速率限制
    RATE_LIMIT = "rate_limit"


class CacheKeyBuilder:
    """缓存键构建器"""

    CACHE_VERSION = "v1"  # 缓存版本，变更时清空所有缓存

    @classmethod
    def build(cls, prefix: str, *parts: Union[str, int], version: Optional[str] = None) -> str:
        """
        构建标准化的缓存键

        Args:
            prefix: 键前缀
            *parts: 键的其他部分
            version: 版本号，默认使用全局版本

        Returns:
            str: 完整的缓存键
        """
        cache_version = version or cls.CACHE_VERSION
        parts_str = ":".join(str(p) for p in parts)
        return f"{settings.REDIS_CACHE_PREFIX}:{cache_version}:{prefix}:{parts_str}"

    @classmethod
    def article_stats(cls, article_id: int) -> str:
        """文章统计缓存键"""
        return cls.build(CacheKeyPrefix.ARTICLE_STATS, article_id)

    @classmethod
    def article_detail(cls, article_id: int) -> str:
        """文章详情缓存键"""
        return cls.build(CacheKeyPrefix.ARTICLE_DETAIL, article_id)

    @classmethod
    def article_list(cls, **params) -> str:
        """文章列表缓存键"""
        # 对参数排序以确保一致性
        sorted_params = sorted(params.items())
        param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
        return cls.build(CacheKeyPrefix.ARTICLE_LIST, hash(param_str))

    @classmethod
    def user_profile(cls, user_id: int) -> str:
        """用户资料缓存键"""
        return cls.build(CacheKeyPrefix.USER_PROFILE, user_id)

    @classmethod
    def category_list(cls) -> str:
        """分类列表缓存键"""
        return cls.build(CacheKeyPrefix.CATEGORY_LIST)

    @classmethod
    def tag_list(cls) -> str:
        """标签列表缓存键"""
        return cls.build(CacheKeyPrefix.TAG_LIST)

    @classmethod
    def stats_overview(cls) -> str:
        """总览统计缓存键"""
        return cls.build(CacheKeyPrefix.STATS_OVERVIEW)

    @classmethod
    def rate_limit(cls, identifier: str, action: str) -> str:
        """速率限制缓存键"""
        return cls.build(CacheKeyPrefix.RATE_LIMIT, action, identifier)


# ============================================
# 缓存装饰器
# ============================================

def cached(
    key_prefix: str,
    ttl: int = 300,
    key_builder: Optional[Callable] = None,
    vary_on: Optional[List[str]] = None
):
    """
    通用缓存装饰器

    Args:
        key_prefix: 缓存键前缀
        ttl: 过期时间（秒）
        key_builder: 自定义键构建函数
        vary_on: 变化的参数名列表

    Returns:
        装饰后的函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 构建缓存键
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # 默认使用函数名和参数
                parts = [func.__name__]
                if vary_on:
                    for param in vary_on:
                        if param in kwargs:
                            parts.append(str(kwargs[param]))
                cache_key = CacheKeyBuilder.build(key_prefix, *parts)

            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                return result

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


def cache_result(ttl: int = 300, key: Optional[str] = None):
    """
    简化的结果缓存装饰器

    Args:
        ttl: 过期时间（秒）
        key: 自定义缓存键，默认使用函数名

    Returns:
        装饰后的函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = key or CacheKeyBuilder.build("func", func.__name__)
            result = cache.get(cache_key)

            if result is not None:
                return result

            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


# ============================================
# 缓存穿透/击穿防护
# ============================================

class CacheLock:
    """缓存锁 - 防止缓存击穿"""

    DEFAULT_LOCK_TIMEOUT = 10  # 锁超时时间（秒）

    @classmethod
    def acquire(cls, lock_key: str, timeout: int = None) -> bool:
        """
        获取锁

        Args:
            lock_key: 锁的键名
            timeout: 超时时间（秒）

        Returns:
            bool: 是否成功获取锁
        """
        timeout = timeout or cls.DEFAULT_LOCK_TIMEOUT
        # 使用 setnx 实现
        return cache.add(lock_key, "1", timeout)

    @classmethod
    def release(cls, lock_key: str) -> bool:
        """
        释放锁

        Args:
            lock_key: 锁的键名

        Returns:
            bool: 是否成功释放锁
        """
        cache.delete(lock_key)
        return True


def get_or_set(
    cache_key: str,
    fallback: Callable,
    ttl: int = 300,
    lock_timeout: Optional[int] = None,
    null_ttl: int = 60
) -> Any:
    """
    获取缓存或设置缓存（带锁和空值缓存）

    Args:
        cache_key: 缓存键
        fallback: 缓存未命中时的回调函数
        ttl: 缓存过期时间（秒）
        lock_timeout: 锁超时时间（秒），None 表示不加锁
        null_ttl: 空值缓存时间（秒），防止缓存穿透

    Returns:
        缓存的值或回调函数的结果
    """
    # 尝试从缓存获取
    value = cache.get(cache_key)
    if value is not None:
        # 检查是否是空值标记
        if value == "__NULL__":
            return None
        return value

    # 检查是否需要加锁
    lock_key = f"{cache_key}:lock" if lock_timeout else None

    if lock_key:
        if not CacheLock.acquire(lock_key, lock_timeout):
            # 获取锁失败，等待后重试
            import time
            time.sleep(0.1)
            value = cache.get(cache_key)
            if value is not None:
                return None if value == "__NULL__" else value

    try:
        # 执行回调函数
        value = fallback()

        # 缓存结果
        if value is None:
            # 缓存空值，防止穿透
            cache.set(cache_key, "__NULL__", null_ttl)
        else:
            cache.set(cache_key, value, ttl)

        return value

    except Exception as e:
        logger.error(f"缓存操作失败: {cache_key}, 错误: {e}")
        # 缓存失败时直接执行回调
        return fallback()

    finally:
        if lock_key:
            CacheLock.release(lock_key)


# ============================================
# 批量缓存操作
# ============================================

def get_many(cache_keys: List[str]) -> Dict[str, Any]:
    """
    批量获取缓存

    Args:
        cache_keys: 缓存键列表

    Returns:
        dict: 键值对字典
    """
    return cache.get_many(cache_keys)


def set_many(data: Dict[str, Any], ttl: int = 300) -> bool:
    """
    批量设置缓存

    Args:
        data: 键值对字典
        ttl: 过期时间（秒）

    Returns:
        bool: 是否成功
    """
    return cache.set_many(data, ttl)


def delete_many(cache_keys: List[str]) -> bool:
    """
    批量删除缓存

    Args:
        cache_keys: 缓存键列表

    Returns:
        bool: 是否成功
    """
    return cache.delete_many(cache_keys)


def delete_pattern(pattern: str) -> int:
    """
    根据模式删除缓存键

    Args:
        pattern: 缓存键模式（支持通配符）

    Returns:
        int: 删除的键数量
    """
    from django_redis import get_redis_connection
    redis_conn = get_redis_connection("default")
    keys = redis_conn.keys(f"{settings.REDIS_CACHE_PREFIX}*{pattern}*")
    if keys:
        return redis_conn.delete(*keys)
    return 0


# ============================================
# 缓存预热和刷新
# ============================================

class CacheWarmer:
    """缓存预热器"""

    @classmethod
    def warm_article_stats(cls, article_ids: List[int]) -> bool:
        """
        预热文章统计缓存

        Args:
            article_ids: 文章 ID 列表

        Returns:
            bool: 是否成功
        """
        from articles.models import Article

        articles = Article.objects.filter(id__in=article_ids)
        cache_data = {}

        for article in articles:
            cache_key = CacheKeyBuilder.article_stats(article.id)
            cache_data[cache_key] = {
                "view_count": article.view_count,
                "like_count": article.like_count,
                "comment_count": article.comment_count
            }

        if cache_data:
            return set_many(cache_data, ttl=300)
        return True

    @classmethod
    def invalidate_article(cls, article_id: int) -> bool:
        """
        使文章相关缓存失效

        Args:
            article_id: 文章 ID

        Returns:
            bool: 是否成功
        """
        keys_to_delete = [
            CacheKeyBuilder.article_stats(article_id),
            CacheKeyBuilder.article_detail(article_id),
        ]
        delete_many(keys_to_delete)

        # 删除文章列表缓存
        delete_pattern(CacheKeyPrefix.ARTICLE_LIST)

        return True


# ============================================
# 速率限制工具
# ============================================

class RateLimiter:
    """速率限制器"""

    @classmethod
    def check_rate_limit(
        cls,
        identifier: str,
        action: str,
        max_requests: int = 10,
        period: int = 60
    ) -> tuple[bool, int]:
        """
        检查速率限制

        Args:
            identifier: 唯一标识符（IP 地址或用户 ID）
            action: 操作类型
            max_requests: 时间段内最大请求数
            period: 时间段（秒）

        Returns:
            tuple: (是否允许, 剩余请求数)
        """
        cache_key = CacheKeyBuilder.rate_limit(identifier, action)
        request_count = cache.get(cache_key, 0)

        if request_count >= max_requests:
            return False, 0

        # 增加计数器
        cache.set(cache_key, request_count + 1, period)
        return True, max_requests - request_count - 1

    @classmethod
    def reset_rate_limit(cls, identifier: str, action: str) -> bool:
        """
        重置速率限制

        Args:
            identifier: 唯一标识符
            action: 操作类型

        Returns:
            bool: 是否成功
        """
        cache_key = CacheKeyBuilder.rate_limit(identifier, action)
        cache.delete(cache_key)
        return True


# ============================================
# 缓存健康检查
# ============================================

def check_cache_health() -> Dict[str, Any]:
    """
    检查缓存健康状态

    Returns:
        dict: 健康状态信息
    """
    try:
        # 测试读写
        test_key = CacheKeyBuilder.build("_health", "test")
        cache.set(test_key, "ping", 10)
        result = cache.get(test_key)
        cache.delete(test_key)

        if result != "ping":
            return {
                "status": "error",
                "message": "缓存读写测试失败"
            }

        # 获取 Redis 信息
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        info = redis_conn.info()

        return {
            "status": "healthy",
            "used_memory": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "uptime_in_days": info.get("uptime_in_days"),
            "keyspace": info.get("db0"),
        }

    except Exception as e:
        logger.error(f"缓存健康检查失败: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
