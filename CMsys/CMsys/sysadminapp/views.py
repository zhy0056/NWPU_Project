# Create your views here.
from django_redis import get_redis_connection
from rest_framework.generics import ListAPIView
import datetime
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from sysadminapp import models, serializer
import sysadminapp, adminapp, judgeapp, studentapp
from studentapp import models
from adminapp import models
from judgeapp import models
from utils.auth import JwtQueryParamsAuthentication, PhoneBingdingAuthentication
from utils.jwt_auth import create_token
from utils.page import LimitPagination


class MyPageNumberPagination(PageNumberPagination):
    page_size = 5


class LoginView(APIView):
    """系统管理员使用手机号码和密码登录"""
    parser_classes = [JSONParser, ]

    def post(self, request, *args, **kwargs):
        # print(request.data)
        account = request.data.get('account')
        password = request.data.get('password')
        obj = sysadminapp.models.SysAdmin.objects.filter(account=account).first()
        if not obj:
            return Response({'code': 1000, 'error': '账号错误'})
        obj = sysadminapp.models.SysAdmin.objects.filter(account=account, password=password).first()
        if not obj:
            return Response({'code': 1000, 'error': '密码错误'})
        token = create_token({'id': obj.id, 'account': obj.account})
        return Response({'code': 1001, 'status': '登录成功', 'data': token})  # 返回token


class PhoneBindingView(APIView):
    """系统管理员绑定手机号"""
    authentication_classes = [JwtQueryParamsAuthentication, ]

    def put(self, request, *args, **kwargs):

        # print(request.data)
        phone = request.data.get('phone')
        obj = sysadminapp.models.SysAdmin.objects.filter(phone=phone).first()
        if obj:
            return Response({'status': False, 'message': '手机号已被绑定'})
        ser = serializer.PhoneBindingSerializer(data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': '验证码错误'})
        pk = request.user.get('id')
        sysadminapp.models.SysAdmin.objects.filter(pk=pk).update(phone=ser.validated_data.get('phone'))
        sysadminapp.models.SysAdmin.objects.filter(pk=pk).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '手机号绑定成功'})


class InfoView(APIView):
    """系统管理员对自己的信息进行查看和修改"""
    authentication_classes = [JwtQueryParamsAuthentication, ]

    def get(self, request, *args, **kwargs):

        print(request.user)
        pk = request.user.get('id')
        info = sysadminapp.models.SysAdmin.objects.filter(pk=pk).first()
        ser = serializer.InfoSerializer(instance=info, many=False)
        # info = list(info)
        return Response(ser.data)

    def put(self, request, *args, **kwargs):
        print(request.user)
        pk = request.user.get('id')
        # print(ser.initial_data.get('name'))
        phone = sysadminapp.models.SysAdmin.objects.filter(pk=pk).first().phone
        print(phone)
        if not phone:
            return Response({'status': False, 'message': '请先绑定手机号'})
        ser = serializer.ChangeInfoSerializer(data=request.data)
        if not ser.is_valid():
            return Response({'status': False, 'message': '信息修改失败'})
        sysadminapp.models.SysAdmin.objects.filter(pk=pk).update(account=ser.validated_data.get('account'))
        sysadminapp.models.SysAdmin.objects.filter(pk=pk).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '信息修改成功'})


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
        phone = sysadminapp.models.SysAdmin.objects.filter(pk=pk).first().phone
        password = sysadminapp.models.SysAdmin.objects.filter(pk=pk).first().password
        print(phone)
        if not phone:
            return Response({'status': False, 'message': '请先绑定手机号'})
        ser = serializer.PasswordSerializer(data=request.data)
        if not ser.is_valid():
            return Response({'status': False, 'message': '密码修改失败'})
        if password == ser.validated_data.get('password'):
            return Response({'status': False, 'message': '新密码不可与原密码相同'})
        sysadminapp.models.SysAdmin.objects.filter(pk=pk).update(password=ser.validated_data.get('password'))
        sysadminapp.models.SysAdmin.objects.filter(pk=pk).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '信息修改成功'})


class AdminInfoView(APIView):
    """系统管理员对普通管理员进行增删改（局部和全部）查"""
    authentication_classes = [JwtQueryParamsAuthentication, ]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            queryset = adminapp.models.Admin.objects.all()
            page_obj = PageNumberPagination()
            result = page_obj.paginate_queryset(queryset, request, self)
            ser = serializer.AdminInfoSerializer(instance=result, many=True)
            return page_obj.get_paginated_response(ser.data)

        admin = adminapp.models.Admin.objects.filter(id=pk).first()
        if not admin:
            return Response({'status': False, 'message': '管理员不存在'})
        ser = serializer.AdminInfoSerializer(instance=admin, many=False)
        return Response(ser.data)

    def post(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        ser = serializer.AdminInfoSerializer(data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        account = ser.validated_data.get('account')
        obj = adminapp.models.Admin.objects.filter(account=account).first()
        if obj:
            return Response({'status': False, 'message': '账号已存在'})
        adminapp.models.Admin.objects.create(account=account,
                                             password=ser.validated_data.get('password'),
                                             update_time=datetime.datetime.now(),
                                             create_time=datetime.datetime.now())
        return Response({'status': True, 'message': '管理员添加成功'})

    def put(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        pk = kwargs.get('pk')
        obj = adminapp.models.Admin.objects.filter(id=pk).first()
        ser = serializer.AdminInfoSerializer(instance=obj, data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        if not obj:
            return Response({'status': False, 'message': '管理员不存在'})
        account = ser.validated_data.get('account')
        acc = adminapp.models.Admin.objects.filter(account=account).first()
        if acc:
            return Response({'status': False, 'message': '账号已存在'})
        phone = ser.validated_data.get('phone')
        pho = adminapp.models.Admin.objects.filter(phone=phone).first()
        if pho:
            return Response({'status': False, 'message': '手机号已被注册'})

        ser.save()
        adminapp.models.Admin.objects.filter(id=pk).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '管理员信息修改成功'})

    def patch(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        pk = kwargs.get('pk')
        obj = adminapp.models.Admin.objects.filter(id=pk).first()
        ser = serializer.AdminInfoSerializer(instance=obj, data=request.data, partial=True)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        if not obj:
            return Response({'status': False, 'message': '管理员不存在'})
        account = ser.validated_data.get('account')
        acc = adminapp.models.Admin.objects.filter(account=account).first()
        if acc:
            return Response({'status': False, 'message': '账号已存在'})
        phone = ser.validated_data.get('phone')
        pho = adminapp.models.Admin.objects.filter(phone=phone).first()
        if pho:
            return Response({'status': False, 'message': '手机号已被注册'})
        ser.save()
        adminapp.models.Admin.objects.filter(id=pk).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '管理员信息修改成功'})

    def delete(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        pk = kwargs.get('pk')
        obj = adminapp.models.Admin.objects.filter(id=pk).first()
        if not obj:
            return Response({'status': False, 'message': '管理员不存在'})
        adminapp.models.Admin.objects.filter(id=pk).delete()
        return Response({'status': True, 'message': '管理员删除成功'})


class JudgeInfoView(APIView):
    """系统管理员对评委进行增删改（局部和全部）查"""

    authentication_classes = [JwtQueryParamsAuthentication, PhoneBingdingAuthentication]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            queryset = judgeapp.models.Judge.objects.all()
            page_obj = PageNumberPagination()
            result = page_obj.paginate_queryset(queryset, request, self)
            ser = serializer.JudgeInfoSerializer(instance=result, many=True)
            return page_obj.get_paginated_response(ser.data)
        judge = judgeapp.models.Judge.objects.filter(id=pk).first()
        if not judge:
            return Response({'status': False, 'message': '评委不存在'})
        ser = serializer.JudgeInfoSerializer(instance=judge, many=False)
        return Response(ser.data)

    def post(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        ser = serializer.JudgeInfoSerializer(data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        account = ser.validated_data.get('account')
        obj = judgeapp.models.Judge.objects.filter(account=account).first()
        if obj:
            return Response({'status': False, 'message': '账号已存在'})
        judgeapp.models.Judge.objects.create(account=account,
                                             password=ser.validated_data.get('password'),
                                             update_time=datetime.datetime.now(),
                                             create_time=datetime.datetime.now())
        return Response({'status': True, 'message': '评委添加成功'})

    def put(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        pk = kwargs.get('pk')
        obj = judgeapp.models.Judge.objects.filter(id=pk).first()
        ser = serializer.JudgeInfoSerializer(instance=obj, data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        if not obj:
            return Response({'status': False, 'message': '评委不存在'})
        account = ser.validated_data.get('account')
        acc = judgeapp.models.Judge.objects.filter(account=account).first()
        if acc:
            return Response({'status': False, 'message': '账号已存在'})
        phone = ser.validated_data.get('phone')
        pho = judgeapp.models.Judge.objects.filter(phone=phone).first()
        if pho:
            return Response({'status': False, 'message': '手机号已被注册'})

        ser.save()
        judgeapp.models.Judge.objects.filter(id=pk).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '评委信息修改成功'})

    def patch(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        pk = kwargs.get('pk')
        obj = judgeapp.models.Judge.objects.filter(id=pk).first()
        ser = serializer.JudgeInfoSerializer(instance=obj, data=request.data, partial=True)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        if not obj:
            return Response({'status': False, 'message': '评委不存在'})
        account = ser.validated_data.get('account')
        acc = judgeapp.models.Judge.objects.filter(account=account).first()
        if acc:
            return Response({'status': False, 'message': '账号已存在'})
        phone = ser.validated_data.get('phone')
        if phone:
            pho = judgeapp.models.Judge.objects.filter(phone=phone).first()

            if pho:
                return Response({'status': False, 'message': '手机号已被注册'})
        ser.save()
        judgeapp.models.Judge.objects.filter(id=pk).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '评委信息修改成功'})

    def delete(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        pk = kwargs.get('pk')
        obj = judgeapp.models.Judge.objects.filter(id=pk).first()
        if not obj:
            return Response({'status': False, 'message': '评委不存在'})
        judgeapp.models.Judge.objects.filter(id=pk).delete()
        return Response({'status': True, 'message': '评委删除成功'})


class StudentInfoView(APIView):
    """系统管理员对学生进行增删改（局部和全部）查"""

    authentication_classes = [JwtQueryParamsAuthentication, ]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            queryset = studentapp.models.Student.objects.all()
            page_obj = PageNumberPagination()
            result = page_obj.paginate_queryset(queryset, request, self)
            ser = serializer.StudentInfoSerializer(instance=result, many=True)
            return page_obj.get_paginated_response(ser.data)
        student = studentapp.models.Student.objects.filter(id=pk).first()
        if not student:
            return Response({'status': False, 'message': '学生不存在'})
        ser = serializer.StudentInfoSerializer(instance=student, many=False)
        return Response(ser.data)

    def post(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        ser = serializer.StudentInfoSerializer(data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        phone = ser.validated_data.get('phone')
        print(ser.validated_data)
        obj = studentapp.models.Student.objects.filter(phone=phone).first()
        if obj:
            return Response({'status': False, 'message': '手机号已被注册'})
        studentapp.models.Student.objects.create(phone=phone,
                                                 name=ser.validated_data.get('name'),
                                                 password=ser.validated_data.get('password'),
                                                 school=ser.validated_data.get('school'),
                                                 update_time=datetime.datetime.now(),
                                                 create_time=datetime.datetime.now())
        return Response({'status': True, 'message': '学生添加成功'})

    def put(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        pk = kwargs.get('pk')
        obj = studentapp.models.Student.objects.filter(id=pk).first()
        ser = serializer.StudentInfoSerializer(instance=obj, data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        if not obj:
            return Response({'status': False, 'message': '学生不存在'})
        phone = ser.validated_data.get('phone')
        pho = studentapp.models.Student.objects.filter(phone=phone).first()
        if pho:
            return Response({'status': False, 'message': '手机号已被注册'})
        team = ser.validated_data.get('team')
        if not team:
            ser.save()
            studentapp.models.Student.objects.filter(id=pk).update(student_type=1,
                                                                   update_time=datetime.datetime.now(),
                                                                   )
            return Response({'status': True, 'message': '学生信息修改成功1'})
        ser.save()
        studentapp.models.Student.objects.filter(id=pk).update(
            student_type=2,
            update_time=datetime.datetime.now(),
        )
        return Response({'status': True, 'message': '学生信息修改成功'})

    def patch(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        pk = kwargs.get('pk')
        obj = studentapp.models.Student.objects.filter(id=pk).first()
        ser = serializer.StudentInfoSerializer(instance=obj, data=request.data, partial=True)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        if not obj:
            return Response({'status': False, 'message': '学生不存在'})
        phone = ser.validated_data.get('phone')
        pho = studentapp.models.Student.objects.filter(phone=phone).first()
        if pho:
            return Response({'status': False, 'message': '手机号已被注册'})
        team = ser.validated_data.get('team', -1)
        if not team:
            ser.save()
            studentapp.models.Student.objects.filter(id=pk).update(student_type=1,
                                                                   update_time=datetime.datetime.now(),
                                                                   )
            return Response({'status': True, 'message': '学生信息修改成功'})
        ser.save()
        studentapp.models.Student.objects.filter(id=pk).update(
            student_type=2,
            update_time=datetime.datetime.now(),
        )
        return Response({'status': True, 'message': '学生信息修改成功'})

    def delete(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        pk = kwargs.get('pk')
        obj = studentapp.models.Student.objects.filter(id=pk).first()
        if not obj:
            return Response({'status': False, 'message': '学生不存在'})
        studentapp.models.Student.objects.filter(id=pk).delete()
        return Response({'status': True, 'message': '学生删除成功'})


class TeamInfoView(APIView):
    """系统管理员对参赛队伍进行删改（局部和全部）查"""

    authentication_classes = [JwtQueryParamsAuthentication, ]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            queryset = studentapp.models.Team.objects.all().order_by('id')
            page_obj = PageNumberPagination()
            result = page_obj.paginate_queryset(queryset, request, self)
            ser = serializer.TeamInfoSerializer(instance=result, many=True)
            return page_obj.get_paginated_response(ser.data)
        team = studentapp.models.Team.objects.filter(id=pk).first()
        if not team:
            return Response({'status': False, 'message': '队伍不存在'})
        ser = serializer.TeamInfoSerializer(instance=team, many=False)
        return Response(ser.data)

    def put(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        pk = kwargs.get('pk')
        obj = studentapp.models.Team.objects.filter(id=pk).first()
        ser = serializer.TeamInfoSerializer(instance=obj, data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        if not obj:
            return Response({'status': False, 'message': '团队不存在'})
        ser.save()
        studentapp.models.Team.objects.filter(id=pk).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '团队信息修改成功'})

    def patch(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        pk = kwargs.get('pk')
        obj = studentapp.models.Team.objects.filter(id=pk).first()
        ser = serializer.TeamInfoSerializer(instance=obj, data=request.data, partial=True)
        if not ser.is_valid():
            print(ser.errors)
            return Response({'status': False, 'message': ser.errors})
        if not obj:
            return Response({'status': False, 'message': '团队不存在'})
        ser.save()
        studentapp.models.Team.objects.filter(id=pk).update(update_time=datetime.datetime.now())
        return Response({'status': True, 'message': '团队信息修改成功'})

    def delete(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        pk = kwargs.get('pk')
        obj = studentapp.models.Team.objects.filter(id=pk).first()
        if not obj:
            return Response({'status': False, 'message': '团队不存在'})

        studentapp.models.Student.objects.filter(team_id=pk).all().update(student_type=1,
                                                                          update_time=datetime.datetime.now(),
                                                                          )
        studentapp.models.Team.objects.filter(id=pk).delete()
        return Response({'status': True, 'message': '团队删除成功'})


class WorkInfoView(APIView):
    """系统管理员对学生进行增删改（局部和全部）查"""

    authentication_classes = [JwtQueryParamsAuthentication, ]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            queryset = studentapp.models.Work.objects.all()
            page_obj = PageNumberPagination()
            result = page_obj.paginate_queryset(queryset, request, self)
            ser = serializer.WorkInfoSerializer(instance=result, many=True)
            return page_obj.get_paginated_response(ser.data)
        work = studentapp.models.Work.objects.filter(id=pk).first()
        if not work:
            return Response({'status': False, 'message': '作品不存在'})
        ser = serializer.WorkInfoSerializer(instance=work, many=False)
        return Response(ser.data)

    def delete(self, request, *args, **kwargs):
        account = request.user.get('account')
        pb = sysadminapp.models.SysAdmin.objects.filter(account=account).first().phone
        if not pb:
            return Response({'status': False, 'message': '请先绑定手机号'})
        pk = kwargs.get('pk')
        obj = studentapp.models.Work.objects.filter(id=pk).first()
        if not obj:
            return Response({'status': False, 'message': '作品不存在'})
        studentapp.models.Work.objects.filter(id=pk).delete()
        return Response({'status': True, 'message': '作品删除成功'})


class TSInfoView(APIView):
    """系统管理员对查看某团队学生"""

    authentication_classes = [JwtQueryParamsAuthentication, ]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        team = studentapp.models.Team.objects.filter(id=pk).first()
        if not team:
            return Response({'status': False, 'message': '队伍不存在'})
        queryset = studentapp.models.Student.objects.filter(team=pk).all()
        page_obj = PageNumberPagination()
        result = page_obj.paginate_queryset(queryset, request, self)
        ser = serializer.StudentInfoSerializer(instance=result, many=True)
        return page_obj.get_paginated_response(ser.data)


class JWInfoView(APIView):
    """系统管理员对查看某评委的打分情况"""

    # authentication_classes = [JwtQueryParamsAuthentication, ]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        judge = judgeapp.models.Judge.objects.filter(id=pk).first()
        if not judge:
            return Response({'status': False, 'message': '评委不存在'})
        queryset = studentapp.models.Work.objects.filter(judge=pk).all()
        page_obj = PageNumberPagination()
        result = page_obj.paginate_queryset(queryset, request, self)
        ser = serializer.WorkInfoSerializer(instance=result, many=True)
        return page_obj.get_paginated_response(ser.data)
