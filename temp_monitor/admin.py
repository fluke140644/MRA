from django.contrib import admin
from .models import TemperatureLog

@admin.register(TemperatureLog)
class TemperatureLogAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'temperature', 'humidity', 'recorded_at')
    list_filter = ('room_name', 'recorded_at')