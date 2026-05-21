from django.contrib import admin
from django.utils.html import format_html
from .models import Document,PatientScore,OPDScore
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "doc_date", "is_active", "created_at")
    search_fields = ("number", "title")
    list_filter = ("is_active", "doc_date", "created_at")

@admin.register(PatientScore)
class PatientScoreAdmin(admin.ModelAdmin):
    # 1. ปรับหน้า List ให้ดูง่าย มีสีสัน และ Breadcrumb วันที่
    list_display = ("id", "hcode", "hn", "an", "total_yes", "total_counted", "percent_badge", "created_at")
    list_display_links = ("id", "hcode", "hn")
    search_fields = ("hcode", "hname", "hn", "an", "title")
    list_filter = ("hcode", "created_by", "created_at")
    date_hierarchy = "created_at"  # เพิ่มแถบกรองวันที่ด้านบนสุด
    list_per_page = 50

    # 2. ป้องกันการแก้ไขฟิลด์ที่ระบบคำนวณอัตโนมัติ
    readonly_fields = ("total_yes", "total_counted", "percent", "created_by", "created_at")

    # 3. จัดกลุ่มฟิลด์ในหน้าแก้ไขให้เป็นระเบียบ (Fieldsets) สามารถคลิกซ่อนพับได้
    fieldsets = (
        ("ข้อมูลผู้ป่วยและหน่วยบริการ", {
            "fields": (
                ("hcode", "hname"),
                ("hn", "an", "title"),
                ("date_admitted", "date_discharged"),
            )
        }),
        ("ส่วนที่ 1: Discharge summary : Dx., OP", {
            "classes": ("collapse",),
            "fields": (
                ("s1_1", "s1_2", "s1_3", "s1_4", "s1_5"),
                ("s1_6", "s1_7", "s1_8", "s1_9"),
                "bonus_s1", "s1_note"
            )
        }),
        ("ส่วนที่ 2: Discharge summary : Other", {
            "classes": ("collapse",),
            "fields": (
                ("s2_1", "s2_2", "s2_3", "s2_4"),
                ("s2_5", "s2_6", "s2_7"),  # ข้อนี้มีแค่ 7 เกณฑ์
                "s2_note"
            )
        }),
        ("ส่วนที่ 3: Informed consent", {
            "classes": ("collapse",),
            "fields": (
                ("s3_1", "s3_2", "s3_3", "s3_4", "s3_5"),
                ("s3_6", "s3_7", "s3_8", "s3_9"),
                "s3_note"
            )
        }),
        ("ส่วนที่ 4: History", {
            "classes": ("collapse",),
            "fields": (
                ("s4_1", "s4_2", "s4_3", "s4_4", "s4_5"),
                ("s4_6", "s4_7", "s4_8", "s4_9"),
                "s4_note"
            )
        }),
        ("ส่วนที่ 5: Physical exam", {
            "classes": ("collapse",),
            "fields": (
                ("s5_1", "s5_2", "s5_3", "s5_4", "s5_5"),
                ("s5_6", "s5_7", "s5_8", "s5_9"),
                "s5_note"
            )
        }),
        ("ส่วนที่ 6: Progress note", {
            "classes": ("collapse",),
            "fields": (
                ("s6_1", "s6_2", "s6_3", "s6_4", "s6_5"),
                ("s6_6", "s6_7", "s6_8", "s6_9"),
                "s6_note"
            )
        }),
        ("ส่วนที่ 7: Consultation record", {
            "classes": ("collapse",),
            "fields": (
                ("s7_1", "s7_2", "s7_3", "s7_4", "s7_5"),
                ("s7_6", "s7_7", "s7_8", "s7_9"),
                "s7_note"
            )
        }),
        ("ส่วนที่ 8: Anesthetic record", {
            "classes": ("collapse",),
            "fields": (
                ("s8_1", "s8_2", "s8_3", "s8_4", "s8_5"),
                ("s8_6", "s8_7", "s8_8", "s8_9"),
                "s8_note"
            )
        }),
        ("ส่วนที่ 9: Operative note", {
            "classes": ("collapse",),
            "fields": (
                ("s9_1", "s9_2", "s9_3", "s9_4", "s9_5"),
                ("s9_6", "s9_7", "s9_8", "s9_9"),
                "s9_note"
            )
        }),
        ("ส่วนที่ 10: Labour record", {
            "classes": ("collapse",),
            "fields": (
                ("s10_1", "s10_2", "s10_3", "s10_4", "s10_5"),
                ("s10_6", "s10_7", "s10_8", "s10_9"),
                "s10_note"
            )
        }),
        ("ส่วนที่ 11: Rehabilitation record", {
            "classes": ("collapse",),
            "fields": (
                ("s11_1", "s11_2", "s11_3", "s11_4", "s11_5"),
                ("s11_6", "s11_7", "s11_8", "s11_9"),
                "s11_note"
            )
        }),
        ("ส่วนที่ 12: Nurses' note", {
            "classes": ("collapse",),
            "fields": (
                ("s12_1", "s12_2", "s12_3", "s12_4", "s12_5"),
                ("s12_6", "s12_7", "s12_8", "s12_9"),
                "bonus_s12", "s12_note"
            )
        }),
        ("สรุปผลคะแนนและระบบ", {
            "fields": (
                ("total_yes", "total_counted", "percent"),
                ("created_by", "created_at")
            )
        }),
    )

    actions = ["export_as_csv"]

    def percent_badge(self, obj):
        """ ทำสีเปอร์เซ็นต์หน้า List ถ้า >= 80% ให้เป็นสีเขียว ถ้าน้อยกว่าเป็นสีแดง """
        if obj.percent and obj.percent >= 80:
            color = "#198754"
        else:
            color = "#dc3545"
            
        pct_str = f"{obj.percent or 0:.2f}"
        
        return format_html('<span style="color: {}; font-weight: bold;">{}%</span>', color, pct_str)
    percent_badge.short_description = "ร้อยละ (%)"

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def export_as_csv(self, request, queryset):
        """ ส่งออก CSV ข้อมูล IPD """
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response.write('\ufeff'.encode('utf8'))
        response["Content-Disposition"] = 'attachment; filename="ipd_scores.csv"'
        writer = csv.writer(response)

        writer.writerow(["ID", "HCODE", "HNAME", "HN", "AN", "Date Admitted", "Date Discharged", "Total Yes", "Total Counted", "Percent", "Created At"])
        for o in queryset:
            writer.writerow([
                o.id, o.hcode, o.hname, o.hn, o.an, o.date_admitted, o.date_discharged, o.total_yes, o.total_counted, o.percent, o.created_at
            ])
        return response
    export_as_csv.short_description = "Export เลือกเป็น CSV"

@admin.register(OPDScore)
class OPDScoreAdmin(admin.ModelAdmin):
    # คอลัมน์ในหน้า list
    list_display = (
        "id", "hcode", "hname", "hn", "pid",
        "is_general", "is_chronic","is_psychiatric",
        "diagnosis_short",
        "first_visit_date", "visit_date_start", "visit_date_end",
        "total_score", "total_possible", "percent","review_status",
        "created_by", "created_at",
    )
    list_display_links = ("id", "hcode", "hname")
    ordering = ("-created_at",)
    list_per_page = 50

    # ค้นหา/กรอง
    search_fields = ("hcode", "hname", "hn", "pid", "diagnosis")
    list_filter = (
        "is_general", "is_chronic", "is_psychiatric", "created_by",
        ("first_visit_date", admin.DateFieldListFilter),
        ("visit_date_start", admin.DateFieldListFilter),
        ("visit_date_end", admin.DateFieldListFilter),
        ("created_at", admin.DateFieldListFilter),
    )

    # ฟิลด์ในหน้าแก้ไข
    readonly_fields = ("total_score", "total_possible", "percent", "created_by", "created_at", "data_pretty")
    fieldsets = (
        ("ข้อมูลหน่วยบริการ/ผู้ป่วย", {
            "fields": (("hcode", "hname"), ("hn", "pid"), ("is_general", "is_chronic", "is_psychiatric"), "diagnosis","review_status")
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
            "is_general", "is_chronic", "is_psychiatric", "diagnosis","review_status",
            "audit_period", "first_visit_date", "visit_date_start", "visit_date_end",
            "total_score", "total_possible", "percent",
            "created_by", "created_at",
        ])
        for o in queryset:
            writer.writerow([
                o.id, o.hcode, o.hname, o.hn, o.pid,
                o.is_general, o.is_chronic, o.is_psychiatric, (o.diagnosis or ""),
                (o.audit_period or ""), o.first_visit_date, o.visit_date_start, o.visit_date_end,
                o.total_score, o.total_possible, o.percent,
                getattr(o.created_by, "username", ""), o.created_at,
            ])
        return response
    export_as_csv.short_description = "Export เลือกเป็น CSV"