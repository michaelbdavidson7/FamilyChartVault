from django.contrib import admin
from .models import (
    Allergy,
    CareTeam,
    CareTeamParticipant,
    Condition,
    Encounter,
    Immunization,
    Location,
    Medication,
    Observation,
    Organization,
    Practitioner,
)


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "name", "clinical_status", "onset_date")
    list_display_links = ("name",)
    search_fields = ("name", "icd10_code", "snomed_code")
    list_filter = ("patient", "clinical_status")
    autocomplete_fields = ["patient"]
    ordering = ("-onset_date",)


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "substance", "category", "severity")
    list_display_links = ("substance",)
    search_fields = ("substance", "rxnorm_code", "snomed_code")
    list_filter = ("patient", "category", "severity", "criticality")
    autocomplete_fields = ["patient"]


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "name", "status", "indication", "start_date")
    list_display_links = ("name",)
    search_fields = ("name", "rxnorm_code", "prescriber")
    list_filter = ("patient", "status")
    ordering = ("-start_date",)
    autocomplete_fields = ["patient"]


@admin.register(Immunization)
class ImmunizationAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "vaccine_name", "occurrence_date")
    list_display_links = ("vaccine_name",)
    search_fields = ("vaccine_name", "cvx_code")
    list_filter = ("patient",)
    ordering = ("-occurrence_date",)
    autocomplete_fields = ["patient"]


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "name", "category", "effective_datetime")
    list_display_links = ("name",)
    search_fields = ("name", "loinc_code")
    list_filter = ("patient", "category")
    ordering = ("-effective_datetime",)
    autocomplete_fields = ["patient"]


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "encounter_type", "provider_name", "facility_name", "display_start_time")
    list_display_links = ("encounter_type",)
    search_fields = ("provider_name", "facility_name", "reason")
    list_filter = ("patient", "status")
    ordering = ("-start_time",)
    autocomplete_fields = ["patient"]

    @admin.display(description="Start time", ordering="start_time")
    def display_start_time(self, obj):
        if not obj.start_time:
            return "-"
        if obj.start_time.hour == 0 and obj.start_time.minute == 0 and obj.start_time.second == 0:
            return obj.start_time.date()
        return obj.start_time


class CareTeamParticipantInline(admin.StackedInline):
    model = CareTeamParticipant
    extra = 0
    fieldsets = (
        (None, {
            "fields": (
                "role",
                "practitioner",
                "organization",
                "location",
            ),
        }),
        ("Source details", {
            "fields": (
                "member_display",
                "member_reference",
                "on_behalf_of_display",
                "on_behalf_of_reference",
                "start_date",
                "end_date",
            ),
            "classes": ("collapse",),
        }),
    )
    autocomplete_fields = ["practitioner", "organization", "location"]


@admin.register(CareTeam)
class CareTeamAdmin(admin.ModelAdmin):
    inlines = (CareTeamParticipantInline,)
    list_display = ("id", "patient", "name", "status", "category", "start_date")
    list_display_links = ("name",)
    search_fields = ("name", "category", "participants", "reason")
    list_filter = ("patient", "status", "category")
    ordering = ("patient", "name")
    autocomplete_fields = ["patient", "managing_organizations"]
    filter_horizontal = ("managing_organizations",)


@admin.register(Practitioner)
class PractitionerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "qualification", "phone", "email", "active", "care_team_count")
    list_display_links = ("name",)
    search_fields = ("name", "npi", "qualification", "phone", "email")
    list_filter = ("active", "qualification")
    ordering = ("name",)

    @admin.display(description="Care teams")
    def care_team_count(self, obj):
        return obj.care_team_participations.count()


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "organization_type", "phone", "email", "active", "care_team_count")
    list_display_links = ("name",)
    search_fields = ("name", "organization_type", "phone", "email")
    list_filter = ("active", "organization_type")
    ordering = ("name",)

    @admin.display(description="Care teams")
    def care_team_count(self, obj):
        participation_count = obj.care_team_participations.count()
        managing_count = obj.managed_care_teams.count()
        return participation_count + managing_count


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "mode", "location_type", "managing_organization", "care_team_count")
    list_display_links = ("name",)
    search_fields = ("name", "location_type", "managing_organization", "phone", "email")
    list_filter = ("status", "mode", "location_type")
    ordering = ("name",)

    @admin.display(description="Care teams")
    def care_team_count(self, obj):
        return obj.care_team_participations.count()
