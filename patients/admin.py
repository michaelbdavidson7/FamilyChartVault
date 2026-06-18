from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.html import format_html, format_html_join

from clinical.models import Allergy, CareTeam, Condition, Encounter, Immunization, Medication, Observation
from documents.models import ClinicalDocument

from .models import PatientProfile, RecoveryCredential


User = get_user_model()


def human_date(value):
    if not value:
        return "-"
    return date_format(value, "M. j, Y")


def human_datetime(value):
    if not value:
        return "-"
    local_value = timezone.localtime(value) if timezone.is_aware(value) else value
    if local_value.hour == 0 and local_value.minute == 0 and local_value.second == 0:
        return human_date(local_value.date())
    return date_format(local_value, "M. j, Y, g:i a")


class ReadOnlyPatientRecordInline(admin.TabularInline):
    extra = 0
    max_num = 0
    can_delete = False
    show_change_link = False
    classes = ("patient-record-inline",)
    readonly_fields = ("open_record",)

    @admin.display(description="")
    def open_record(self, obj):
        if not obj or not obj.pk:
            return ""

        url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=[obj.pk],
        )
        return format_html('<a class="btn btn-primary btn-sm" href="{}">Open</a>', url)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ConditionInline(ReadOnlyPatientRecordInline):
    model = Condition
    fields = (
        "name",
        "clinical_status",
        "onset",
        "abatement",
        "icd10_code",
        "snomed_code",
        "open_record",
    )
    readonly_fields = fields

    @admin.display(description="Onset")
    def onset(self, obj):
        return human_date(obj.onset_date)

    @admin.display(description="Abatement")
    def abatement(self, obj):
        return human_date(obj.abatement_date)


class AllergyInline(ReadOnlyPatientRecordInline):
    model = Allergy
    fields = (
        "substance",
        "category",
        "criticality",
        "reaction",
        "severity",
        "open_record",
    )
    readonly_fields = fields


class MedicationInline(ReadOnlyPatientRecordInline):
    model = Medication
    fields = (
        "name",
        "status",
        "dosage_text",
        "frequency",
        "start",
        "end",
        "open_record",
    )
    readonly_fields = fields

    @admin.display(description="Start")
    def start(self, obj):
        return human_date(obj.start_date)

    @admin.display(description="End")
    def end(self, obj):
        return human_date(obj.end_date)


class ImmunizationInline(ReadOnlyPatientRecordInline):
    model = Immunization
    fields = (
        "vaccine_name",
        "occurrence",
        "lot_number",
        "manufacturer",
        "open_record",
    )
    readonly_fields = fields

    @admin.display(description="Occurrence")
    def occurrence(self, obj):
        return human_date(obj.occurrence_date)


class ObservationInline(ReadOnlyPatientRecordInline):
    model = Observation
    fields = (
        "name",
        "category",
        "display_value",
        "effective",
        "open_record",
    )
    readonly_fields = fields

    @admin.display(description="Value")
    def display_value(self, obj):
        if obj.value_quantity is not None:
            return f"{obj.value_quantity:g} {obj.unit}".strip()
        return obj.value_string or "-"

    @admin.display(description="Effective")
    def effective(self, obj):
        return human_datetime(obj.effective_datetime)

class EncounterInline(ReadOnlyPatientRecordInline):
    model = Encounter
    fields = (
        "encounter_type",
        "status",
        "provider_name",
        "facility_name",
        "start",
        "open_record",
    )
    readonly_fields = fields

    @admin.display(description="Start")
    def start(self, obj):
        return human_datetime(obj.start_time)


class CareTeamInline(ReadOnlyPatientRecordInline):
    model = CareTeam
    fields = (
        "name",
        "status",
        "category",
        "start",
        "end",
        "open_record",
    )
    readonly_fields = fields

    @admin.display(description="Start")
    def start(self, obj):
        return human_date(obj.start_date)

    @admin.display(description="End")
    def end(self, obj):
        return human_date(obj.end_date)


class ClinicalDocumentInline(ReadOnlyPatientRecordInline):
    model = ClinicalDocument
    fields = (
        "title",
        "document_type",
        "source_name",
        "source",
        "open_record",
    )
    readonly_fields = fields

    @admin.display(description="Source date")
    def source(self, obj):
        return human_date(obj.source_date)


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    inlines = (
        ConditionInline,
        AllergyInline,
        MedicationInline,
        ImmunizationInline,
        CareTeamInline,
        ClinicalDocumentInline,
    )


    list_display = (
        "id",
        "full_name",
        "date_of_birth",
        "phone",
        "email",
        "updated_at",
    )
    list_display_links = (
        "full_name",
    )

    search_fields = (
        "first_name",
        "last_name",
        "phone",
        "email",
    )

    list_filter = (
        'sex_at_birth',
        "organ_donor",
        "created_at",
    )

    readonly_fields = (
        "patient_overview",
        "latest_observations",
        "latest_visits",
        "created",
        "updated",
    )

    fieldsets = (
        ("Patient Overview", {
            "fields": ("patient_overview",)
        }),
        ("Basic Info", {
            "fields": (
                "first_name",
                "last_name",
                "date_of_birth",
                'sex_at_birth',
                "gender_identity",
            )
        }),
        ("Contact", {
            "fields": (
                "phone",
                "email",
            )
        }),
        ("Address", {
            "fields": (
                "address_line_1",
                "address_line_2",
                "city",
                "state",
                "postal_code",
                "country",
            )
        }),
        ("Medical Info", {
            "fields": (
                "blood_type",
                "organ_donor",
            )
        }),
        ("Emergency Contact", {
            "fields": (
                "emergency_contact_name",
                "emergency_contact_phone",
                "emergency_contact_relationship",
            )
        }),
        ("Recent Vitals & Labs", {
            "fields": ("latest_observations",)
        }),
        ("Recent Visits & Actions", {
            "fields": ("latest_visits",)
        }),
        ("Meta", {
            "fields": ("created", "updated")
        }),
    )

    @admin.display(description="")
    def patient_overview(self, obj):
        if not obj or not obj.pk:
            return "Save this patient to see their chart overview."

        age = self._age(obj)
        demographics = [
            ("Date of birth", self._display_date(obj.date_of_birth)),
            ("Age", age if age is not None else "-"),
            ("Sex at birth", obj.sex_at_birth or "-"),
            ("Phone", obj.phone or "-"),
            ("Email", obj.email or "-"),
            ("Emergency contact", obj.emergency_contact_name or "-"),
        ]
        stats = [
            self._overview_stat_card(obj, "Conditions", "clinical_condition", obj.conditions.count()),
            self._overview_stat_card(obj, "Allergies", "clinical_allergy", obj.allergies.count()),
            self._overview_stat_card(obj, "Medications", "clinical_medication", obj.medications.count()),
            self._overview_stat_card(obj, "Immunizations", "clinical_immunization", obj.immunizations.count()),
            self._overview_stat_card(obj, "Vitals & Labs", "clinical_observation", obj.observations.count()),
            self._overview_stat_card(obj, "Visits & Actions", "clinical_encounter", obj.encounters.count()),
            self._overview_stat_card(obj, "Care Team", "clinical_careteam", obj.care_teams.count()),
            self._overview_stat_card(obj, "Documents", "documents_clinicaldocument", obj.documents.count()),
        ]

        return format_html(
            '<div class="patient-overview">'
            '<div class="patient-overview-main">'
            '<h3>{}</h3>'
            '<dl>{}</dl>'
            '</div>'
            '<div class="patient-overview-stats">{}</div>'
            '</div>',
            self._patient_name(obj),
            format_html_join(
                "",
                '<div><dt>{}</dt><dd>{}</dd></div>',
                demographics,
            ),
            format_html_join("", "{}", ((stat,) for stat in stats)),
        )

    @admin.display(description="")
    def latest_observations(self, obj):
        if not obj or not obj.pk:
            return "Save this patient before reviewing vitals and labs."

        observations = obj.observations.order_by("-effective_datetime", "-id")[:8]
        if not observations:
            add_url = reverse("admin:clinical_observation_add")
            return format_html(
                '<div class="patient-empty-state">No vitals or labs yet. <a class="btn btn-primary btn-sm" href="{}?patient={}">Add result</a></div>',
                add_url,
                obj.pk,
            )

        rows = []
        for observation in observations:
            value = self._observation_value(observation)
            rows.append((
                observation.name,
                observation.get_category_display(),
                value,
                self._display_datetime(observation.effective_datetime),
                reverse("admin:clinical_observation_change", args=[observation.pk]),
            ))

        list_url = reverse("admin:clinical_observation_changelist")
        add_url = reverse("admin:clinical_observation_add")
        return format_html(
            '<div class="patient-compact-table">'
            '<table><thead><tr><th>Name</th><th>Category</th><th>Value</th><th>Date</th><th></th></tr></thead>'
            '<tbody>{}</tbody></table>'
            '<div class="patient-table-actions">'
            '<a class="btn btn-primary btn-sm" href="{}?patient__id__exact={}">Open all</a>'
            '<a class="btn btn-outline-primary btn-sm" href="{}?patient={}">Add result</a>'
            '</div></div>',
            format_html_join(
                "",
                '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td><a class="btn btn-primary btn-sm" href="{}">Open</a></td></tr>',
                rows,
            ),
            list_url,
            obj.pk,
            add_url,
            obj.pk,
        )

    @admin.display(description="")
    def latest_visits(self, obj):
        if not obj or not obj.pk:
            return "Save this patient before reviewing visits and actions."

        visits = obj.encounters.order_by("-start_time", "-id")[:8]
        if not visits:
            add_url = reverse("admin:clinical_encounter_add")
            return format_html(
                '<div class="patient-empty-state">No visits or actions yet. <a class="btn btn-primary btn-sm" href="{}?patient={}">Add visit/action</a></div>',
                add_url,
                obj.pk,
            )

        rows = []
        for visit in visits:
            rows.append((
                visit.encounter_type or "-",
                visit.status or "-",
                visit.provider_name or "-",
                visit.facility_name or "-",
                self._display_visit_datetime(visit.start_time),
                reverse("admin:clinical_encounter_change", args=[visit.pk]),
            ))

        list_url = reverse("admin:clinical_encounter_changelist")
        add_url = reverse("admin:clinical_encounter_add")
        return format_html(
            '<div class="patient-compact-table">'
            '<table><thead><tr><th>Visit / Action</th><th>Status</th><th>Provider</th><th>Facility</th><th>Date</th><th></th></tr></thead>'
            '<tbody>{}</tbody></table>'
            '<div class="patient-table-actions">'
            '<a class="btn btn-primary btn-sm" href="{}?patient__id__exact={}">Open all</a>'
            '<a class="btn btn-outline-primary btn-sm" href="{}?patient={}">Add visit/action</a>'
            '</div></div>',
            format_html_join(
                "",
                '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td><a class="btn btn-primary btn-sm" href="{}">Open</a></td></tr>',
                rows,
            ),
            list_url,
            obj.pk,
            add_url,
            obj.pk,
        )

    @admin.display(description="Patient", ordering="last_name")
    def full_name(self, obj):
        name = self._patient_name(obj)
        return format_html("<strong>{}</strong>", name or f"Patient #{obj.pk}")

    def _patient_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def _age(self, obj):
        if not obj.date_of_birth:
            return None
        today = timezone.localdate()
        return today.year - obj.date_of_birth.year - (
            (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
        )

    def _observation_value(self, observation):
        if observation.value_quantity is not None:
            return f"{observation.value_quantity:g} {observation.unit}".strip()
        return observation.value_string or "-"

    def _display_visit_datetime(self, value):
        if not value:
            return "-"
        if value.hour == 0 and value.minute == 0 and value.second == 0:
            return self._display_date(value.date())
        return self._display_datetime(value)

    def _display_date(self, value):
        return human_date(value)

    def _display_datetime(self, value):
        return human_datetime(value)

    @admin.display(description="Created")
    def created(self, obj):
        return human_datetime(obj.created_at)

    @admin.display(description="Updated")
    def updated(self, obj):
        return human_datetime(obj.updated_at)

    def _overview_stat_card(self, obj, label, admin_model_name, count):
        changelist_url = reverse(f"admin:{admin_model_name}_changelist")
        add_url = reverse(f"admin:{admin_model_name}_add")
        query = f"patient__id__exact={obj.pk}"
        return format_html(
            '<div class="patient-stat">'
            '<a class="patient-stat-main" href="{}?{}"><strong>{}</strong><span>{}</span></a>'
            '<a class="patient-stat-add" href="{}?patient={}">Add</a>'
            '</div>',
            changelist_url,
            query,
            count,
            label,
            add_url,
            obj.pk,
        )

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    readonly_fields = (*DjangoUserAdmin.readonly_fields, "recovery_key_status_detail")

    fieldsets = (
        *DjangoUserAdmin.fieldsets,
        (
            "Recovery key",
            {
                "fields": ("recovery_key_status_detail",),
                "description": (
                    "Recovery keys are not fully enabled in first-run setup yet. "
                    "The raw recovery key is never stored and cannot be viewed here."
                ),
            },
        ),
    )

    def get_list_display(self, request):
        base_list_display = list(super().get_list_display(request))

        if "recovery_key_status" not in base_list_display:
            base_list_display.append("recovery_key_status")

        return base_list_display

    @admin.display(description="Recovery key", boolean=True)
    def recovery_key_status(self, obj):
        return hasattr(obj, "recovery_credential")

    @admin.display(description="Recovery key status")
    def recovery_key_status_detail(self, obj):
        if not obj or not obj.pk:
            return "Save this user before configuring recovery."

        if not hasattr(obj, "recovery_credential"):
            return format_html(
                'No recovery key has been created for this user yet. <a href="{}">Generate recovery key</a>.',
                reverse("admin_recovery_key_generate"),
            )

        credential = obj.recovery_credential

        if credential.last_used_at:
            return format_html(
                'Recovery key is configured. Last used: {}. The raw key cannot be viewed here. <a href="{}">Rotate recovery key</a>.',
                credential.last_used_at,
                reverse("admin_recovery_key_generate"),
            )

        return format_html(
            'Recovery key is configured. Created: {}. The raw key cannot be viewed here. <a href="{}">Rotate recovery key</a>.',
            credential.created_at,
            reverse("admin_recovery_key_generate"),
        )


@admin.register(RecoveryCredential)
class RecoveryCredentialAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "hash_preview",
        "created_at",
        "last_used_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "recovery_key_hash",
    )
    readonly_fields = (
        "user",
        "recovery_key_hash",
        "created_at",
        "last_used_at",
    )
    fields = (
        "user",
        "recovery_key_hash",
        "created_at",
        "last_used_at",
    )

    @admin.display(description="Stored hash")
    def hash_preview(self, obj):
        if not obj.recovery_key_hash:
            return "-"

        return f"{obj.recovery_key_hash[:24]}..."

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
