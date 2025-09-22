from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from .models import Document
from .forms import DocumentForm
from django.urls import reverse
from django.db.models import Q
from django import forms

from .forms import OPDScoreForm
from .models import OPDScore

from django.utils.dateparse import parse_date
from .models import IPDContent
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
IPD_N_ITEMS = 9  # IPD มี 9 เกณฑ์/หัวข้อ

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
    """สำหรับ IPD form: สร้าง 12 หัวข้อ × 9 เกณฑ์"""
    sections = []
    for idx, title in enumerate(IPD_SECTION_TITLES, start=1):
        rows = [form[f"s{idx}_{j}"] for j in range(1, IPD_N_ITEMS + 1)]
        note = form[f"s{idx}_note"]
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

    rows = []
    for i, title in enumerate(IPD_SECTION_TITLES, start=1):
        cols = []
        for j in range(1, IPD_N_ITEMS + 1):
            field = f"s{i}_{j}"
            values = list(qs.values_list(field, flat=True))
            counted = _counted(values)
            yes = sum(1 for v in counted if v == "1")
            total = len(counted)
            pct = (yes / total * 100.0) if total else 0.0
            cols.append({"yes": yes, "total": total, "percent": pct})
        avg = sum(c["percent"] for c in cols) / IPD_N_ITEMS if cols else 0.0
        rows.append({"index": i, "title": title, "cols": cols, "avg": avg})

    # Total (รวมทุกหัวข้อในแต่ละเกณฑ์)
    total_cols = []
    for j in range(1, IPD_N_ITEMS + 1):
        all_vals = []
        for i in range(1, len(IPD_SECTION_TITLES) + 1):
            field = f"s{i}_{j}"
            all_vals += list(qs.values_list(field, flat=True))
        counted = _counted(all_vals)
        yes = sum(1 for v in counted if v == "1")
        total = len(counted)
        pct = (yes / total * 100.0) if total else 0.0
        total_cols.append({"percent": pct})
    total_avg = sum(c["percent"] for c in total_cols) / IPD_N_ITEMS if total_cols else 0.0

    ctx = {
        "q": q,
        "rows": rows,
        "total_cols": total_cols,
        "total_avg": total_avg,
        "section_titles": IPD_SECTION_TITLES,
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
    "Rehabilitation record",
]

OPD_N_ITEMS = 7
DEFAULT_ITEMS_TEXTS = [f"เกณฑ์ {i}" for i in range(1, OPD_N_ITEMS + 1)]

# Follow Up: 3 ครั้ง
N_VISITS_SECTION5 = 3
VISIT_LABELS = {1: "ครั้งที่ 1", 2: "ครั้งที่ 2", 3: "ครั้งที่ 3"}

def _blank_sections():
    sections = []
    for i, title in enumerate(OPD_SECTION_TITLES, start=1):
        if i == 5:
            items_by_visit = {}
            for v in range(1, N_VISITS_SECTION5 + 1):
                items_by_visit[v] = [
                    {"index": j, "text": DEFAULT_ITEMS_TEXTS[j-1], "value": "na", "weight": 1}
                    for j in range(1, OPD_N_ITEMS + 1)
                ]
            sections.append({
                "index": i, "title": title, "add": 0, "deduct": 0, "locked": False,
                "active_visit": 1, "items_by_visit": items_by_visit,
                "score": 0, "possible": 0,
            })
        else:
            items = [
                {"index": j, "text": DEFAULT_ITEMS_TEXTS[j-1], "value": "na", "weight": 1}
                for j in range(1, OPD_N_ITEMS + 1)
            ]
            sections.append({
                "index": i, "title": title, "add": 0, "deduct": 0, "locked": False,
                "items": items, "score": 0, "possible": 0,
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

        # เลือก items สำหรับหัวข้อ 5 / อื่น ๆ
        if "items_by_visit" in sec:   # section 5
            # เลือก "ชุดที่จะคิดคะแนน" ตามสูตรของคุณ (ถ้าคิดรวมทุกครั้ง ให้รวมที่นี่)
            active = int(sec.get("active_visit", 1))
            items = sec["items_by_visit"][active]   # <-- ถ้าคุณเปลี่ยนมา "รวมทุกครั้ง" ให้รวมที่นี่แทน
        else:
            items = sec["items"]

        if locked:
            # ❗ เปลี่ยนจาก "ให้เต็ม" เป็น "ไม่นับคะแนน"
            sec_score = 0
            sec_possible = 0
            # ไม่คิด add/deduct เมื่อถูกล็อค
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
        if form.is_valid():
            sections = _blank_sections()
            for i in range(1, 8+1):
                locked = request.POST.get(f"s{i}_lock") == "on"
                sections[i-1]["locked"] = locked

                if i == 5:
                    # หัวข้อ Follow Up
                    active_visit = int(request.POST.get("s5_visit", "1") or 1)
                    sections[i-1]["active_visit"] = active_visit

                    if locked:
                        sections[i-1]["add"] = 0
                        sections[i-1]["deduct"] = 0
                    else:
                        sections[i-1]["add"] = int(request.POST.get("s5_add", "0") or 0)
                        sections[i-1]["deduct"] = int(request.POST.get("s5_ded", "0") or 0)

                        # เก็บค่าทุกครั้ง 1..3: ชื่อ field -> s5_v{v}_i{j}
                        for v in range(1, N_VISITS_SECTION5+1):
                            for j in range(1, N_ITEMS+1):
                                key = f"s5_v{v}_i{j}"
                                val = request.POST.get(key, "na")
                                sections[i-1]["items_by_visit"][v][j-1]["value"] = val
                else:
                    if locked:
                        sections[i-1]["add"] = 0
                        sections[i-1]["deduct"] = 0
                    else:
                        sections[i-1]["add"] = int(request.POST.get(f"s{i}_add", "0") or 0)
                        sections[i-1]["deduct"] = int(request.POST.get(f"s{i}_ded", "0") or 0)
                        for j in range(1, N_ITEMS+1):
                            val = request.POST.get(f"s{i}_i{j}", "na")
                            sections[i-1]["items"][j-1]["value"] = val

            total_score, total_possible, percent = _calc_totals(sections)

            obj: OPDScore = form.save(commit=False)
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
    else:
        form = OPDScoreForm()

    context = {
    "form": form,
    "sections": _blank_sections(),
    "n_items": OPD_N_ITEMS,
    "visit_labels": VISIT_LABELS,
}
    return render(request, "scores/opd_score_form.html", context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import OPDScore

@login_required
def opd_score_detail(request, pk):
    obj = get_object_or_404(OPDScore, pk=pk)
    data = obj.data or {}
    sections = data.get("sections", [])

    overall_display_score = 0
    overall_display_possible = 0

    for s in sections:
        # --- หัวข้อ 5: มีหลายครั้ง ---
        if "items_by_visit" in s:
            # ทำให้ key เป็นสตริง '1'/'2'/'3'
            fixed = {}
            for k, items in s["items_by_visit"].items():
                fixed[str(k)] = items
            s["items_by_visit"] = fixed

            # per-visit summary (ไม่รวม add/deduct)
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

            # display_* สำหรับหัวข้อ 5 = รวม 3 ครั้ง (+ add/deduct ถ้าไม่ล็อค)
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

            # ค่า active_visit เผื่อโชว์ข้อความ
            try:
                s["active_visit"] = int(s.get("active_visit") or 1)
            except Exception:
                s["active_visit"] = 1

        # --- หัวข้ออื่น ---
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

        # รวมเป็นผลรวมทั้งหน้า (display)
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
    qs = OPDScore.objects.all().order_by("-created_at")

    # จำนวนต่อหน้า (default = 10)
    try:
        per_page = int(request.GET.get("per_page", 10))
    except (TypeError, ValueError):
        per_page = 10
    if per_page <= 0:
        per_page = 10

    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # enrich เฉพาะรายการในหน้านี้ ด้วย display_* (รวมข้อ 5 ทั้ง 3 ครั้ง)
    enriched = []
    for o in page_obj.object_list:
        data = o.data or {}
        sections = data.get("sections", [])
        # ทำ key ของ items_by_visit ให้เป็น str เสมอ
        for s in sections:
            if "items_by_visit" in s and isinstance(s["items_by_visit"], dict):
                s["items_by_visit"] = {str(k): v for k, v in s["items_by_visit"].items()}
        sc, ps, pc = _compute_display_totals(sections)
        o.display_score = sc
        o.display_possible = ps
        o.display_percent = pc
        enriched.append(o)

    # แทน object_list ด้วยตัวที่ enrich แล้ว
    page_obj.object_list = enriched

    return render(request, "scores/opd_score_list.html", {
        "page_obj": page_obj,
        "per_page": per_page,
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import OPDScore

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
    return (0, 0)  # NA/ว่าง


    

@login_required
def opd_score_averages(request):
    period = (request.GET.get("period") or "").strip()
    q      = (request.GET.get("q") or "").strip()

    qs = OPDScore.objects.all().order_by("-created_at")
    if period:
        qs = qs.filter(audit_period=period)
    if q:
        from django.db.models import Q
        qs = qs.filter(Q(hn__icontains=q) | Q(pid__icontains=q) | Q(hcode__icontains=q) | Q(hname__icontains=q))

    rows = []
    for i, title in enumerate(OPD_SECTION_TITLES, start=1):
        cols = [{"yes": 0, "counted": 0} for _ in range(OPD_N_ITEMS)]
        rows.append({"index": i, "title": title, "cols": cols, "avg": 0.0})

    total_cols = [{"yes": 0, "counted": 0} for _ in range(OPD_N_ITEMS)]

    for o in qs:
        data = o.data or {}
        sections = data.get("sections", []) or []
        sec_by_idx = {int(s.get("index", idx+1)): s for idx, s in enumerate(sections)}

        for i in range(1, len(OPD_SECTION_TITLES) + 1):
            s = sec_by_idx.get(i)
            if not s:  continue
            if bool(s.get("locked")):
                continue

            if "items_by_visit" in s and i == 5:
                ibv = {str(k): v for k, v in (s.get("items_by_visit") or {}).items()}
                for vkey in ("1", "2", "3"):
                    items = ibv.get(vkey) or []
                    for j in range(min(OPD_N_ITEMS, len(items))):
                        yes = 1 if str(items[j].get("value")).strip().upper() == "1" else 0
                        cnt = 1 if str(items[j].get("value")).strip().upper() in ("0","1") else 0
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
                    rows[i-1]["cols"][j]["yes"]     += yes
                    rows[i-1]["cols"][j]["counted"] += cnt
                    total_cols[j]["yes"]            += yes
                    total_cols[j]["counted"]        += cnt

    for r in rows:
        acc = 0.0
        for c in r["cols"]:
            pct = (c["yes"] / c["counted"] * 100.0) if c["counted"] else 0.0
            c["percent"] = round(pct, 2)
            acc += c["percent"]
        r["avg"] = round(acc / OPD_N_ITEMS, 2)

    total_row = {"title": "รวมทุกหัวข้อ", "cols": [], "avg": 0.0}
    acc = 0.0
    for tc in total_cols:
        pct = (tc["yes"] / tc["counted"] * 100.0) if tc["counted"] else 0.0
        total_row["cols"].append({"percent": round(pct, 2)})
        acc += round(pct, 2)
    total_row["avg"] = round(acc / OPD_N_ITEMS, 2)

    ctx = {
        "period": period,
        "q": q,
        "rows": rows,
        "total_row": total_row,
        "section_titles": OPD_SECTION_TITLES,
        "n_items": OPD_N_ITEMS,
        "item_numbers": list(range(1, OPD_N_ITEMS + 1)),
    }
    return render(request, "scores/opd_avg.html", ctx)
