from django.db import models
from django.utils import timezone

class TemperatureLog(models.Model):
    room_name = models.CharField("ชื่อห้อง", max_length=100)
    temperature = models.FloatField("อุณหภูมิ (°C)")
    humidity = models.FloatField("ความชื้น (%)")
    recorded_at = models.DateTimeField("เวลาที่บันทึก", default=timezone.now)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.room_name} | Temp: {self.temperature}°C | {self.recorded_at.strftime('%d/%m/%Y %H:%M')}"