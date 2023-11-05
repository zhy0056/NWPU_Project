# from django.shortcuts import render
import code
import datetime
import json
import uuid

from django.db.migrations import serializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from six import python_2_unicode_compatible
from rest_framework.parsers import JSONParser
from django_redis import get_redis_connection

import studentapp
from utils.auth import JwtQueryParamsAuthentication
from utils.jwt_auth import create_token

from studentapp import serializer
from studentapp import models


# Create your views here.

@python_2_unicode_compatible
class LoginView(APIView):
    """学生使用手机号码和密码登录"""
    parser_classes = [JSONParser, ]

    def post(self, request, *args, **kwargs):
        # print(request.data)
        phone = request.data.get('phone')
        password = request.data.get('password')
        obj = models.Student.objects.filter(phone=phone).first()
        if not obj:
            return Response({'code': 1000, 'error': '手机号未注册'})
        obj = models.Student.objects.filter(phone=phone, password=password).first()
        if not obj:
            return Response({'code': 1000, 'error': '用户名或密码错误'})
        token = create_token({'id': obj.id, 'phone': obj.phone})

        return Response({'code': 1001, 'status': '登录成功', 'data': token})  # 返回token


class InfoView(APIView):
    """学生对自己的信息进行查看和修改"""
    authentication_classes = [JwtQueryParamsAuthentication, ]

    def get(self, request, *args, **kwargs):
        print(request.user)
        phone = request.user.get('phone')
        info = models.Student.objects.filter(phone=phone).first()
        ser = serializer.InfoSerializer(instance=info, many=False)
        return Response(ser.data)

    def put(self, request, *args, **kwargs):
        print(request.user)
        phone = request.user.get('phone')
        # print(ser.initial_data.get('name'))
        ser = serializer.ChangeInfoSerializer(data=request.data)
        if not ser.is_valid():
            return Response({'status': False, 'message': '信息修改失败'})
        models.Student.objects.filter(phone=phone).update(name=ser.validated_data.get('name'))
        models.Student.objects.filter(phone=phone).update(school=ser.validated_data.get('school'))
        return Response({'status': True, 'message': '信息修改成功'})

    def patch(self, request, *args, **kwargs):
        print(request.user)
        phone = request.user.get('phone')
        # print(ser.initial_data.get('name'))
        ser = serializer.ChangeInfoSerializer(data=request.data, partial=True)
        if not ser.is_valid():
            return Response({'status': False, 'message': '信息修改失败'})
        models.Student.objects.filter(phone=phone).update(name=ser.validated_data.get('name'))
        models.Student.objects.filter(phone=phone).update(school=ser.validated_data.get('school'))
        return Response({'status': True, 'message': '信息修改成功'})


class RegisterView(APIView):

    def post(self, request, *args, **kwargs):
        """
        接收前端传来的：
            -手机号、密码、验证码、姓名、年龄；
        需要校验：
            -手机号是否合法，验证码是否正确（从redis中获取）
            -情况有这几种：
                -无验证码：没有发或者过期
                -有验证码，输入错误
                -有验证码，验证成功
        成功后去数据库创建用户信息
        """
        ser = serializer.RegisterSerializer(data=request.data)

        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        phone = ser.validated_data.get('phone')
        obj = models.Student.objects.filter(phone=phone).first()
        if obj:
            return Response({'status': False, 'message': '手机号已注册'})
        models.Student.objects.create(phone=phone, name=ser.validated_data.get('name'),
                                      school=ser.validated_data.get('school'),
                                      password=ser.validated_data.get('password'),
                                      update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '注册成功'})


class MessageView(APIView):
    """学生通过手机号请求验证码后,MessageView负责发送验证码"""

    def get(self, request, *args, **kwargs):
        ser = serializer.MessageSerializer(data=request.query_params)
        if not ser.is_valid():
            return Response({'status': False, 'message': '手机号格式错误'})
        phone = ser.validated_data.get('phone')
        obj = models.Student.objects.filter(phone=phone).first()
        if obj:
            return Response({'status': False, 'message': '手机号已被注册'})
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


class RecruitmentView(APIView):
    authentication_classes = [JwtQueryParamsAuthentication, ]

    def post(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        pk = models.Student.objects.filter(phone=phone).first().pk
        student_type = models.Student.objects.filter(phone=phone).first().student_type
        if student_type != 3:
            return Response({'status': False, 'message': '只有队长才可以发布招募信息'})
        ser = serializer.RecruitmentSerializer(data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        ser.save(publisher_id=pk)
        return Response({'status': True, 'message': '招募信息发布成功'})

    def get(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        pk = models.Student.objects.filter(phone=phone).first().pk
        recruitment = models.Recruitment.objects.filter(publisher_id=pk).all()
        ser = serializer.RecruitmentSerializer(instance=recruitment, many=True)
        return Response(ser.data)

    def delete(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        pk = models.Student.objects.filter(phone=phone).first().pk
        student_type = models.Student.objects.filter(phone=phone).first().student_type
        if student_type != 3:
            return Response({'status': False, 'message': '只有队长才可以删除招募信息'})
        recruitment_id = kwargs.get('pk')
        obj = studentapp.models.Recruitment.objects.filter(id=recruitment_id, publisher_id=pk).first()
        if not obj:
            return Response({'status': False, 'message': '删除失败，不是您发布的信息或招募信息不存在'})
        studentapp.models.Recruitment.objects.filter(id=recruitment_id).delete()
        return Response({'status': True, 'message': '招募信息删除成功'})


class PasswordView(APIView):
    """学生使用手机号和验证码修改密码"""
    authentication_classes = [JwtQueryParamsAuthentication, ]

    def put(self, request, *args, **kwargs):
        print(request.user)
        pk = request.user.get('id')
        # print(ser.initial_data.get('name'))
        password = studentapp.models.Student.objects.filter(pk=pk).first().password
        ser = serializer.PasswordSerializer(data=request.data)
        if not ser.is_valid():
            return Response({'status': False, 'message': '密码修改失败'})
        if password == ser.validated_data.get('password'):
            return Response({'status': False, 'message': '新密码不可与原密码相同'})
        studentapp.models.Student.objects.filter(pk=pk).update(password=ser.validated_data.get('password'))
        studentapp.models.Student.objects.filter(pk=pk).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '密码修改成功'})


class TeamView(APIView):
    authentication_classes = [JwtQueryParamsAuthentication, ]

    def post(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        pk = models.Student.objects.filter(phone=phone).first().pk
        student_type = models.Student.objects.filter(phone=phone).first().student_type
        if student_type != 1:
            return Response({'status': False, 'message': '您已在队伍中，无法创建团队'})
        ser = serializer.TeamCreateSerializer(data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        ser.save(leader_id=pk, invite_number=uuid.uuid1())
        models.Student.objects.filter(phone=phone).update(student_type=3,
                                                          team_id=models.Team.objects.filter(leader_id=pk).first().pk)
        return Response({'status': True, 'message': '团队创建成功'})

    def get(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        team_exist = models.Student.objects.filter(phone=phone).first().team_id
        if not team_exist:
            return Response({'status': False, 'message': '您还没有团队'})
        team = models.Team.objects.filter(id=team_exist).first()
        ser = serializer.TeamSerializer(instance=team, many=False)
        return Response(ser.data)

    def put(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        team_exist = models.Student.objects.filter(phone=phone).first().team_id
        if not team_exist:
            return Response({'status': False, 'message': '您还没有团队'})
        # print(ser.initial_data.get('name'))
        leader = models.Student.objects.filter(phone=phone).first().student_type
        if leader != 3:
            return Response({'status': False, 'message': '您不是队长，无法编辑信息'})
        ser = serializer.TeamCreateSerializer(data=request.data)
        if not ser.is_valid():
            return Response({'status': False, 'message': '信息修改失败'})
        models.Team.objects.filter(id=team_exist).update(name=ser.validated_data.get('name'))
        models.Team.objects.filter(id=team_exist).update(address=ser.validated_data.get('address'))
        models.Team.objects.filter(id=team_exist).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '信息修改成功'})

    def patch(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        team_exist = models.Student.objects.filter(phone=phone).first().team_id
        if not team_exist:
            return Response({'status': False, 'message': '您还没有团队'})
        # print(ser.initial_data.get('name'))
        leader = models.Student.objects.filter(phone=phone).first().student_type
        if leader != 3:
            return Response({'status': False, 'message': '您不是队长，无法编辑信息'})
        ser = serializer.TeamCreateSerializer(data=request.data, partial=True)
        if not ser.is_valid():
            return Response({'status': False, 'message': '信息修改失败'})
        models.Team.objects.filter(id=team_exist).update(name=ser.validated_data.get('name'))
        models.Team.objects.filter(id=team_exist).update(address=ser.validated_data.get('address'))
        models.Team.objects.filter(id=team_exist).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '信息修改成功'})

    def delete(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        pk = models.Student.objects.filter(phone=phone).first().pk
        student_type = models.Student.objects.filter(phone=phone).first().student_type
        if student_type != 3:
            return Response({'status': False, 'message': '只有队长才可以删除团队'})

        obj = studentapp.models.Team.objects.filter(leader_id=pk).first()
        if not obj:
            return Response({'status': False, 'message': '团队不存在'})

        studentapp.models.Student.objects.filter(team_id=obj.id).all().update(student_type=1,
                                                                              update_time=datetime.datetime.now(),
                                                                              )
        studentapp.models.Team.objects.filter(leader_id=pk).delete()
        return Response({'status': True, 'message': '团队删除成功'})


class ApplicationView(APIView):
    authentication_classes = [JwtQueryParamsAuthentication, ]

    def post(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        pk = models.Student.objects.filter(phone=phone).first().pk
        student_type = models.Student.objects.filter(phone=phone).first().student_type
        if student_type != 1:
            return Response({'status': False, 'message': '您已经有团队，无法发送申请'})
        if models.Application.objects.filter(applicant_id=pk).first():
            if models.Application.objects.filter(applicant_id=pk).first().application_type != 3:
                return Response({'status': False, 'message': '您有正在申请的团队，无法发送申请'})
        # if models.Application.objects.filter(phone=phone).first().pk
        ser = serializer.ApplicationSerializer(data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        ser.save(applicant_id=pk)
        return Response({'status': True, 'message': '申请发送成功'})

    def get(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        pk = models.Student.objects.filter(phone=phone).first().pk
        team = models.Student.objects.filter(phone=phone).first().team_id
        student_type = models.Student.objects.filter(phone=phone).first().student_type
        if student_type != 3:
            application = models.Application.objects.filter(applicant_id=pk).first()
            ser = serializer.ApplicationSerializer(instance=application, many=False)
            return Response(ser.data)
        queryset = studentapp.models.Application.objects.filter(team_id=team).order_by('id')
        page_obj = PageNumberPagination()
        result = page_obj.paginate_queryset(queryset, request, self)
        ser = serializer.ApplicationSerializer(instance=result, many=True)
        return page_obj.get_paginated_response(ser.data)

    def delete(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        pk = models.Student.objects.filter(phone=phone).first().pk
        if not models.Application.objects.filter(applicant_id=pk).first():
            return Response({'status': False, 'message': '没有申请信息'})
        studentapp.models.Application.objects.filter(applicant_id=pk).delete()
        return Response({'status': True, 'message': '申请删除成功'})


class WorkView(APIView):
    authentication_classes = [JwtQueryParamsAuthentication, ]

    def post(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        pk = models.Student.objects.filter(phone=phone).first().pk
        student_type = models.Student.objects.filter(phone=phone).first().student_type
        if student_type != 1:
            return Response({'status': False, 'message': '您已经有团队，无法发送申请'})
        if models.Application.objects.filter(applicant_id=pk).first():
            if models.Application.objects.filter(applicant_id=pk).first().application_type != 3:
                return Response({'status': False, 'message': '您有正在申请的团队，无法发送申请'})
        # if models.Application.objects.filter(phone=phone).first().pk
        ser = serializer.ApplicationSerializer(data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        ser.save(applicant_id=pk)
        return Response({'status': True, 'message': '申请发送成功'})

    def get(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        pk = models.Student.objects.filter(phone=phone).first().pk
        team = models.Student.objects.filter(phone=phone).first().team_id
        student_type = models.Student.objects.filter(phone=phone).first().student_type
        if student_type != 3:
            application = models.Application.objects.filter(applicant_id=pk).first()
            ser = serializer.ApplicationSerializer(instance=application, many=False)
            return Response(ser.data)
        queryset = studentapp.models.Application.objects.filter(team_id=team).order_by('id')
        page_obj = PageNumberPagination()
        result = page_obj.paginate_queryset(queryset, request, self)
        ser = serializer.ApplicationSerializer(instance=result, many=True)
        return page_obj.get_paginated_response(ser.data)

    def delete(self, request, *args, **kwargs):
        phone = request.user.get('phone')
        pk = models.Student.objects.filter(phone=phone).first().pk
        if not models.Application.objects.filter(applicant_id=pk).first():
            return Response({'status': False, 'message': '没有申请信息'})
        studentapp.models.Application.objects.filter(applicant_id=pk).delete()
        return Response({'status': True, 'message': '申请删除成功'})