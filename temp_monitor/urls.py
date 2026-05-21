from django.urls import path
from . import views

app_name = 'temp_monitor'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/record/', views.api_record_temp, name='api_record_temp'),
    path('api/data/', views.api_dashboard_data, name='api_dashboard_data'),
    
]