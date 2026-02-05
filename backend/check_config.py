"""
日志配置修复脚本
"""
import os
import sys

# 设置 Django 环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

import django
django.setup()

# 测试是否可以正常导入
print("测试 Django 配置加载...")

try:
    from users.models import User
    print(f"[OK] 用户模型加载成功")
    print(f"[OK] 用户数量: {User.objects.count()}")

    print("\n[SUCCESS] Django 配置加载成功！")

except Exception as e:
    print(f"[ERROR] Django 配置加载失败: {e}")
    import traceback
    traceback.print_exc()

print("\n建议:")
print("1. 确保 config/settings/base.py 中没有 LOGGING 配置")
print("2. 或使用简化的日志配置")
print("3. 重启所有 Python 进程")
