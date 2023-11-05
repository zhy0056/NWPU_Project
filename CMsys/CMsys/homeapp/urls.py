from django.urls import path, re_path
from homeapp import views

urlpatterns = [
    path('homepage/', views.HomepageView.as_view()),
    # path('detail/', views.DetailView.as_view()),
    re_path('announcementdetail/(?P<pk>\\d+)/', views.DetailView.as_view()),
    path('recruitmentinfo/', views.RecruitmentView.as_view()),
    re_path('recruitmentinfo/(?P<pk>\\d+)/', views.DetailRecruitmentView.as_view()),
]
# re_path('edit/(\d+)'
