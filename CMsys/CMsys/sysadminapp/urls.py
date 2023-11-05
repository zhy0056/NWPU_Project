from django.urls import path, re_path
from sysadminapp import views


urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('phonebinding/', views.PhoneBindingView.as_view()),
    path('info/', views.InfoView.as_view()),
    path('message/', views.MessageView.as_view()),
    path('password/', views.PasswordView.as_view()),
    path('admininfo/', views.AdminInfoView.as_view()),
    re_path('admininfo/(?P<pk>\\d+)/', views.AdminInfoView.as_view()),
    path('judgeinfo/', views.JudgeInfoView.as_view()),
    re_path('judgeinfo/(?P<pk>\\d+)/', views.JudgeInfoView.as_view()),
    path('studentinfo/', views.StudentInfoView.as_view()),
    re_path('studentinfo/(?P<pk>\\d+)/', views.StudentInfoView.as_view()),
    path('teaminfo/', views.TeamInfoView.as_view()),
    re_path('teaminfo/(?P<pk>\\d+)/', views.TeamInfoView.as_view()),
    re_path('tsinfo/(?P<pk>\\d+)/', views.TSInfoView.as_view()),
    re_path('jwinfo/(?P<pk>\\d+)/', views.JWInfoView.as_view()),
]