from django.urls import path, re_path, include
from rest_framework import routers

from adminapp import views

router = routers.DefaultRouter()
router.register(r'file', views.FileViewSet)

urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('announcement/', views.AnnouncementView.as_view()),
    path('phonebinding/', views.PhoneBindingView.as_view()),
    path('password/', views.PasswordView.as_view()),
    re_path('announcement/(?P<pk>\\d+)/', views.AnnouncementView.as_view()),
    path('', include(router.urls))
]
