import datetime

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

import adminapp
from utils.auth import JwtQueryParamsAuthentication
from utils.jwt_auth import create_token
from adminapp import models, serializer


class LoginView(APIView):
    """管理员使用手机号码和密码登录"""
    parser_classes = [JSONParser, ]

    def post(self, request, *args, **kwargs):
        # print(request.data)
        account = request.data.get('account')
        password = request.data.get('password')
        obj = adminapp.models.Admin.objects.filter(account=account).first()
        if not obj:
            return Response({'code': 1000, 'error': '账号错误'})
        obj = adminapp.models.Admin.objects.filter(account=account, password=password).first()
        if not obj:
            return Response({'code': 1000, 'error': '密码错误'})
        token = create_token({'id': obj.id, 'account': obj.account})
        return Response({'code': 1001, 'status': '登录成功', 'data': token})  # 返回token


class PhoneBindingView(APIView):
    """管理员绑定手机号"""
    authentication_classes = [JwtQueryParamsAuthentication, ]

    def put(self, request, *args, **kwargs):

        # print(request.data)
        phone = request.data.get('phone')
        obj = adminapp.models.Admin.objects.filter(phone=phone).first()
        if obj:
            return Response({'status': False, 'message': '手机号已被绑定'})
        ser = serializer.PhoneBindingSerializer(data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': '验证码错误'})
        pk = request.user.get('id')
        adminapp.models.Admin.objects.filter(pk=pk).update(phone=ser.validated_data.get('phone'))
        adminapp.models.Admin.objects.filter(pk=pk).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '手机号绑定成功'})


class MessageView(APIView):
    """系统管理员通过手机号请求验证码后,MessageView负责发送验证码"""

    def get(self, request, *args, **kwargs):
        # 1获取手机号，2进行手机号格式校验，正则表达式
        ser = serializer.MessageSerializer(data=request.query_params)
        if not ser.is_valid():
            return Response({'status': False, 'message': '手机号格式错误'})
        phone = ser.validated_data.get('phone')
        # 3生成随机验证码，
        import random
        random_code = random.randint(1000, 9999)
        random_code = str(random_code)
        """
        为了不浪费短信条数暂时关闭
        result = send_message(phone, code)
        if not result:
            return Response({'status': False, 'message': '验证码发送失败'})
        """
        print(random_code)
        # 5保留手机号和验证码以作校验（30s过期）,自己搭建redis服务（腾讯云服务器贵）,使用django-redis,在settings中配置
        conn = get_redis_connection()
        conn.set(phone, random_code, ex=60)
        return Response({'status': True, 'message': '验证码发送成功'})


class PasswordView(APIView):
    """系统管理员使用手机号和验证码修改密码"""
    authentication_classes = [JwtQueryParamsAuthentication, ]

    def put(self, request, *args, **kwargs):
        print(request.user)
        pk = request.user.get('id')
        # print(ser.initial_data.get('name'))
        phone = adminapp.models.Admin.objects.filter(pk=pk).first().phone
        password = adminapp.models.Admin.objects.filter(pk=pk).first().password
        print(phone)
        if not phone:
            return Response({'status': False, 'message': '请先绑定手机号'})
        ser = serializer.PasswordSerializer(data=request.data)
        if not ser.is_valid():
            return Response({'status': False, 'message': '密码修改失败'})
        if password == ser.validated_data.get('password'):
            return Response({'status': False, 'message': '新密码不可与原密码相同'})
        adminapp.models.Admin.objects.filter(pk=pk).update(password=ser.validated_data.get('password'))
        adminapp.models.Admin.objects.filter(pk=pk).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '密码修改成功'})


class InfoView(APIView):
    """系统管理员对自己的信息进行查看和修改"""
    authentication_classes = [JwtQueryParamsAuthentication, ]

    def get(self, request, *args, **kwargs):

        print(request.user)
        pk = request.user.get('id')
        info = adminapp.models.Admin.objects.filter(pk=pk).first()
        ser = serializer.InfoSerializer(instance=info, many=False)
        # info = list(info)
        return Response(ser.data)

    def put(self, request, *args, **kwargs):
        print(request.user)
        pk = request.user.get('id')
        # print(ser.initial_data.get('name'))
        phone = adminapp.models.Admin.objects.filter(pk=pk).first().phone
        print(phone)
        if not phone:
            return Response({'status': False, 'message': '请先绑定手机号'})
        ser = serializer.ChangeInfoSerializer(data=request.data)
        if not ser.is_valid():
            return Response({'status': False, 'message': '信息修改失败'})
        adminapp.models.Admin.objects.filter(pk=pk).update(account=ser.validated_data.get('account'))
        adminapp.models.Admin.objects.filter(pk=pk).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '信息修改成功'})


class AnnouncementView(APIView):
    authentication_classes = [JwtQueryParamsAuthentication, ]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            id = request.user.get('id')
            queryset = adminapp.models.Announcement.objects.filter(publisher=id).all()
            page_obj = PageNumberPagination()
            result = page_obj.paginate_queryset(queryset, request, self)
            ser = serializer.AnnouncementSerializer(instance=result, many=True)
            return page_obj.get_paginated_response(ser.data)
        announcement = adminapp.models.Announcement.objects.filter(id=pk).first()
        if not announcement:
            return Response({'status': False, 'message': '公告不存在'})
        ser = serializer.AnnouncementSerializer(instance=announcement, many=False)
        return Response(ser.data)

    def post(self, request, *args, **kwargs):
        account = request.user.get('account')
        pk = models.Admin.objects.filter(account=account).first().pk
        file_serializer = serializer.AnnouncementSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save(publisher_id=pk)
            return Response({
                "code": 0,
                "msg": "success!",
                "data": file_serializer.data
            },
                status=status.HTTP_200_OK
            )
        else:
            return Response({
                "code": 400,
                "msg": "bad request",
                "data": file_serializer.errors
            },
                status=status.HTTP_400_BAD_REQUEST)


class FileViewSet(ModelViewSet):
    authentication_classes = [JwtQueryParamsAuthentication, ]

    queryset = adminapp.models.FilesModel.objects.all()
    serializer_class = adminapp.serializer.FilesSerializer
