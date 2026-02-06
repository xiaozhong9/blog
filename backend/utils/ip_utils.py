"""
IP 地址处理工具
"""


def get_client_ip(request):
    """
    获取客户端真实 IP 地址

    优先从 X-Forwarded-For 获取，考虑代理服务器情况
    如果没有则使用 REMOTE_ADDR

    Args:
        request: Django 请求对象

    Returns:
        str: 客户端 IP 地址
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For 可能包含多个 IP，取第一个
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip
