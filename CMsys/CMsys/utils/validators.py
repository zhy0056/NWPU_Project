from django_redis import get_redis_connection
import re
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


def phone_validator(value):
    """
    校验手机号格式
    """
    if re.match(r"^(1[3|4|5|6|7|8|9])\d{9}$", value):
        return
    raise ValidationError('手机号格式错误')


