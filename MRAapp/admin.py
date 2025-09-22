from django.contrib import admin
from .models import Document,PatientScore,OPDScore

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "doc_date", "is_active", "created_at")
    search_fields = ("number", "title")
    list_filter = ("is_active", "doc_date", "created_at")

@admin.register(PatientScore)
class PatientScoreAdmin(admin.ModelAdmin):
    list_display = ("hcode","hn","an","total_yes","total_counted","percent","created_at")
    search_fields = ("hcode","hname","hn","an",)
    list_filter = ("hcode","created_at")

@admin.register(OPDScore)
class OPDScoreAdmin(admin.ModelAdmin):
    # คอลัมน์ในหน้า list
    list_display = (
        "id", "hcode", "hname", "hn", "pid",
        "is_general", "is_chronic",
        "diagnosis_short",
        "first_visit_date", "visit_date_start", "visit_date_end",
        "total_score", "total_possible", "percent",
        "created_by", "created_at",
    )
    list_display_links = ("id", "hcode", "hname")
    ordering = ("-created_at",)
    list_per_page = 50

    # ค้นหา/กรอง
    search_fields = ("hcode", "hname", "hn", "pid", "diagnosis")
    list_filter = (
        "is_general", "is_chronic", "created_by",
        ("first_visit_date", admin.DateFieldListFilter),
        ("visit_date_start", admin.DateFieldListFilter),
        ("visit_date_end", admin.DateFieldListFilter),
        ("created_at", admin.DateFieldListFilter),
    )

    # ฟิลด์ในหน้าแก้ไข
    readonly_fields = ("total_score", "total_possible", "percent", "created_by", "created_at", "data_pretty")
    fieldsets = (
        ("ข้อมูลหน่วยบริการ/ผู้ป่วย", {
            "fields": (("hcode", "hname"), ("hn", "pid"), ("is_general", "is_chronic"), "diagnosis")
        }),
        ("ช่วงเวลา", {
            "fields": ("audit_period", "first_visit_date", ("visit_date_start", "visit_date_end"))
        }),
        ("หมายเหตุ", {"fields": ("note",)}),
        ("ผลคะแนน", {
            "fields": (("total_score", "total_possible", "percent"),)
        }),
        ("ข้อมูลดิบ (JSON)", {
            "classes": ("collapse",),
            "fields": ("data_pretty",)
        }),
        ("ระบบ", {
            "fields": ("created_by", "created_at")
        }),
    )

    # ปุ่ม action
    actions = ["export_as_csv"]

    def diagnosis_short(self, obj):
        """ตัดข้อความ Diagnosis ให้สั้นลงใน list"""
        if not obj.diagnosis:
            return ""
        return (obj.diagnosis[:50] + "…") if len(obj.diagnosis) > 50 else obj.diagnosis
    diagnosis_short.short_description = "Diagnosis"

    def data_pretty(self, obj):
        """แสดง JSON ที่เก็บคะแนนแบบสวยๆ (read-only)"""
        import json
        try:
            return json.dumps(obj.data, ensure_ascii=False, indent=2)
        except Exception:
            return str(obj.data)
    data_pretty.short_description = "data (JSON)"

    def save_model(self, request, obj, form, change):
        # เผื่อกรณีสร้างในแอดมิน: ติด user ให้ created_by ครั้งแรก
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def export_as_csv(self, request, queryset):
        """ส่งออก CSV เฉพาะฟิลด์สำคัญ"""
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="opd_scores.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "id", "hcode", "hname", "hn", "pid",
            "is_general", "is_chronic", "diagnosis",
            "audit_period", "first_visit_date", "visit_date_start", "visit_date_end",
            "total_score", "total_possible", "percent",
            "created_by", "created_at",
        ])
        for o in queryset:
            writer.writerow([
                o.id, o.hcode, o.hname, o.hn, o.pid,
                o.is_general, o.is_chronic, (o.diagnosis or ""),
                (o.audit_period or ""), o.first_visit_date, o.visit_date_start, o.visit_date_end,
                o.total_score, o.total_possible, o.percent,
                getattr(o.created_by, "username", ""), o.created_at,
            ])
        return response
    export_as_csv.short_description = "Export เลือกเป็น CSV"