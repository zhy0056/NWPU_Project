"""CMsys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, re_path
from studentapp import views


urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('info/', views.InfoView.as_view()),
    path('message/', views.MessageView.as_view()),
    path('register/', views.RegisterView.as_view()),
    path('recruitment/', views.RecruitmentView.as_view()),
    re_path('recruitment/(?P<pk>\\d+)/', views.RecruitmentView.as_view()),
    path('team/', views.TeamView.as_view()),
    path('application/', views.ApplicationView.as_view()),
]
