from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import adminapp
from adminapp import models
from utils.validators import phone_validator


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
        phone = self.initial_data.get('phone')  # initial，self.data必须在is_valid()之后用
        conn = get_redis_connection()
        code = conn.get(phone)
        if not code:
            raise ValidationError('验证码过期')
        if value != code.decode('utf-8'):
            raise ValidationError('验证码错误')
        return value


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


class InfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = adminapp.models.Admin
        fields = ["id", "account", "phone", "password"]


class AnnouncementSerializer(serializers.ModelSerializer):
    """序列化"""
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    file = serializers.FileField(label='附件', required=False)

    class Meta():
        model = adminapp.models.Announcement
        fields = '__all__'


class ChangeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = adminapp.models.Admin
        fields = ["account"]


class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FilesModel
        fields = '__all__'
