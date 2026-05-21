from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import login_view, logout_view
app_name = "MRA" 
urlpatterns = [
    path('',views.listformdata, name='listformdata'),
    path('base',views.base),
    path('sheet',views.sheet),
    path('report',views.report),
    path('index', views.index, name='index'),
    path('login',views.login),
    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path("documents/", views.document_list, name="document_list"),
    path("documents/new/", views.document_create, name="document_create"),
    path('ipdcontent/new/', views.ipdcontent_create, name='ipdcontent_create'),
    path("ipdcontent/", views.ipdcontent_list, name="ipdcontent_list"),
    path('opd_sum',views.opd_sum),
    path("scores/notes/", views.note_summary, name="note_summary"),

    # -------------------------------IPD---------------------------------

    path('ipd1',views.ipd1),
    path("scores/", views.score_list, name="score_list"),
    path("scores/new/", views.score_create, name="score_create"),
    path("scores/<int:pk>/", views.score_detail, name="score_detail"),
    path("scores/<int:pk>/edit/", views.score_edit, name="score_edit"),
    path('score/<int:pk>/delete/', views.score_delete, name='score_delete'),

    path("scores/summary/", views.score_summary, name="score_summary"),
    path("scores/coverage/", views.score_coverage, name="score_coverage"),

    # ----------------------------------------------------------------

    # -------------------------------OPD---------------------------------
    path("opd/scores/", views.opd_score_list, name="opd_score_list"),
    path("opd/scores/new/", views.opd_score_create, name="opd_score_create"),
    path("opd/scores/<int:pk>/", views.opd_score_detail, name="opd_score_detail"),
    path("opd/scores/<int:pk>/edit/", views.opd_score_edit, name="opd_score_edit"),
    path('opd-score/<int:pk>/delete/', views.opd_score_delete, name='opd_score_delete'),

    path("opd/opd_avg/", views.opd_score_averages, name="opd_score_averages"),
    

    # ----------------------------------------------------------------
    path("my-records/", views.my_records, name="my_records"),
    path('change_password/', views.change_password, name='change_password'),
    # ----------------------------------------------------------------

    path('temp/', include('temp_monitor.urls')),
    
]