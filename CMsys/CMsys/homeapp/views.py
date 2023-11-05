from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

import studentapp
from studentapp import models, serializer
from adminapp import models
from utils.page import LimitPagination
from homeapp.serializer import HomeAnnouncementSerializer, DetailSerializer, RecruitmentSerializer, \
    BasicRecruitmentSerializer


class HomepageView(ListAPIView):
    serializer_class = HomeAnnouncementSerializer
    queryset = models.Announcement.objects.all().order_by('-id')
    pagination_class = LimitPagination

    # queryset = models.Announcement.objects.all().order_by('-id')[0:10]
    # ser = HomeAnnouncementSerializer(instance=queryset, many=True)
    # return Response(ser.data, status=200)


class DetailView(RetrieveAPIView):
    queryset = models.Announcement.objects
    serializer_class = DetailSerializer


class RecruitmentView(ListAPIView):
    queryset = studentapp.models.Recruitment.objects.all().order_by('-id')
    serializer_class = BasicRecruitmentSerializer
    pagination_class = LimitPagination


class DetailRecruitmentView(RetrieveAPIView):
    queryset = studentapp.models.Recruitment.objects
    serializer_class = RecruitmentSerializer

    """
        def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            queryset = studentapp.models.Recruitment.objects.all()
            page_obj = PageNumberPagination()
            result = page_obj.paginate_queryset(queryset, request, self)
            ser = serializer.BasicRecruitmentSerializer(instance=result, many=True)
            return page_obj.get_paginated_response(ser.data)
        recruitment = studentapp.models.Recruitment.objects.filter(id=pk).first()
        if not recruitment:
            return Response({'status': False, 'message': '招募信息不存在'})
        ser = serializer.RecruitmentSerializer(instance=recruitment, many=False)
        return Response(ser.data)
    """
