from django.contrib import admin
from .models import ClinicalDocument


@admin.register(ClinicalDocument)
class ClinicalDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "title",
        "document_type",
        "encounter",
        "custodian",
        "source_name",
        "source_date",
    )
    list_display_links = ("title",)
    ordering = ("-source_date",)

    search_fields = (
        "title",
        "document_type",
        "source_name",
    )

    list_filter = (
        "patient",
        "document_type",
        "custodian",
        "source_date",
    )

    autocomplete_fields = ["patient", "encounter", "custodian"]
    filter_horizontal = ("authors", "related_documents")
