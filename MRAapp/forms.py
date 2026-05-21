from django import forms
from .models import Document
from .models import PatientScore, SCORE_CHOICES
from .models import OPDScore

BONUS_CHOICES = [
    (0, '0 '),
    (1, '+1 '),
    (-1, '-1 '),
]

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
from .models import PatientScore, SCORE_CHOICES, BONUS_CHOICES

class PatientScoreForm(forms.ModelForm):
    class Meta:
        model = PatientScore
        # --- จุดที่ 1: เพิ่ม field ใหม่เข้าไปใน list ---
        fields = (
            [
                "title","hcode","hname","hn","an",
                "date_admitted","date_discharged",
                "max_score","final_score","note","bonus_s1","bonus_s12",
                "finding_sorting_issue", 
                "finding_no_id_issue", 
                "overall_finding", 
                "certain_issue_note"
            ]
            + [f"s{i}_{j}" for i in range(1,13) for j in range(1,10)]
            + [f"s{i}_note" for i in range(1,13)]
        )
        
        # --- จุดที่ 2: กำหนด Widget ให้เป็น Checkbox และ Radio ---
        widgets = {
            "title": forms.TextInput(attrs={"class":"form-control","placeholder":"หัวข้อ ไม่จำเป็นต้องใส่ก็ได้"}),
            "hcode": forms.TextInput(attrs={"class":"form-control","placeholder":"Hcode"}),
            "hname": forms.TextInput(attrs={"class":"form-control","placeholder":"Hname"}),
            
            "hn": forms.TextInput(attrs={"class":"form-control", "placeholder":"HN"}), 
            "an": forms.TextInput(attrs={"class":"form-control", "placeholder":"AN"}),
            
            "date_admitted": forms.DateInput(attrs={"type":"date","class":"form-control"}),
            "date_discharged": forms.DateInput(attrs={"type":"date","class":"form-control"}),
            "note": forms.TextInput(attrs={"class":"form-control"}),
            "bonus_s1": forms.Select(
                choices=BONUS_CHOICES, 
                attrs={"class":"form-select shadow-sm", "style":"border-left: 5px solid #458fff;"}
            ),
            "bonus_s12": forms.Select(
                choices=BONUS_CHOICES, 
                attrs={"class":"form-select shadow-sm", "style":"border-left: 5px solid #458fff;"}
            ),
            
            "finding_sorting_issue": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "finding_no_id_issue": forms.CheckboxInput(attrs={"class": "form-check-input"}),

            "overall_finding": forms.RadioSelect(attrs={"class": "list-unstyled"}), 

            "certain_issue_note": forms.TextInput(attrs={"class": "form-control", "placeholder": "ระบุรายละเอียด..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_choices = self.fields['overall_finding'].choices
        self.fields['overall_finding'].choices = [
            c for c in current_choices if c[0] != ''
        ]
        self.fields['overall_finding'].initial = None
    

        for i in range(1, 13):
            for j in range(1, 10):
                self.fields[f"s{i}_{j}"].widget = forms.Select(
                    choices=SCORE_CHOICES, attrs={"class":"form-select"}
                )
        
        for i in range(1, 13):
            self.fields[f"s{i}_note"].widget = forms.TextInput(
                attrs={"class":"form-control form-control-sm","placeholder":"หมายเหตุหัวข้อ (ถ้ามี)"}
            )
            
        self.fields["finding_sorting_issue"].required = False
        self.fields["finding_no_id_issue"].required = False
        self.fields["certain_issue_note"].required = False

# ******************************************************* OPD บันทึกคะแนน *************************************************************************

REVIEW_STATUS_CHOICES = [
    ('inadequate', 'Documenttation inadequate for meaningful review (ข้อมูลไม่เพียงพอสำหรับการทบทวน)'),
    ('no_issue', 'No significant medical recode issue identified (ไม่มีปัญหาสำคัญจากการทบทวน)'),
    ('has_issue', 'Certain issue in question specify (มีปัญหาจากการทบทวนที่ต้องค้นต่อ ระบุ)'),
]

class OPDScoreForm(forms.ModelForm):
    class Meta:
        model = OPDScore
        fields = [
            "hcode", "hname", "hn", "pid",
            "is_general", "is_chronic", "is_psychiatric",
            "diagnosis",
            "audit_period",
            "visit_date_start", "visit_date_end", "first_visit_date",
            "review_status",
            "certain_issue_note",
            "note",
        ]
        widgets = {
            "hcode": forms.TextInput(attrs={"class": "form-control"}),
            "hname": forms.TextInput(attrs={"class": "form-control"}),
            "hn": forms.TextInput(attrs={"class": "form-control"}),
            "pid": forms.TextInput(attrs={"class": "form-control"}),

            "is_general": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_chronic": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_psychiatric": forms.CheckboxInput(attrs={"class": "form-check-input"}),

            "diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "audit_period": forms.TextInput(attrs={"type": "month", "class": "form-control"}),

            "visit_date_start": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "visit_date_end": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "first_visit_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),

            "review_status": forms.RadioSelect(
                choices=REVIEW_STATUS_CHOICES,
                attrs={"class": "form-check-input"}
            ),
            
            "certain_issue_note": forms.TextInput(attrs={
                "class": "form-control form-control-sm", 
                "placeholder": "ระบุรายละเอียด...",
                "id": "id_certain_issue_note"
            }),

            "note": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "ระบุรายละเอียดเพิ่มเติม..."}),
        }


    def __init__(self, *args, **kwargs):
        super(OPDScoreForm, self).__init__(*args, **kwargs)
        current_choices = self.fields['review_status'].choices
        self.fields['review_status'].choices = [c for c in current_choices if c[0]]