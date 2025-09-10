from django.contrib import admin
from .models import Document,PatientScore

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