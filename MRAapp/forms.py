from django import forms
from .models import Document
from .models import PatientScore, SCORE_CHOICES

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["doc_date", "title", "file", "external_url", "is_active"]
        widgets = {
            "doc_date": forms.DateInput(attrs={"type": "date", "class": "border p-2 rounded"}),
            "title": forms.TextInput(attrs={"class": "border p-2 rounded w-full"}),
            "external_url": forms.URLInput(attrs={"class": "border p-2 rounded w-full", "placeholder": "https://... (ถ้าไม่มีไฟล์)"}),
            "is_active": forms.CheckboxInput(attrs={"class": "mr-2"}),
        }

    def clean(self):
        cleaned = super().clean()
        file = cleaned.get("file")
        url = cleaned.get("external_url")
        if not file and not url:
            raise forms.ValidationError("กรุณาอัปโหลดไฟล์ หรือใส่ลิงก์อย่างน้อยหนึ่งอย่าง")
        return cleaned
# ********************************************************************************************************************************************************
# ********************************************************************************************************************************************************
# ********************************************************************************************************************************************************

from django import forms
from .models import PatientScore, SCORE_CHOICES

class PatientScoreForm(forms.ModelForm):
    class Meta:
        model = PatientScore
        fields = (
            [
                "title","hcode","hname","hn","an",
                "date_admitted","date_discharged",
                "max_score","final_score","note",   # note รวมทั้งฟอร์ม (ของเดิม)
            ]
            + [f"s{i}_{j}" for i in range(1,13) for j in range(1,10)]   # คะแนน 12×9
            + [f"s{i}_note" for i in range(1,13)]                        # ✅ หมายเหตุหัวข้อ 12 ช่อง
        )
        widgets = {
            "title": forms.TextInput(attrs={"class":"form-control","placeholder":"หัวข้อ ไม่จำเป็นต้องใส่ก็ได้"}),
            "hcode": forms.TextInput(attrs={"class":"form-control","placeholder":"Hcode"}),
            "hname": forms.TextInput(attrs={"class":"form-control","placeholder":"Hname"}),
            "hn": forms.TextInput(attrs={"class":"form-control"}),"placeholder":"HN",
            "an": forms.TextInput(attrs={"class":"form-control"}),"placeholder":"AN",
            "date_admitted": forms.DateInput(attrs={"type":"date","class":"form-control"}),
            "date_discharged": forms.DateInput(attrs={"type":"date","class":"form-control"}),
            "note": forms.TextInput(attrs={"class":"form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].required = False
        for i in range(1, 13):
            for j in range(1, 10):
                self.fields[f"s{i}_{j}"].widget = forms.Select(
                    choices=SCORE_CHOICES, attrs={"class":"form-select"}
                )
        # ตั้ง widget ของหมายเหตุหัวข้อให้เป็นกล่องเล็ก
        for i in range(1, 13):
            self.fields[f"s{i}_note"].widget = forms.TextInput(
                attrs={"class":"form-control form-control-sm","placeholder":"หมายเหตุหัวข้อ (ถ้ามี)"}
            )

