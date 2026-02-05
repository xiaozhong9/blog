"""
自定义异常处理
"""

from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    自定义异常处理函数
    """
    # 调用 DRF 默认异常处理
    response = exception_handler(exc, context)

    if response is not None:
        # 自定义错误响应格式
        custom_response_data = {
            'code': response.status_code,
            'message': get_error_message(response.status_code),
            'errors': response.data if hasattr(response, 'data') else {}
        }

        response.data = custom_response_data

        # 记录错误日志
        logger.error(
            f"API Error: {response.status_code} - {context['view'].__class__.__name__}",
            extra={
                'view_name': context['view'].__class__.__name__,
                'view_args': context['args'],
                'view_kwargs': context['kwargs']
            },
            exc_info=exc
        )
    else:
        # 处理非 DRF 异常
        logger.error(f"Unexpected error: {str(exc)}", exc_info=exc)

        response = Response(
            {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': '内部服务器错误',
                'errors': {'detail': str(exc)} if settings.DEBUG else {}
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response


def get_error_message(status_code):
    """
    根据状态码返回错误消息
    """
    error_messages = {
        400: '请求参数错误',
        401: '未授权，请先登录',
        403: '权限不足',
        404: '资源不存在',
        405: '请求方法不允许',
        409: '资源冲突',
        429: '请求过于频繁，请稍后再试',
        500: '内部服务器错误',
        503: '服务暂时不可用',
    }
    return error_messages.get(status_code, '未知错误')
