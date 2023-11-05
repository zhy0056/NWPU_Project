from rest_framework.authentication import BaseAuthentication
from django.http import JsonResponse
import jwt
from jwt import exceptions
from six import python_2_unicode_compatible
from rest_framework.exceptions import AuthenticationFailed

from sysadminapp import models


@python_2_unicode_compatible
class JwtQueryParamsAuthentication(BaseAuthentication):

    def authenticate(self, request):
        salt = '200056zhanghaiyang2018303029'
        # 获取token并校验合法性
        token = request.query_params.get('token')
        # print(token)
        # 对token进行：1.切割 2.解密第二段和判断是否过期 3.验证第三段合法性，都由jwt完成
        try:
            payload = jwt.decode(token, salt, algorithms=['HS256'])
        except exceptions.ExpiredSignatureError:
            raise AuthenticationFailed({'code': 1003, 'error': "token已失效"})
        except jwt.DecodeError:
            raise AuthenticationFailed({'code': 1003, 'error': "token认证失败"})
        except jwt.InvalidTokenError:
            raise AuthenticationFailed({'code': 1003, 'error': "非法的token"})

        return payload, token


class PhoneBingdingAuthentication(BaseAuthentication):
    def authenticate(self, request):
        salt = '200056zhanghaiyang2018303029'
        # 获取token并校验合法性
        token = request.query_params.get('token')
        # print(token)
        # 对token进行：1.切割 2.解密第二段和判断是否过期 3.验证第三段合法性，都由jwt完成
        payload = jwt.decode(token, salt, algorithms=['HS256'])
        account = payload['account']
        obj = models.SysAdmin.objects.filter(account=account).first().phone
        if not obj:
            raise AuthenticationFailed({'code': 1003, 'error': "未绑定手机号，无权限操作"})
        return payload, token

