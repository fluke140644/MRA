from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from .models import Document
from .forms import DocumentForm
from django.urls import reverse
from django.db.models import Q
from django import forms

from django.utils.dateparse import parse_date
from .models import IPDContent
# Create your views here.

def index(request):
    return render(request,"index.html")

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
from django.utils.dateparse import parse_date
from .models import IPDContent

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

# MRAapp/views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import PatientScoreForm
from .models import PatientScore


# ************************************ตัวกรอกวันที่ scores-list***************************************************************

from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date
import datetime, re

# --- parser วันเดียว/ช่วงวัน รองรับหลายรูปแบบ ---
def _parse_custom_date(s: str):
    s = (s or "").strip()
    if not s:
        return None
    # ISO ก่อน (YYYY-MM-DD)
    d = parse_date(s)
    if d:
        return d
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})$", s)
    if not m:
        return None
    day, month, year = map(int, m.groups())
    if year < 100:           # 2 หลัก => 20xx
        year += 2000
    if year >= 2400:         # พ.ศ. => ค.ศ.
        year -= 543
    try:
        return datetime.date(year, month, day)
    except ValueError:
        return None

def _parse_date_or_day_range(q: str):
    """
    คืนค่า (start_date, end_date) เป็น date (inclusive) ถ้า q เป็นวันเดียว/ช่วงวัน
    รองรับ: '09/09/2025', '2025-09-09',
            '09/09/2025 - 10/09/2025', '2025-09-09 ถึง 2025-09-10',
            '9', '9 - 8' (ยึดเดือน/ปีปัจจุบันตามเวลาไทย)
    """
    if not q:
        return None, None
    t = q.strip()

    # เคสวันเดียว
    one = _parse_custom_date(t)
    if one:
        return one, one

    # ช่วง DD/MM/YYYY หรือ DD-MM-YYYY (มีตัวคั่น -, –, —, ถึง)
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

    # ช่วง ISO มีช่องว่างรอบตัวคั่น
    parts = re.split(r"\s+(?:-|–|—|ถึง)\s+", t)
    if len(parts) == 2:
        d1, d2 = _parse_custom_date(parts[0]), _parse_custom_date(parts[1])
        if d1 and d2:
            if d1 > d2:
                d1, d2 = d2, d1
            return d1, d2

    # เลขวันล้วน ในเดือน/ปีปัจจุบัน (อิงเวลาไทย)
    today = timezone.localdate()
    y, mth = today.year, today.month

    m = re.match(r"^\s*(\d{1,2})\s*(?:-|–|—|ถึง)\s*(\d{1,2})\s*$", t)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if 1 <= a <= 31 and 1 <= b <= 31:
            lo, hi = min(a, b), max(a, b)
            try:
                return datetime.date(y, mth, lo), datetime.date(y, mth, hi)
            except ValueError:
                return None, None

    m = re.match(r"^\s*(\d{1,2})\s*$", t)
    if m:
        d = int(m.group(1))
        if 1 <= d <= 31:
            try:
                one = datetime.date(y, mth, d)
                return one, one
            except ValueError:
                return None, None

    return None, None

# --- สร้าง datetime ช่วงวันแบบ aware ตามเวลาไทย ---
def _aware_range_from_dates(start_date: datetime.date, end_date: datetime.date):
    tz = timezone.get_current_timezone()  # Asia/Bangkok ตาม settings
    start_naive = datetime.datetime.combine(start_date, datetime.time.min)
    end_naive   = datetime.datetime.combine(end_date + datetime.timedelta(days=1), datetime.time.min)  # exclusive
    start_aware = timezone.make_aware(start_naive, tz)
    end_aware   = timezone.make_aware(end_naive, tz)
    return start_aware, end_aware

def score_list(request):
    q = (request.GET.get("q") or "").strip()
    limit = request.GET.get("limit")  # รับค่ามาจาก query
    try:
        limit = int(limit)
        if limit <= 0:
            limit = None
    except (TypeError, ValueError):
        limit = None  # ถ้าไม่มี หรือผิด ให้เป็น None

    items = PatientScore.objects.all().order_by("-created_at")

    # ---- กรองวันที่/hn/an เหมือนเดิม ----
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
    "Nurses note",
]
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
            continue  # ว่าง/NA = ไม่นับ
        if s in ("0", "1"):
            out.append(s)
    return out

def sections_from_form(form):
    sections = []
    for idx, title in enumerate(SECTION_TITLES, start=1):
        rows = [form[f"s{idx}_{j}"] for j in range(1, 10)]  # 9 เกณฑ์/หัวข้อ
        note = form[f"s{idx}_note"]                          # ✅ หมายเหตุหัวข้อนี้
        sections.append({"index": idx, "title": title, "rows": rows, "note": note})
    return sections

def score_create(request):
    if request.method == "POST":
        form = PatientScoreForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f"บันทึกสำเร็จ #{obj.id}")
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
    # ผูกสรุปคะแนนรายหัวข้อจากโมเดลเข้าไปในแต่ละ section
    stats = {s["index"]: s for s in obj.section_scores()}
    for sec in sections:
        sec["stat"] = stats.get(sec["index"], {"yes": 0, "counted": 0, "percent": 0.0})
    return render(request, "scores/score_detail.html", {"obj": obj, "form": form, "sections": sections})


# ****************************************************************************************************************************************

from django.db.models import Value

def score_summary(request):
    q = (request.GET.get("q") or "").strip()
    qs = PatientScore.objects.all().order_by("-created_at")

    # กรองวันที่ถ้ามี q
    start_d, end_d = _parse_date_or_day_range(q)
    if start_d and end_d:
        start_dt, end_dt_excl = _aware_range_from_dates(start_d, end_d)
        qs = qs.filter(created_at__gte=start_dt, created_at__lt=end_dt_excl)

    # ตาราง: แถว = 12 หัวข้อ, คอลัมน์ = เกณฑ์ 1..9
    rows = []
    for i, title in enumerate(SECTION_TITLES, start=1):
        cols = []
        for j in range(1, 10):
            field = f"s{i}_{j}"
            values = list(qs.values_list(field, flat=True))
            counted = _counted(values)  # ตัดค่าว่างและ NA ออก
            yes = sum(1 for v in counted if v == "1")
            total = len(counted)
            pct = (yes / total * 100.0) if total else 0.0
            cols.append({"yes": yes, "total": total, "percent": pct})
        avg = sum(c["percent"] for c in cols) / 9.0 if cols else 0.0
        rows.append({"index": i, "title": title, "cols": cols, "avg": avg})

    # แถว Total: รวมทุกหัวข้อในแต่ละคอลัมน์
    total_cols = []
    for j in range(1, 10):
        all_vals = []
        for i in range(1, 13):
            field = f"s{i}_{j}"
            all_vals += list(qs.values_list(field, flat=True))
        counted = _counted(all_vals)
        yes = sum(1 for v in counted if v == "1")
        total = len(counted)
        pct = (yes / total * 100.0) if total else 0.0
        total_cols.append({"percent": pct})
    total_avg = sum(c["percent"] for c in total_cols) / 9.0 if total_cols else 0.0

    ctx = {
        "q": q,
        "rows": rows,
        "total_cols": total_cols,
        "total_avg": total_avg,
        "section_titles": SECTION_TITLES,
    }
    return render(request, "scores/summary.html", ctx)


# ************************************/score coverage*****************************************************************
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, time, timedelta
from .models import PatientScore

# ---------- helper ----------
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
    # รับได้ทั้ง YYYY-MM-DD (จาก input type=date) และ DD/MM/YYYY
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
    end_dt   = timezone.make_aware(datetime.combine(d2 + timedelta(days=1), time.min), tz)  # half-open
    return start_dt, end_dt

# ---------- VIEW: สรุปจำนวนที่ตรวจ + ร้อยละความสมบูรณ์ ----------
def score_coverage(request):
    # รับช่วงวันที่จาก GET
    a_start = _parse_date(request.GET.get("admit_start"))
    a_end   = _parse_date(request.GET.get("admit_end"))
    d_start = _parse_date(request.GET.get("disch_start"))
    d_end   = _parse_date(request.GET.get("disch_end"))

    qs = PatientScore.objects.all().order_by("-created_at")

    # เงื่อนไขกรองช่วงวันที่ (อิสระต่อกัน)
    if a_start and a_end:
        qs = qs.filter(date_admitted__gte=a_start, date_admitted__lte=a_end)
    if d_start and d_end:
        qs = qs.filter(date_discharged__gte=d_start, date_discharged__lte=d_end)

    # รวมทุกช่องของทุกราย เพื่อนับ overall
    yes_all = 0
    counted_all = 0

    rows = []   # สำหรับแถว 12 หัวข้อ

    # จำนวนเวชระเบียนทั้งหมด (ในช่วงที่เลือก)
    total_records = qs.count()

    # จำนวนเวชระเบียนที่ “ถูกตรวจอย่างน้อย 1 เกณฑ์” ต่อหัวข้อ
    # และ % ความสมบูรณ์ = (จำนวน 1)/(ช่องที่นับได้ทั้งหมดของหัวข้อนั้น)
    for i, title in enumerate(SECTION_TITLES, start=1):
        # ดึงค่า 9 เกณฑ์ของหัวข้อ i สำหรับทุกเวชระเบียน
        section_matrix = []
        checked_records = 0  # เวชระเบียนที่มีอย่างน้อยหนึ่งค่าเป็น 0/1
        yes = 0
        counted = 0

        for rec in qs.values_list(
            *[f"s{i}_{j}" for j in range(1, 10)]
        ):
            vals = list(rec)
            counted_vals = _counted_list(vals)  # เฉพาะ 0/1
            if counted_vals:
                checked_records += 1
                yes     += sum(1 for v in counted_vals if v == "1")
                counted += len(counted_vals)

        # อัปเดตรวมทั้งระบบ
        yes_all     += yes
        counted_all += counted

        pct = (yes * 100.0 / counted) if counted else 0.0
        rows.append({
            "index": i,
            "title": title,
            "checked_records": checked_records,  # จำนวนเวชระเบียนที่ตรวจหัวข้อนี้
            "percent": pct,                      # ร้อยละความสมบูรณ์ของหัวข้อนี้
        })

    overall_pct = (yes_all * 100.0 / counted_all) if counted_all else 0.0

    ctx = {
        "rows": rows,
        "total_records": total_records,     # จำนวนเวชระเบียนในช่วง
        "examined_total": max(r["checked_records"] for r in rows) if rows else 0,  # ถ้าทุกหัวข้อถูกตรวจครบ จะเท่ากับ total_records
        "overall_pct": overall_pct,

        # ค่าฟอร์ม
        "admit_start": request.GET.get("admit_start", ""),
        "admit_end": request.GET.get("admit_end", ""),
        "disch_start": request.GET.get("disch_start", ""),
        "disch_end": request.GET.get("disch_end", ""),
    }
    return render(request, "scores/coverage.html", ctx)





