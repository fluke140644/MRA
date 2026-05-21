from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import localtime # 📌 นำเข้าเครื่องมือแปลงเวลาท้องถิ่น
import json
from .models import TemperatureLog
from django.contrib.auth.decorators import login_required, user_passes_test

def is_temp_staff(user):
    return user.is_superuser or user.groups.filter(name='temp').exists()

@login_required(login_url='/admin/login/')
@user_passes_test(is_temp_staff, login_url='/')
def dashboard(request):
    rooms = TemperatureLog.objects.order_by().values_list('room_name', flat=True).distinct()

    latest_data = []
    for room in rooms:
        latest = TemperatureLog.objects.filter(room_name=room).order_by('-recorded_at').first()
        if latest:
            latest_data.append(latest)

    logs_qs = TemperatureLog.objects.all().order_by('-recorded_at')[:50]
    history_logs = list(logs_qs)

    chart_data = {}
    reversed_logs = list(history_logs)
    reversed_logs.reverse() 

    for log in reversed_logs:
        r = log.room_name
        if r not in chart_data:
            chart_data[r] = {'labels': [], 'temps': [], 'hums': []}
        
        # 📌 แปลงเป็นเวลาไทยก่อนเอาไปโชว์ในกราฟ
        local_time = localtime(log.recorded_at)
        chart_data[r]['labels'].append(local_time.strftime("%H:%M"))
        chart_data[r]['temps'].append(log.temperature)
        chart_data[r]['hums'].append(log.humidity)

    context = {
        'latest_data': latest_data,
        'history_logs': history_logs,
        'chart_data_json': json.dumps(chart_data), 
    }
    return render(request, 'temp_monitor/dashboard.html', context)

@login_required(login_url='/admin/login/')
@user_passes_test(is_temp_staff, login_url='/')
def api_dashboard_data(request):
    rooms = TemperatureLog.objects.order_by().values_list('room_name', flat=True).distinct()
    latest_data = []
    for room in rooms:
        latest = TemperatureLog.objects.filter(room_name=room).order_by('-recorded_at').first()
        if latest:
            # 📌 แปลงเวลาไทยให้กล่องการ์ด
            local_time = localtime(latest.recorded_at)
            latest_data.append({
                'room_name': latest.room_name,
                'temperature': latest.temperature,
                'humidity': latest.humidity,
                'recorded_at': local_time.strftime("%d/%m/%Y %H:%M")
            })

    logs_qs = TemperatureLog.objects.all().order_by('-recorded_at')[:50]
    
    # 📌 แปลงเวลาไทยให้ตารางประวัติ
    history_logs = []
    for log in logs_qs:
        local_time = localtime(log.recorded_at)
        history_logs.append({
            'time': local_time.strftime("%H:%M"),
            'room_name': log.room_name,
            'temperature': log.temperature,
            'humidity': log.humidity
        })

    chart_data = {}
    reversed_logs = list(logs_qs)
    reversed_logs.reverse() 
    for log in reversed_logs:
        r = log.room_name
        if r not in chart_data:
            chart_data[r] = {'labels': [], 'temps': [], 'hums': []}
        
        # 📌 แปลงเวลาไทยให้แกน X ของกราฟ
        local_time = localtime(log.recorded_at)
        chart_data[r]['labels'].append(local_time.strftime("%H:%M"))
        chart_data[r]['temps'].append(log.temperature)
        chart_data[r]['hums'].append(log.humidity)

    return JsonResponse({
        'latest_data': latest_data,
        'history_logs': history_logs,
        'chart_data': chart_data
    })


# --- 3. ฟังก์ชันรับค่าจาก ESP32 (เหมือนเดิม) ---
@csrf_exempt
def api_record_temp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            TemperatureLog.objects.create(
                room_name=data.get('room_name', 'Unknown Room'),
                temperature=float(data.get('temperature', 0.0)),
                humidity=float(data.get('humidity', 0.0))
            )
            return JsonResponse({"status": "success", "message": "บันทึกอุณหภูมิสำเร็จ!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "รองรับเฉพาะ POST"}, status=405)