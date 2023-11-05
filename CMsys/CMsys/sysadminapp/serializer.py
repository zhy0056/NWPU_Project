from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from adminapp import models
from judgeapp import models
import adminapp, judgeapp, studentapp
from sysadminapp import models
from studentapp import models
from utils.validators import phone_validator
import sysadminapp


class PhoneBindingSerializer(serializers.Serializer):
    phone = serializers.CharField(label='手机号', validators=[phone_validator, ])
    code = serializers.CharField(label='短信验证码')

    def validate_code(self, value):
        """
        校验验证码
        """
        if len(value) != 4:
            raise ValidationError('格式错误')
        if not value.isdecimal():
            raise ValidationError('格式错误')
        phone = self.initial_data.get('phone')  # 必须使用initial，self.data必须在is_valid()之后用
        conn = get_redis_connection()
        code = conn.get(phone)
        if not code:
            raise ValidationError('验证码过期')
        if value != code.decode('utf-8'):
            raise ValidationError('验证码错误')
        return value


class InfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = sysadminapp.models.SysAdmin
        fields = ["id", "account", "phone", "password"]


class ChangeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = sysadminapp.models.SysAdmin
        fields = ["account"]


class MessageSerializer(serializers.Serializer):
    phone = serializers.CharField(label='手机号', validators=[phone_validator, ])


class PasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(label='手机号', validators=[phone_validator, ])
    code = serializers.CharField(label='短信验证码')
    password = serializers.CharField(label='密码')

    def validate_code(self, value):
        """
        校验验证码
        """
        if len(value) != 4:
            raise ValidationError('格式错误')
        if not value.isdecimal():
            raise ValidationError('格式错误')
        phone = self.initial_data.get('phone')  # 必须使用initial，self.data必须在is_valid()之后用
        conn = get_redis_connection()
        code = conn.get(phone)
        if not code:
            raise ValidationError('验证码过期')
        if value != code.decode('utf-8'):
            raise ValidationError('验证码错误')
        return value


class StudentInfoSerializer(ModelSerializer):
    student_type = serializers.CharField(source="get_student_type_display", required=False)
    # team_name = serializers.CharField(source="team.name", required=False)
    team_name = serializers.SerializerMethodField()
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = models.Student
        fields = "__all__"
        # ["id", "name", "phone", "password", "age", "team_id", "student_type", "team_name", "create_time",
        #  "update_time"]

    def get_team_name(self, obj):
        return obj.team.name


class AdminInfoSerializer(ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = adminapp.models.Admin
        fields = "__all__"


class JudgeInfoSerializer(ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = judgeapp.models.Judge
        fields = "__all__"


class TeamInfoSerializer(ModelSerializer):
    team_type = serializers.CharField(source="get_team_type_display", required=False)
    leader_name = serializers.SerializerMethodField()
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    work_grade = serializers.SerializerMethodField(required=False)
    invite_number = serializers.SerializerMethodField(required=False)

    class Meta:
        model = models.Team
        fields = ["id", "name", "address", "team_type", "leader_name", "leader_id", "work_id", "work_grade",
                  "invite_number", "create_time", "update_time"]

    def get_leader_name(self, obj):
        return obj.leader.name

    def get_work_grade(self, obj):
        if obj.work:
            return obj.work.grade

    def get_invite_number(self, obj):
        return obj.invite_number


class WorkInfoSerializer(ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = studentapp.models.Work
        fields = "__all__"
