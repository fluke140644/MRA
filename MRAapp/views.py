from .models import Document,IPDContent,PatientScore,OPDScore
from .forms import DocumentForm,PatientScoreForm,OPDScoreForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect,HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django import forms
from django.utils.dateparse import parse_date
from django.utils import timezone
import datetime, re
from datetime import datetime, time, timedelta
from django.utils.safestring import mark_safe
import datetime as python_datetime
import calendar


# Create your views here.

def index(request):
    return render(request,"index.html")

def opd_sum(request):
    return render(request,"opd_sum.html")

def base(request):
    return render(request,"base.html")

def sheet(request):
    return render(request,"sheet.html")

@login_required
def report(request):
    return render(request,"report.html")

@login_required
def listformdata(request):
    return render(request,"listformdata.html")

def login(request):
    return render(request,"login.html")

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)

            if next_url:
                return HttpResponseRedirect(next_url)
            else:
                return redirect('/')
        else:
            error = 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'
            return render(request, 'login.html', {'error': error})
    
    next_url = request.GET.get('next', '')
    return render(request, 'login.html', {'next': next_url})

def logout_view(request):
    auth_logout(request)
    return redirect('login')


# ---- ฟอร์มเอกสาร ----
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["doc_date", "title", "file", "external_url", "is_active"]
        widgets = {
            "doc_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "external_url": forms.URLInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# ---- รายการเอกสาร (ค้นหา + จำกัดจำนวน + เพจจิเนชัน) ----
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["doc_date", "title", "file", "external_url", "is_active"]
        widgets = {
            "doc_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "external_url": forms.URLInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

def document_list(request):
    q = (request.GET.get("q") or "").strip()
    per_page = request.GET.get("per_page")
    try:
        per_page = int(per_page)
        if per_page not in (5, 10, 15):
            per_page = 10
    except (TypeError, ValueError):
        per_page = 10

    qs = Document.objects.all()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(number__icontains=q))

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    return render(request, "docs/document_list.html", {  # ← ชี้ไปใน docs/
        "q": q,
        "per_page": per_page,
        "page_obj": page_obj,
    })

def document_create(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse("MRA:document_list"))  # ← ใช้ namespace MRA
    else:
        form = DocumentForm()
    return render(request, "docs/document_form.html", {"form": form})  # ← ชี้ไปใน docs/


# ----------------------IPD CONTENT----------------------------


def _to_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default

def _to_float(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

def _to_date(v):
    return parse_date(v) if v else None

def ipdcontent_list(request):
    items = IPDContent.objects.order_by("-id")[:50]
    return render(request, "ipdcontent/list.html", {"items": items})

def ipdcontent_create(request):
    if request.method == 'POST':
        raw_percent = (request.POST.get('percent') or '').replace('%', '').strip()
        IPDContent.objects.create(
            fiscal_year=_to_int(request.POST.get('fiscal_year')) if request.POST.get('fiscal_year') else None,
            month=request.POST.get('month'),
            department=request.POST.get('department'),
            hn=request.POST.get('hn'),
            an=request.POST.get('an'),
            hname=request.POST.get('hname'),
            date_admitted=_to_date(request.POST.get('date_admitted')),
            date_discharged=_to_date(request.POST.get('date_discharged')),
            score_1=_to_int(request.POST.get('score_1')),
            score_2=_to_int(request.POST.get('score_2')),
            score_3=_to_int(request.POST.get('score_3')),
            score_4=_to_int(request.POST.get('score_4')),
            score_5=_to_int(request.POST.get('score_5')),
            score_6=_to_int(request.POST.get('score_6')),
            score_7=_to_int(request.POST.get('score_7')),
            score_8=_to_int(request.POST.get('score_8')),
            score_9=_to_int(request.POST.get('score_9')),
            score_10=_to_int(request.POST.get('score_10')),
            score_11=_to_int(request.POST.get('score_11')),
            score_12=_to_int(request.POST.get('score_12')),
            full_score=_to_int(request.POST.get('full_score'), 56),
            sum_score=_to_int(request.POST.get('sum_score'), 0),
            percent=_to_float(raw_percent, 0.0),
        )
        return redirect('ipdcontent_list')

    return render(request, 'ipdcontent/form.html')

# ***************************************************************************************************
def ipd1(request):
    return render(request,"ipd1.html")





def _parse_custom_date(s: str):
    s = (s or "").strip()
    if not s:
        return None
    d = parse_date(s)
    if d:
        return d
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})$", s)
    if not m:
        return None
    day, month, year = map(int, m.groups())
    if year < 100:
        year += 2000
    if year >= 2400:
        year -= 543
    try:
        # ใช้ python_datetime.date แทน
        return python_datetime.date(year, month, day)
    except ValueError:
        return None

def _parse_date_or_day_range(q: str):
    if not q:
        return None, None
    t = q.strip()

    one = _parse_custom_date(t)
    if one:
        return one, one

    m = re.match(
        r"^\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:-|–|—|ถึง)\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*$",
        t
    )
    if m:
        d1, d2 = _parse_custom_date(m.group(1)), _parse_custom_date(m.group(2))
        if d1 and d2:
            if d1 > d2:
                d1, d2 = d2, d1
            return d1, d2

    parts = re.split(r"\s+(?:-|–|—|ถึง)\s+", t)
    if len(parts) == 2:
        d1, d2 = _parse_custom_date(parts[0]), _parse_custom_date(parts[1])
        if d1 and d2:
            if d1 > d2:
                d1, d2 = d2, d1
            return d1, d2

    today = timezone.localdate()
    y, mth = today.year, today.month

    m = re.match(r"^\s*(\d{1,2})\s*(?:-|–|—|ถึง)\s*(\d{1,2})\s*$", t)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if 1 <= a <= 31 and 1 <= b <= 31:
            lo, hi = min(a, b), max(a, b)
            try:
                # ใช้ python_datetime.date แทน
                return python_datetime.date(y, mth, lo), python_datetime.date(y, mth, hi)
            except ValueError:
                return None, None

    m = re.match(r"^\s*(\d{1,2})\s*$", t)
    if m:
        d = int(m.group(1))
        if 1 <= d <= 31:
            try:
                # ใช้ python_datetime.date แทน
                one = python_datetime.date(y, mth, d)
                return one, one
            except ValueError:
                return None, None

    return None, None

def _aware_range_from_dates(start_date, end_date):
    tz = timezone.get_current_timezone()
    # ใช้ python_datetime ให้ชัดเจนทั้งหมดเพื่อป้องกัน Error
    start_naive = python_datetime.datetime.combine(start_date, python_datetime.time.min)
    end_naive   = python_datetime.datetime.combine(end_date + python_datetime.timedelta(days=1), python_datetime.time.min)
    start_aware = timezone.make_aware(start_naive, tz)
    end_aware   = timezone.make_aware(end_naive, tz)
    return start_aware, end_aware

def score_list(request):
    q = (request.GET.get("q") or "").strip()
    limit = request.GET.get("limit")
    try:
        limit = int(limit)
        if limit <= 0:
            limit = None
    except (TypeError, ValueError):
        limit = None

    items = PatientScore.objects.all().order_by("-created_at")

    start_d, end_d = _parse_date_or_day_range(q)
    if start_d and end_d:
        start_dt, end_dt_excl = _aware_range_from_dates(start_d, end_d)
        items = items.filter(created_at__gte=start_dt, created_at__lt=end_dt_excl)
    else:
        if q:
            items = items.filter(
                Q(title__icontains=q) |
                Q(hn__icontains=q) |
                Q(an__icontains=q)
            )

    # ---- apply limit ----
    if limit:
        items = items[:limit]

    return render(request, "scores/score_list.html", {
        "items": items,
        "q": q,
        "limit": limit,
    })


# ************************************//ตัวกรอกวันที่ scores-list//***************************************************************




# ***************************************************************************************************
# def score_create(request):
#     if request.method == "POST":
#         form = PatientScoreForm(request.POST)
#         if form.is_valid():
#             obj = form.save()
#             messages.success(request, f"บันทึกสำเร็จ #{obj.id} (คะแนน {obj.total_yes}/{obj.total_counted})")
#             return redirect(reverse("MRA:score_detail", args=[obj.id]))
#         else:
#             print("FORM ERRORS:", form.errors.as_json())
#             messages.error(request, "กรอกไม่ครบหรือรูปแบบไม่ถูกต้อง ลองดูช่องที่มีข้อความสีแดง")
#     else:
#         form = PatientScoreForm()
#     return render(request, "scores/score_form.html", {"form": form})

# def score_detail(request, pk):
#     obj = get_object_or_404(PatientScore, pk=pk)
#     return render(request, "scores/score_detail.html", {"obj": obj})

IPD_SECTION_TITLES = [
    "Discharge summary : Dx., OP",
    "Discharge summary : Other",
    "Informed consent",
    "History",
    "Physical exam",
    "Progress note",
    "Consultation record",
    "Anesthetic record",
    "Operative note",
    "Labour record",
    "Rehabilitation record",
    "Nurses' note",
]

IPD_N_ITEMS = 9
IPD_CRITERIA_NAMES = {
    1: [
        "<strong>1.1</strong> สรุปการวินิจฉัยโรคในส่วนการวินิจฉัยโรคหลัก (principal diagnosis) ดังนี้ <br>&nbsp;1) สรุปเป็นคำวินิจฉัยโรค (clinical term) ไม่สรุปเป็นคำวินิจฉัยตามการให้รหัส ICD-10 <br>&nbsp;(ตัวอย่างคำวินิจฉัยตามการให้รหัส ICD-10: “D64.8 Other specified anaemias” <br>&nbsp;“J20.9 Acute bronchitis, unspecified” เป็นต้น) และ<br>&nbsp; 2) สรุปการวินิจฉัยโรคในส่วน principal diagnosis สอดคล้องกับข้อมูลในเวชระเบียน และมีเพียงโรคเดียว",
        "<strong>1.2</strong> สรุปการวินิจฉัยโรคในส่วนการวินิจฉัยโรคร่วม (comorbidity) โรคแทรก (complication) ดังนี้ <br>&nbsp;1) สรุปเป็นคำวินิจฉัยโรค (clinical term) ไม่สรุปเป็นคำวินิจฉัยตามการให้รหัส ICD และ<br>&nbsp;2) สรุปการวินิจฉัยโรคสอดคล้องกับข้อมูลในเวชระเบียน และสรุปสาเหตุการบาดเจ็บ (กรณีอุบัติเหตุ) หรือเป็นพิษจากสารเคมี (external cause) (ถ้ามี) สอดคล้องตรงกับข้อมูลในเวชระเบียน <br>&nbsp;3) การสรุปโรคให้ใช้ภาษาไทยได้เฉพาะในส่วนของ external cause เท่านั้น <br>&nbsp;- กรณีที่ไม่มีการวินิจฉัยโรคร่วม โรคแทรก และสาเหตุการบาดเจ็บ (กรณีอุบัติเหตุ) ให้ผู้ตรวจประเมินระบุ NA",
        "<strong>1.3</strong> สรุปการทำหัตถการและหรือการผ่าตัด (procedure/operation) ถูกต้องและครบถ้วนตรงกับข้อมูลในเวชระเบียน <br>&nbsp;- กรณีไม่มีการทำหัตถการหรือการผ่าตัด ให้ผู้ตรวจประเมินระบุ NA",
        "<strong>1.4</strong> บันทึกวันเดือนปี และเวลาที่เริ่มต้น และสิ้นสุดของการทำหัตถการในห้องผ่าตัด (operating room procedure) ทุกครั้ง<br>&nbsp;- กรณีไม่มีการทำหัตถการหรือการผ่าตัด ให้ผู้ตรวจประเมินระบุ NA",
        "<strong>1.5</strong> ไม่ใช้ตัวย่อในการสรุป การวินิจฉัยโรคหลัก (principal diagnosis) การวินิจฉัยโรคร่วม (comorbidity) โรคแทรก (complication) สาเหตุจากภายนอก (external cause) การทำหัตถการ และหรือการผ่าตัด และสรุปด้วยลายมือที่สามารถอ่านออกได้ <br>&nbsp;- ในกรณีที่จำเป็นต้องสรุปด้วยตัวย่อสามารถใช้ตัวย่อที่อ้างอิงตาม WHO ICD 10 และ ICD 9 CM",
        "<strong>1.6</strong> สรุปข้อมูลในส่วน clinical summary (ซึ่งอาจอยู่ในส่วนใดส่วนหนึ่งของเวชระเบียนก็ได้) โดยต้องมีทุกข้อโดยสังเขป ดังนี้ <br>&nbsp;(1) สาเหตุหรือปัญหาผู้ป่วยแรกรับหรือการวินิจฉัยโรคเมื่อสิ้นสุดการรักษา <br>&nbsp;(2) การส่งตรวจเพื่อประกอบการวินิจฉัยโรค (investigated) ที่สำคัญและเกี่ยวข้อง (ถ้ามี) <br>&nbsp;(3) การรักษาและผลการรักษาที่จำเป็น <br>&nbsp;(4) แผนการรักษาฟื้นฟูและสร้างเสริมสุขภาพหลังจำหน่ายผู้ป่วย (ถ้ามี) <br>&nbsp;(5) Home medication",
        "<strong>1.7</strong> สรุปสาเหตุการตายให้สอดคล้องกับข้อมูลในเวชระเบียน <br>&nbsp; <span style='color: red;'>- กรณีที่ผู้ป่วยไม่เสียชีวิต ให้ผู้ตรวจประเมินระบุ NA </span>",
        "<strong>1.8</strong> สรุป discharge status และ discharge type ถูกต้องตรงกับข้อมูลในเวชระเบียน ในกรณีที่ discharge type เป็น “by transfer” ต้องระบุชื่อสถานพยาบาลที่ส่งต่อ",
        "<strong>1.9</strong> มีการลงลายมือแพทย์ผู้รับผิดชอบในการรักษา หรือแพทย์ผู้สรุป โดยต้องระบุชื่อ นามสกุล และเลขที่ใบประกอบวิชาชีพเวชกรรม<br>&nbsp;-         กรณีเวชระเบียนในระบบอิเล็กทรอนิกส์ต้องสามารถสืบค้นในระบบ log in ได้ว่าแพทย์ผู้ใด เป็นผู้สรุปการรักษาพยาบาลในใบ discharge summary",
    ],
    2: [
        "<strong>2.1</strong> มีข้อมูลชื่อ นามสกุล เพศ (หรือคำนำหน้าชื่อเช่น นาย นาง) และอายุ (หรือวัน เดือน ปีเกิด ของผู้ป่วย ถูกต้องครบถ้วน)<br>&nbsp;- กรณีไม่ทราบวัน เดือนเกิด อนุโลมให้มีเฉพาะปี พ.ศ.ได้<br>&nbsp;- กรณีที่ไม่ทราบว่าผู้ป่วยเป็นใครและไม่สามารถสืบค้นได้ มีระบุ“ชายหรือหญิงไม่ทราบชื่อ”",
        "<strong>2.2</strong> มีข้อมูลเลขประจำตัวประชาชนของผู้ป่วย หรือเลขที่ใบต่างด้าว<br>&nbsp;- กรณีคนต่างด้าวที่เกิดในไทยแต่ไม่สามารถขึ้นทะเบียนเป็นคนไทยได้ มีระบุ “ไม่มีเลขที่บัตร”<br>&nbsp;- กรณีชาวต่างชาติ มีระบุเลขที่หนังสือเดินทาง<br>&nbsp;- กรณีที่ผู้ป่วยไม่รู้สึกตัว มีระบุรายละเอียดว่า “ไม่รู้สึกตัว”",
        "<strong>2.3</strong> มีข้อมูลที่อยู่ปัจจุบันของผู้ป่วย <br>&nbsp;- กรณีที่ผู้ป่วยไม่รู้สึกตัวต้องระบุรายละเอียดว่า “ไม่รู้สึกตัว” <br>&nbsp;- กรณีผู้ป่วยเสียชีวิตและไม่พบหลักฐาน ต้องระบุ“เสียชีวิตและไม่พบหลักฐาน” <br>&nbsp;- กรณีผู้ป่วยที่ไม่สามารถซักประวัติได้ ต้องระบุ “ซักประวัติไม่ได้”",
        "<strong>2.4</strong> มีข้อมูลชื่อโรงพยาบาล HN และ AN ถูกต้องตรงกับข้อมูลที่ปรากฏทุกแห่งในเวชระเบียน",
        "<strong>2.5</strong> มีข้อมูลวัน เดือน ปี และเวลาที่ admit วัน เดือน ปี และเวลาที่ discharge ถูกต้องตรงกับข้อมูลในเวชระเบียน",
        "<strong>2.6</strong> มีข้อมูลจำนวนวันที่อยู่ในโรงพยาบาล (LOS: length of stay) และจำนวนวันที่ลากลับบ้าน ระหว่างอยู่ในโรงพยาบาล (total leave days) ถูกต้องตรงกับข้อมูลในเวชระเบียน",
        "<strong>2.7</strong> มีข้อมูล ชื่อ นามสกุล ผู้ให้รหัสโรค และข้อมูลชื่อ นามสกุล ผู้ให้รหัสหัตถการ",
    ],
    3: [
        "<strong>3.1</strong> มีการบันทึกชื่อ และนามสกุล ผู้ป่วยถูกต้องชัดเจน",
        "<strong>3.2</strong> มีลายมือชื่อผู้ให้คำอธิบาย (โดยระบุชื่อ นามสกุล และตำแหน่ง) เกี่ยวกับการรักษาพยาบาลก่อนการลงลายมือชื่อยินยอมรับการรักษา หรือปฏิเสธการรักษา",
        "<strong>3.3</strong> มีลายมือชื่อหรือลายพิมพ์นิ้วมือ (โดยต้องระบุว่าเป็นของใครและใช้นิ้วใด) ชื่อ และนามสกุล ของผู้รับทราบข้อมูลและยินยอมให้ทำการรักษาหรือหัตถการ กรณีที่อายุน้อยกว่า 18 ปี (ยกเว้นสมรสตามกฎหมาย) หรือผู้ป่วยอยู่ในสภาพที่สติสัมปชัญญะไม่สมบูรณ์ ให้มีผู้ลงนามยินยอม โดยต้องระบุชื่อ นามสกุล และความสัมพันธ์กับผู้ป่วยให้ชัดเจน ยกเว้นกรณีดังนี้ <br>&nbsp;1) กรณีมารับการรักษาที่มีภาวะฉุกเฉิน หรือสติสัมปชัญญะไม่สมบูรณ์ ให้ถือเป็นกรณีมีความจำเป็นอาจเป็นอันตรายต่อชีวิต ผู้ให้บริการต้องช่วยเหลือให้การรักษาทันทีไม่จำเป็นต้องได้รับความยินยอมจากผู้ป่วยหรือผู้ปกครอง <br>&nbsp;2) กรณีผู้ป่วยอายุน้อยกว่า 18 ปี ถ้ามาคนเดียว และมารับการรักษาด้วยภาวะฉุกเฉิน สามารถให้ความยินยอมด้วยตนเองได้โดยต้องระบุว่าผู้ป่วยมาคนเดียว ซึ่งควรให้ผู้ปกครองที่ชอบด้วยกฎหมายเซ็นรับทราบภายหลัง พร้อมระบุวันเดือนปีและเวลาที่รับทราบการรักษานั้น",
        "<strong>3.4</strong> มีลายมือชื่อ หรือลายพิมพ์นิ้วมือของพยานฝ่ายผู้ป่วย 1 คน (กรณีลายพิมพ์นิ้วมือต้องระบุว่าเป็นของใครและใช้นิ้วใด) โดยระบุชื่อ นามสกุล และความสัมพันธ์กับผู้ป่วยอย่างชัดเจน <br>&nbsp;- กรณีที่มาคนเดียว ต้องระบุว่า “มาคนเดียว”",
        "<strong>3.5</strong> มีลายมือชื่อพยานฝ่ายเจ้าหน้าที่โรงพยาบาล 1 คน โดยระบุชื่อ นามสกุล และตำแหน่ง โดยต้องไม่เป็นบุคคลเดียวกันกับผู้ให้คำอธิบาย",
        "<strong>3.6</strong> มีข้อมูลรายละเอียดเหตุผล หรือความจำเป็นในการเข้ารับการรักษา วิธีการรักษาหรือหัตถการการใช้ยาระงับความรู้สึก ที่สอดคล้องกับสภาพปัญหาของผู้ป่วย ที่แจ้งแก่ผู้ป่วยและญาติรับทราบ",
        "<strong>3.7</strong> มีข้อมูลรายละเอียดเกี่ยวกับทางเลือก ข้อดี ข้อเสียของทางเลือกในการรักษาที่แจ้งแก่ผู้ป่วยและญาติรับทราบ <span style='color: red;'>(สอดคล้องกับเกณฑ์ข้อที่ 6)</span>",
        "<strong>3.8</strong> มีข้อมูลรายละเอียดเกี่ยวกับระยะเวลาในการรักษา ผลการรักษา ความเสี่ยง และภาวะ แทรกซ้อนที่อาจเกิดขึ้น <span style='color: red;'>(สอดคล้องกับเกณฑ์ข้อที่ 6)</span><br>&nbsp;- กรณีที่เขียนว่า “ได้อธิบายให้ผู้ป่วยรับทราบถึงผลดี ผลเสียของการผ่าตัดแล้ว” ไม่ถือว่ามี ข้อมูลรายละเอียดเนื้อหาที่แจ้งแก่ผู้ป่วยและญาติรับทราบ",
        "<strong>3.9</strong> มีการบันทึกระบุวันเดือนปี และเวลา ที่รับทราบและยินยอมให้ทำการรักษา",
    ],
    4: [
        "<strong>4.1</strong> บันทึก chief complaint: อาการและระยะเวลา หรือปัญหาที่ผู้ป่วยต้องมาโรงพยาบาล",
        "<strong>4.2</strong> บันทึก present illness: ในส่วน 5W, 2H (what, where, when, why, who, how, how many) โดยต้องมีอย่างน้อย 3 ข้อ<br>&nbsp; - กรณีผู้ป่วย “ไม่รู้สึกตัว” หรือ “ไม่สามารถซักประวัติได้” ต้องมีบันทึกว่า “ไม่รู้สึกตัว” หรือ “ซักประวัติไม่ได้”",
        "<strong>4.3</strong> บันทึก present illness ในส่วนการรักษาที่ได้มาแล้ว หรือในส่วนประวัติการรักษาที่ผ่านมา (รวมถึงการรับประทานยาเองจากบ้าน หรือการจัดการ การดูแลตนเองอื่น ๆ ที่เกี่ยวข้อง ก่อนมาโรงพยาบาล)<br>&nbsp;- กรณีไม่ได้รักษาที่ใดมาก่อนต้องระบุว่า “ไม่ได้รักษาจากที่ใด”<br>&nbsp;- กรณีผู้ป่วย “ไม่รู้สึกตัว” หรือ “ไม่สามารถซักประวัติได้” ต้องมีบันทึกว่า “ไม่รู้สึกตัว” หรือ “ซักประวัติไม่ได้”",
        "<strong>4.4</strong> บันทึก past illness ที่สำคัญและเกี่ยวข้องกับปัญหาที่มา หรือสอดคล้องกับปัญหาที่สงสัย <br>&nbsp;- กรณีไม่มี past illness ต้องระบุว่าไม่มี <br>&nbsp;- กรณีผู้ป่วย “ไม่รู้สึกตัว” หรือ “ไม่สามารถซักประวัติได้” ต้องมีบันทึกว่า “ไม่รู้สึกตัว” หรือ “ซักประวัติไม่ได้”",
        "<strong>4.5</strong> บันทึกประวัติการแพ้ยาและประวัติการแพ้อื่นๆ พร้อมระบุชื่อยา และสิ่งที่แพ้ <br>&nbsp;- กรณีไม่ทราบชื่อยาหรือสิ่งที่แพ้ต้องระบุ “ไม่ทราบ” <br>&nbsp;- กรณีไม่มีประวัติการแพ้ ต้องระบุ“ไม่มีประวัติการแพ้ยาและการแพ้อื่น ๆ” หรือข้อความอื่นที่แสดงถึงมีการซักประวัติและไม่พบประวัติการแพ้ยาและสารนั้น",
        "<strong>4.6</strong> บันทึกประวัติอื่นๆ ดังนี้ <br>&nbsp;1) Family history หรือ personal history หรือ social history หรือประวัติการทำงานที่เกี่ยวข้อง หรือสอดคล้องกับปัญหาที่มาในครั้งนี้ <br>&nbsp;2) กรณีเป็นผู้หญิงอายุ 11-60 ปี ต้องบันทึกประวัติประจำเดือน<br>&nbsp;3) กรณีเป็นเด็ก 0-14 ปี ต้องบันทึกประวัติ vaccination และ growth development",
        "<strong>4.7</strong> บันทึกการซักประวัติการเจ็บป่วยของระบบร่างกายอื่นๆ (review of system) ทุกระบบ",
        "<strong>4.8</strong> มีการบันทึกด้วยลายมือชื่อแพทย์ โดยสามารถระบุได้ว่าเป็นผู้ใด จากชื่อ นามสกุล และ เลขที่ใบอนุญาตประกอบวิชาชีพเวชกรรม (ในกรณีที่แยกใบกับ physical examination) <br>&nbsp;- กรณีที่มีการบันทึกผ่านระบบคอมพิวเตอร์ ต้องสามารถสืบค้นในระบบ log in ได้ว่าแพทย์ผู้ใดเป็นผู้บันทึก โดยไม่ต้องลงลายมือชื่อใหม่",
        "<strong>4.9</strong> ระบุแหล่งที่มาของข้อมูล เช่น ประวัติได้จากตัวผู้ป่วยเองหรือญาติ หรือประวัติเก่าจากเอกสารในเวชระเบียนหรือเอกสารใบส่งต่อ",
    ],
    5: [
        "<strong>5.1</strong> มีการบันทึก vital signs: temperature, pulse rate, respiration rate และ blood pressure <br>&nbsp;(กรณี blood pressure ให้ยกเว้นในเด็กเล็กอายุน้อยกว่า 5 ปีโดยพิจารณาตามสภาพปัญหาของผู้ป่วย)",
        "<strong>5.2</strong> มีบันทึกนำหนัก ทุกราย และส่วนสูงในกรณีดังต่อไปนี้ <br>&nbsp;(1) กรณีเด็ก บันทึกส่วนสูงทุกราย <br>&nbsp;(2) กรณีผู้ใหญ่ บันทึกส่วนสูงในกรณีที่มีความจำเป็นต้องใช้ค่า BMI (Body Mass Index) หรือค่า BSA (Body Surface Area) ในการวางแผนการรักษา เช่น รายที่ต้องให้ยาเคมีบำบัด เป็นต้น<br>&nbsp;- กรณีที่ชั่งน้ำหนัก และวัดส่วนสูงไม่ได้ ต้องระบุเหตุผลที่เหมาะสม",
        "<strong>5.3</strong> มีการบันทึกการตรวจร่างกายจากการ ดู คลำ เคาะ ฟัง ที่นำไปสู่การวินิจฉัยที่สอดคล้องกับ chief complaint ซึ่งมิใช่เขียนแค่คำว่า “ปกติ” หรือเขียนว่า “WNL”",
        "<strong>5.4</strong> มีการบันทึกโดยการวาดรูปหรือแสดงกราฟิก สิ่งที่ตรวจพบความผิดปกติที่ถูกต้อง <br>&nbsp;- ในกรณีที่ตรวจไม่พบความผิดปกติ หรือความผิดปกตินั้นไม่สามารถแสดงกราฟฟิกได้ ให้ผู้ตรวจประเมินระบุ NA โดยจะต้องได้คะแนนในเกณฑ์ข้อ 3",
        "<strong>5.5</strong> มีการบันทึกการตรวจร่างกายทุกระบบ ซึ่งมิใช่เขียนแค่ค3Eว่า “ปกติ” หรือเขียนว่า “ทุกระบบ WNL”",
        "<strong>5.6</strong> มีการสรุปปัญหาของผู้ป่วย ที่เข้ารับการรักษาในครั้งนี้ (problem list)",
        "<strong>5.7</strong> มีการสรุปวินิจฉัยขั้นต้น (provisional diagnosis) ที่สอดคล้องกับประวัติ และ หรือ ผลการตรวจร่างกาย",
        "<strong>5.8</strong> มีการบันทึกรายละเอียดแผนการรักษาในการ admit ครั้งนี้<span style='color: red;'><br>&nbsp; - กรณีบันทึกว่า admit ถือว่าไม่ผ่านเกณฑ์ข้อนี้</span>",
        "<strong>5.9</strong> มีการบันทึกลายมือชื่อแพทย์ที่รับผิดชอบ ในการตรวจร่างกาย โดยสามารถระบุได้ว่าเป็นผู้ใด จากชื่อ นามสกุล และเลขที่ใบอนุญาตประกอบวิชาชีพเวชกรรม (ในกรณีที่แยกใบกับ history) <br>&nbsp;- กรณีที่มีการบันทึกผ่านระบบคอมพิวเตอร์ ต้องสามารถสืบค้นในระบบ log in ได้ว่า แพทย์ผู้ใดเป็นผู้บันทึก โดยไม่ต้องลงลายมือชื่อใหม่",
    ],
    6: [
        "<strong>6.1</strong> มีการลงวันเดือนปี และเวลา ทุกครั้งที่บันทึก progress note",
        "<strong>6.2</strong> มีการบันทึกทุกวันใน 3 วันแรก",
        "<strong>6.3</strong> มีการบันทึกเนื้อหาครอบคลุม S O A P (subjective, objective, assessment, plan) ใน 3 วันแรก",
        "<strong>6.4</strong> มีการบันทึกทุกครั้งที่มีการเปลี่ยนแปลงอาการ หรือการรักษา หรือให้ยา หรือมีการทำ invasive procedure หรือเปลี่ยนแปลงแพทย์ผู้ดูแล",
        "<strong>6.5</strong> บันทึกเนื้อหาครอบคลุม S O A P ทุกครั้งที่มีการเปลี่ยนแปลงอาการ หรือการรักษา หรือ ให้ยาหรือมีการทำ invasive procedure หรือเปลี่ยนแปลงแพทย์ผู้ดูแล",
        "<strong>6.6</strong> มีการบันทึกการแปลผล investigation ที่สำคัญ และมีการวินิจฉัยร่วมกับการวางแผน การรักษาเมื่อผล investigation ผิดปกติ",
        "<strong>6.7</strong> มีการบันทึก progress note ลงตรงตำแหน่งที่หน่วยบริการกำหนดให้บันทึก",
        "<strong>6.8</strong> มีการบันทึกด้วยลายมือที่อ่านออกได้ และลงลายมือชื่อแพทย์ที่รับผิดชอบในการบันทึก progress note โดยสามารถระบุได้ว่าเป็นผู้ใด <br>&nbsp;- กรณีเวชระเบียนในระบบอิเล็กทรอนิกส์ต้องสามารถสืบค้นในระบบ log in ได้ว่าแพทย์ผู้ใดเป็นผู้บันทึก",
        "<strong>6.9</strong> การลงวันเดือนปีและเวลา พร้อมลงนามกำกับในใบคำสั่งการรักษา (ทั้งกรณี order for one day และ continue) ทุกครั้งที่มีการสั่งการรักษา โดยสามารถระบุได้ว่าเป็นผู้ใด <br>&nbsp;- กรณีนักศึกษาแพทย์ หรือการบันทึกของพยาบาลวิชาชีพที่รับคำสั่ง (รคส.) หรือมีการสั่งการรักษาทางช่องทางอื่นๆ เช่น แอปพลิเคชันไลน์ เป็นต้น ต้องมีการลงนามกำกับโดยแพทย์ผู้รักษาทุกครั้งที่สั่งการรักษา",
    ],
    7: [
        "<strong>7.1</strong> มีบันทึกวันเดือนปี เวลา ความจำเป็นรีบด่วน และหน่วยงานที่ขอปรึกษา",
        "<strong>7.2</strong> มีการบันทึกขอปรึกษา โดยระบุปัญหาที่ต้องการปรึกษาที่ชัดเจน",
        "<strong>7.3</strong> มีบันทึกประวัติการตรวจร่างกายและการรักษาโดยย่อ ของแพทย์ผู้ขอปรึกษา",
        "<strong>7.4</strong> มีการบันทึกด้วยลายมือที่อ่านออกได้และลงลายมือชื่อแพทย์ผู้ขอปรึกษา โดยสามารถระบุได้ ว่าเป็นผู้ใด จากชื่อ นามสกุล และเลขที่ใบอนุญาตประกอบวิชาชีพเวชกรรม <br>&nbsp;- กรณีไม่มีการลงลายมือชื่อแพทย์ผู้ขอปรึกษา จะไม่ได้คะแนนในเกณฑ์ข้อ 1-4 <br>&nbsp;- กรณีเป็นเวชระเบียนแบบอิเล็กทรอนิกส์ต้องสามารถสืบค้นในระบบ log in ได้ว่าแพทย์ผู้ใดเป็นผู้บันทึกขอปรึกษา รวมทั้งระบุเลขที่ใบอนุญาตประกอบวิชาชีพเวชกรรม",
        "<strong>7.5</strong> มีบันทึกผลการตรวจประเมินเพิ่มเติมและคำวินิจฉัยของผู้รับปรึกษา",
        "<strong>7.6</strong> มีบันทึกความเห็น หรือแผนการรักษา หรือการให้คำแนะนำ",
        "<strong>7.7</strong> มีบันทึก วัน เดือน ปี และ เวลา ที่ผู้รับปรึกษามาตรวจผู้ป่วย",
        "<strong>7.8</strong> มีการบันทึกด้วยลายมือที่อ่านออกได้ และลงลายมือชื่อแพทย์ผู้ให้คำปรึกษาโดย สามารถระบุ ได้ว่าเป็นผู้ใดจากชื่อ นามสกุล และเลขที่ใบอนุญาตประกอบวิชาชีพเวชกรรม <br>&nbsp;- กรณีไม่มีการลงลายมือชื่อแพทย์ผู้ให้คำปรึกษาจะไม่ได้คะแนนในเกณฑ์ข้อ 5-8 <br>&nbsp;- กรณีเป็นเวชระเบียนแบบอิเล็กทรอนิกส์ต้องสามารถสืบค้นในระบบ log in ได้ว่าแพทย์ผู้ใด เป็นผู้บันทึกการให้คำปรึกษา รวมทั้งระบุเลขที่ใบอนุญาตประกอบวิชาชีพเวชกรรม",
        "<strong>7.9</strong> แพทย์ผู้ให้คำปรึกษา บันทึกผลการให้คำปรึกษาลงตรงตำแหน่งที่หน่วยบริการกำหนด",
    ],
    8: [
        "<strong>8.1</strong> มีการบันทึก status ผู้ป่วยก่อนให้ยาระงับความรู้สึกและวิธีให้ยาระงับความรู้สึก",
        "<strong>8.2</strong> มีบันทึกโรคก่อนผ่าตัด ซึ่งต้องสอดคล้องกับการวินิจฉัยของแพทย์ <span style='color: red;'>หากข้อมูลขัดแย้งกัน ถือว่าไม่ผ่านเกณฑ์</span>",
        "<strong>8.3</strong> มีบันทึกชนิดและชื่อการผ่าตัด ซึ่งต้องสอดคล้องกับการผ่าตัดของแพทย์ <span style='color: red;'>หากข้อมูลขัดแย้งกัน ถือว่าไม่ผ่านเกณฑ์</span>",
        "<strong>8.4</strong> มีบันทึกก่อนการผ่าตัด (pre anesthetic evaluation) โดยทีมวิสัญญี มีการระบุประวัติ การได้รับยาระงับความรู้สึกก่อนหน้า (ถ้ามี) ยกเว้น (1) กรณีที่ผู้ป่วยเข้า admit ในวันเดียวกับวันที่เข้ารับการผ่าตัด <br>&nbsp;(2) กรณีที่ผู้ป่วยฉุกเฉิน สามารถบันทึกการตรวจเยี่ยมวันเดียวกับวันที่ผ่าตัดได้",
        "<strong>8.5</strong> มีบันทึกสัญญาณชีพและบันทึกการติดตามเฝ้าระวัง ระหว่างดมยาอย่างเหมาะสมทุก 5 นาที",
        "<strong>8.6</strong> มีบันทึก intake, output, blood loss, total intake และ total output",
        "<strong>8.7</strong> มีบันทึกการดูแลผู้ป่วยหลังสิ้นสุดการผ่าตัด 1 ชั่วโมง (recovery room) ตามมาตรฐาน ราชวิทยาลัยวิสัญญีแพทย์ โดยทีมวิสัญญี ยกเว้น - กรณีที่ผู้ป่วย on endotracheal tube และส่งต่อเข้ารับการรักษาในตึกผู้ป่วย ให้ผู้ตรวจ ประเมินระบุ NA",
        "<strong>8.8</strong> มีบันทึกการดูแลผู้ป่วยหลังการผ่าตัด (post anesthetic round) โดยทีมวิสัญญี และต้องระบุปัญหาจากการได้ยาระงับความรู้สึกในครั้งนี้ <span style='color: red;'>หากไม่มีต้องระบุ “ไม่พบปัญหา”</span>",
        "<strong>8.9</strong> มีการบันทึกด้วยลายมือที่อ่านออกได้และระบุ ชื่อ นามสกุล วิสัญญีแพทย์ /พยาบาล ที่รับผิดชอบ<br>&nbsp;- กรณีเวชระเบียนในระบบอิเล็กทรอนิกส์ต้องสามารถสืบค้นในระบบ log in ได้ว่า วิสัญญีแพทย์ / พยาบาล เป็นผู้ใดเป็นผู้บันทึก",
    ],
    9: [
        "<strong>9.1</strong> มีการบันทึกข้อมูลผู้ป่วยถูกต้อง ครบถ้วน ประกอบด้วย ชื่อ สกุล อายุ HN AN เพศ เป็นต้น",
        "<strong>9.2</strong> มีบันทึกการวินิจฉัยโรคก่อนทำหัตถการ (pre-operative diagnosis) และหลังทำหัตถการ (post-operative diagnosis) หากจะใช้ตัวย่อใช้ได้เฉพาะที่ปรากฏในหนังสือ ICD-10 เท่านั้น โดย post-operative diagnosis ต้องบันทึกเป็นชื่อโรคที่แพทย์วินิจฉัยเท่านั้น ไม่สามารถใช้ “same” หรือใช้เครื่องหมาย “ปีกกา” หรือเครื่องหมาย “------------” หรืออื่นๆ",
        "<strong>9.3</strong> มีบันทึกชื่อการทำหัตถการ ถูกต้อง ครบถ้วน สอดคล้องกับวิธีการทำหัตถการนั้น",
        "<strong>9.4</strong> มีบันทึกรายละเอียดสิ่งที่ตรวจพบ สอดคล้องกับ post-operative diagnosis",
        "<strong>9.5</strong> มีบันทึกรายละเอียดวิธีการทำหัตถการประกอบด้วย position incision สิ่งที่ตัดออก เป็นต้น รวมถึงการส่งชิ้นเนื้อเพื่อส่งตรวจ",
        "<strong>9.6</strong> มีบันทึกภาวะแทรกซ้อน และจำนวนเลือดที่สูญเสียระหว่างผ่าตัด (สามารถใช้คำว่า minimal blood loss ได้)<br>&nbsp; - กรณีไม่มีภาวะดังกล่าวต้องระบุ “ไม่มี”",
        "<strong>9.7</strong> มีบันทึกวัน เวลา ที่เริ่มต้นและสิ้นสุดการทำหัตถการ",
        "<strong>9.8</strong> มีบันทึก ชื่อ-นามสกุล คณะผู้ร่วมทำหัตถการ ได้แก่ แพทย์ วิสัญญี และ scrub nurse เป็นต้น และวิธีการให้ยาระงับความรู้สึก",
        "<strong>9.9</strong> มีการบันทึกด้วยลายมือที่อ่านออกได้ และลงลายมือชื่อแพทย์ผู้ทำหัตถการ โดยสามารถระบุ ได้ว่าเป็นผู้ใด จากชื่อ นามสกุล และเลขที่ใบอนุญาตประกอบวิชาชีพเวชกรรม <br>&nbsp;- กรณีเป็น operative note แบบอิเล็กทรอนิกส์ต้องสามารถสืบค้นในระบบ log in ได้ว่า แพทย์ผู้ใดเป็นผู้บันทึกการทำหัตถการ รวมทั้งระบุเลขที่ใบอนุญาตประกอบวิชาชีพเวชกรรม",
    ],
    10: [
        "<strong>10.1</strong> บันทึกการประเมินผู้คลอดแรกรับในส่วนของประวัติ: obstetric history (gravida,parity, abortion, live, LMP, EDC, gestational age), ANC history, complication,risk monitoring และการตรวจร่างกายโดยแพทย์หรือพยาบาล",
        "<strong>10.2</strong> การประเมินผู้คลอดระยะรอคลอด สอดคล้องตามสภาพผู้คลอด: วันเดือนปี เวลา ชีพจรความดันโลหิต progress labour (uterine contraction, cervical dilation and effacement membrane), fetal assessment (fetal heart sound, station),complication",
        "<strong>10.3</strong> มีบันทึกวันที่ ระยะเวลา การคลอดแต่ละ stage <span style='color: red;'><br>&nbsp;- กรณี elective caesarean section ไม่ต้องประเมิน ให้ผู้ตรวจประเมินระบุ NA</span>",
        "<strong>10.4</strong> มีบันทึกหัตถการ วิธีการคลอด ข้อบ่งชี้ในการทำสูติศาสตร์หัตถการ ภาวะแทรกซ้อน และการระงับความรู้สึก(ถ้ามี)การทำ episiotomy ตามสภาพและสอดคล้องกับปัญหาของผู้คลอด",
        "<strong>10.5</strong> มีบันทึกคำสั่ง และบันทึกการให้ยาในระยะก่อน ระหว่าง และหลังคลอด",
        "<strong>10.6</strong> มีบันทึก วันเดือนปี และเวลาที่ทารกคลอด เพศ น้ำหนัก และความยาวของทารก",
        "<strong>10.7</strong> มีบันทึกการประเมินมารดาระยะหลังคลอด ในส่วน: placenta checked, complication ในระยะหลังคลอด, blood loss, vital signs และสภาพคนไข้ก่อนย้ายออกจากห้องคลอด หรือหลังคลอด 2 ชั่วโมง",
        "<strong>10.8</strong> มีบันทึกการประเมินทารก Apgar score (1 นาที 5 นาทีและ 10 นาที) ประเมินสภาพทารก เบื้องต้น (initial assessment) และประเมินภาวะแทรกซ้อน<span style='color: red;'> หากไม่มีภาวะแทรกซ้อน ต้องระบุ “ไม่มี”</span>",
        "<strong>10.9</strong> มีการบันทึกด้วยลายมือที่อ่านออกได้และลงลายมือชื่อแพทย์ หรือพยาบาลวิชาชีพผู้ทำคลอด โดยสามารถระบุได้ว่าเป็นผู้ใด จากชื่อและนามสกุล<br>&nbsp; - กรณีเวชระเบียนในระบบอิเล็กทรอนิกส์ต้องสามารถสืบค้นในระบบ log in ได้ว่า ชื่อแพทย์ หรือพยาบาลผู้บันทึกการทำคลอดเป็นผู้ใด ",
    ],
    11: [
        "<strong>11.1</strong> มีบันทึกการซักประวัติอาการสำคัญ ประวัติปัจจุบัน และประวัติอดีตที่เกี่ยวข้องกับปัญหาที่ต้องการฟื้นฟูสมรรถภาพ",
        "<strong>11.2</strong> มีบันทึกการตรวจร่างกายในส่วนที่เกี่ยวข้อง สอดคล้องกับปัญหาที่ต้องการฟื้นฟูสมรรถภาพ",
        "<strong>11.3</strong> มีบันทึกการวินิจฉัยโรคที่สอดคล้อง หรือการวินิจฉัยทางกายภาพบำบัด และมีบันทึกสรุป ปัญหาที่ต้องการฟื้นฟูสมรรถภาพ",
        "<strong>11.4</strong> มีบันทึกเป้าหมายในการฟื้นฟูสมรรถภาพ การวางแผนในการฟื้นฟูสมรรถภาพ ชนิดของการบำบัดหรือหัตถการ ข้อห้ามและข้อควรระวัง",
        "<strong>11.5</strong> มีบันทึกการรักษาที่ให้ในแต่ละครั้ง โดยระบุอวัยวะหรือตำแหน่งที่ทำการบำบัดและระยะเวลาที่ใช้",
        "<strong>11.6</strong> มีบันทึกการประเมินผลการให้บริการ และความก้าวหน้าของการฟื้นฟูสมรรถภาพตามเป้าหมายที่ได้ตั้งไว้",
        "<strong>11.7</strong> มีบันทึกสรุปผลการให้บริการฟื้นฟูสมรรถภาพ และแผนการจำหน่ายผู้ป่วย",
        "<strong>11.8</strong> มีบันทึกรายละเอียดการให้ home program หรือการให้คำแนะนำในการปฏิบัติตัว (patient and family education) หรือแผนการดูแลต่อเนื่อง",
        "<strong>11.9</strong> มีการบันทึกด้วยลายมือที่อ่านออกได้ และลงลายมือชื่อแพทย์เวชศาสตร์ฟื้นฟู และ เลขที่ใบอนุญาตประกอบวิชาชีพเวชกรรม หรือนักกายภาพบำบัดให้ระบุ ชื่อ สกุล และตำแหน่ง โดยสามารถระบุได้ว่าเป็นผู้ใด ทุกครั้งที่มีการบำบัด <br>&nbsp;- กรณีเวชระเบียนในระบบอิเล็กทรอนิกส์ต้องสามารถสืบค้นในระบบ log in ได้ว่า แพทย์เวชศาสตร์ฟื้นฟู หรือนักกายภาพบำบัด ผู้บันทึกการทำกายภาพบำบัดเป็นผู้ใด",
    ],
    12: [
        "<strong>12.1</strong> <span style = 'font-weight: bold;' >การประเมินแรกรับ </span>: มีการบันทึกที่สะท้อนข้อมูลสำคัญ ได้แก่ <br>&nbsp;1.1 อาการสำคัญ: อาการที่ผู้ป่วยกังวลมากที่สุดที่ต้องมาพบแพทย์ โดยระบุอาการหลัก เพียง 1-2 อาการ ตามด้วยระยะเวลาที่เกิดอาการ ส่วนประวัติการเจ็บป่วยปัจจุบันและอดีตที่เกี่ยวข้อง คือการซักถามถึงอาการ หรือ เหตุการณ์การเจ็บป่วยตั้งแต่เริ่มต้นของการเจ็บป่วย จนถึงปัจจุบันตามลำดับเวลาที่เกิดขึ้นนั้น และ <br>&nbsp;1.2 อาการผู้ป่วยแรกรับ ครอบคลุมตามสภาวะของผู้ป่วย และระบุเวลาแรกรับผู้ป่วยไว้ในความดูแล",
        "<strong>12.2</strong> การระบุปัญหาทางการพยาบาล <br>&nbsp;2.1 มีการระบุปัญหาการพยาบาลที่สำคัญสอดคล้องกับอาการ อาการแสดงด้านร่างกาย และ/หรือด้านจิตใจ อารมณ์ สังคม และจิตวิญญาณ ตั้งแต่แรกรับจนกระทั่งจำหน่าย",
        "<strong>12.3</strong> กิจกรรมการพยาบาล (Nursing intervention)<br>&nbsp; 3.1 ระบุกิจกรรมการพยาบาล ที่ครอบคลุมอาการแสดง หรือปัญหาที่สำคัญตามสภาวะของผู้ป่วย และ <br>&nbsp; 3.2 มีการประเมินซ้ำ: ผู้ป่วยได้รับการประเมินซ้ำตามช่วงเวลาที่เหมาะสม เพื่อประเมินการตอบสนองต่อการรักษาพยาบาล โดยในบันทึกการพยาบาล ควรระบุอาการหรืออาการแสดงที่ไม่ปกติ หรือรุนแรงขึ้น หรือข้อบ่งชี้ถึงการเกิดภาวะแทรกซ้อน อย่างเหมาะสม ทันเหตุการณ์ (early detection) และตัดสินใจรายงานแพทย์ได้เหมาะสมทันเวลา และ/หรือ <br>&nbsp;3.3 ระบุกิจกรรมที่ตอบสนอง ต่อการตรวจเยี่ยมร่วมกับทีมสุขภาพในปัญหา หรือกิจกรรมที่สำคัญ (ถ้ามี)",
        "<strong>12.4</strong> การประเมินการตอบสนองต่อการรักษาพยาบาล <br>&nbsp; 4.1 มีบันทึกการเปลี่ยนแปลงของการเจ็บป่วย ที่ตอบสนองต่อกิจกรรมการพยาบาล หรือ การรักษาของแพทย์<br>&nbsp; 4.2 มีบันทึกการตรวจ หรือการให้การรักษาที่สำคัญ (ถ้ามี) เช่น การเจาะปอด การผ่าตัด โดยบันทึก วันเดือนปี และเวลา อาการก่อน ขณะ และหลังทำ ตลอดจนผลที่ได้ เช่น น้ำจากการเจาะปอดลักษณะเป็นอย่างไร จำนวนเท่าใด ส่งไปตรวจวินิจฉัยอะไรบ้าง เป็นต้น",
        "<strong>12.5</strong> การให้ข้อมูลระหว่างการรักษาพยาบาล <br>&nbsp;5.1 มีบันทึกการให้ข้อมูลที่จำเป็นและการช่วยเหลือด้านร่างกาย และหรือ ด้านอารมณ์ จิตใจ และคำปรึกษาที่เหมาะสมสอดคล้องกับปัญหา ความต้องการของผู้ป่วย/ครอบครัว",
        "<strong>12.6</strong> การเตรียมความพร้อมผู้ป่วยเพื่อการดูแลต่อเนื่องที่บ้าน (Discharge plan) <br>&nbsp;6.1 มีการบันทึกระบุอาการ หรือปัญหาสำคัญ หรือความต้องการของผู้ป่วยที่อาจเกิดขึ้นหลังจำหน่าย และ <br>&nbsp;6.2 มีการบันทึก <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;6.2.1 การให้ข้อมูลที่จำเป็นและการช่วยเหลือให้เกิดการเรียนรู้ สำหรับการดูแลตนเอง ให้มีพฤติกรรมสุขภาพที่เอื้อต่อการมีสุขภาพดี และหรือ อาจมีการจัดกิจกรรมเสริมทักษะที่จำเป็นให้แก่ผู้ป่วย/ครอบครัว สามารถปฏิบัติได้ด้วยตนเอง <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;6.2.2 มีการระบุข้อมูล ที่สะท้อนความก้าวหน้าในการเรียนรู้ และหรือ ฝึกทักษะของผู้ป่วย/ครอบครัว",
        "<strong>12.7</strong> การประสานการดูแลต่อเนื่อง <br>&nbsp; 7.1 มีการระบุปัญหา ความต้องการ ข้อมูลอาการของผู้ป่วยที่ต้องได้รับการดูแลต่อเนื่อง ทั้งในโรงพยาบาล และในเครือข่าย/ชุมชน <br>&nbsp; 7.2 มีบันทึกการนัดหมายผู้ป่วยกลับมารับการรักษาต่อเนื่องเมื่อมีข้อบ่งชี้ รวมทั้งแนวทางการช่วยเหลือและให้คำปรึกษาแก่ผู้ป่วยที่ออกจากโรงพยาบาลตามความเหมาะสม (ถ้ามี)",
        "<strong>12.8</strong> การจำหน่ายผู้ป่วย <br>&nbsp; 8.1 มีการสรุปอาการ อาการแสดงและสัญญาณชีพ รวมทั้งผลการประเมินความพร้อมของ ผู้ป่วย และหรือ ผู้ดูแลก่อนจำหน่าย และ <br>&nbsp; 8.2 มีการระบุ กิจกรรมการพยาบาลที่สอดคล้องกับอาการ และอาการแสดงของผู้ป่วยก่อนจำหน่าย เช่น คำแนะนำก่อนกลับบ้าน การดูแลต่อเนื่อง และการนัดตรวจครั้งต่อไป (ถ้ามี) <br>&nbsp; 8.3 ระบุข้อมูลผู้ป่วยเพื่อต้องส่งต่อสถานบริการ หรือหน่วยงานที่เกี่ยวข้อง (ถ้ามี)",
        "<strong>12.9</strong> การบันทึกวันเดือนปีเวลา และการลงลายมือชื่อ <br>&nbsp;9.1 การบันทึกวันเดือนปี และเวลา <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;9.1.1 แรกรับ : ระบุวันเดือนปี และเวลา แรกรับผู้ป่วยไว้ในความดูแล <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;9.1.2 ระหว่างการดูแล : <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;9.1.2.1 มีบันทึกวันเดือนปีและเวลา ชัดเจนในแต่ละเหตุการณ์ และสัมพันธ์กับ การเปลี่ยนแปลง และการตัดสินใจรายงานแพทย์ในเวลาที่เหมาะสมทันการณ์และการตอบสนอง <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;9.1.2.2 มีบันทึกวันเดือนปีและเวลา ในคำสั่งการรักษาของแพทย์ กรณี มีการเปลี่ยนแปลงการรักษา <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;9.1.2.3 มีบันทึกวันเดือนปี และเวลาในใบการให้ยา (medication administration record) ที่สอดคล้องกับคำสั่งการรักษา <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;9.1.3 ก่อนจำหน่าย: ระบุวันเดือนปี และเวลา ที่จำหน่ายชัดเจน <br>&nbsp;9.2 การบันทึกและลงลายมือชื่อ <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;9.2.1 บันทึกด้วยลายมือที่อ่านออกได้ <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;9.2.2 มีการลงลายมือชื่อ และนามสกุล ของพยาบาลวิชาชีพผู้บันทึกทุกครั้ง โดยสามารถระบุได้ว่าเป็นผู้ใด ยกเว้นใบบันทึกการให้ยา (medication administration record) ที่ให้ลงเฉพาะชื่อ ไม่ต้องระบุนามสกุลได้ โดยอนุโลมให้ผ่านเกณฑ์เนื่องจากมีข้อจำกัดของพื้นที่ในการบันทึก",
    ],
}


def _norm(v):
    if v is None:
        return None
    return str(v).strip().upper()

def _counted(values):
    """คืนเฉพาะค่าที่นับได้จริง (0/1) โดย normalize ก่อน"""
    out = []
    for v in values:
        s = _norm(v)
        if s in (None, "", "NA"):
            continue  
        if s in ("0", "1"):
            out.append(s)
    return out

def sections_from_form(form):
    sections = []
    for idx, title in enumerate(IPD_SECTION_TITLES, start=1):
        criteria_labels = IPD_CRITERIA_NAMES.get(idx, [])
        rows_with_labels = []
        
        for j, label in enumerate(criteria_labels, start=1):
            field_name = f"s{idx}_{j}"
            try:
                f = form[field_name] 
                
                rows_with_labels.append({
                    'field': f, 
                    'label': mark_safe(label),
                    'val': f.value()
                })
            except KeyError:
                continue
            
        note_field_name = f"s{idx}_note"
        try:
            note = form[note_field_name]
        except KeyError:
            note = None

        bonus_field = None
        if idx == 1:
            bonus_field = form['bonus_s1']
        elif idx == 12:
            bonus_field = form['bonus_s12']

        sections.append({
            "index": idx, 
            "title": title, 
            "rows": rows_with_labels, 
            "note": note,
            "bonus_field": bonus_field
        })
    return sections

def score_create(request):
    if request.method == "POST":
        form = PatientScoreForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request, "บันทึกข้อมูลสำเร็จ")
            return redirect(reverse("MRA:score_detail", args=[obj.id]))
        else:
            print("FORM ERRORS:", form.errors.as_json())
            messages.error(request, "กรอกไม่ครบหรือรูปแบบไม่ถูกต้อง")
    else:
        form = PatientScoreForm()

    ctx = {"form": form, "sections": sections_from_form(form)}
    return render(request, "scores/score_form.html", ctx)

def score_detail(request, pk):
    obj = get_object_or_404(PatientScore, pk=pk)
    form = PatientScoreForm(instance=obj)
    sections = sections_from_form(form)
    stats = {s["index"]: s for s in obj.section_scores()}
    for sec in sections:
        sec["stat"] = stats.get(sec["index"], {"yes": 0, "counted": 0, "percent": 0.0})
    return render(request, "scores/score_detail.html", {"obj": obj, "form": form, "sections": sections})


# ***************************************************** IPD EDIT ***********************************************************************************
@login_required
def score_edit(request, pk):

    obj = get_object_or_404(PatientScore, pk=pk)
    is_owner = (obj.created_by == request.user)
    is_admin = request.user.is_superuser or request.user.is_staff

    if not (is_owner or is_admin):
        messages.error(request, "คุณไม่มีสิทธิ์แก้ไขรายการที่ผู้อื่นสร้าง")
        return redirect('MRA:score_detail', pk=pk)

    if request.method == "POST":
        form = PatientScoreForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "แก้ไขข้อมูลเรียบร้อยแล้ว")
            return redirect(reverse("MRA:score_detail", args=[obj.id]))
    else:
        form = PatientScoreForm(instance=obj)

    ctx = {
        "form": form, 
        "sections": sections_from_form(form),
        "editing": True,
        "obj": obj
    }
    return render(request, "scores/score_form.html", ctx)



# ****************************************************************************************************************************************

from django.db.models import Value

def score_summary(request):
    q = (request.GET.get("q") or "").strip()
    qs = PatientScore.objects.all().order_by("-created_at")

    # 1. ค้นหาจาก created_at
    start_d, end_d = _parse_date_or_day_range(q)
    if start_d and end_d:
        start_dt, end_dt_excl = _aware_range_from_dates(start_d, end_d)
        qs = qs.filter(created_at__gte=start_dt, created_at__lt=end_dt_excl)

    max_criteria = 0
    for section_idx in IPD_CRITERIA_NAMES:
        count = len(IPD_CRITERIA_NAMES[section_idx])
        if count > max_criteria:
            max_criteria = count
    if max_criteria == 0:
        max_criteria = 9

    rows = []
    for i, title in enumerate(IPD_SECTION_TITLES, start=1):
        cols = []
        valid_pcts = []
        
        # 2. จำนวนรายการแยกตามรายหัวข้อ
        max_records = 0 
        
        section_criteria = IPD_CRITERIA_NAMES.get(i, [])
        num_items = len(section_criteria) if section_criteria else max_criteria

        for j in range(1, max_criteria + 1):
            if j <= num_items:
                field = f"s{i}_{j}"
                try:
                    values = list(qs.values_list(field, flat=True))
                    
                    # --- แก้ไขตรงนี้: กรองนับเฉพาะคนที่ได้คะแนน "1" หรือ "0" เท่านั้น ---
                    # ป้องกันการเผลอนับค่าว่าง ("") หรือ N/A เข้าไปในจำนวนรายการ
                    valid_values = [str(v).strip() for v in values if str(v).strip() in ["0", "1"]]
                    total = len(valid_values)
                    yes = sum(1 for v in valid_values if v == "1")
                    
                    if total > max_records:
                        max_records = total
                        
                    if total > 0:
                        pct = (yes / total * 100.0)
                        cols.append({"percent": pct, "is_empty": False})
                        valid_pcts.append(pct)
                    else:
                        cols.append({"is_empty": True})
                except:
                    cols.append({"is_empty": True})
            else: 
                cols.append({"is_empty": True})
        
        avg = sum(valid_pcts) / len(valid_pcts) if valid_pcts else 0.0
        is_empty_avg = len(valid_pcts) == 0 
        
        rows.append({
            "index": i, 
            "title": title, 
            "cols": cols, 
            "avg": avg, 
            "is_empty_avg": is_empty_avg, 
            "records_count": max_records # คืนค่าที่กรองแล้ว
        })

    # --- คำนวณแถว Total ด้านล่างสุด ---
    total_cols = []
    valid_total_pcts = []
    for j in range(1, max_criteria + 1):
        col_sum = 0.0
        col_count = 0
        for r in rows:
            if (j - 1) < len(r["cols"]) and not r["cols"][j - 1].get("is_empty"):
                col_sum += r["cols"][j - 1]["percent"]
                col_count += 1
                
        if col_count > 0:
            avg_pct = col_sum / col_count  
            total_cols.append({"percent": avg_pct, "is_empty": False})
            valid_total_pcts.append(avg_pct)
        else:
            total_cols.append({"is_empty": True})
            
    total_avg = sum(valid_total_pcts) / len(valid_total_pcts) if valid_total_pcts else 0.0

    # -------------------------------------------------------------
    # คำนวณข้อมูลสำหรับกราฟเส้นรายเดือน
    # -------------------------------------------------------------
    import json
    monthly_data_dict = {}
    for obj in qs:
        if obj.created_at:
            # ดึง ปี-เดือน เช่น 2026-03
            m_label = obj.created_at.strftime("%Y-%m")
            if m_label not in monthly_data_dict:
                monthly_data_dict[m_label] = {'yes': 0, 'counted': 0}
            monthly_data_dict[m_label]['yes'] += (obj.total_yes or 0)
            monthly_data_dict[m_label]['counted'] += (obj.total_counted or 0)

    sorted_months = sorted(list(monthly_data_dict.keys()))
    thai_months = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
    
    trend_labels = []
    trend_data = []
    for m in sorted_months:
        y, mo = m.split('-')
        thai_year = int(y) + 543 # แปลงเป็น พ.ศ.
        trend_labels.append(f"{thai_months[int(mo)-1]} {thai_year}")
        
        d = monthly_data_dict[m]
        pct = (d['yes'] / d['counted'] * 100.0) if d['counted'] > 0 else 0.0
        trend_data.append(round(pct, 2))
    # -------------------------------------------------------------

    ctx = {
        "q": q,
        "rows": rows,
        "total_cols": total_cols,
        "total_avg": total_avg,
        "section_titles": IPD_SECTION_TITLES,
        "trend_labels": json.dumps(trend_labels),
        "trend_data": json.dumps(trend_data), 
    }
    return render(request, "scores/summary.html", ctx)

# ************************************/score coverage*****************************************************************


def _norm(v):
    if v is None:
        return ""
    return str(v).strip().upper()

IGNORED = {"", "NA", None}

def _counted_list(values):
    """คืนเฉพาะค่า 0/1 (ตัดว่าง/NA ออก)"""
    out = []
    for v in values:
        s = _norm(v)
        if s in ("0", "1"):
            out.append(s)
    return out

SECTION_TITLES = [
    "Discharge summary : Dx., OP",
    "Discharge summary : Other",
    "Informed consent",
    "History",
    "Physical exam",
    "Progress note",
    "Consultation record",
    "Anesthetic record",
    "Operative note",
    "Labour record",
    "Rehabilitation record",
    "Nurses' note",
]

def _parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except Exception:
            pass
    return None

def _make_aware_day_range(d1, d2):
    tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(datetime.combine(d1, time.min), tz)
    end_dt   = timezone.make_aware(datetime.combine(d2 + timedelta(days=1), time.min), tz)
    return start_dt, end_dt

# ---------- VIEW: สรุปจำนวนที่ตรวจ + ร้อยละความสมบูรณ์ ----------
def score_coverage(request):
    a_start = _parse_date(request.GET.get("admit_start"))
    a_end   = _parse_date(request.GET.get("admit_end"))
    d_start = _parse_date(request.GET.get("disch_start"))
    d_end   = _parse_date(request.GET.get("disch_end"))

    qs = PatientScore.objects.all().order_by("-created_at")

    if a_start and a_end:
        qs = qs.filter(date_admitted__gte=a_start, date_admitted__lte=a_end)
    if d_start and d_end:
        qs = qs.filter(date_discharged__gte=d_start, date_discharged__lte=d_end)

    yes_all = 0
    counted_all = 0
    rows = []
    total_records = qs.count()

    for i, title in enumerate(IPD_SECTION_TITLES, start=1):
        checked_records = 0
        yes = counted = 0

        for rec in qs.values_list(*[f"s{i}_{j}" for j in range(1, IPD_N_ITEMS + 1)]):
            vals = list(rec)
            counted_vals = [str(v).strip().upper() for v in vals if str(v).strip().upper() in ("0", "1")]
            if counted_vals:
                checked_records += 1
                yes     += sum(1 for v in counted_vals if v == "1")
                counted += len(counted_vals)

        yes_all     += yes
        counted_all += counted

        pct = (yes * 100.0 / counted) if counted else 0.0
        rows.append({
            "index": i,
            "title": title,
            "checked_records": checked_records,
            "percent": pct,
        })

    overall_pct = (yes_all * 100.0 / counted_all) if counted_all else 0.0

    ctx = {
        "rows": rows,
        "total_records": total_records,
        "examined_total": max(r["checked_records"] for r in rows) if rows else 0,
        "overall_pct": overall_pct,
        "admit_start": request.GET.get("admit_start", ""),
        "admit_end": request.GET.get("admit_end", ""),
        "disch_start": request.GET.get("disch_start", ""),
        "disch_end": request.GET.get("disch_end", ""),
    }
    return render(request, "scores/coverage.html", ctx)


@login_required
def score_delete(request, pk):
    """ ฟังก์ชันสำหรับลบข้อมูล IPD (PatientScore) """
    obj = get_object_or_404(PatientScore, pk=pk)
    
    is_owner = (obj.created_by == request.user)
    is_admin = request.user.is_superuser or request.user.is_staff

    if not (is_owner or is_admin):
        messages.error(request, "คุณไม่มีสิทธิ์ลบรายการที่ผู้อื่นสร้าง")
        return redirect('MRA:score_detail', pk=pk)

    # ลบข้อมูล
    obj.delete()
    messages.success(request, "ลบข้อมูล IPD เรียบร้อยแล้ว")
    return redirect('MRA:score_list')

# **************************************************************************************************************************************************
# ********************************************  OPD  ***********************************************************************************************
# ********************************************  OPD  ***********************************************************************************************
# **************************************************************************************************************************************************
# **************************************************************************************************************************************************



OPD_SECTION_TITLES = [
    "Patient Profile",
    "History (1st visit)",
    "Physical examination/Diagnosis",
    "Treatment/Investigation",
    "Follow Up",
    "Operative note",
    "Informed consent",
]

OPD_SECTION_REMARKS = {
    2: "ให้คะแนนเพิ่ม 1 คะแนน \n- กรณีที่มีการบันทึก present illness ครบทั้ง 5W, 2H (what, where, when, why, who, how, how many)",
    4: "ให้คะแนนเพิ่ม 1 คะแนน \n- กรณีที่มีการสั่งใช้ยานอกบัญชียาหลักแห่งชาติ แล้วมีการระบุเหตุผลการใช้ยา (ภาคผนวก ค.)",
    5: "ให้คะแนนเพิ่ม 1 คะแนน \n- กรณีที่มีการสั่งใช้ยานอกบัญชียาหลักแห่งชาติ แล้วมีการระบุเหตุผลการใช้ยา (ภาคผนวก ค.)",

}
OPD_N_ITEMS = 7
DEFAULT_ITEMS_TEXTS = [f"เกณฑ์ {i}" for i in range(1, OPD_N_ITEMS + 1)]

N_VISITS_SECTION5 = 3
VISIT_LABELS = {1: "ครั้งที่ 1", 2: "ครั้งที่ 2", 3: "ครั้งที่ 3"}

OPD_CRITERIA_NAMES = {
    1: [
        "1. มีข้อมูลผู้ป่วยถูกต้อง ครบถ้วน ได้แก่ ข้อมูลชื่อ นามสกุล เพศ (หรือคำนำหน้าชื่อ เช่น นาย นาง) HN และอายุ หรือวัน เดือน ปีเกิดของผู้ป่วย \n-   กรณีไม่ทราบวันเดือนเกิดอนุโลมให้มีเฉพาะปี พ.ศ.ได้ \n-   กรณีที่ไม่ทราบว่าผู้ป่วยเป็นใครและไม่สามารถสืบค้นได้ มีระบุ “ชายหรือหญิงไม่ทราบชื่อ”",
        "2. มีข้อมูลที่อยู่ปัจจุบันและข้อมูลเลขประจำตัวประชาชนของผู้ป่วย หรือเลขที่ใบต่างด้าว \n-   กรณีคนต่างด้าวที่เกิดในไทยแต่ไม่สามารถที่จะขึ้นทะเบียนเป็นคนไทยได้ มีระบุ “ไม่มีเลขที่บัตร” \n-   กรณีชาวต่างชาติ มีระบุเลขที่หนังสือเดินทาง \n-   กรณีที่ผู้ป่วยไม่รู้สึกตัว ให้ระบุรายละเอียดว่า “ไม่รู้สึกตัว” \n-   กรณีผู้ป่วยเสียชีวิตและไม่พบหลักฐาน มีระบุ “เสียชีวิตและไม่พบหลักฐาน”",
        "3. มีข้อมูลชื่อและนามสกุลของญาติ หรือผู้ที่ติดต่อได้ในกรณีฉุกเฉิน โดยระบุความสัมพันธ์กับผู้ป่วย และที่อยู่หรือหมายเลขโทรศัพท์ที่ติดต่อได้ \n-   กรณีที่เป็นที่อยู่เดียวกับผู้ป่วย อาจบันทึกว่า บ้านเดียวกัน หรือ บดก. \n-   กรณีผู้ป่วยไม่รู้สึกตัวหรือไม่มีญาติ มีระบุ “ไม่รู้สึกตัว” หรือ “ไม่มีญาติ”",
        "4. มีข้อมูลประวัติการแพ้ยาและประวัติการแพ้อื่น ๆ พร้อมระบุยาหรือสิ่งที่แพ้ หรือ “ปฏิเสธ” การแพ้ยา/แพ้อื่น ๆ หรือมีข้อความที่สื่อความหมายว่า\n    ได้มีการซักประวัติแพ้ยาและประวัติ การแพ้อื่น ๆ",
        "5. มีข้อมูลหมู่เลือดหรือบันทึกว่า “ไม่ทราบ” หรือ “ไม่เคยตรวจหมู่เลือด”",
        "6. มีข้อมูลวันเดือนปีที่บันทึกข้อมูล ชื่อ และนามสกุลผู้รับผิดชอบในการบันทึกข้อมูล ที่สามารถ ระบุได้ว่าเป็นผู้ใด",
        "7. มีข้อมูลชื่อ นามสกุล และ HN ทุกหน้าของเวชระเบียนที่มีการบันทึกข้อมูลการรักษา \n-   กรณีเวชระเบียนบันทึกในรูปของอิเล็กทรอนิกส์ ต้องมีข้อมูลชื่อ นามสกุล และ HN ทุกหน้าที่ส่งให้ตรวจสอบ \n-   กรณีเป็นเวชระเบียนฉบับจริงต้องมีข้อมูล ชื่อ นามสกุล และ HN ในทุกแผ่น",
    ],
    2: [
        "1. มีบันทึก chief complaint: อาการและระยะเวลา หรือปัญหาที่ผู้ป่วยต้องมาโรงพยาบาล",
        "2. มีบันทึก present illness ในส่วนของอาการแสดงและการรักษาที่ได้มาแล้ว (กรณีผู้ป่วยนอกโรคทั่วไป) หรือในส่วนของประวัติการรักษาที่ผ่านมา \n(กรณีผู้ป่วยนอกโรคเรื้อรังที่เคยรักษาที่อื่นมาก่อน) \n-   กรณีไม่ได้รักษาที่ใดมาก่อนมีระบุว่า “ไม่ได้รักษาจากที่ใด” \n-   กรณีซักประวัติไม่ได้มีระบุว่า “ซักประวัติไม่ได้”",
        "3. มีบันทึก underlying disease และการรักษาที่ได้รับอยู่ในปัจจุบัน \n-   กรณีที่ไม่มี underlying disease หรือไม่มีการรักษาต้องระบุ “ไม่มี...” หรือข้อความอื่นที่แสดงถึงมีการซักประวัติและไม่พบ underlying disease\n    หรือไม่มีการรักษา \n-   กรณีผู้ป่วย “ไม่รู้สึกตัว” หรือ “ไม่สามารถซักประวัติได้” มีบันทึกว่า “ไม่รู้สึกตัว” หรือ “ซักประวัติไม่ได้” ให้ผู้ตรวจประเมินระบุ NA",
        "4. มีบันทึกประวัติการเจ็บป่วยในอดีตที่สำคัญ (past illness) และหรือ ประวัติความเจ็บป่วยในครอบครัว ที่เกี่ยวข้องกับปัญหาที่มา หรือสอดคล้อง\n    กับปัญหาที่สงสัย\n-   กรณีผู้ป่วย “ไม่รู้สึกตัว” หรือ “ไม่สามารถซักประวัติได้” มีบันทึกว่า “ไม่รู้สึกตัว” หรือ\n   “ซักประวัติไม่ได้” ให้ผู้ตรวจประเมินระบุ NA",
        "5. มีบันทึกประวัติการแพ้ยาและประวัติการแพ้อื่น ๆ พร้อมระบุชื่อยาหรือสิ่งที่แพ้\n-   กรณีผู้ป่วย “ไม่รู้สึกตัว” หรือ “ไม่สามารถซักประวัติได้” มีบันทึกว่า “ไม่รู้สึกตัว” หรือ “ซักประวัติไม่ได้” ให้ผู้ตรวจประเมินระบุ NA",
        "6. มีบันทึกประวัติอื่น ๆ ในส่วนของ \n 1) Family history หรือ Personal history หรือ Social history หรือ ประวัติการทำงานที่เกี่ยวข้อง หรือสอดคล้องกับปัญหาที่มาในครั้งนี้ \n 2) กรณีเป็นผู้หญิงอายุ 11 - 60 ปี มีบันทึกประวัติประจำเดือน \n 3) กรณีเป็นเด็ก 0 - 14 ปี มีบันทึกประวัติ vaccination และ growth development \n 4) กรณีผู้ป่วย “ไม่รู้สึกตัว” หรือ “ไม่สามารถซักประวัติได้” มีบันทึกว่า “ไม่รู้สึกตัว” หรือ “ซักประวัติไม่ได้” ให้ผู้ตรวจประเมินระบุ NA",
        "7. มีบันทึกประวัติการใช้สารเสพติดหรือการสูบบุหรี่ หรือการดื่มสุรา โดยระบุจำนวน ความถี่และระยะเวลาที่ใช้\n-   กรณีผู้ป่วยเด็ก (0-14 ปี) มีซักประวัติการใช้สารเสพติด การสูบบุหรี่ และการดื่มสุราของบุคคลในครอบครัว\n-   กรณีผู้ป่วย “ไม่รู้สึกตัว” หรือ “ไม่สามารถซักประวัติได้” มีบันทึกว่า “ไม่รู้สึกตัว” หรือ “ซักประวัติไม่ได้” ให้ผู้ตรวจประเมินระบุ NA",
        
    ],
    3: [
        "1. มีบันทึกวันเดือนปี และ เวลาที่ผู้ป่วยได้รับการประเมินครั้งแรก",
        "2. มีบันทึกการตรวจร่างกายโดยการ ดู หรือ เคาะ ที่นำไปสู่การวินิจฉัยที่สอดคล้องกับ chief complaint มีบันทึกรายงานผลสิ่งที่ตรวจพบปกติ\n    หรือสิ่งที่ผิดปกติ\n-   กรณีไม่มีความจำเป็นต้องตรวจ ให้ผู้ตรวจประเมินระบุ NA\n-   กรณีญาติรับยาแทน ให้ผู้ตรวจประเมินระบุ NA",
        "3. มีบันทึกการตรวจร่างกายโดยการ คลำ หรือ ฟัง ที่นำไปสู่การวินิจฉัยที่สอดคล้องกับ chief complaint มีบันทึกรายงานผลสิ่งที่ตรวจพบปกติ\n    หรือสิ่งที่ผิดปกติ\n-   กรณีไม่มีความจำเป็นต้องตรวจ ให้ผู้ตรวจประเมินระบุ NA \n-   กรณีญาติรับยาแทน ให้ผู้ตรวจประเมินระบุ NA",
        "4. มีบันทึก pulse rate, respiration rate และ temperature ทุกราย\n-   กรณีญาติรับยาแทน ให้ผู้ตรวจประเมินระบุ NA",
        "5. มีบันทึก Blood Pressure ทุกราย ยกเว้นในเด็กเล็กอายุน้อยกว่า 5 ปีให้พิจารณาตามสภาพปัญหาของผู้ป่วย กรณีไม่จำเป็นต้องบันทึก \n    ให้ผู้ตรวจประเมินระบุ NA\n-   กรณีญาติรับยาแทน ให้ผู้ตรวจประเมินระบุ NA",
        "6. มีบันทึกน้ำหนัก ทุกราย กรณีที่ชั่งน้ำหนักไม่ได้ต้องระบุเหตุผล และมีการบันทึกส่วนสูงในกรณีดังต่อไปนี้ \n1) กรณีเด็ก บันทึกส่วนสูงทุกราย \n2) กรณีผู้ใหญ่ บันทึกส่วนสูงในกรณีที่มีความจำเป็นต้องใช้ในการวางแผนการรักษา เช่น ค่า BMI (Body Mass Index) หรือค่า BSA (Body Surface Area) \n    ในรายที่ต้องให้ ยาเคมีบำบัด เป็นต้น \n-   กรณีญาติรับยาแทน ให้ผู้ตรวจประเมินระบุ NA",
        "7. มีการสรุปการวินิจฉัยโรคที่ครอบคลุมตามเกณฑ์ดังนี้ \n 1) บันทึกการวินิจฉัยเป็นคำวินิจฉัยโรค (clinical term) ไม่บันทึกคำวินิจฉัยเป็นรหัส ICD-10 และไม่บันทึกเป็นคำวินิจฉัยตามการให้รหัส ICD-10 \n    (ตัวอย่างคำวินิจฉัยตามการให้รหัส ICD-10 : “D64.8 Other specified anaemias” “J20.9 Acute bronchitis, unspecified” เป็นต้น และ \n 2) ในผู้ป่วยนอกทั่วไป/ฉุกเฉิน มีการวินิจฉัยโรคหรือการสรุปการวินิจฉัยโรคขั้นต้น (provisional diagnosis) ที่สอดคล้องกับผลการซักประวัติ\n    หรือผลการตรวจร่างกาย \n 3) ในผู้ป่วยโรคเรื้อรัง มีการวินิจฉัยโรคที่เฉพาะเจาะจง และสอดคล้องกับผลการซักประวัติ หรือผลการตรวจร่างกาย หรือประวัติการรักษาในครั้งก่อน \n    เช่น diabetes mellitus type 2, chronic kidney disease stage 4 เป็นต้น",
    ],
    4: [
        "1. มีบันทึกการสั่ง และมีผลการตรวจทางห้องปฏิบัติการ หรือรังสี หรือการตรวจอื่นๆ การสั่งตรวจอาจจะอยู่ครั้งก่อนหน้าได้\n-   กรณีที่เป็น standing order หน่วยบริการต้องแสดงหลักฐาน standing order นั้น\n-   กรณีที่ไม่จำเป็นต้องส่งตรวจวินิจฉัยและไม่มีผลการตรวจ ให้ผู้ตรวจประเมินระบุ NA\n-   กรณีที่ไม่มีบันทึกการสั่งตรวจวินิจฉัยแต่มีผลการตรวจ หรือมีบันทึกการสั่งตรวจวินิจฉัยแต่ไม่มีผลการตรวจ ถือว่าไม่ผ่านเกณฑ์\n    การตรวจประเมินในข้อนี้\n-   กรณีที่ผลการตรวจนั้นได้ข้อมูลจากใบส่งต่อ (ใบ refer) ต้องมีระบุ",
        "2. มีบันทึกการให้การรักษา การสั่งยา การทำหัตถการ (ถ้ามี) ที่สอดคล้องกับการวินิจฉัย ยกเว้น กรณีที่แพทย์รับผู้ป่วยเข้าพักรักษาอยู่ในโรงพยาบาล\n    ต้องมีบันทึกว่า “admit..”",
        "3. มีบันทึกการสั่งยาที่ระบุรายละเอียด ชื่อยา ความแรง ขนาดที่ใช้ และจำนวนยาที่สั่งจ่าย หรือ จำนวนวันที่สั่งจ่าย\n-   กรณีไม่มีการสั่งยา ให้ผู้ตรวจประเมินระบุ NA",
        "4. มีบันทึกการให้คำแนะนำเกี่ยวกับโรค หรือภาวะการเจ็บป่วย หรือการปฏิบัติตัว หรือ การสังเกตอาการที่ผิดปกติ หรือข้อควรระวัง\n    เกี่ยวกับการรับประทานยา ยกเว้นกรณีที่แพทย์ รับผู้ป่วยเข้าพักรักษาอยู่ในโรงพยาบาลต้องระบุเหตุผล หรือแผนการรักษา",
        "5. กรณีมีการปรึกษาระหว่างแผนก ต้องมีการบันทึกผลการตรวจวินิจฉัย หรือการรักษาที่ผ่านมา\n-   กรณีที่ไม่มีการส่งพบแพทย์ต่างแผนก ให้ผู้ตรวจประเมินระบุ NA",
        "6. มีบันทึกแผนการดูแลรักษาต่อเนื่อง หรือการนัดมาติดตามการรักษา\n-   กรณีที่แพทย์รับผู้ป่วยเข้าพักรักษาอยู่ในโรงพยาบาล ให้ผู้ตรวจประเมินระบุ NA",
        "7. มีการบันทึกด้วยลายมือที่อ่านออกได้ และลงลายมือชื่อแพทย์หรือผู้ที่รับผิดชอบ ในการตรวจรักษาโดยสามารถระบุได้ว่าเป็นผู้ใด\n-   กรณีที่มีการบันทึกผ่านระบบคอมพิวเตอร์ ต้องสามารถตรวจสอบได้ว่าเป็นการบันทึกข้อมูลของแพทย์หรือผู้สั่งการรักษาท่านใด \n    และการสั่งการรักษานั้นต้องมีระบบที่ไม่สามารถทำย้อนหลังหรือแก้ไขโดยผู้อื่นได้\n-   กรณี รคส.แพทย์ ต้องพบการรับรองลงนามลายมือชื่อแพทย์ หรือบันทึกผ่านระบบคอมพิวเตอร์ ต้องสามารถตรวจสอบได้ว่าเป็นการบันทึกข้อมูล\n    ของแพทย์หรือผู้สั่งการรักษาท่านใด",
        
    ],
    5: [
        "1. มีการบันทึกประวัติ หรือเหตุผลในการมา follow up",
        "2. มีการบันทึกการวินิจฉัยโรค ที่สอดคล้องกับการรักษาที่ให้",
        "3. มีบันทึก vital signs ในส่วนที่เกี่ยวข้อง และหรือการตรวจร่างกายที่จำเป็น (ดู คลำ เคาะ ฟัง)\n-   กรณีญาติรับยาแทนให้ผู้ตรวจประเมินระบุ NA",
        "4. มีบันทึกการประเมินผลการรักษาในครั้งที่ผ่านมา (evaluation) หรือ สรุปปัญหาที่เกิดขึ้นและมีบันทึกการรักษาที่ให้ในครั้งนี้ (treatment)\n-   กรณีที่แพทย์รับผู้ป่วยเข้าพักรักษาอยู่ในโรงพยาบาลต้องระบุเหตุผล หรือแผนการรักษา",
        "5. มีบันทึกการสั่ง และมีผลการตรวจทางห้องปฏิบัติการ หรือการตรวจทางรังสี หรือการตรวจอื่น ๆ การสั่งตรวจอาจจะอยู่ใน visit ครั้งก่อนหน้าได้\n-   กรณีที่เป็น standing order หน่วยบริการต้องแสดงหลักฐาน standing order นั้น\n-   กรณีที่ไม่จำเป็นต้องส่งตรวจวินิจฉัย และไม่มีผลการตรวจให้ผู้ตรวจประเมินระบุ NA\n-   กรณีที่ไม่มีการบันทึกการสั่งการตรวจวินิจฉัย แต่มีผลการตรวจ หรือกรณีมีบันทึกการสั่งตรวจวินิจฉัย แต่ไม่มีผลการตรวจ ถือว่าไม่ผ่านเกณฑ์\n    การตรวจประเมินในข้อนี้\n-   กรณีที่ผลการตรวจนั้นได้ข้อมูลจากใบส่งต่อ (ใบ refer) ต้องระบุ",
        "6. มีบันทึกการให้คำแนะนำเกี่ยวกับการปฏิบัติตัว หรือการสังเกตอาการที่ผิดปกติ หรือข้อควรระวังเกี่ยวกับการรับประทานยา\n    แผนการดูแลรักษาต่อเนื่อง หรือการนัดมาติดตามการรักษาครั้งต่อไป\n-   กรณีที่แพทย์รับผู้ป่วยเข้าพักรักษาอยู่ในโรงพยาบาล ให้ผู้ตรวจประเมินระบุ NA",
        "7. มีการบันทึกด้วยลายมือที่อ่านออกได้ และลงลายมือชื่อแพทย์หรือผู้ที่รับผิดชอบในการตรวจรักษา โดยสามารถระบุได้ว่าเป็นผู้ใด\n-   กรณีที่มีการบันทึกผ่านระบบคอมพิวเตอร์ ต้องสามารถตรวจสอบได้ว่าเป็นการบันทึกข้อมูลของแพทย์หรือผู้สั่งการรักษาท่านใด \n    และการสั่งการรักษานั้นต้องมีระบบที่ไม่สามารถทำย้อนหลังหรือแก้ไขโดยผู้อื่นได้\n-   กรณี รคส.แพทย์ ต้องพบการรับรองลงนามลายมือชื่อแพทย์ หรือบันทึกผ่านระบบคอมพิวเตอร์ ต้องสามารถตรวจสอบได้ว่าเป็นการบันทึกข้อมูล\n    ของแพทย์หรือผู้สั่งการรักษาท่านใด",
        
    ],
    6: [
        "1. มีการบันทึกชื่อ และนามสกุล ผู้ป่วยชัดเจน",
        "2. มีบันทึกสิ่งที่ตรวจพบจากการผ่าตัดหรือหัตถการ (operative findings)",
        "3. มีบันทึกวิธีการทำผ่าตัด หรือหัตถการ (operative procedures)",
        "4. มีบันทึกวิธีการให้ยาชา หรือยาระงับความรู้สึก",
        "5. มีบันทึกผลการทำผ่าตัดหรือหัตถการ หรือการวินิจฉัยโรคหลังทำผ่าตัดหรือหัตถการ (post-operative diagnosis)\n    รวมถึงภาวะแทรกซ้อนที่เกิดขึ้น กรณีที่มีการตัดชิ้นเนื้อเพื่อส่งตรวจต้องมีการติดตามผล pathology หรือระบุในใบบันทึกว่า\n    “รอผล pathology” หรือ “รอผลชิ้นเนื้อ”",
        "6. บันทึกวันเดือนปี และเวลา ที่เริ่มต้นและสิ้นสุดการทำผ่าตัดหรือหัตถการ",
        "7. มีการบันทึกด้วยลายมือที่อ่านออกได้ และลงลายมือชื่อแพทย์หรือผู้ที่รับผิดชอบในการผ่าตัด โดยสามารถระบุได้ว่าเป็นผู้ใด จากชื่อ นามสกุล\n    และเลขที่ใบอนุญาตประกอบวิชาชีพเวชกรรม\n1) กรณีผู้บันทึกการผ่าตัด หรือหัตถการนั้นเป็นผู้ที่ไม่มีใบอนุญาตประกอบวิชาชีพเวชกรรม (ใบประกอบโรคศิลปะของแพทย์) ต้องมีการลงนามกำกับ\n    โดยแพทย์ทุกครั้ง\n2) กรณีเป็น operative note แบบอิเล็กทรอนิกส์ต้องสามารถสืบค้นในระบบ log in ได้ว่าแพทย์ผู้ใดเป็นผู้บันทึก แพทย์ผู้ที่ทำหัตถการ \n    รวมทั้งระบุเลขที่ใบอนุญาตประกอบวิชาชีพเวชกรรม",
    ],
    7: [
        "1. มีการบันทึกชื่อ และนามสกุล ผู้ป่วยถูกต้องชัดเจน",
        "2. มีลายมือชื่อ หรือลายพิมพ์นิ้วมือ (โดยต้องระบุว่าเป็นของใครและใช้นิ้วใด) ชื่อ และนามสกุลของผู้รับทราบข้อมูลและยินยอมให้ทำการรักษา\n    หรือหัตถการ กรณีที่อายุน้อยกว่า 18 ปี (ยกเว้นสมรสตามกฎหมาย) หรือผู้ป่วยอยู่ในสภาพที่สติสัมปชัญญะไม่สมบูรณ์ ให้มีผู้ลงนามยินยอม\n    โดยต้องระบุชื่อ นามสกุล และความสัมพันธ์กับผู้ป่วยให้ชัดเจน ยกเว้นกรณีดังนี้\n1) กรณีมารับการรักษาที่มีภาวะฉุกเฉิน หรือสติสัมปชัญญะไม่สมบูรณ์ ให้ถือเป็นกรณีมีความจำเป็นอาจเป็นอันตรายต่อชีวิต \n    ผู้ให้บริการต้องช่วยเหลือให้การรักษาทันทีไม่จำเป็นต้องได้รับความยินยอมจากผู้ป่วยหรือผู้ปกครอง\n2) กรณีผู้ป่วยอายุน้อยกว่า 18 ปี ถ้ามาคนเดียว และมารับการรักษาด้วยภาวะฉุกเฉินสามารถให้ความยินยอมด้วยตนเองได้ \n    โดยต้องระบุว่าผู้ป่วยมาคนเดียว ซึ่งควรให้ผู้ปกครองที่ชอบด้วยกฎหมายเซ็นรับทราบภายหลัง พร้อมระบุ วัน เดือน ปี และเวลาที่รับทราบการรักษานั้น",
        "3. มีลายมือชื่อพยานครบถ้วน โดยระบุชื่อ นามสกุล และความสัมพันธ์กับผู้ป่วยอย่างชัดเจน (กรณีที่ผู้ป่วยมาคนเดียว ให้ระบุว่า “ผู้ป่วยมาคนเดียว”) \n    ยกเว้นกรณีที่เป็นการเจาะเลือด ส่งตรวจที่เป็นความลับของผู้ป่วย เช่น การเจาะ HIV ซึ่งมีการบันทึกในขั้นตอนของการให้ คำปรึกษา (counseling)",
        "4. มีการบันทึกเหตุผล ความจำเป็นที่ต้องทำการผ่าตัด หรือหัตถการ",
        "5. มีการบันทึกการให้ข้อมูลเกี่ยวกับภาวะแทรกซ้อนที่อาจเกิดขึ้นโดยสังเขป",
        "6. มีการระบุลายมือชื่อผู้ให้ข้อมูล หรือรายละเอียดของการทำผ่าตัด หรือหัตถการ",
        "7. มีการบันทึกระบุ วัน เดือน ปีและเวลา ที่รับทราบและยินยอมให้ทำการรักษา",
    ],
    
}



def _blank_sections():
    sections = []
    for i, title in enumerate(OPD_SECTION_TITLES, start=1):
        
        custom_texts = OPD_CRITERIA_NAMES.get(i, [])
        if custom_texts:
            n_current = len(custom_texts)
        else:
            n_current = OPD_N_ITEMS

        def get_text(idx):
            if custom_texts and (idx - 1) < len(custom_texts):
                return custom_texts[idx - 1]
            return f"เกณฑ์ {idx}"

        remark_text = OPD_SECTION_REMARKS.get(i, "")

        if i == 5:
            items_by_visit = {}
            visit_groups = [] 
            
            for v in range(1, N_VISITS_SECTION5 + 1):
                items = [
                    {"index": j, "text": get_text(j), "value": "", "weight": 1}
                    for j in range(1, n_current + 1)
                ]
                items_by_visit[v] = items

                visit_groups.append({
                    "v": v,
                    "items": items,
                    "add": 0,
                    "deduct": 0
                })

            sections.append({
                "index": i, "title": title, "add": 0, "deduct": 0, "locked": False,
                "active_visit": 1, 
                "items_by_visit": items_by_visit,
                "visit_groups": visit_groups,
                "score": 0, "possible": 0,
                "suggestion": "",
                "remark": remark_text,
            })
        else:
            items = [
                {"index": j, "text": get_text(j), "value": "", "weight": 1}
                for j in range(1, n_current + 1)
            ]
            sections.append({
                "index": i, "title": title, "add": 0, "deduct": 0, "locked": False,
                "items": items, "score": 0, "possible": 0,
                "suggestion": "",
                "remark": remark_text,
            })
    return sections

def _sum_possible(items):
    return sum(int(it.get("weight", 1)) for it in items)

def _calc_totals(sections):
    total_score = 0
    total_possible = 0
    for sec in sections:
        locked = bool(sec.get("locked"))
        add = int(sec.get("add", 0) or 0)
        deduct = int(sec.get("deduct", 0) or 0)

        if "items_by_visit" in sec:
            active = int(sec.get("active_visit", 1))
            items = sec["items_by_visit"][active]
        else:
            items = sec["items"]

        if locked:
            sec_score = 0
            sec_possible = 0
        else:
            sec_score = 0
            sec_possible = 0
            for it in items:
                v = it.get("value", "na")
                w = int(it.get("weight", 1))
                if v == "1":
                    sec_score += w; sec_possible += w
                elif v == "0":
                    sec_possible += w
            sec_score = sec_score + add - deduct

        sec["score"] = sec_score
        sec["possible"] = sec_possible
        total_score += sec_score
        total_possible += sec_possible

    percent = round((total_score / total_possible) * 100, 2) if total_possible else 0
    return total_score, total_possible, percent


@login_required
def opd_score_create(request):
    if request.method == "POST":
        form = OPDScoreForm(request.POST)
        
        # 1. ย้ายการดึงข้อมูลคะแนนจาก POST มาไว้ตรงนี้ (ดึงเสมอไม่ว่าฟอร์มจะผ่านหรือไม่)
        sections = _blank_sections()
        for i in range(1, len(sections) + 1):
            sec = sections[i-1] 
            locked = request.POST.get(f"s{i}_lock") == "on"
            sec["locked"] = locked

            if i == 5: # จัดการหัวข้อ 5 (Follow Up)
                active_visit = int(request.POST.get("s5_visit", "1") or 1)
                sec["active_visit"] = active_visit
                visit_groups = []
                sum_add = sum_ded = 0

                for v in range(1, N_VISITS_SECTION5 + 1):
                    items = sec["items_by_visit"][v]
                    if locked:
                        v_add = v_ded = 0
                        for it in items: it["value"] = "na"
                    else:
                        v_add = int(request.POST.get(f"s5_v{v}_add", "0") or 0)
                        v_ded = int(request.POST.get(f"s5_v{v}_ded", "0") or 0)
                        for j in range(1, OPD_N_ITEMS + 1):
                            val = request.POST.get(f"s5_v{v}_i{j}", "na")
                            if (j-1) < len(items):
                                items[j-1]["value"] = val

                    sum_add += v_add
                    sum_ded += v_ded
                    visit_groups.append({"v": v, "items": items, "add": v_add, "deduct": v_ded})

                sec["add"] = sum_add
                sec["deduct"] = sum_ded
                sec["visit_groups"] = visit_groups
            else: # หัวข้ออื่นๆ
                if locked:
                    sec["add"] = sec["deduct"] = 0
                else:
                    sec["add"] = int(request.POST.get(f"s{i}_add", "0") or 0)
                    sec["deduct"] = int(request.POST.get(f"s{i}_ded", "0") or 0)
                    current_items = sec["items"]
                    for j in range(1, len(current_items) + 1):
                        val = request.POST.get(f"s{i}_i{j}", "na")
                        current_items[j-1]["value"] = val

            sec["suggestion"] = request.POST.get(f"s{i}_suggestion", "").strip()

        # 2. เช็คความถูกต้อง ถ้าผ่านให้ Save, ถ้าไม่ผ่าน sections จะถูกนำกลับไปโชว์ให้แก้
        if form.is_valid():
            total_score, total_possible, percent = _calc_totals(sections)

            obj = form.save(commit=False)
            obj.data = {
                "sections": sections,
                "overall": {"score": total_score, "possible": total_possible, "percent": float(percent)}
            }
            obj.total_score = total_score
            obj.total_possible = total_possible
            obj.percent = percent
            obj.created_by = request.user
            obj.save()

            messages.success(request, "บันทึกคะแนน OPD สำเร็จ")
            return redirect(reverse("MRA:opd_score_detail", args=[obj.id]))
        else:
            messages.error(request, "กรุณาตรวจสอบข้อมูลให้ครบถ้วน")
            # ถ้ามาตรงนี้ ตัวแปร sections ด้านบน จะถูกส่งไปใน context ทันที ค่าจึงไม่หาย
    else:
        form = OPDScoreForm()
        sections = _blank_sections()

    context = {
        "form": form,
        "sections": sections,
        "n_items": OPD_N_ITEMS,
        "visit_labels": VISIT_LABELS,
    }
    return render(request, "scores/opd_score_form.html", context)


@login_required
def opd_score_detail(request, pk):
    obj = get_object_or_404(OPDScore, pk=pk)
    data = obj.data or {}
    sections = data.get("sections", [])

    overall_display_score = 0
    overall_display_possible = 0

    for s in sections:
        # --- หัวข้อ 5:  ---
        if "items_by_visit" in s:
            fixed = {}
            for k, items in s["items_by_visit"].items():
                fixed[str(k)] = items
            s["items_by_visit"] = fixed

            per_visit_list = []
            for v in ("1", "2", "3"):
                items = s["items_by_visit"].get(v, []) or []
                sc = poss = 0
                for it in items:
                    val = str(it.get("value", "na")).lower()
                    w = int(it.get("weight", 1) or 1)
                    if val == "1":
                        sc += w; poss += w
                    elif val == "0":
                        poss += w
                per_visit_list.append({
                    "visit": int(v),
                    "score": sc,
                    "possible": poss,
                    "percent": round(sc * 100.0 / poss, 2) if poss else 0.0
                })
            s["per_visit_list"] = per_visit_list

            locked = bool(s.get("locked"))
            add = int(s.get("add", 0) or 0)
            deduct = int(s.get("deduct", 0) or 0)

            if locked:
                disp_score = 0
                disp_possible = 0
            else:
                disp_score = sum(p["score"] for p in per_visit_list) + add - deduct
                disp_possible = sum(p["possible"] for p in per_visit_list)

            s["display_score"] = disp_score
            s["display_possible"] = disp_possible
            s["display_percent"] = round((disp_score / disp_possible) * 100, 2) if disp_possible else 0.0

            try:
                s["active_visit"] = int(s.get("active_visit") or 1)
            except Exception:
                s["active_visit"] = 1

        else:
            if bool(s.get("locked")):
                s["display_score"] = 0
                s["display_possible"] = 0
            else:
                s["display_score"] = int(s.get("score") or 0)
                s["display_possible"] = int(s.get("possible") or 0)
            s["display_percent"] = (
                round((s["display_score"] / s["display_possible"]) * 100, 2)
                if s["display_possible"] else 0.0
            )


        overall_display_score += s["display_score"]
        overall_display_possible += s["display_possible"]

    overall_display_percent = (
        round((overall_display_score / overall_display_possible) * 100, 2)
        if overall_display_possible else 0.0
    )

    return render(request, "scores/opd_score_detail.html", {
        "obj": obj,
        "sections": sections,
        "overall_display": {
            "score": overall_display_score,
            "possible": overall_display_possible,
            "percent": overall_display_percent,
        }
    })

    # ********************************************************** OPD EDIT *******************************************************
@login_required
def opd_score_edit(request, pk):
    obj = get_object_or_404(OPDScore, pk=pk)
    
    is_owner = (obj.created_by == request.user)
    is_admin = request.user.is_superuser or request.user.is_staff

    if not (is_owner or is_admin):
        messages.error(request, "คุณไม่มีสิทธิ์แก้ไขรายการที่ผู้อื่นสร้าง")
        return redirect('MRA:opd_score_detail', pk=pk)

    if request.method == "POST":
        form = OPDScoreForm(request.POST, instance=obj)
        if form.is_valid():
            sections = _blank_sections()
            for i in range(1, len(sections) + 1):
                sec = sections[i-1]
                locked = request.POST.get(f"s{i}_lock") == "on"
                sec["locked"] = locked

                if i == 5:
                    active_visit = int(request.POST.get("s5_visit", "1") or 1)
                    sec["active_visit"] = active_visit
                    visit_groups = []
                    sum_add = sum_ded = 0
                    for v in range(1, N_VISITS_SECTION5 + 1):
                        items = sec["items_by_visit"][v]
                        if locked:
                            v_add = v_ded = 0
                            for it in items: it["value"] = "na"
                        else:
                            v_add = int(request.POST.get(f"s5_v{v}_add", "0") or 0)
                            v_ded = int(request.POST.get(f"s5_v{v}_ded", "0") or 0)
                            for j in range(1, OPD_N_ITEMS + 1):
                                key = f"s5_v{v}_i{j}"
                                val = request.POST.get(key, "na")
                                if (j-1) < len(items): items[j-1]["value"] = val
                        sum_add += v_add
                        sum_ded += v_ded
                        visit_groups.append({"v": v, "items": items, "add": v_add, "deduct": v_ded})
                    sec["add"], sec["deduct"], sec["visit_groups"] = sum_add, sum_ded, visit_groups
                else:
                    if locked:
                        sec["add"] = sec["deduct"] = 0
                    else:
                        sec["add"] = int(request.POST.get(f"s{i}_add", "0") or 0)
                        sec["deduct"] = int(request.POST.get(f"s{i}_ded", "0") or 0)
                        current_items = sec["items"]
                        for j in range(1, len(current_items) + 1):
                            val = request.POST.get(f"s{i}_i{j}", "na")
                            current_items[j-1]["value"] = val

                sec["suggestion"] = request.POST.get(f"s{i}_suggestion", "").strip()

            total_score, total_possible, percent = _calc_totals(sections)
            
            # บันทึกข้อมูล
            updated_obj = form.save(commit=False)
            updated_obj.data = {
                "sections": sections,
                "overall": {"score": total_score, "possible": total_possible, "percent": float(percent)}
            }
            updated_obj.total_score = total_score
            updated_obj.total_possible = total_possible
            updated_obj.percent = percent
            updated_obj.save()

            messages.success(request, "แก้ไขคะแนน OPD สำเร็จ")
            return redirect(reverse("MRA:opd_score_detail", args=[updated_obj.id]))
    else:
        form = OPDScoreForm(instance=obj)
        saved_sections = (obj.data or {}).get("sections")
        if not saved_sections:
            saved_sections = _blank_sections()


    ctx = {
        "form": form,
        "sections": saved_sections,
        "n_items": OPD_N_ITEMS,
        "visit_labels": VISIT_LABELS,
        "editing": True,
        "obj": obj,
    }
    return render(request, "scores/opd_score_form.html", ctx)

    # ********************************************************** ********* *******************************************************


def _count_items(items):
    score = possible = 0
    for it in (items or []):
        val = str(it.get("value", "na")).lower()
        w = int(it.get("weight", 1) or 1)
        if val == "1":
            score += w; possible += w
        elif val == "0":
            possible += w
    return score, possible

def _compute_display_totals(sections):
    """รวมคะแนนทุกหัวข้อ โดยหัวข้อ 5 รวมทุกครั้ง (1..3) และถ้าล็อค = ไม่นับ (0/0)"""
    total_score = total_possible = 0
    for s in (sections or []):
        locked = bool(s.get("locked"))
        add = int(s.get("add", 0) or 0)
        deduct = int(s.get("deduct", 0) or 0)

        if locked:
            sc = 0; ps = 0
        else:
            if "items_by_visit" in s:
                sc = ps = 0
                for _, lst in (s.get("items_by_visit") or {}).items():
                    ss, pp = _count_items(lst)
                    sc += ss; ps += pp
                sc = sc + add - deduct
            else:
                ss, pp = _count_items(s.get("items"))
                sc = ss + add - deduct
                ps = pp

        total_score += sc
        total_possible += ps

    pct = round((total_score / total_possible) * 100, 2) if total_possible else 0.0
    return total_score, total_possible, pct



@login_required
def opd_score_list(request):
    # 1. Query เริ่มต้น
    qs = OPDScore.objects.all().order_by("-created_at")

    # 2. ส่วนค้นหา (Search Logic) - ทำก่อน Pagination
    search_query = request.GET.get('search', '').strip()
    if search_query:
        qs = qs.filter(
            Q(hn__icontains=search_query) |
            Q(hcode__icontains=search_query) |
            Q(hname__icontains=search_query) |
            Q(pid__icontains=search_query)  # เพิ่มค้นหาด้วย PID
        )

    # 3. จัดการ Pagination
    try:
        per_page = int(request.GET.get("per_page", 10))
    except (TypeError, ValueError):
        per_page = 10
    if per_page <= 0:
        per_page = 10

    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # 4. คำนวณคะแนน (Enrichment) - ทำเฉพาะหน้าปัจจุบันเพื่อ Performance
    enriched = []
    for o in page_obj.object_list:
        data = o.data or {}
        sections = data.get("sections", [])
        
        # แปลง key dictionary ให้เป็น string (เผื่อมีปัญหา JSON keys เป็น int)
        for s in sections:
            if "items_by_visit" in s and isinstance(s["items_by_visit"], dict):
                s["items_by_visit"] = {str(k): v for k, v in s["items_by_visit"].items()}
        
        # ฟังก์ชันคำนวณคะแนนของคุณ (สมมติว่า import มาแล้ว)
        sc, ps, pc = _compute_display_totals(sections)
        
        o.display_score = sc
        o.display_possible = ps
        o.display_percent = pc
        enriched.append(o)

    # update object_list ใน page_obj ให้เป็นตัวที่คำนวณแล้ว
    page_obj.object_list = enriched

    return render(request, "scores/opd_score_list.html", {
        "page_obj": page_obj,
        "per_page": per_page,
        "search": search_query, # ส่งค่า search กลับไปที่ template เพื่อแสดงในช่อง input
    })




def _norm(v):
    if v is None:
        return ""
    return str(v).strip().upper()

def _count_01(value):
    """รับค่าเป็น '1'|'0'|'NA'|'', คืน (yes, counted)"""
    s = _norm(value)
    if s == "1":
        return (1, 1)
    if s == "0":
        return (0, 1)
    return (0, 0)


    

@login_required
def opd_score_averages(request):
    # 1. รับค่าจากช่องค้นหา (q) ช่องเดียว
    q = (request.GET.get("q") or "").strip()

    qs = OPDScore.objects.all().order_by("-created_at")

    # 2. ตรวจสอบว่าสิ่งที่พิมพ์มาเป็นรูปแบบวันที่หรือไม่
    start_d, end_d = _parse_date_or_day_range(q)
    
    if start_d and end_d:
        start_dt, end_dt_excl = _aware_range_from_dates(start_d, end_d)
        qs = qs.filter(created_at__gte=start_dt, created_at__lt=end_dt_excl)
    elif q:
        from django.db.models import Q
        qs = qs.filter(Q(hn__icontains=q) | Q(pid__icontains=q) | Q(hcode__icontains=q) | Q(hname__icontains=q))

    rows = []
    for i, title in enumerate(OPD_SECTION_TITLES, start=1):
        cols = [{"yes": 0, "counted": 0, "is_empty": True} for _ in range(OPD_N_ITEMS)]
        rows.append({"index": i, "title": title, "cols": cols, "avg": 0.0, "records_count": 0})

    total_cols = [{"yes": 0, "counted": 0, "is_empty": True} for _ in range(OPD_N_ITEMS)]

    for o in qs:
        data = o.data or {}
        sections = data.get("sections", []) or []
        sec_by_idx = {int(s.get("index", idx+1)): s for idx, s in enumerate(sections)}

        for i in range(1, len(OPD_SECTION_TITLES) + 1):
            s = sec_by_idx.get(i)
            if not s:  continue
            if bool(s.get("locked")):
                continue
            
            # --- สร้างตัวแปรไว้เช็คว่ามีการกรอกคะแนน (0 หรือ 1) หรือไม่ ---
            section_has_data = False 

            if "items_by_visit" in s and i == 5:
                ibv = {str(k): v for k, v in (s.get("items_by_visit") or {}).items()}
                for vkey in ("1", "2", "3"):
                    items = ibv.get(vkey) or []
                    for j in range(min(OPD_N_ITEMS, len(items))):
                        val = str(items[j].get("value")).strip().upper()
                        yes = 1 if val == "1" else 0
                        cnt = 1 if val in ("0","1") else 0
                        
                        # ถ้ามีคะแนนถูกนับ (cnt > 0) แปลว่าหัวข้อนี้ไม่ได้ว่างเปล่า
                        if cnt > 0:
                            section_has_data = True
                            rows[i-1]["cols"][j]["is_empty"] = False
                            total_cols[j]["is_empty"] = False
                            
                        rows[i-1]["cols"][j]["yes"]     += yes
                        rows[i-1]["cols"][j]["counted"] += cnt
                        total_cols[j]["yes"]            += yes
                        total_cols[j]["counted"]        += cnt
            else:
                items = s.get("items") or []
                for j in range(min(OPD_N_ITEMS, len(items))):
                    val = str(items[j].get("value")).strip().upper()
                    yes = 1 if val == "1" else 0
                    cnt = 1 if val in ("0","1") else 0
                    
                    # ถ้ามีคะแนนถูกนับ (cnt > 0) แปลว่าหัวข้อนี้ไม่ได้ว่างเปล่า
                    if cnt > 0:
                        section_has_data = True
                        rows[i-1]["cols"][j]["is_empty"] = False
                        total_cols[j]["is_empty"] = False
                        
                    rows[i-1]["cols"][j]["yes"]     += yes
                    rows[i-1]["cols"][j]["counted"] += cnt
                    total_cols[j]["yes"]            += yes
                    total_cols[j]["counted"]        += cnt
                    
            # --- ถ้ายืนยันว่าหัวข้อนี้มีการตรวจให้คะแนนจริงๆ ค่อยนับ +1 ---
            if section_has_data:
                rows[i-1]["records_count"] += 1

    # ประมวลผลคำนวณ % ขั้นสุดท้ายของแต่ละแถว
    for r in rows:
        valid_pcts = []
        for c in r["cols"]:
            if c["counted"] > 0:
                pct = (c["yes"] / c["counted"] * 100.0)
                c["percent"] = pct
                valid_pcts.append(pct)
            else:
                c["percent"] = 0.0
        
        r["avg"] = sum(valid_pcts) / len(valid_pcts) if valid_pcts else 0.0
        r["is_empty_avg"] = len(valid_pcts) == 0

    # ประมวลผลแถว Total
    valid_total_pcts = []
    for tc in total_cols:
        if tc["counted"] > 0:
            pct = (tc["yes"] / tc["counted"] * 100.0)
            tc["percent"] = pct
            valid_total_pcts.append(pct)
        else:
            tc["percent"] = 0.0
    total_avg = sum(valid_total_pcts) / len(valid_total_pcts) if valid_total_pcts else 0.0

    # -------------------------------------------------------------
    # คำนวณข้อมูลสำหรับกราฟเส้นรายเดือน (Trend) ของ OPD
    # -------------------------------------------------------------
    import json
    monthly_data_dict = {}
    for obj in qs:
        if obj.created_at:
            m_label = obj.created_at.strftime("%Y-%m")
            if m_label not in monthly_data_dict:
                monthly_data_dict[m_label] = {'score': 0, 'possible': 0}
            
            monthly_data_dict[m_label]['score'] += (obj.total_score or 0)
            monthly_data_dict[m_label]['possible'] += (obj.total_possible or 0)

    sorted_months = sorted(list(monthly_data_dict.keys()))
    thai_months = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
    
    trend_labels = []
    trend_data = []
    for m in sorted_months:
        y, mo = m.split('-')
        thai_year = int(y) + 543
        trend_labels.append(f"{thai_months[int(mo)-1]} {thai_year}")
        d = monthly_data_dict[m]
        pct = (d['score'] / d['possible'] * 100.0) if d['possible'] > 0 else 0.0
        trend_data.append(round(pct, 2))
    # -------------------------------------------------------------

    ctx = {
        "q": q, 
        "rows": rows,
        "total_cols": total_cols,
        "total_avg": total_avg,
        "section_titles": OPD_SECTION_TITLES,
        "n_items": OPD_N_ITEMS,
        "item_numbers": list(range(1, OPD_N_ITEMS + 1)),
        "trend_labels": json.dumps(trend_labels),
        "trend_data": json.dumps(trend_data),
    }
    return render(request, "scores/opd_avg.html", ctx)
    
@login_required
def opd_score_delete(request, pk):
    """ ฟังก์ชันสำหรับลบข้อมูล OPD (OPDScore) """
    obj = get_object_or_404(OPDScore, pk=pk)
    
    # ตรวจสอบสิทธิ์ (ต้องเป็น Admin, Staff หรือผู้สร้างข้อมูลเท่านั้น)
    is_owner = (obj.created_by == request.user)
    is_admin = request.user.is_superuser or request.user.is_staff

    if not (is_owner or is_admin):
        messages.error(request, "คุณไม่มีสิทธิ์ลบรายการที่ผู้อื่นสร้าง")
        return redirect('MRA:opd_score_detail', pk=pk)

    # ลบข้อมูล
    obj.delete()
    messages.success(request, "ลบข้อมูล OPD เรียบร้อยแล้ว")
    return redirect('MRA:opd_score_list')


# # กันเคสยังไม่มีคอนสแตนต์
# try:
#     OPD_N_ITEMS
# except NameError:
#     OPD_N_ITEMS = 7

# @login_required
# def opd_score_update(request, pk):
#     # 1) โหลด object
#     obj = get_object_or_404(OPDScore, pk=pk)

#     # 2) สิทธิ์: เจ้าของ/แอดมินเท่านั้น
#     if not (request.user.is_superuser or request.user.is_staff or obj.created_by_id == request.user.id):
#         return HttpResponseForbidden("คุณไม่มีสิทธิ์แก้ไขรายการนี้")

#     # 3) ฟอร์มข้อมูลทั่วไป (วันที่/ชื่อ ฯลฯ)
#     form = OPDScoreForm(request.POST or None, instance=obj)

#     # 4) sections ที่เคยบันทึกไว้ (ถ้าไม่มี ให้โครงว่าง)
#     saved_sections = (obj.data or {}).get("sections") or _blank_sections()

#     # ปรับ key visit ให้เป็น string เสมอ (หัวข้อ 5)
#     for s in saved_sections:
#         if isinstance(s, dict) and "items_by_visit" in s and isinstance(s["items_by_visit"], dict):
#             s["items_by_visit"] = {str(k): v for k, v in s["items_by_visit"].items()}

#     if request.method == "POST" and form.is_valid():
#         # *** เวอร์ชันปลอดภัย: ยังไม่คำนวณใหม่ แค่เซฟข้อมูลหัวฟอร์ม ***
#         obj = form.save(commit=False)
#         obj.data = obj.data or {}
#         obj.data["sections"] = saved_sections  # คงค่าเดิมไว้ก่อน
#         obj.save()

#         messages.success(request, "บันทึกการแก้ไขข้อมูลทั่วไปเรียบร้อย (คะแนนเดิมยังคงไว้)")
#         return redirect(reverse("MRA:opd_score_detail", args=[obj.id]))

#     # context ที่เทมเพลตต้องใช้
#     ctx = {
#         "form": form,
#         "sections": saved_sections,
#         "n_items": OPD_N_ITEMS,
#         "editing": True,
#         "obj": obj,
#     }
#     return render(request, "scores/opd_score_form.html", ctx)

@login_required
def my_records(request):

    my_ipd = PatientScore.objects.filter(created_by=request.user).order_by("-created_at")
    
    my_opd = OPDScore.objects.filter(created_by=request.user).order_by("-created_at")
    
    return render(request, "my_records.html", {
        "my_ipd": my_ipd,
        "my_opd": my_opd,
    })

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'เปลี่ยนรหัสผ่านสำเร็จแล้ว!')
            return redirect('/')
        else:
            messages.error(request, 'กรุณาตรวจสอบข้อมูลให้ถูกต้อง')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


@login_required
def note_summary(request):
    q = (request.GET.get("q") or "").strip()
    
    # ดึงข้อมูลทั้งหมดก่อน
    ipd_qs = PatientScore.objects.all().order_by("-created_at")
    opd_qs = OPDScore.objects.all().order_by("-created_at")

    # ตัวกรองวันที่ (อ้างอิงจาก created_at เหมือนหน้ารายการ)
    start_d, end_d = _parse_date_or_day_range(q)
    if start_d and end_d:
        start_dt, end_dt_excl = _aware_range_from_dates(start_d, end_d)
        ipd_qs = ipd_qs.filter(created_at__gte=start_dt, created_at__lt=end_dt_excl)
        opd_qs = opd_qs.filter(created_at__gte=start_dt, created_at__lt=end_dt_excl)

    # 1. จัดเตรียมข้อมูลฝั่ง IPD
    ipd_data = []
    for i, title in enumerate(IPD_SECTION_TITLES, start=1):
        notes = []
        for obj in ipd_qs:
            # ดึงค่าจาก s1_note ถึง s12_note
            note_text = getattr(obj, f"s{i}_note", "")
            if note_text and str(note_text).strip():
                notes.append({
                    "hn": obj.hn,
                    "an": obj.an,
                    "date": obj.created_at,
                    "text": str(note_text).strip(),
                    "pk": obj.pk
                })
        ipd_data.append({"index": i, "title": title, "notes": notes, "count": len(notes)})

    # 2. จัดเตรียมข้อมูลฝั่ง OPD
    opd_data = []
    for i, title in enumerate(OPD_SECTION_TITLES, start=1):
        notes = []
        for obj in opd_qs:
            sections = (obj.data or {}).get("sections", [])
            for sec in sections:
                if sec.get("index") == i:
                    # ของ OPD เราเก็บข้อเสนอแนะไว้ใน suggestion
                    suggestion = sec.get("suggestion", "")
                    if suggestion and str(suggestion).strip():
                        notes.append({
                            "hn": obj.hn,
                            "date": obj.created_at,
                            "text": str(suggestion).strip(),
                            "pk": obj.pk
                        })
        opd_data.append({"index": i, "title": title, "notes": notes, "count": len(notes)})

    ctx = {
        "q": q,
        "ipd_data": ipd_data,
        "opd_data": opd_data,
    }
    return render(request, "scores/note_summary.html", ctx)