from django.db import models
from django.utils import timezone


def document_upload_to(instance, filename):
    return f"documents/{timezone.now():%Y/%m}/{filename}"

def current_fiscal_year():
    # ถ้าต้องการ พ.ศ. ใช้: return timezone.now().year + 543
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
            continue  # ว่าง/NA = ไม่นับ
        if s in ("0", "1"):
            out.append(s)
    return out

class PatientScore(models.Model):
    # ส่วนที่ 1
    hcode = models.CharField("Hcode", max_length=20)  # ถ้าอยากไม่บังคับ -> ใส่ blank=True
    hname = models.CharField("Hname", max_length=255, blank=True)
    hn = models.CharField("HN", max_length=50, blank=True)
    an = models.CharField("AN", max_length=50, blank=True)
    date_admitted = models.DateField("Date admitted", null=True, blank=True)
    date_discharged = models.DateField("Date discharged", null=True, blank=True)

    # สรุปรวม
    total_yes = models.PositiveIntegerField(default=0)
    total_counted = models.PositiveIntegerField(default=0)
    percent = models.FloatField(default=0.0)

    max_score   = models.IntegerField(default=12*9, blank=True)  # 12 หัวข้อ × 9 เกณฑ์
    final_score = models.IntegerField(default=0, blank=True)
    note        = models.TextField(blank=True)

    title = models.CharField(
        "หัวข้อแบบประเมิน",
        max_length=255,
        
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # def compute_score(self):
    #     # รวมค่า 12×9 ช่องแบบไล่ชื่อฟิลด์
    #     values = []
    #     for i in range(1, 13):
    #         for j in range(1, 10):
    #             values.append(getattr(self, f"s{i}_{j}", "NA"))
    #     counted = [v for v in values if v != "NA"]
    #     total_yes = sum(1 for v in counted if v == "1")
    #     total_counted = len(counted)
    #     percent = (total_yes / total_counted * 100.0) if total_counted else 0.0
    #     return total_yes, total_counted, percent
    
    def compute_score(self):
        values = [getattr(self, f"s{i}_{j}", None) for i in range(1,13) for j in range(1,10)]
        counted = _counted_values(values)
        total_yes = sum(1 for v in counted if v == "1")
        total_counted = len(counted)
        percent = (total_yes / total_counted * 100.0) if total_counted else 0.0
        return total_yes, total_counted, percent

    def save(self, *args, **kwargs):
        # ใส่ชื่อ default ถ้าเว้นว่าง
        if not (self.title or "").strip():
            self.title = "แบบประเมินคุณภาพการดูแลผู้ป่วย (ชั่วคราว)"
        self.total_yes, self.total_counted, self.percent = self.compute_score()
        self.final_score = self.total_yes   # คะแนนที่ได้ = จำนวน 1 ที่นับจริง
        super().save(*args, **kwargs)

    def section_scores(self):
        out = []
        for i in range(1, 13):
            vals = [getattr(self, f"s{i}_{j}", None) for j in range(1, 10)]
            counted = _counted_values(vals)
            yes = sum(1 for v in counted if v == "1")
            total = len(counted)
            pct = (yes / total * 100.0) if total else 0.0
            out.append({"index": i, "yes": yes, "counted": total, "percent": pct})
        return out  

# ✅ เพิ่มฟิลด์ s1_1..s12_9 แบบไดนามิก (default=NA, choices=0/1/NA)
# for i in range(1, 13):
#     for j in range(1, 10):
#         PatientScore.add_to_class(
#             f"s{i}_{j}",
#             models.CharField(max_length=3, choices=SCORE_CHOICES, default=""),
#         )

for i in range(1, 13):
    for j in range(1, 10):
        PatientScore.add_to_class(
            f"s{i}_{j}",
            models.CharField(
                max_length=3,
                choices=SCORE_CHOICES,
                blank=True,      # อนุญาตให้ว่าง
                default="",      # default คือค่าว่าง
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
    # ส่วนที่ 2: คะแนน 12 ช่อง (0/1/NA) -> ตั้ง default = 'NA' ทั้งหมด
    # s1  = models.CharField(max_length=3, choices=SCORE_CHOICES, )
    # s2  = models.CharField(max_length=3, choices=SCORE_CHOICES, )
    # s3  = models.CharField(max_length=3, choices=SCORE_CHOICES, )
    # s4  = models.CharField(max_length=3, choices=SCORE_CHOICES, )
    # s5  = models.CharField(max_length=3, choices=SCORE_CHOICES, )
    # s6  = models.CharField(max_length=3, choices=SCORE_CHOICES, )
    # s7  = models.CharField(max_length=3, choices=SCORE_CHOICES, )
    # s8  = models.CharField(max_length=3, choices=SCORE_CHOICES, )
    # s9  = models.CharField(max_length=3, choices=SCORE_CHOICES, )

    # สรุปผล
    # total_yes = models.PositiveIntegerField(default=0)
    # total_counted = models.PositiveIntegerField(default=0)
    # percent = models.FloatField(default=0.0)

    # created_at = models.DateTimeField(auto_now_add=True)

    # def compute_score(self):
    #     fields = [self.s1,self.s2,self.s3,self.s4,self.s5,self.s6,
    #               self.s7,self.s8,self.s9]
    #     counted = [v for v in fields if v != 'NA']
    #     total_yes = sum(1 for v in counted if v == '1')
    #     total_counted = len(counted)
    #     percent = (total_yes / total_counted * 100.0) if total_counted > 0 else 0.0
    #     return total_yes, total_counted, percent

    # def save(self, *args, **kwargs):
    #     self.total_yes, self.total_counted, self.percent = self.compute_score()
    #     # ให้ final_score = คะแนนที่ได้จริง (จำนวน 1 ที่นับ)
    #     self.final_score = self.total_yes
    #     super().save(*args, **kwargs)
