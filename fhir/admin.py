from django.contrib import admin
from .models import FHIRResourceSnapshot, FHIRLink


@admin.register(FHIRResourceSnapshot)
class FHIRResourceSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "resource_label",
        "source",
        "import_status",
        "is_valid",
        "created_at",
    )
    list_display_links = ("resource_label",)

    search_fields = (
        "resource_type",
        "resource_id",
    )

    list_filter = (
        "patient",
        "resource_type",
        "import_status",
        "source",
        "is_valid",
    )

    readonly_fields = (
        "created_at",
        "import_status",
        "raw_json",
        "validation_errors",
    )

    @admin.display(description="FHIR resource", ordering="resource_type")
    def resource_label(self, obj):
        return str(obj)


@admin.register(FHIRLink)
class FHIRLinkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "resource_label",
        "django_model",
        "django_object_id",
        "last_synced_at",
    )
    list_display_links = ("resource_label",)

    search_fields = (
        "resource_type",
        "resource_id",
        "django_model",
    )

    list_filter = (
        "resource_type",
        "direction",
    )

    @admin.display(description="FHIR resource", ordering="resource_type")
    def resource_label(self, obj):
        return f"{obj.resource_type}/{obj.resource_id}".rstrip("/") or "FHIR resource"
