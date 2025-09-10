from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import login_view, logout_view
app_name = "MRA" 
urlpatterns = [
    path('',views.index),
    path('base',views.base),
    path('sheet',views.sheet),
    path('report',views.report),
    path('listformdata',views.listformdata),
    path('login',views.login),
    # ใช้ login_view ที่เขียนเอง
    path('accounts/login/', login_view, name='login'),

    # logout
    path('accounts/logout/', logout_view, name='logout'),
    # path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    # path('accounts/logout/', logout_view, name='logout'),
    path("documents/", views.document_list, name="document_list"),
    path("documents/new/", views.document_create, name="document_create"),

    path('ipdcontent/new/', views.ipdcontent_create, name='ipdcontent_create'),
    path("ipdcontent/", views.ipdcontent_list, name="ipdcontent_list"),

    



    # ----------------------------------------------------------------
    path('ipd1',views.ipd1),
    path("scores/", views.score_list, name="score_list"),
    path("scores/new/", views.score_create, name="score_create"),
    path("scores/<int:pk>/", views.score_detail, name="score_detail"),

    path("scores/summary/", views.score_summary, name="score_summary"),
    path("scores/coverage/", views.score_coverage, name="score_coverage"),
]