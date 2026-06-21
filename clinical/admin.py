from django import forms
from django.contrib import admin
from django.db import models
from .models import (
    Account,
    ActivityDefinition,
    AdverseEvent,
    Allergy,
    CarePlan,
    CareTeam,
    CareTeamParticipant,
    ClinicalImpression,
    ClinicalImpressionFinding,
    CodeSystem,
    ConceptMap,
    EventDefinition,
    ExampleScenario,
    Condition,
    DetectedIssue,
    DeviceDefinition,
    Device,
    DeviceRequest,
    DeviceUseStatement,
    DiagnosticReport,
    Encounter,
    EpisodeOfCare,
    FamilyMemberHistory,
    FamilyMemberHistoryCondition,
    FHIRGroup,
    FHIRGroupMember,
    FHIRList,
    GraphDefinition,
    GuidanceResponse,
    Goal,
    ImagingStudy,
    Immunization,
    ImmunizationEvaluation,
    ImmunizationRecommendation,
    ImplementationGuide,
    Location,
    Media,
    MessageDefinition,
    MedicationAdministration,
    MedicationCatalog,
    MedicationDispense,
    MedicationKnowledge,
    Medication,
    Library,
    Measure,
    MeasureReport,
    MolecularSequence,
    NutritionOrder,
    NamingSystem,
    Observation,
    ObservationDefinition,
    OperationDefinition,
    Organization,
    PaymentNotice,
    PaymentReconciliation,
    PlanDefinition,
    Person,
    PersonLink,
    Practitioner,
    PractitionerRole,
    Procedure,
    ProcedurePerformer,
    RelatedPerson,
    ResearchStudy,
    ResearchSubject,
    RiskAssessment,
    ServiceRequest,
    Specimen,
    SpecimenDefinition,
    BodyStructure,
    Communication,
    CommunicationRequest,
    Consent,
    Coverage,
    Appointment,
    AppointmentResponse,
    AuditEvent,
    CapabilityStatement,
    ChargeItem,
    CompartmentDefinition,
    Claim,
    ClaimResponse,
    CoverageEligibilityRequest,
    CoverageEligibilityResponse,
    BinaryResource,
    Composition,
    DeviceMetric,
    DocumentManifest,
    EnrollmentRequest,
    EnrollmentResponse,
    Invoice,
    Endpoint,
    ExplanationOfBenefit,
    Flag,
    HealthcareService,
    InsurancePlan,
    Questionnaire,
    QuestionnaireResponse,
    RequestGroup,
    Schedule,
    SearchParameter,
    Slot,
    Substance,
    SupplyDelivery,
    SupplyRequest,
    StructureDefinition,
    StructureMap,
    Task,
    ValueSet,
    TestScript,
    TestReport,
    TerminologyCapabilities,
    VisionPrescription,
    OrganizationAffiliation,
    Provenance,
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


@admin.register(MedicationCatalog)
class MedicationCatalogAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "form", "manufacturer", "batch_lot_number")
    list_display_links = ("name",)
    search_fields = ("name", "code", "form", "ingredient_summary", "batch_lot_number")
    list_filter = ("status", "form", "manufacturer")
    ordering = ("name",)
    autocomplete_fields = ["manufacturer"]


@admin.register(MedicationAdministration)
class MedicationAdministrationAdmin(admin.ModelAdmin):
    list_display = ("id", "administration_label", "patient", "status", "effective_start", "dose_value", "dose_unit")
    list_display_links = ("administration_label",)
    search_fields = ("medication_text", "dosage_text", "route", "notes")
    list_filter = ("patient", "status", "route")
    ordering = ("-effective_start",)
    autocomplete_fields = ["patient", "encounter", "medication", "medication_catalog", "performer_practitioner", "performer_role"]
    filter_horizontal = ("service_requests", "reason_conditions")

    @admin.display(description="Medication administration", ordering="medication_text")
    def administration_label(self, obj):
        return obj.medication_text or str(obj.medication or obj.medication_catalog or f"Medication Administration #{obj.pk}")


@admin.register(MedicationDispense)
class MedicationDispenseAdmin(admin.ModelAdmin):
    list_display = ("id", "dispense_label", "patient", "status", "when_handed_over", "quantity", "days_supply")
    list_display_links = ("dispense_label",)
    search_fields = ("medication_text", "quantity", "days_supply", "dosage_instruction", "notes")
    list_filter = ("patient", "status")
    ordering = ("-when_handed_over", "-when_prepared")
    autocomplete_fields = ["patient", "medication", "medication_catalog", "performer_practitioner", "performer_organization"]
    filter_horizontal = ("authorizing_requests",)

    @admin.display(description="Medication dispense", ordering="medication_text")
    def dispense_label(self, obj):
        return obj.medication_text or str(obj.medication or obj.medication_catalog or f"Medication Dispense #{obj.pk}")


@admin.register(Immunization)
class ImmunizationAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "vaccine_name", "occurrence_date")
    list_display_links = ("vaccine_name",)
    search_fields = ("vaccine_name", "cvx_code")
    list_filter = ("patient",)
    ordering = ("-occurrence_date",)
    autocomplete_fields = ["patient"]


@admin.register(ImmunizationRecommendation)
class ImmunizationRecommendationAdmin(admin.ModelAdmin):
    list_display = ("id", "recommendation_label", "patient", "forecast_status", "target_disease", "date")
    list_display_links = ("recommendation_label",)
    search_fields = ("vaccine_code", "target_disease", "forecast_status", "forecast_reason", "recommendation_summary")
    list_filter = ("patient", "forecast_status", "target_disease", "authority")
    ordering = ("-date",)
    autocomplete_fields = ["patient", "authority"]
    filter_horizontal = ("supporting_immunizations", "supporting_observations", "supporting_diagnostic_reports")

    @admin.display(description="Recommendation", ordering="vaccine_code")
    def recommendation_label(self, obj):
        return obj.vaccine_code or obj.target_disease or f"Immunization Recommendation #{obj.pk}"


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "name", "category", "specimen", "device", "effective_datetime")
    list_display_links = ("name",)
    search_fields = ("name", "loinc_code")
    list_filter = ("patient", "category")
    ordering = ("-effective_datetime",)
    autocomplete_fields = ["patient", "specimen", "device"]


@admin.register(DiagnosticReport)
class DiagnosticReportAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "code", "status", "category", "effective_datetime", "issued")
    list_display_links = ("code",)
    search_fields = ("code", "category", "conclusion", "conclusion_code", "notes")
    list_filter = ("patient", "status", "category")
    ordering = ("-effective_datetime", "-issued")
    autocomplete_fields = ["patient", "encounter"]
    filter_horizontal = (
        "care_plans",
        "service_requests",
        "specimens",
        "observations",
        "performers_practitioners",
        "performers_roles",
        "performers_organizations",
        "performers_care_teams",
        "interpreter_practitioners",
        "interpreter_roles",
        "interpreter_organizations",
        "interpreter_care_teams",
        "presented_documents",
    )


@admin.register(DetectedIssue)
class DetectedIssueAdmin(admin.ModelAdmin):
    list_display = ("id", "issue_label", "patient", "severity", "status", "identified_datetime")
    list_display_links = ("issue_label",)
    search_fields = ("code", "detail", "evidence_summary", "mitigation_summary", "implicated_summary", "notes")
    list_filter = ("patient", "status", "severity", "code")
    ordering = ("-identified_datetime", "-updated_at")
    autocomplete_fields = ["patient", "author_practitioner", "author_role", "author_device"]
    filter_horizontal = (
        "implicated_conditions",
        "implicated_medications",
        "implicated_immunizations",
        "implicated_observations",
        "implicated_service_requests",
        "implicated_procedures",
        "implicated_devices",
        "implicated_diagnostic_reports",
        "evidence_observations",
        "evidence_conditions",
        "evidence_diagnostic_reports",
    )

    @admin.display(description="Issue", ordering="code")
    def issue_label(self, obj):
        return obj.code or obj.detail or f"Detected Issue #{obj.pk}"


class PersonLinkInline(admin.StackedInline):
    model = PersonLink
    fk_name = "person"
    extra = 0
    fields = (
        "patient",
        "practitioner",
        "related_person",
        "linked_person",
        "assurance",
        "target_display",
        "target_reference",
    )
    autocomplete_fields = ["patient", "practitioner", "related_person", "linked_person"]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = (PersonLinkInline,)
    list_display = ("id", "person_label", "gender", "birth_date", "phone", "email", "managing_organization", "active")
    list_display_links = ("person_label",)
    search_fields = ("name", "phone", "email", "address", "notes")
    list_filter = ("active", "gender", "managing_organization")
    ordering = ("name",)
    autocomplete_fields = ["managing_organization"]

    @admin.display(description="Person", ordering="name")
    def person_label(self, obj):
        return obj.name or f"Person #{obj.pk}"


@admin.register(RelatedPerson)
class RelatedPersonAdmin(admin.ModelAdmin):
    list_display = ("id", "person_label", "person", "patient", "relationship", "phone", "email", "active")
    list_display_links = ("person_label",)
    search_fields = ("name", "relationship", "phone", "email", "address", "notes")
    list_filter = ("patient", "active", "relationship", "gender", "person")
    ordering = ("patient", "name", "relationship")
    autocomplete_fields = ["person", "patient"]

    @admin.display(description="Related person", ordering="name")
    def person_label(self, obj):
        return obj.name or obj.relationship or f"Related Person #{obj.pk}"


class FHIRGroupMemberInline(admin.StackedInline):
    model = FHIRGroupMember
    fk_name = "group"
    extra = 0
    fieldsets = (
        (None, {
            "fields": (
                "patient",
                "practitioner",
                "practitioner_role",
                "device",
                "medication",
                "member_group",
            ),
        }),
        ("Source details", {
            "fields": (
                "entity_display",
                "entity_reference",
                "start_date",
                "end_date",
                "inactive",
            ),
            "classes": ("collapse",),
        }),
    )
    autocomplete_fields = ["patient", "practitioner", "practitioner_role", "device", "medication", "member_group"]


@admin.register(FHIRGroup)
class FHIRGroupAdmin(admin.ModelAdmin):
    inlines = (FHIRGroupMemberInline,)
    list_display = ("id", "group_label", "group_type", "actual", "quantity", "active")
    list_display_links = ("group_label",)
    search_fields = ("name", "code", "characteristic_summary", "notes")
    list_filter = ("active", "actual", "group_type")
    ordering = ("name", "code")
    autocomplete_fields = [
        "managing_organization",
        "managing_practitioner",
        "managing_role",
        "managing_related_person",
    ]

    @admin.display(description="Group", ordering="name")
    def group_label(self, obj):
        return obj.name or obj.code or f"Group #{obj.pk}"


@admin.register(BodyStructure)
class BodyStructureAdmin(admin.ModelAdmin):
    list_display = ("id", "structure_label", "patient", "location", "morphology", "active")
    list_display_links = ("structure_label",)
    search_fields = ("description", "location", "morphology", "location_qualifier", "notes")
    list_filter = ("patient", "active", "location")
    ordering = ("patient", "location", "description")
    autocomplete_fields = ["patient"]

    @admin.display(description="Body structure", ordering="description")
    def structure_label(self, obj):
        return obj.description or obj.location or obj.morphology or f"Body Structure #{obj.pk}"


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ("id", "risk_label", "patient", "status", "occurrence_datetime", "authored_on")
    list_display_links = ("risk_label",)
    search_fields = ("code", "method", "prediction_summary", "mitigation", "notes")
    list_filter = ("patient", "status", "code")
    ordering = ("-occurrence_datetime", "-authored_on")
    autocomplete_fields = [
        "patient",
        "encounter",
        "performer_practitioner",
        "performer_role",
        "performer_organization",
        "performer_device",
    ]
    filter_horizontal = ("conditions", "observations", "diagnostic_reports")

    @admin.display(description="Risk assessment", ordering="code")
    def risk_label(self, obj):
        return obj.code or obj.prediction_summary or f"Risk Assessment #{obj.pk}"


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "patient", "lifecycle_status", "achievement_status", "priority", "start_date")
    list_display_links = ("description",)
    search_fields = ("description", "target_summary", "outcome_summary", "status_reason", "notes")
    list_filter = ("patient", "lifecycle_status", "achievement_status", "category", "priority")
    ordering = ("patient", "description")
    autocomplete_fields = [
        "patient",
        "subject_group",
        "expressed_by_practitioner",
        "expressed_by_role",
        "expressed_by_related_person",
    ]
    filter_horizontal = (
        "addresses_conditions",
        "addresses_observations",
        "addresses_medications",
        "addresses_service_requests",
        "addresses_risk_assessments",
        "outcome_observations",
    )


@admin.register(DeviceRequest)
class DeviceRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "patient", "status", "intent", "priority", "authored_on")
    list_display_links = ("code",)
    search_fields = ("code", "reason", "notes")
    list_filter = ("patient", "status", "intent", "priority")
    ordering = ("-authored_on", "code")
    autocomplete_fields = ["patient", "encounter", "requester_practitioner", "requester_role"]
    filter_horizontal = (
        "devices",
        "care_plans",
        "service_requests",
        "replaces",
        "conditions",
        "observations",
        "diagnostic_reports",
        "risk_assessments",
        "performers_practitioners",
        "performers_roles",
        "performers_organizations",
    )


@admin.register(DeviceUseStatement)
class DeviceUseStatementAdmin(admin.ModelAdmin):
    list_display = ("id", "use_label", "patient", "status", "recorded_on", "timing_start")
    list_display_links = ("use_label",)
    search_fields = ("body_site", "notes", "device__display_name")
    list_filter = ("patient", "status", "device")
    ordering = ("-recorded_on", "-timing_start")
    autocomplete_fields = ["patient", "device", "source_practitioner", "source_role", "source_related_person"]
    filter_horizontal = (
        "based_on_service_requests",
        "based_on_device_requests",
        "reason_conditions",
        "reason_observations",
        "reason_diagnostic_reports",
        "reason_risk_assessments",
    )

    @admin.display(description="Device use")
    def use_label(self, obj):
        return str(obj.device or f"Device Use Statement #{obj.pk}")


@admin.register(NutritionOrder)
class NutritionOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "nutrition_label", "patient", "status", "intent", "date_time")
    list_display_links = ("nutrition_label",)
    search_fields = (
        "oral_diet_summary",
        "supplement_summary",
        "enteral_formula_summary",
        "food_preference_summary",
        "exclude_food_summary",
        "notes",
    )
    list_filter = ("patient", "status", "intent")
    ordering = ("-date_time",)
    autocomplete_fields = ["patient", "encounter", "orderer_practitioner"]

    @admin.display(description="Nutrition order")
    def nutrition_label(self, obj):
        return obj.oral_diet_summary or obj.supplement_summary or obj.enteral_formula_summary or f"Nutrition Order #{obj.pk}"


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ("id", "communication_label", "patient", "status", "category", "sent", "received")
    list_display_links = ("communication_label",)
    search_fields = ("topic", "payload_summary", "reason", "notes")
    list_filter = ("patient", "status", "category", "priority", "medium")
    ordering = ("-sent", "-received")
    autocomplete_fields = ["patient", "encounter", "sender_practitioner", "sender_organization", "sender_related_person"]
    filter_horizontal = ("recipients_practitioners", "recipients_organizations", "recipients_related_people", "in_response_to")

    @admin.display(description="Communication", ordering="topic")
    def communication_label(self, obj):
        return obj.topic or obj.payload_summary[:80] or f"Communication #{obj.pk}"


@admin.register(CommunicationRequest)
class CommunicationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "request_label", "patient", "status", "category", "priority", "authored_on")
    list_display_links = ("request_label",)
    search_fields = ("payload_summary", "reason", "category", "notes")
    list_filter = ("patient", "status", "category", "priority", "medium")
    ordering = ("-authored_on",)
    autocomplete_fields = ["patient", "encounter", "requester_practitioner", "sender_practitioner"]
    filter_horizontal = ("recipients_practitioners", "recipients_related_people", "based_on_service_requests", "replaces")

    @admin.display(description="Communication request")
    def request_label(self, obj):
        return obj.payload_summary[:80] or obj.category or f"Communication Request #{obj.pk}"


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "patient", "status", "category", "start_date", "end_date")
    list_display_links = ("code",)
    search_fields = ("code", "category", "notes")
    list_filter = ("patient", "status", "category")
    ordering = ("-start_date",)
    autocomplete_fields = ["patient", "encounter", "author_practitioner", "author_organization"]


@admin.register(FHIRList)
class FHIRListAdmin(admin.ModelAdmin):
    list_display = ("id", "list_label", "patient", "status", "mode", "date")
    list_display_links = ("list_label",)
    search_fields = ("title", "code", "entry_summary", "empty_reason", "notes")
    list_filter = ("patient", "status", "mode", "code")
    ordering = ("-date", "title")
    autocomplete_fields = ["patient", "encounter", "source_practitioner", "source_organization"]
    filter_horizontal = ("conditions", "observations", "medications", "procedures", "diagnostic_reports", "documents")

    @admin.display(description="List", ordering="title")
    def list_label(self, obj):
        return obj.title or obj.code or f"FHIR List #{obj.pk}"


@admin.register(QuestionnaireResponse)
class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "response_label", "patient", "status", "authored", "encounter")
    list_display_links = ("response_label",)
    search_fields = ("questionnaire", "item_summary", "notes")
    list_filter = ("patient", "status")
    ordering = ("-authored",)
    autocomplete_fields = ["patient", "encounter", "author_practitioner", "source_patient", "source_related_person"]
    filter_horizontal = ("based_on_service_requests", "part_of_observations", "part_of_procedures")

    @admin.display(description="Questionnaire response", ordering="questionnaire")
    def response_label(self, obj):
        return obj.questionnaire or f"Questionnaire Response #{obj.pk}"


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("id", "media_label", "patient", "status", "media_type", "modality", "created_datetime")
    list_display_links = ("media_label",)
    search_fields = ("media_type", "modality", "view", "body_site", "content_title", "content_url", "notes")
    list_filter = ("patient", "status", "media_type", "modality")
    ordering = ("-created_datetime", "-issued")
    autocomplete_fields = ["patient", "encounter", "operator_practitioner", "device"]
    filter_horizontal = ("based_on_service_requests",)

    @admin.display(description="Media", ordering="content_title")
    def media_label(self, obj):
        return obj.content_title or obj.media_type or f"Media #{obj.pk}"


@admin.register(ImagingStudy)
class ImagingStudyAdmin(admin.ModelAdmin):
    list_display = ("id", "study_label", "patient", "status", "started", "procedure_code")
    list_display_links = ("study_label",)
    search_fields = ("description", "procedure_code", "reason", "modality_summary", "series_summary", "notes")
    list_filter = ("patient", "status", "procedure_code")
    ordering = ("-started",)
    autocomplete_fields = ["patient", "encounter", "referrer_practitioner"]
    filter_horizontal = ("endpoint_organizations", "based_on_service_requests", "interpreter_practitioners")

    @admin.display(description="Imaging study", ordering="description")
    def study_label(self, obj):
        return obj.description or obj.procedure_code or f"Imaging Study #{obj.pk}"


@admin.register(MolecularSequence)
class MolecularSequenceAdmin(admin.ModelAdmin):
    list_display = ("id", "sequence_label", "patient", "sequence_type", "specimen", "performer_organization")
    list_display_links = ("sequence_label",)
    search_fields = ("sequence_type", "observed_sequence", "reference_sequence_summary", "variant_summary", "repository_summary")
    list_filter = ("patient", "sequence_type", "performer_organization")
    ordering = ("patient", "sequence_type")
    autocomplete_fields = ["patient", "specimen", "device", "performer_organization"]

    @admin.display(description="Molecular sequence", ordering="sequence_type")
    def sequence_label(self, obj):
        return obj.sequence_type or f"Molecular Sequence #{obj.pk}"


@admin.register(MedicationKnowledge)
class MedicationKnowledgeAdmin(admin.ModelAdmin):
    list_display = ("id", "knowledge_label", "status", "dose_form", "product_type")
    list_display_links = ("knowledge_label",)
    search_fields = ("code", "dose_form", "synonym", "product_type", "ingredient_summary", "contraindication_summary", "notes")
    list_filter = ("status", "dose_form", "product_type")
    ordering = ("code",)
    autocomplete_fields = ["medication"]
    filter_horizontal = ("associated_medications",)

    @admin.display(description="Medication knowledge", ordering="code")
    def knowledge_label(self, obj):
        return obj.code or str(obj.medication or f"Medication Knowledge #{obj.pk}")


@admin.register(ImmunizationEvaluation)
class ImmunizationEvaluationAdmin(admin.ModelAdmin):
    list_display = ("id", "evaluation_label", "patient", "status", "target_disease", "dose_status")
    list_display_links = ("evaluation_label",)
    search_fields = ("target_disease", "dose_status", "dose_status_reason", "description", "series", "notes")
    list_filter = ("patient", "status", "target_disease", "dose_status", "authority")
    ordering = ("patient", "target_disease")
    autocomplete_fields = ["patient", "immunization", "authority"]

    @admin.display(description="Evaluation", ordering="target_disease")
    def evaluation_label(self, obj):
        return obj.target_disease or obj.dose_status or f"Immunization Evaluation #{obj.pk}"


@admin.register(VisionPrescription)
class VisionPrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "status", "date_written", "prescriber_practitioner")
    list_display_links = ("status",)
    search_fields = ("status", "lens_summary", "notes")
    list_filter = ("patient", "status", "prescriber_practitioner")
    ordering = ("-date_written", "-created_datetime")
    autocomplete_fields = ["patient", "encounter", "prescriber_practitioner", "prescriber_role"]


@admin.register(RequestGroup)
class RequestGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "group_label", "patient", "status", "intent", "priority", "authored_on")
    list_display_links = ("group_label",)
    search_fields = ("code", "reason", "action_summary", "notes")
    list_filter = ("patient", "status", "intent", "priority")
    ordering = ("-authored_on",)
    autocomplete_fields = ["patient", "encounter", "author_practitioner"]
    filter_horizontal = ("based_on_service_requests", "replaces")

    @admin.display(description="Request group", ordering="code")
    def group_label(self, obj):
        return obj.code or f"Request Group #{obj.pk}"


@admin.register(GuidanceResponse)
class GuidanceResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "guidance_label", "patient", "status", "occurrence_datetime")
    list_display_links = ("guidance_label",)
    search_fields = ("module_uri", "status", "reason", "result_summary", "data_requirement_summary", "notes")
    list_filter = ("patient", "status", "performer_organization")
    ordering = ("-occurrence_datetime",)
    autocomplete_fields = ["patient", "encounter", "performer_organization"]

    @admin.display(description="Guidance", ordering="module_uri")
    def guidance_label(self, obj):
        return obj.module_uri or obj.status or f"Guidance Response #{obj.pk}"


@admin.register(SupplyRequest)
class SupplyRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "patient", "status", "priority", "authored_on")
    list_display_links = ("item",)
    search_fields = ("item", "category", "reason", "quantity", "notes")
    list_filter = ("patient", "status", "priority", "category")
    ordering = ("-authored_on",)
    autocomplete_fields = ["patient", "requester_practitioner", "requester_organization", "supplier_organization", "deliver_to_location"]
    filter_horizontal = ("based_on_service_requests",)


@admin.register(SupplyDelivery)
class SupplyDeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "patient", "status", "delivery_type", "occurrence_start")
    list_display_links = ("item",)
    search_fields = ("item", "quantity", "delivery_type", "notes")
    list_filter = ("patient", "status", "delivery_type", "supplier_organization")
    ordering = ("-occurrence_start",)
    autocomplete_fields = ["patient", "supplier_practitioner", "supplier_organization", "destination"]
    filter_horizontal = ("based_on_supply_requests", "part_of_deliveries", "receivers")


@admin.register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "specimen_type", "status", "accession_identifier", "collected_datetime")
    list_display_links = ("specimen_type",)
    search_fields = ("specimen_type", "accession_identifier", "body_site", "collector_display")
    list_filter = ("patient", "status", "specimen_type")
    ordering = ("-collected_datetime", "-received_time")
    autocomplete_fields = ["patient"]
    filter_horizontal = ("parent_specimens",)


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "encounter_type", "provider_name", "facility_name", "display_start_time")
    list_display_links = ("encounter_type",)
    search_fields = ("provider_name", "facility_name", "reason")
    list_filter = ("patient", "status")
    ordering = ("-start_time",)
    autocomplete_fields = ["patient"]
    filter_horizontal = ("episodes_of_care",)

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
                "related_person",
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
    autocomplete_fields = ["practitioner", "organization", "location", "related_person"]


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


@admin.register(CarePlan)
class CarePlanAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "title", "status", "intent", "start_date")
    list_display_links = ("title",)
    search_fields = ("title", "category", "description", "author_display")
    list_filter = ("patient", "status", "intent", "category")
    ordering = ("patient", "-start_date", "title")
    autocomplete_fields = ["patient"]
    filter_horizontal = ("conditions", "care_teams")


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "name", "status", "intent", "priority", "authored_on")
    list_display_links = ("name",)
    search_fields = ("name", "category", "reason", "patient_instruction")
    list_filter = ("patient", "status", "intent", "priority", "category")
    ordering = ("-authored_on",)
    autocomplete_fields = [
        "patient",
        "encounter",
        "requester_practitioner",
        "requester_role",
        "requester_organization",
        "requester_device",
    ]
    filter_horizontal = (
        "care_plans",
        "replaces",
        "performers_practitioners",
        "performers_roles",
        "performers_organizations",
        "performers_care_teams",
        "performers_devices",
        "locations",
        "conditions",
        "specimens",
    )


@admin.register(EpisodeOfCare)
class EpisodeOfCareAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "episode_type", "status", "managing_organization", "start_date", "end_date")
    list_display_links = ("episode_type",)
    search_fields = ("episode_type", "diagnosis_summary", "notes")
    list_filter = ("patient", "status", "episode_type", "managing_organization")
    ordering = ("-start_date",)
    autocomplete_fields = [
        "patient",
        "managing_organization",
        "care_manager_practitioner",
        "care_manager_role",
    ]
    filter_horizontal = ("referral_requests", "care_teams")


@admin.register(AdverseEvent)
class AdverseEventAdmin(admin.ModelAdmin):
    list_display = ("id", "event_label", "patient", "actuality", "severity", "outcome", "event_date")
    list_display_links = ("event_label",)
    search_fields = ("event", "category", "seriousness", "severity", "outcome", "suspect_entity_summary")
    list_filter = ("patient", "actuality", "severity", "outcome", "category")
    ordering = ("-event_date", "-recorded_date")
    autocomplete_fields = [
        "patient",
        "encounter",
        "location",
        "recorder_practitioner",
        "recorder_role",
    ]
    filter_horizontal = (
        "resulting_conditions",
        "contributor_practitioners",
        "contributor_roles",
        "contributor_devices",
        "suspect_immunizations",
        "suspect_procedures",
        "suspect_medications",
        "suspect_devices",
        "reference_documents",
        "subject_medical_history_conditions",
        "subject_medical_history_observations",
        "subject_medical_history_immunizations",
        "subject_medical_history_procedures",
    )

    @admin.display(description="Event", ordering="event")
    def event_label(self, obj):
        return obj.event or obj.category or f"Adverse Event #{obj.pk}"


class FamilyMemberHistoryConditionInline(admin.StackedInline):
    model = FamilyMemberHistoryCondition
    extra = 0
    autocomplete_fields = ["condition"]
    fieldsets = (
        (None, {
            "fields": (
                "condition",
                "condition_text",
                "outcome",
                "contributed_to_death",
                "onset_text",
            ),
        }),
        ("Notes", {
            "fields": ("notes",),
            "classes": ("collapse",),
        }),
    )
    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"rows": 3})},
    }


@admin.register(FamilyMemberHistory)
class FamilyMemberHistoryAdmin(admin.ModelAdmin):
    inlines = (FamilyMemberHistoryConditionInline,)
    list_display = ("id", "patient", "relationship", "status", "sex", "age_text", "deceased")
    list_display_links = ("relationship",)
    search_fields = ("relationship", "reason", "notes", "condition_links__condition_text")
    list_filter = ("patient", "status", "relationship", "sex", "deceased")
    ordering = ("patient", "relationship")
    autocomplete_fields = ["patient"]
    filter_horizontal = ("conditions",)


class ClinicalImpressionFindingInline(admin.StackedInline):
    model = ClinicalImpressionFinding
    extra = 0
    autocomplete_fields = ["condition", "observation"]
    fieldsets = (
        (None, {
            "fields": (
                "condition",
                "observation",
                "finding_text",
            ),
        }),
        ("Basis", {
            "fields": ("basis",),
            "classes": ("collapse",),
        }),
    )
    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"rows": 3})},
    }


@admin.register(ClinicalImpression)
class ClinicalImpressionAdmin(admin.ModelAdmin):
    inlines = (ClinicalImpressionFindingInline,)
    list_display = ("id", "impression_label", "patient", "status", "date", "encounter")
    list_display_links = ("impression_label",)
    search_fields = ("description", "summary", "prognosis", "notes")
    list_filter = ("patient", "status", "date")
    ordering = ("-date", "-effective_datetime")
    autocomplete_fields = [
        "patient",
        "encounter",
        "assessor_practitioner",
        "assessor_role",
    ]
    filter_horizontal = ("conditions", "observations", "problems", "investigations_observations")

    @admin.display(description="Impression", ordering="description")
    def impression_label(self, obj):
        return obj.description or obj.summary or f"Clinical Impression #{obj.pk}"


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


@admin.register(PractitionerRole)
class PractitionerRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "role_label", "practitioner", "organization", "specialty", "active")
    list_display_links = ("role_label",)
    search_fields = ("role", "specialty", "practitioner__name", "organization__name")
    list_filter = ("active", "role", "specialty", "organization")
    ordering = ("practitioner__name", "organization__name", "role")
    autocomplete_fields = ["practitioner", "organization"]
    filter_horizontal = ("locations",)

    @admin.display(description="Role", ordering="role")
    def role_label(self, obj):
        return obj.role or obj.specialty or str(obj.practitioner or obj.organization or f"Practitioner Role #{obj.pk}")


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "display_name", "device_type", "status", "manufacturer", "owner")
    list_display_links = ("display_name",)
    search_fields = (
        "display_name",
        "device_type",
        "manufacturer",
        "model_number",
        "serial_number",
        "lot_number",
        "distinct_identifier",
    )
    list_filter = ("patient", "status", "device_type", "manufacturer", "owner")
    ordering = ("display_name",)
    autocomplete_fields = ["patient", "owner", "location"]


class ProcedurePerformerInline(admin.StackedInline):
    model = ProcedurePerformer
    extra = 0
    fieldsets = (
        (None, {
            "fields": (
                "role",
                "practitioner",
                "organization",
            ),
        }),
        ("Source details", {
            "fields": (
                "actor_display",
                "actor_reference",
                "on_behalf_of_display",
                "on_behalf_of_reference",
            ),
            "classes": ("collapse",),
        }),
    )
    autocomplete_fields = ["practitioner", "organization"]


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    inlines = (ProcedurePerformerInline,)
    list_display = ("id", "patient", "name", "status", "category", "performed_start")
    list_display_links = ("name",)
    search_fields = ("name", "category", "reason", "body_site", "outcome")
    list_filter = ("patient", "status", "category")
    ordering = ("-performed_start",)
    autocomplete_fields = ["patient", "encounter"]
    filter_horizontal = ("care_plans", "service_requests", "conditions")


@admin.register(InsurancePlan)
class InsurancePlanAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "plan_type", "owned_by", "administered_by")
    list_display_links = ("name",)
    search_fields = ("name", "alias", "plan_type", "coverage_area", "benefit_summary")
    list_filter = ("status", "plan_type", "owned_by", "administered_by")
    ordering = ("name",)
    autocomplete_fields = ["owned_by", "administered_by"]


@admin.register(Provenance)
class ProvenanceAdmin(admin.ModelAdmin):
    list_display = ("id", "activity", "patient", "recorded", "location")
    list_display_links = ("activity",)
    search_fields = ("activity", "target_summary", "agent_summary", "entity_summary", "policy", "notes")
    list_filter = ("patient", "activity", "location")
    ordering = ("-recorded",)
    autocomplete_fields = ["patient", "location"]


@admin.register(Composition)
class CompositionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "patient", "status", "composition_type", "date")
    list_display_links = ("title",)
    search_fields = ("title", "composition_type", "category", "section_summary", "notes")
    list_filter = ("patient", "status", "composition_type", "custodian")
    ordering = ("-date",)
    autocomplete_fields = ["patient", "encounter", "custodian"]
    filter_horizontal = ("authors_practitioners",)


@admin.register(DocumentManifest)
class DocumentManifestAdmin(admin.ModelAdmin):
    list_display = ("id", "manifest_type", "patient", "status", "created_datetime")
    list_display_links = ("manifest_type",)
    search_fields = ("manifest_type", "description", "content_summary", "related_summary", "source")
    list_filter = ("patient", "status", "manifest_type")
    ordering = ("-created_datetime",)
    autocomplete_fields = ["patient", "author_practitioner"]


@admin.register(BinaryResource)
class BinaryResourceAdmin(admin.ModelAdmin):
    list_display = ("id", "content_type", "patient", "data_size", "security_context")
    list_display_links = ("content_type",)
    search_fields = ("content_type", "security_context", "data_hash", "notes")
    list_filter = ("patient", "content_type")
    autocomplete_fields = ["patient"]


@admin.register(Endpoint)
class EndpointAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "connection_type", "managing_organization")
    list_display_links = ("name",)
    search_fields = ("name", "connection_type", "address", "payload_type")
    list_filter = ("status", "connection_type", "managing_organization")
    autocomplete_fields = ["managing_organization"]


@admin.register(HealthcareService)
class HealthcareServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "provided_by", "active", "service_type", "specialty")
    list_display_links = ("name",)
    search_fields = ("name", "category", "service_type", "specialty", "comment")
    list_filter = ("active", "category", "service_type", "provided_by")
    autocomplete_fields = ["provided_by"]
    filter_horizontal = ("locations", "endpoints")


@admin.register(OrganizationAffiliation)
class OrganizationAffiliationAdmin(admin.ModelAdmin):
    list_display = ("id", "role", "organization", "participating_organization", "active", "start_date", "end_date")
    list_display_links = ("role",)
    search_fields = ("role", "specialty", "telecom", "notes")
    list_filter = ("active", "role", "organization", "participating_organization")
    autocomplete_fields = ["organization", "participating_organization"]
    filter_horizontal = ("networks", "locations", "healthcare_services", "endpoints")


@admin.register(Substance)
class SubstanceAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "status", "category")
    list_display_links = ("code",)
    search_fields = ("code", "category", "description", "instance_summary", "ingredient_summary")
    list_filter = ("status", "category")


@admin.register(DeviceMetric)
class DeviceMetricAdmin(admin.ModelAdmin):
    list_display = ("id", "metric_type", "source", "category", "operational_status", "unit")
    list_display_links = ("metric_type",)
    search_fields = ("metric_type", "unit", "category", "calibration_summary")
    list_filter = ("category", "operational_status", "source")
    autocomplete_fields = ["source", "parent"]


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "service_type", "patient", "active", "planning_horizon_start", "planning_horizon_end")
    list_display_links = ("service_type",)
    search_fields = ("service_category", "service_type", "specialty", "comment")
    list_filter = ("patient", "active", "service_category", "service_type")
    autocomplete_fields = ["patient"]
    filter_horizontal = ("actors_practitioners", "actors_locations", "actors_healthcare_services")


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("id", "schedule", "status", "start_time", "end_time", "overbooked")
    list_display_links = ("schedule",)
    search_fields = ("service_category", "service_type", "specialty", "appointment_type", "comment")
    list_filter = ("status", "overbooked", "schedule")
    autocomplete_fields = ["schedule"]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "patient", "status", "appointment_type", "start_time")
    list_display_links = ("description",)
    search_fields = ("description", "appointment_type", "reason", "participant_summary", "comment")
    list_filter = ("patient", "status", "appointment_type")
    autocomplete_fields = ["patient"]
    filter_horizontal = ("slots", "participants_practitioners", "participants_locations", "based_on_service_requests")


@admin.register(AppointmentResponse)
class AppointmentResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment", "patient", "participant_status", "start_time")
    list_display_links = ("appointment",)
    search_fields = ("participant_status", "participant_type", "comment")
    list_filter = ("patient", "participant_status", "appointment")
    autocomplete_fields = ["appointment", "patient", "actor_practitioner", "actor_location"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "patient", "status", "intent", "priority", "authored_on")
    list_display_links = ("code",)
    search_fields = ("code", "description", "input_summary", "output_summary", "notes")
    list_filter = ("patient", "status", "intent", "priority")
    ordering = ("-authored_on",)
    autocomplete_fields = ["patient", "encounter", "owner_practitioner", "owner_organization"]
    filter_horizontal = ("based_on_service_requests",)
@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("id", "audit_type", "patient", "action", "outcome", "recorded")
    list_display_links = ("audit_type",)
    search_fields = ("audit_type", "subtype", "action", "outcome", "outcome_description", "agent_summary", "entity_summary")
    list_filter = ("patient", "action", "outcome", "audit_type")
    ordering = ("-recorded",)
    autocomplete_fields = ["patient"]

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("id", "account_label", "patient", "status", "account_type", "owner", "service_period_start")
    list_display_links = ("account_label",)
    search_fields = ("name", "account_type", "description", "guarantor_summary", "balance_summary")
    list_filter = ("patient", "status", "account_type", "owner")
    autocomplete_fields = ["patient", "owner"]
    filter_horizontal = ("coverages",)

    @admin.display(description="Account", ordering="name")
    def account_label(self, obj):
        return obj.name or obj.account_type or f"Account #{obj.pk}"


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("id", "claim_label", "patient", "status", "claim_type", "use", "created_date")
    list_display_links = ("claim_label",)
    search_fields = ("claim_type", "use", "priority", "diagnosis_summary", "item_summary", "insurance_summary")
    list_filter = ("patient", "status", "claim_type", "use", "insurer")
    ordering = ("-created_date", "-billable_period_start")
    autocomplete_fields = ["patient", "insurer", "provider_practitioner", "provider_organization"]
    filter_horizontal = ("coverages",)

    @admin.display(description="Claim", ordering="claim_type")
    def claim_label(self, obj):
        return obj.claim_type or obj.use or f"Claim #{obj.pk}"


@admin.register(ClaimResponse)
class ClaimResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "response_label", "patient", "status", "response_type", "outcome", "created_date")
    list_display_links = ("response_label",)
    search_fields = ("response_type", "outcome", "disposition", "item_summary", "total_summary", "payment_summary", "error_summary")
    list_filter = ("patient", "status", "response_type", "outcome", "insurer")
    ordering = ("-created_date",)
    autocomplete_fields = ["patient", "request_claim", "insurer"]

    @admin.display(description="Claim response", ordering="response_type")
    def response_label(self, obj):
        return obj.response_type or obj.outcome or f"Claim Response #{obj.pk}"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "invoice_label", "patient", "status", "invoice_type", "date", "total_gross")
    list_display_links = ("invoice_label",)
    search_fields = ("invoice_type", "participant_summary", "line_item_summary", "total_net", "total_gross", "payment_terms")
    list_filter = ("patient", "status", "invoice_type", "issuer_organization")
    ordering = ("-date",)
    autocomplete_fields = ["patient", "account", "issuer_organization"]

    @admin.display(description="Invoice", ordering="invoice_type")
    def invoice_label(self, obj):
        return obj.invoice_type or obj.status or f"Invoice #{obj.pk}"


@admin.register(ChargeItem)
class ChargeItemAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "patient", "status", "encounter", "occurrence_datetime")
    list_display_links = ("code",)
    search_fields = ("code", "quantity", "price_override", "total_price_component", "reason", "notes")
    list_filter = ("patient", "status", "encounter", "account")
    ordering = ("-occurrence_datetime",)
    autocomplete_fields = ["patient", "encounter", "account"]
    filter_horizontal = ("service_requests", "performer_practitioners")


@admin.register(ResearchStudy)
class ResearchStudyAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "phase", "sponsor", "period_start", "period_end")
    list_display_links = ("title",)
    search_fields = ("title", "phase", "category", "focus", "condition", "description")
    list_filter = ("status", "phase", "sponsor")
    ordering = ("title",)
    autocomplete_fields = ["sponsor", "principal_investigator"]
    filter_horizontal = ("sites",)


@admin.register(ResearchSubject)
class ResearchSubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "study", "status", "assigned_arm", "period_start", "period_end")
    list_display_links = ("patient",)
    search_fields = ("assigned_arm", "actual_arm", "notes", "study__title")
    list_filter = ("patient", "status", "study")
    autocomplete_fields = ["patient", "study", "consent"]


@admin.register(DeviceDefinition)
class DeviceDefinitionAdmin(admin.ModelAdmin):
    list_display = ("id", "device_name", "device_type", "manufacturer", "model_number", "version")
    list_display_links = ("device_name",)
    search_fields = ("device_name", "device_type", "model_number", "version", "udi_device_identifier")
    list_filter = ("device_type", "manufacturer")
    autocomplete_fields = ["manufacturer"]


@admin.register(ObservationDefinition)
class ObservationDefinitionAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "category", "permitted_data_type", "multiple_results_allowed")
    list_display_links = ("code",)
    search_fields = ("code", "category", "method", "preferred_report_name", "qualified_interval_summary")
    list_filter = ("category", "permitted_data_type", "multiple_results_allowed")


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "version", "publisher", "approval_date")
    list_display_links = ("title",)
    search_fields = ("title", "name", "url", "publisher", "subject_type", "item_summary")
    list_filter = ("status", "publisher", "subject_type")
    ordering = ("title",)
@admin.register(Measure)
class MeasureAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "measure_type", "scoring", "publisher")
    list_display_links = ("title",)
    search_fields = ("title", "name", "url", "publisher", "description", "group_summary")
    list_filter = ("status", "measure_type", "scoring", "publisher")
    ordering = ("title",)


@admin.register(MeasureReport)
class MeasureReportAdmin(admin.ModelAdmin):
    list_display = ("id", "measure", "patient", "status", "report_type", "date")
    list_display_links = ("measure",)
    search_fields = ("group_summary", "evaluated_resource_summary", "notes")
    list_filter = ("patient", "status", "report_type", "measure")
    ordering = ("-date",)
    autocomplete_fields = ["patient", "measure"]


@admin.register(TestScript)
class TestScriptAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "version", "publisher", "date")
    list_display_links = ("title",)
    search_fields = ("title", "name", "url", "publisher", "fixture_summary", "test_summary")
    list_filter = ("status", "publisher")
    ordering = ("title",)


@admin.register(TestReport)
class TestReportAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "test_script", "status", "result", "issued")
    list_display_links = ("name",)
    search_fields = ("name", "tester", "participant_summary", "action_summary")
    list_filter = ("status", "result", "test_script")
    ordering = ("-issued",)
    autocomplete_fields = ["test_script"]


@admin.register(CoverageEligibilityRequest)
class CoverageEligibilityRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "status", "purpose", "insurer", "created_date")
    search_fields = ("purpose", "priority", "insurance_summary", "item_summary", "notes")
    list_filter = ("patient", "status", "purpose", "insurer")
    ordering = ("-created_date",)
    autocomplete_fields = ["patient", "insurer", "provider_organization"]


@admin.register(CoverageEligibilityResponse)
class CoverageEligibilityResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "status", "purpose", "outcome", "created_date")
    search_fields = ("purpose", "outcome", "disposition", "insurance_summary", "error_summary")
    list_filter = ("patient", "status", "purpose", "outcome", "insurer")
    ordering = ("-created_date",)
    autocomplete_fields = ["patient", "request", "insurer"]


@admin.register(EnrollmentRequest)
class EnrollmentRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "status", "insurer", "provider", "created_date")
    search_fields = ("status", "notes")
    list_filter = ("patient", "status", "insurer", "provider")
    ordering = ("-created_date",)
    autocomplete_fields = ["patient", "insurer", "provider", "coverage"]


@admin.register(EnrollmentResponse)
class EnrollmentResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "request", "status", "outcome", "organization", "created_date")
    search_fields = ("outcome", "disposition", "notes")
    list_filter = ("status", "outcome", "organization")
    ordering = ("-created_date",)
    autocomplete_fields = ["request", "organization"]


@admin.register(PaymentNotice)
class PaymentNoticeAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "status", "payment_status", "amount", "payment_date")
    search_fields = ("payment_status", "amount", "request_summary", "response_summary", "notes")
    list_filter = ("patient", "status", "payment_status", "recipient")
    ordering = ("-payment_date", "-created_date")
    autocomplete_fields = ["patient", "recipient"]


@admin.register(PaymentReconciliation)
class PaymentReconciliationAdmin(admin.ModelAdmin):
    list_display = ("id", "payment_issuer", "status", "outcome", "payment_amount", "payment_date")
    search_fields = ("outcome", "disposition", "payment_amount", "detail_summary", "process_note_summary")
    list_filter = ("status", "outcome", "payment_issuer")
    ordering = ("-payment_date", "-created_date")
    autocomplete_fields = ["payment_issuer"]



class CanonicalMetadataAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "version", "publisher", "date")
    list_display_links = ("title",)
    search_fields = ("url", "name", "title", "publisher", "description", "notes")
    list_filter = ("status", "publisher")
    ordering = ("title", "version")


@admin.register(CapabilityStatement)
class CapabilityStatementAdmin(CanonicalMetadataAdmin):
    search_fields = CanonicalMetadataAdmin.search_fields + ("kind", "fhir_version", "format_summary", "rest_summary")
    list_filter = ("status", "kind", "publisher")


@admin.register(StructureDefinition)
class StructureDefinitionAdmin(CanonicalMetadataAdmin):
    search_fields = CanonicalMetadataAdmin.search_fields + ("kind", "type_code", "base_definition", "derivation", "element_summary")
    list_filter = ("status", "kind", "derivation", "publisher")


@admin.register(ImplementationGuide)
class ImplementationGuideAdmin(CanonicalMetadataAdmin):
    search_fields = CanonicalMetadataAdmin.search_fields + ("package_id", "fhir_version_summary", "definition_summary")
    list_filter = ("status", "publisher")


@admin.register(SearchParameter)
class SearchParameterAdmin(CanonicalMetadataAdmin):
    list_display = ("id", "title", "code", "search_type", "status", "publisher")
    search_fields = CanonicalMetadataAdmin.search_fields + ("code", "base_summary", "search_type", "expression")
    list_filter = ("status", "search_type", "publisher")


@admin.register(MessageDefinition)
class MessageDefinitionAdmin(CanonicalMetadataAdmin):
    search_fields = CanonicalMetadataAdmin.search_fields + ("event", "category", "response_required", "focus_summary")
    list_filter = ("status", "category", "response_required", "publisher")


@admin.register(OperationDefinition)
class OperationDefinitionAdmin(CanonicalMetadataAdmin):
    list_display = ("id", "title", "kind", "code", "status", "publisher")
    search_fields = CanonicalMetadataAdmin.search_fields + ("kind", "code", "resource_summary", "parameter_summary")
    list_filter = ("status", "kind", "system", "type_level", "instance", "publisher")


@admin.register(CompartmentDefinition)
class CompartmentDefinitionAdmin(CanonicalMetadataAdmin):
    list_display = ("id", "title", "code", "status", "publisher")
    search_fields = CanonicalMetadataAdmin.search_fields + ("code", "resource_summary")
    list_filter = ("status", "code", "search", "publisher")


@admin.register(StructureMap)
class StructureMapAdmin(CanonicalMetadataAdmin):
    search_fields = CanonicalMetadataAdmin.search_fields + ("structure_summary", "group_summary")


@admin.register(GraphDefinition)
class GraphDefinitionAdmin(CanonicalMetadataAdmin):
    search_fields = CanonicalMetadataAdmin.search_fields + ("start", "profile", "link_summary")
    list_filter = ("status", "start", "publisher")


@admin.register(ExampleScenario)
class ExampleScenarioAdmin(CanonicalMetadataAdmin):
    search_fields = CanonicalMetadataAdmin.search_fields + ("actor_summary", "instance_summary", "process_summary")


@admin.register(NamingSystem)
class NamingSystemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "kind", "publisher", "date")
    list_display_links = ("name",)
    search_fields = ("name", "publisher", "description", "unique_id_summary", "notes")
    list_filter = ("status", "kind", "publisher")
    ordering = ("name",)


@admin.register(TerminologyCapabilities)
class TerminologyCapabilitiesAdmin(CanonicalMetadataAdmin):
    search_fields = CanonicalMetadataAdmin.search_fields + ("kind", "code_system_summary", "expansion_summary")
    list_filter = ("status", "kind", "publisher")


@admin.register(ActivityDefinition)
class ActivityDefinitionAdmin(CanonicalMetadataAdmin):
    search_fields = CanonicalMetadataAdmin.search_fields + ("activity_kind", "intent", "priority", "code", "participant_summary")
    list_filter = ("status", "activity_kind", "intent", "priority", "publisher")


@admin.register(EventDefinition)
class EventDefinitionAdmin(CanonicalMetadataAdmin):
    search_fields = CanonicalMetadataAdmin.search_fields + ("trigger_summary",)


@admin.register(SpecimenDefinition)
class SpecimenDefinitionAdmin(CanonicalMetadataAdmin):
    search_fields = CanonicalMetadataAdmin.search_fields + ("specimen_type", "collection_summary", "type_tested_summary")
    list_filter = ("status", "specimen_type", "publisher")

@admin.register(CodeSystem)
class CodeSystemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "version", "publisher", "content", "date")
    list_display_links = ("title",)
    search_fields = ("url", "name", "title", "publisher", "description", "concept_summary")
    list_filter = ("status", "content", "publisher")
    ordering = ("title", "version")


@admin.register(ValueSet)
class ValueSetAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "version", "publisher", "date")
    list_display_links = ("title",)
    search_fields = ("url", "name", "title", "publisher", "description", "compose_summary", "expansion_summary")
    list_filter = ("status", "publisher", "immutable")
    ordering = ("title", "version")


@admin.register(ConceptMap)
class ConceptMapAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "version", "publisher", "date")
    list_display_links = ("title",)
    search_fields = ("url", "name", "title", "publisher", "description", "source_uri", "target_uri", "group_summary")
    list_filter = ("status", "publisher")
    ordering = ("title", "version")


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "library_type", "version", "publisher", "date")
    list_display_links = ("title",)
    search_fields = ("url", "name", "title", "publisher", "description", "library_type", "subject", "content_summary")
    list_filter = ("status", "library_type", "publisher")
    ordering = ("title", "version")


@admin.register(PlanDefinition)
class PlanDefinitionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "plan_type", "version", "publisher", "date")
    list_display_links = ("title",)
    search_fields = ("url", "name", "title", "publisher", "description", "plan_type", "subject", "goal_summary", "action_summary")
    list_filter = ("status", "plan_type", "publisher")
    ordering = ("title", "version")

@admin.register(Coverage)
class CoverageAdmin(admin.ModelAdmin):
    list_display = ("id", "coverage_label", "patient", "status", "coverage_type", "payor_organization", "period_start", "period_end")
    list_display_links = ("coverage_label",)
    search_fields = ("coverage_type", "subscriber_id", "dependent", "relationship", "network", "class_summary", "notes")
    list_filter = ("patient", "status", "coverage_type", "payor_organization")
    ordering = ("patient", "order", "-period_start")
    autocomplete_fields = ["patient", "insurer_plan", "payor_organization", "policy_holder_patient", "subscriber_patient"]

    @admin.display(description="Coverage", ordering="coverage_type")
    def coverage_label(self, obj):
        return obj.coverage_type or obj.subscriber_id or f"Coverage #{obj.pk}"


@admin.register(ExplanationOfBenefit)
class ExplanationOfBenefitAdmin(admin.ModelAdmin):
    list_display = ("id", "eob_label", "patient", "status", "eob_type", "outcome", "created_date")
    list_display_links = ("eob_label",)
    search_fields = ("eob_type", "outcome", "disposition", "total_summary", "diagnosis_summary", "item_summary", "payment_summary")
    list_filter = ("patient", "status", "eob_type", "outcome", "insurer")
    ordering = ("-created_date", "-billable_period_start")
    autocomplete_fields = ["patient", "insurer", "provider_practitioner", "provider_organization"]
    filter_horizontal = ("coverages", "encounters")

    @admin.display(description="Explanation of benefit", ordering="eob_type")
    def eob_label(self, obj):
        return obj.eob_type or obj.outcome or f"Explanation of Benefit #{obj.pk}"


@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ("id", "consent_label", "patient", "status", "scope", "category", "decision", "start_date", "end_date")
    list_display_links = ("consent_label",)
    search_fields = ("scope", "category", "policy_rule", "decision", "provision_summary", "verification_summary", "notes")
    list_filter = ("patient", "status", "scope", "category", "decision", "organization")
    ordering = ("-start_date", "-updated_at")
    autocomplete_fields = ["patient", "organization"]
    filter_horizontal = ("performer_practitioners", "source_documents", "related_immunizations", "questionnaire_responses")

    @admin.display(description="Consent", ordering="category")
    def consent_label(self, obj):
        return obj.category or obj.scope or f"Consent #{obj.pk}"


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



