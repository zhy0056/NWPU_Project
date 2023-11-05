from django_redis import get_redis_connection
from rest_framework.exceptions import ValidationError

from studentapp import models
from rest_framework import serializers

from utils.validators import phone_validator


class InfoSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_student_type_display", required=False)
    team_name = serializers.CharField(source="team.name", required=False)

    class Meta:
        model = models.Student
        fields = ["name", "phone", "password", "school", "status", "team_id", "team_name"]


class ChangeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Student
        fields = ["name", "school"]


class MessageSerializer(serializers.Serializer):
    phone = serializers.CharField(label='手机号', validators=[phone_validator, ])


class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(label='手机号', validators=[phone_validator, ])
    code = serializers.CharField(label='短信验证码')
    name = serializers.CharField(label='姓名')
    school = serializers.CharField(label='学校')
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


class BasicRecruitmentSerializer(serializers.Serializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = models.Recruitment
        fields = ["title", "summary", "comment_count", "update_time", "create_time"]


class RecruitmentSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = models.Recruitment
        fields = ["id", "title", "summary", "comment_count", "content", "update_time", "create_time"]


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


class TeamSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    team_type = serializers.CharField(source="get_team_type_display", required=False)
    work_grade = serializers.SerializerMethodField(required=False)
    leader_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Team
        fields = '__all__'

    def get_leader_name(self, obj):
        return obj.leader.name

    def get_work_grade(self, obj):
        if obj.work:
            return obj.work.grade


class TeamCreateSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = models.Team
        fields = ["name", "address", "update_time", "create_time"]


class ApplicationSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    team_name = serializers.SerializerMethodField()
    leader_name = serializers.SerializerMethodField()
    application_type = serializers.CharField(source="get_application_type_display", required=False)
    applicant_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Application
        fields = ['applicant_id', 'applicant_name', 'content', 'team', 'team_name', 'leader_name', 'application_type', 'create_time']

    def get_team_name(self, obj):
        return obj.team.name

    def get_leader_name(self, obj):
        return obj.team.leader.name

    def get_applicant_name(self, obj):
        return obj.applicant.name
