from rest_framework import serializers
import adminapp, studentapp
from studentapp import models
from adminapp import models

import datetime


class HomeAnnouncementSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = models.Announcement
        fields = ['id', 'title', 'update_time', 'create_time']


class DetailSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = models.Announcement
        fields = "__all__"


class BasicRecruitmentSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = studentapp.models.Recruitment
        fields = ["id", "title", "summary", "update_time", "create_time"]


class RecruitmentSerializer(serializers.ModelSerializer):
    publisher_name = serializers.SerializerMethodField()
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = studentapp.models.Recruitment
        fields = '__all__'

    def get_publisher_name(self, obj):
        return obj.publisher.name

