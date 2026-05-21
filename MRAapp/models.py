from django.db import models
from django.utils import timezone
from django.conf import settings

def document_upload_to(instance, filename):
    return f"documents/{timezone.now():%Y/%m}/{filename}"

def current_fiscal_year():
    return timezone.now().year


class Document(models.Model):
    number = models.CharField("เลขที่เอกสาร", max_length=50, blank=True)
    doc_date = models.DateField("วัน/เดือน/ปี", default=timezone.now)
    title = models.CharField("หัวข้อเรื่อง", max_length=255)
    file = models.FileField("ไฟล์เอกสาร", upload_to=document_upload_to, blank=True, null=True)
    external_url = models.URLField("ลิงก์ภายนอก", blank=True)
    is_active = models.BooleanField("แสดงผล", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.number or '-'} : {self.title}"

    def save(self, *args, **kwargs):
        if not self.number:
            last = Document.objects.order_by("-id").first()
            next_no = (last.id + 1) if last else 1
            self.number = f"RP{next_no:03d}"
        super().save(*args, **kwargs)

    @property
    def download_href(self):
        if self.file:
            return self.file.url
        if self.external_url:
            return self.external_url
        return ""


# --------- ย้าย IPDContent ออกมาเป็น class แยก (ระดับโมดูล) ---------

class IPDContent(models.Model):
    fiscal_year = models.IntegerField(default=current_fiscal_year)
    month = models.CharField(max_length=20)
    department = models.CharField(max_length=255, blank=True, null=True)
    hn = models.CharField(max_length=50, blank=True, null=True)
    an = models.CharField(max_length=50, blank=True, null=True)
    hname = models.CharField(max_length=255, blank=True, null=True)
    date_admitted = models.DateField(blank=True, null=True)
    date_discharged = models.DateField(blank=True, null=True)

    # 12 ข้อ
    score_1 = models.IntegerField(default=0)
    score_2 = models.IntegerField(default=0)
    score_3 = models.IntegerField(default=0)
    score_4 = models.IntegerField(default=0)
    score_5 = models.IntegerField(default=0)
    score_6 = models.IntegerField(default=0)
    score_7 = models.IntegerField(default=0)
    score_8 = models.IntegerField(default=0)
    score_9 = models.IntegerField(default=0)
    score_10 = models.IntegerField(default=0)
    score_11 = models.IntegerField(default=0)
    score_12 = models.IntegerField(default=0)

    full_score = models.IntegerField(default=56)
    sum_score = models.IntegerField(default=0)
    percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.fiscal_year} - {self.month} ({self.hn})"
# ****************************************************************************************************

# --- ตรงส่วนประกาศ choices เหมือนเดิม ---
SCORE_CHOICES = [
    ('', ''),
    ('0', '0'),
    ('1', '1'),
    ('NA', 'NA'),
]

BONUS_CHOICES = [
    (0, '0'),
    (1, '+1'),
    (-1, '-1'),
]

FINDING_RADIO_CHOICES = [
    ('inadequate', 'Documentation inadequate for meaningful review (ข้อมูลไม่เพียงพอสำหรับการทบทวน)'),
    ('no_issue', 'No significant medical recode issue identified (ไม่มีปัญหาสำคัญจากการทบทวน)'),
    ('certain_issue', 'Certain issue in question specify (มีปัญหาจากการทบทวนที่ต้องค้นต่อ ระบุ)'),
]

def _norm(v):
    if v is None:
        return None
    return str(v).strip().upper()

def _counted_values(values):
    """คืนเฉพาะค่าที่นับได้จริง (0/1) โดย normalize ก่อน"""
    out = []
    for v in values:
        s = _norm(v)
        if s in (None, "", "NA"):
            continue
        if s in ("0", "1"):
            out.append(s)
    return out

class PatientScore(models.Model):
    # ส่วนที่ 1
    hcode = models.CharField("Hcode", max_length=20) 
    hname = models.CharField("Hname", max_length=255, blank=True)
    hn = models.CharField("HN", max_length=50, blank=True)
    an = models.CharField("AN", max_length=50, blank=True)
    date_admitted = models.DateField("Date admitted", null=True, blank=True)
    date_discharged = models.DateField("Date discharged", null=True, blank=True)
    bonus_s1 = models.IntegerField("คะแนนพิเศษ หัวข้อ 1", choices=BONUS_CHOICES, default=0)
    bonus_s12 = models.IntegerField("คะแนนพิเศษ หัวข้อ 12", choices=BONUS_CHOICES, default=0)

    # สรุปรวม
    total_yes = models.PositiveIntegerField(default=0)
    total_counted = models.PositiveIntegerField(default=0)
    percent = models.FloatField(default=0.0)

    max_score   = models.IntegerField(default=12*9, blank=True)
    final_score = models.IntegerField(default=0, blank=True)
    note        = models.TextField(blank=True)

    title = models.CharField(
        "หัวข้อแบบประเมิน",
        max_length=255,
        
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="ผู้บันทึกข้อมูล")

    finding_sorting_issue = models.BooleanField(
        "การจัดเรียงเวชระเบียนไม่เป็นไปตามมาตรฐานที่กำหนด",
        default=False
    )

    # Checkbox 2: ไม่มีชื่อผู้รับบริการ
    finding_no_id_issue = models.BooleanField(
        "เอกสารบางแผ่น ไม่มีชื่อผู้รับบริการ HN AN ทำให้ไม่สามารถระบุได้...",
        default=False
    )
    # --- ส่วนที่ 2: Radio (เลือกได้เพียง 1 ข้อ) ---
    overall_finding = models.CharField(
        "Overall finding (เลือกเพียง 1 ข้อ)",
        max_length=50,
        choices=FINDING_RADIO_CHOICES,
        default='no_issue',
        blank=True,
        null=True
    )

    # --- ส่วนที่ 3: ช่องกรอกข้อมูลเพิ่มเติม  ---
    certain_issue_note = models.CharField(
        "ระบุปัญหา (กรณีเลือก Certain issue)",
        max_length=255,
        blank=True,
        default=""
    )

    
    def compute_score(self):
        values = [getattr(self, f"s{i}_{j}", None) for i in range(1,13) for j in range(1,10)]
        counted = _counted_values(values)
        total_yes = sum(1 for v in counted if v == "1")
        total_counted = len(counted)
        b1 = self.bonus_s1 if self.bonus_s1 is not None else 0
        b12 = self.bonus_s12 if self.bonus_s12 is not None else 0
        adjusted_yes = total_yes + b1 + b12
        if adjusted_yes < 0: 
            adjusted_yes = 0
        percent = (adjusted_yes / total_counted * 100.0) if total_counted else 0.0
        return total_yes, total_counted, percent, adjusted_yes

    def save(self, *args, **kwargs):
        if not (self.title or "").strip():
            self.title = "แบบประเมินคุณภาพการดูแลผู้ป่วย (ชั่วคราว)"
            
        t_yes, t_counted, pct, final_val = self.compute_score()
        
        self.total_yes = t_yes
        self.total_counted = t_counted
        self.percent = pct
        self.final_score = final_val
        
        super().save(*args, **kwargs)

    def section_scores(self):
        out = []
        for i in range(1, 13):
            vals = [getattr(self, f"s{i}_{j}", None) for j in range(1, 10)]
            counted = _counted_values(vals)
            yes = sum(1 for v in counted if v == "1")

            bonus = 0
            if i == 1: bonus = self.bonus_s1
            if i == 12: bonus = self.bonus_s12

            section_yes = yes + bonus
            total = len(counted)
            pct = (yes / total * 100.0) if total else 0.0
            out.append({
                "index": i, 
                "yes": yes, 
                "bonus": bonus, # เก็บค่า bonus แยกไว้แสดงผล
                "total_yes": section_yes,
                "counted": total, 
                "percent": pct
            })
        return out  


for i in range(1, 13):
    for j in range(1, 10):
        PatientScore.add_to_class(
            f"s{i}_{j}",
            models.CharField(
                max_length=3,
                choices=SCORE_CHOICES,
                blank=True,
                default="",
            ),
        )
for i in range(1, 13):
    PatientScore.add_to_class(
        f"s{i}_note",
        models.TextField(blank=True, null=True)
    )

IGNORED = {None, "", "NA"}

def _counted_values(values):
    """คืนเฉพาะค่าที่นับคะแนนจริง (0/1)"""
    return [v for v in values if v not in IGNORED]


# ******************************************************** OPD บันทึกคะแนน **********************************************************************************

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class OPDScore(models.Model):
    # Header fields
    hcode = models.CharField("Hcode", max_length=20, blank=True, null=True)
    hname = models.CharField("Hname", max_length=255, blank=True, null=True)
    hn = models.CharField("HN", max_length=20, blank=True, null=True)
    pid = models.CharField("PID", max_length=20, blank=True, null=True)

    is_general = models.BooleanField("General", default=False)
    is_chronic = models.BooleanField("Chronic", default=False)
    is_psychiatric = models.BooleanField("Psychiatric", default=False)
    

    diagnosis = models.TextField("Diagnosis", blank=True, null=True)

    audit_period = models.CharField("ช่วงเวลาที่ตรวจสอบ (เดือน/ปี YYYY-MM)", max_length=7, blank=True, null=True)

    visit_date_start = models.DateField("Visit Date (เริ่ม)", blank=True, null=True)
    visit_date_end   = models.DateField("Visit Date (ถึง)", blank=True, null=True)
    first_visit_date = models.DateField("1st Visit Date", blank=True, null=True)

    data = models.JSONField(default=dict, blank=True)

    total_score = models.IntegerField(default=0)
    total_possible = models.IntegerField(default=0)
    percent = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    REVIEW_CHOICES = [
        ('inadequate', 'Documenttation inadequate for meaningful review (ข้อมูลไม่เพียงพอสำหรับการทบทวน)'),
        ('no_issue', 'No significant medical recode issue identified (ไม่มีปัญหาสำคัญจากการทบทวน)'),
        ('has_issue', 'Certain issue in question specify (มีปัญหาจากการทบทวนที่ต้องค้นต่อ ระบุ)'),
    ]

    review_status = models.CharField(
        "Review Status", 
        max_length=50, 
        choices=REVIEW_CHOICES,
        blank=True, 
        null=True
    )

    certain_issue_note = models.CharField(
        "ระบุปัญหา (กรณีเลือก Certain issue)",
        max_length=255,
        blank=True,
        default=""
    )

    note = models.TextField("หมายเหตุ", blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="ผู้บันทึกข้อมูล")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"OPD Score #{self.id} - {self.hn or ''}"

