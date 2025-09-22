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
    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path("documents/", views.document_list, name="document_list"),
    path("documents/new/", views.document_create, name="document_create"),
    path('ipdcontent/new/', views.ipdcontent_create, name='ipdcontent_create'),
    path("ipdcontent/", views.ipdcontent_list, name="ipdcontent_list"),
    path('opd_sum',views.opd_sum),

    # -------------------------------IPD---------------------------------

    path('ipd1',views.ipd1),
    path("scores/", views.score_list, name="score_list"),
    path("scores/new/", views.score_create, name="score_create"),
    path("scores/<int:pk>/", views.score_detail, name="score_detail"),

    path("scores/summary/", views.score_summary, name="score_summary"),
    path("scores/coverage/", views.score_coverage, name="score_coverage"),

    # ----------------------------------------------------------------

    # -------------------------------OPD---------------------------------
    path("opd/scores/", views.opd_score_list, name="opd_score_list"),
    path("opd/scores/new/", views.opd_score_create, name="opd_score_create"),
    path("opd/scores/<int:pk>/", views.opd_score_detail, name="opd_score_detail"),

    path("opd/averages/", views.opd_score_averages, name="opd_score_averages"),
    

    # ----------------------------------------------------------------
    
]