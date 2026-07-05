from django.contrib import admin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from .fhir_explorer_registry import build_fhir_explorer_sections
from .personal_emr_resource_registry_alphabetized import (
    build_personal_emr_resource_sections,
)


from clinical.models import (
    Account,
    TerminologyCapabilities,
    StructureMap,
    StructureDefinition,
    SpecimenDefinition,
    SearchParameter,
    OperationDefinition,
    NamingSystem,
    MessageDefinition,
    ImplementationGuide,
    GraphDefinition,
    ExampleScenario,
    EventDefinition,
    CompartmentDefinition,
    CapabilityStatement,
    ActivityDefinition,
    AdverseEvent,
    Allergy,
    Appointment,
    AppointmentResponse,
    AuditEvent,
    ChargeItem,
    Claim,
    ClaimResponse,
    CoverageEligibilityRequest,
    CoverageEligibilityResponse,
    BinaryResource,
    BodyStructure,
    CarePlan,
    CareTeam,
    ClinicalImpression,
    CodeSystem,
    ConceptMap,
    Communication,
    CommunicationRequest,
    Composition,
    Consent,
    Condition,
    Coverage,
    DetectedIssue,
    DeviceDefinition,
    Device,
    DeviceMetric,
    DeviceRequest,
    DeviceUseStatement,
    DiagnosticReport,
    DocumentManifest,
    EnrollmentRequest,
    EnrollmentResponse,
    Invoice,
    Encounter,
    EpisodeOfCare,
    Endpoint,
    FamilyMemberHistory,
    FHIRGroup,
    FHIRList,
    Flag,
    GuidanceResponse,
    Goal,
    HealthcareService,
    ImagingStudy,
    Immunization,
    ImmunizationEvaluation,
    ImmunizationRecommendation,
    InsurancePlan,
    Location,
    Library,
    Media,
    Medication,
    Measure,
    MeasureReport,
    MedicationAdministration,
    MedicationCatalog,
    MedicationDispense,
    MedicationKnowledge,
    MolecularSequence,
    NutritionOrder,
    Observation,
    ObservationDefinition,
    Organization,
    OrganizationAffiliation,
    PaymentNotice,
    PaymentReconciliation,
    PlanDefinition,
    Person,
    Practitioner,
    PractitionerRole,
    Procedure,
    Provenance,
    RelatedPerson,
    ResearchStudy,
    ResearchSubject,
    RiskAssessment,
    ServiceRequest,
    Specimen,
    ExplanationOfBenefit,
    Questionnaire,
    QuestionnaireResponse,
    RequestGroup,
    SupplyDelivery,
    SupplyRequest,
    Schedule,
    Slot,
    Substance,
    Task,
    ValueSet,
    TestScript,
    TestReport,
    VisionPrescription,
)
from documents.models import ClinicalDocument
from fhir.backups import (
    database_path,
    fhir_import_backup_dir,
    list_fhir_import_database_backups,
)
from fhir.models import FHIRResourceSnapshot
from patients.models import PatientProfile
from patients.models import RecoveryCredential
from patients.recovery import generate_recovery_key, hash_recovery_key
from system_settings.models import SystemSettings


def settings_hub(request):
    system_settings = SystemSettings.get_solo()
    recovery_credential = None

    if request.user.is_authenticated:
        recovery_credential = RecoveryCredential.objects.filter(
            user=request.user
        ).first()

    if recovery_credential:
        recovery_status = {
            "configured": True,
            "message": "Configured",
            "detail": "A recovery key hash exists for this system user.",
            "created_at": recovery_credential.created_at,
            "last_used_at": recovery_credential.last_used_at,
        }
    else:
        recovery_status = {
            "configured": False,
            "message": "Not configured",
            "detail": "No recovery key has been created for this system user yet.",
            "created_at": None,
            "last_used_at": None,
        }

    cards = [
        {
            "title": "App Settings",
            "description": f"Manage local time, lock-screen behavior, and desktop preferences. Current time zone: {system_settings.time_zone}.",
            "url": reverse(
                "admin:system_settings_systemsettings_change", args=[system_settings.pk]
            ),
            "icon": "fas fa-sliders-h",
        },
        {
            "title": "Users",
            "description": "Manage the local system owner account and password.",
            "url": reverse("admin:auth_user_changelist"),
            "icon": "fas fa-user",
        },
        {
            "title": "Groups",
            "description": "Advanced Django permission groups.",
            "url": reverse("admin:auth_group_changelist"),
            "icon": "fas fa-users",
        },
        {
            "title": "Recovery Keys",
            "description": "View recovery-key status and stored hashes.",
            "url": reverse("admin:patients_recoverycredential_changelist"),
            "icon": "fas fa-key",
        },
        {
            "title": "Backups",
            "description": "Find local FHIR pre-import database copies and review the manual restore steps.",
            "url": reverse("admin_backups"),
            "icon": "fas fa-archive",
        },
    ]

    context = {
        **admin.site.each_context(request),
        "title": "Settings",
        "settings_cards": cards,
        "recovery_status": recovery_status,
        "recovery_key_action_url": reverse("admin_recovery_key_generate"),
    }
    return render(request, "admin/settings_hub.html", context)


def backups_hub(request):
    context = {
        **admin.site.each_context(request),
        "title": "Backups",
        "database_path": database_path(),
        "backup_dir": fhir_import_backup_dir(),
        "backups": list_fhir_import_database_backups(),
    }
    return render(request, "admin/backups_hub.html", context)


def recovery_key_generate(request):
    if not request.user.is_authenticated:
        return redirect("admin:login")

    credential = RecoveryCredential.objects.filter(user=request.user).first()

    if request.method == "POST":
        recovery_key = generate_recovery_key()
        RecoveryCredential.objects.update_or_create(
            user=request.user,
            defaults={"recovery_key_hash": hash_recovery_key(recovery_key)},
        )

        messages.warning(
            request,
            "Save this recovery key now. HolyFHIR cannot show it again.",
        )
        return render(
            request,
            "admin/recovery_key_generated.html",
            {
                **admin.site.each_context(request),
                "title": "Recovery Key Generated",
                "recovery_key": recovery_key,
            },
        )

    context = {
        **admin.site.each_context(request),
        "title": "Generate Recovery Key",
        "has_existing_key": credential is not None,
    }
    return render(request, "admin/recovery_key_generate_confirm.html", context)


def clinical_care_team_directory(request):
    cards = [
        {
            "title": "Care Teams",
            "description": "Manage patient care-team records imported from FHIR or entered locally.",
            "url": reverse("admin:clinical_careteam_changelist"),
            "icon": "fas fa-user-friends",
            "count": CareTeam.objects.count(),
            "count_label": "managed record",
        },
        {
            "title": "Practitioners",
            "description": "Manage clinicians and other people involved in care.",
            "url": reverse("admin:clinical_practitioner_changelist"),
            "icon": "fas fa-user-md",
            "count": Practitioner.objects.count(),
            "count_label": "managed record",
        },
        {
            "title": "Organizations",
            "description": "Manage facilities, practices, departments, and other care organizations.",
            "url": reverse("admin:clinical_organization_changelist"),
            "icon": "fas fa-hospital",
            "count": Organization.objects.count(),
            "count_label": "managed record",
        },
        {
            "title": "Locations",
            "description": "Manage clinics, hospitals, rooms, and other care sites.",
            "url": reverse("admin:clinical_location_changelist"),
            "icon": "fas fa-map-marker-alt",
            "count": Location.objects.count(),
            "count_label": "managed record",
        },
    ]

    context = {
        **admin.site.each_context(request),
        "title": "Care Team",
        "directory_cards": cards,
    }
    return render(request, "admin/clinical_care_team_directory.html", context)


def clinical_resources_directory(request):
    sections = [
        {
            "title": "Patient Records",
            "cards": [
                {
                    "title": "Conditions",
                    "description": "Problems, diagnoses, and active or historical conditions.",
                    "url": reverse("admin:clinical_condition_changelist"),
                    "icon": "fas fa-heartbeat",
                    "count": Condition.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Allergies",
                    "description": "Allergies, intolerances, reactions, and severity details.",
                    "url": reverse("admin:clinical_allergy_changelist"),
                    "icon": "fas fa-exclamation-triangle",
                    "count": Allergy.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Adverse Events",
                    "description": "Actual or potential harm events, contributors, outcomes, and suspect entities.",
                    "url": reverse("admin:clinical_adverseevent_changelist"),
                    "icon": "fas fa-exclamation-circle",
                    "count": AdverseEvent.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Family History",
                    "description": "Family member relationships, conditions, outcomes, and notes.",
                    "url": reverse("admin:clinical_familymemberhistory_changelist"),
                    "icon": "fas fa-people-arrows",
                    "count": FamilyMemberHistory.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Related People",
                    "description": "Personal contacts involved with a patient, such as family, guardians, or caregivers.",
                    "url": reverse("admin:clinical_relatedperson_changelist"),
                    "icon": "fas fa-address-book",
                    "count": RelatedPerson.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "People",
                    "description": "Shared identity records linking patients, practitioners, and related people.",
                    "url": reverse("admin:clinical_person_changelist"),
                    "icon": "fas fa-user-circle",
                    "count": Person.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Clinical Impressions",
                    "description": "Clinical assessments, summaries, findings, and supporting investigations.",
                    "url": reverse("admin:clinical_clinicalimpression_changelist"),
                    "icon": "fas fa-notes-medical",
                    "count": ClinicalImpression.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Detected Issues",
                    "description": "Imported or entered detected-issue records, such as noted interactions or duplicate therapy.",
                    "url": reverse("admin:clinical_detectedissue_changelist"),
                    "icon": "fas fa-shield-alt",
                    "count": DetectedIssue.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Medications",
                    "description": "Medication requests, statements, dosage text, and status.",
                    "url": reverse("admin:clinical_medication_changelist"),
                    "icon": "fas fa-pills",
                    "count": Medication.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Medication Catalog",
                    "description": "Standalone FHIR Medication definitions used by orders, dispenses, and administrations.",
                    "url": reverse("admin:clinical_medicationcatalog_changelist"),
                    "icon": "fas fa-capsules",
                    "count": MedicationCatalog.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Medication Administrations",
                    "description": "Medication events where a dose was administered to a patient.",
                    "url": reverse(
                        "admin:clinical_medicationadministration_changelist"
                    ),
                    "icon": "fas fa-prescription-bottle",
                    "count": MedicationAdministration.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Medication Dispenses",
                    "description": "Pharmacy or supply events where medication was dispensed.",
                    "url": reverse("admin:clinical_medicationdispense_changelist"),
                    "icon": "fas fa-prescription-bottle-alt",
                    "count": MedicationDispense.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Immunizations",
                    "description": "Vaccines, occurrence dates, lot numbers, and performers.",
                    "url": reverse("admin:clinical_immunization_changelist"),
                    "icon": "fas fa-syringe",
                    "count": Immunization.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Immunization Recommendations",
                    "description": "Vaccine forecasts, recommended timing, and supporting immunization history.",
                    "url": reverse(
                        "admin:clinical_immunizationrecommendation_changelist"
                    ),
                    "icon": "fas fa-calendar-check",
                    "count": ImmunizationRecommendation.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Vitals & Labs",
                    "description": "Observations, vital signs, lab values, and specimen links.",
                    "url": reverse("admin:clinical_observation_changelist"),
                    "icon": "fas fa-chart-line",
                    "count": Observation.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Diagnostic Reports",
                    "description": "Lab, pathology, imaging, and diagnostic reports with results and specimens.",
                    "url": reverse("admin:clinical_diagnosticreport_changelist"),
                    "icon": "fas fa-file-medical-alt",
                    "count": DiagnosticReport.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Flags",
                    "description": "Patient alerts, warnings, and awareness notes.",
                    "url": reverse("admin:clinical_flag_changelist"),
                    "icon": "fas fa-flag",
                    "count": Flag.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Consents",
                    "description": "Treatment, privacy, procedure, vaccine, and other consent directives.",
                    "url": reverse("admin:clinical_consent_changelist"),
                    "icon": "fas fa-file-signature",
                    "count": Consent.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Communications",
                    "description": "Messages or information sent between people, organizations, and patients.",
                    "url": reverse("admin:clinical_communication_changelist"),
                    "icon": "fas fa-comments",
                    "count": Communication.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Questionnaire Responses",
                    "description": "Completed forms, assessments, and patient-entered answers.",
                    "url": reverse("admin:clinical_questionnaireresponse_changelist"),
                    "icon": "fas fa-clipboard-list",
                    "count": QuestionnaireResponse.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "FHIR Lists",
                    "description": "Curated FHIR lists of problems, medications, results, or other records.",
                    "url": reverse("admin:clinical_fhirlist_changelist"),
                    "icon": "fas fa-list",
                    "count": FHIRList.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Risk Assessments",
                    "description": "Imported or entered risk-assessment records, basis records, and mitigation notes.",
                    "url": reverse("admin:clinical_riskassessment_changelist"),
                    "icon": "fas fa-chart-pie",
                    "count": RiskAssessment.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Body Structures",
                    "description": "Anatomical locations, morphology, qualifiers, and body-site descriptions.",
                    "url": reverse("admin:clinical_bodystructure_changelist"),
                    "icon": "fas fa-diagnoses",
                    "count": BodyStructure.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Visits & Actions",
                    "description": "Encounters, visits, facilities, provider text, and summaries.",
                    "url": reverse("admin:clinical_encounter_changelist"),
                    "icon": "fas fa-stethoscope",
                    "count": Encounter.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Devices",
                    "description": "Patient devices, implanted devices, owners, locations, and identifiers.",
                    "url": reverse("admin:clinical_device_changelist"),
                    "icon": "fas fa-laptop-medical",
                    "count": Device.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Device Use",
                    "description": "Statements that a patient uses or used a device.",
                    "url": reverse("admin:clinical_deviceusestatement_changelist"),
                    "icon": "fas fa-notes-medical",
                    "count": DeviceUseStatement.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Groups",
                    "description": "FHIR groups of people, practitioners, devices, medications, or other groups.",
                    "url": reverse("admin:clinical_fhirgroup_changelist"),
                    "icon": "fas fa-layer-group",
                    "count": FHIRGroup.objects.count(),
                    "count_label": "record",
                },
            ],
        },
        {
            "title": "Care Planning",
            "cards": [
                {
                    "title": "Care Teams",
                    "description": "Patient care-team records and structured participants.",
                    "url": reverse("admin:clinical_careteam_changelist"),
                    "icon": "fas fa-user-friends",
                    "count": CareTeam.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Care Plans",
                    "description": "Care plans connected to conditions and care teams.",
                    "url": reverse("admin:clinical_careplan_changelist"),
                    "icon": "fas fa-clipboard-list",
                    "count": CarePlan.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Service Requests",
                    "description": "Orders, referrals, requested services, performers, reasons, and specimens.",
                    "url": reverse("admin:clinical_servicerequest_changelist"),
                    "icon": "fas fa-tasks",
                    "count": ServiceRequest.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Communication Requests",
                    "description": "Requests to convey information to specific recipients.",
                    "url": reverse("admin:clinical_communicationrequest_changelist"),
                    "icon": "fas fa-paper-plane",
                    "count": CommunicationRequest.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Nutrition Orders",
                    "description": "Diet, supplement, oral, and enteral nutrition orders.",
                    "url": reverse("admin:clinical_nutritionorder_changelist"),
                    "icon": "fas fa-utensils",
                    "count": NutritionOrder.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Goals",
                    "description": "Care goals, addressed concerns, targets, outcomes, and status.",
                    "url": reverse("admin:clinical_goal_changelist"),
                    "icon": "fas fa-bullseye",
                    "count": Goal.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Device Requests",
                    "description": "Orders and requests for devices, performers, reasons, and timing.",
                    "url": reverse("admin:clinical_devicerequest_changelist"),
                    "icon": "fas fa-toolbox",
                    "count": DeviceRequest.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Episodes of Care",
                    "description": "Care responsibility intervals, care managers, teams, and referral requests.",
                    "url": reverse("admin:clinical_episodeofcare_changelist"),
                    "icon": "fas fa-project-diagram",
                    "count": EpisodeOfCare.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Procedures",
                    "description": "Completed procedures, actions, performers, and reasons.",
                    "url": reverse("admin:clinical_procedure_changelist"),
                    "icon": "fas fa-procedures",
                    "count": Procedure.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Specimens",
                    "description": "Lab specimens, collection details, and parent specimens.",
                    "url": reverse("admin:clinical_specimen_changelist"),
                    "icon": "fas fa-vial",
                    "count": Specimen.objects.count(),
                    "count_label": "record",
                },
            ],
        },
        {
            "title": "Insurance & Billing",
            "cards": [
                {
                    "title": "Coverages",
                    "description": "Insurance coverage, subscriber IDs, payer details, and benefit classifications.",
                    "url": reverse("admin:clinical_coverage_changelist"),
                    "icon": "fas fa-id-card-alt",
                    "count": Coverage.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Explanations of Benefits",
                    "description": "Adjudicated claims, payer statements, service lines, totals, and payments.",
                    "url": reverse("admin:clinical_explanationofbenefit_changelist"),
                    "icon": "fas fa-file-invoice-dollar",
                    "count": ExplanationOfBenefit.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Claims",
                    "description": "Submitted claims, diagnoses, service lines, coverages, and totals.",
                    "url": reverse("admin:clinical_claim_changelist"),
                    "icon": "fas fa-file-invoice",
                    "count": Claim.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Claim Responses",
                    "description": "Claim adjudication responses, outcomes, totals, payments, and errors.",
                    "url": reverse("admin:clinical_claimresponse_changelist"),
                    "icon": "fas fa-receipt",
                    "count": ClaimResponse.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Accounts",
                    "description": "Billing/account groupings, guarantors, balances, owners, and coverages.",
                    "url": reverse("admin:clinical_account_changelist"),
                    "icon": "fas fa-wallet",
                    "count": Account.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Invoices",
                    "description": "Invoices, line items, participants, payment terms, and totals.",
                    "url": reverse("admin:clinical_invoice_changelist"),
                    "icon": "fas fa-file-invoice-dollar",
                    "count": Invoice.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Charge Items",
                    "description": "Billable charge lines linked to patients, visits, accounts, and services.",
                    "url": reverse("admin:clinical_chargeitem_changelist"),
                    "icon": "fas fa-tags",
                    "count": ChargeItem.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Coverage Eligibility Requests",
                    "description": "Eligibility checks for benefits, validation, discovery, and authorizations.",
                    "url": reverse(
                        "admin:clinical_coverageeligibilityrequest_changelist"
                    ),
                    "icon": "fas fa-clipboard-check",
                    "count": CoverageEligibilityRequest.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Coverage Eligibility Responses",
                    "description": "Eligibility outcomes, benefits, dispositions, and processing errors.",
                    "url": reverse(
                        "admin:clinical_coverageeligibilityresponse_changelist"
                    ),
                    "icon": "fas fa-clipboard-list",
                    "count": CoverageEligibilityResponse.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Enrollment Requests",
                    "description": "Enrollment requests for coverage with insurer, provider, candidate, and coverage links.",
                    "url": reverse("admin:clinical_enrollmentrequest_changelist"),
                    "icon": "fas fa-user-plus",
                    "count": EnrollmentRequest.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Enrollment Responses",
                    "description": "Enrollment outcomes and dispositions returned by responding organizations.",
                    "url": reverse("admin:clinical_enrollmentresponse_changelist"),
                    "icon": "fas fa-reply",
                    "count": EnrollmentResponse.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Payment Notices",
                    "description": "Payment notifications with recipients, statuses, amounts, and dates.",
                    "url": reverse("admin:clinical_paymentnotice_changelist"),
                    "icon": "fas fa-money-check-alt",
                    "count": PaymentNotice.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Payment Reconciliations",
                    "description": "Payment reconciliation details, payment issuer, allocations, and process notes.",
                    "url": reverse("admin:clinical_paymentreconciliation_changelist"),
                    "icon": "fas fa-balance-scale",
                    "count": PaymentReconciliation.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Insurance Plans",
                    "description": "Payer plan/product definitions, contacts, coverage areas, and benefit summaries.",
                    "url": reverse("admin:clinical_insuranceplan_changelist"),
                    "icon": "fas fa-umbrella",
                    "count": InsurancePlan.objects.count(),
                    "count_label": "record",
                },
            ],
        },
        {
            "title": "Advanced Clinical",
            "cards": [
                {
                    "title": "Research Studies",
                    "description": "Research study definitions, sponsors, investigators, sites, and focus areas.",
                    "url": reverse("admin:clinical_researchstudy_changelist"),
                    "icon": "fas fa-flask",
                    "count": ResearchStudy.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Research Subjects",
                    "description": "Patient research participation, study arm, period, status, and consent.",
                    "url": reverse("admin:clinical_researchsubject_changelist"),
                    "icon": "fas fa-user-graduate",
                    "count": ResearchSubject.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Media",
                    "description": "Clinical images, videos, audio, and attached media metadata.",
                    "url": reverse("admin:clinical_media_changelist"),
                    "icon": "fas fa-photo-video",
                    "count": Media.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Imaging Studies",
                    "description": "DICOM study, series, instance, modality, and imaging metadata.",
                    "url": reverse("admin:clinical_imagingstudy_changelist"),
                    "icon": "fas fa-x-ray",
                    "count": ImagingStudy.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Molecular Sequences",
                    "description": "Genomic sequence, variant, repository, and quality details.",
                    "url": reverse("admin:clinical_molecularsequence_changelist"),
                    "icon": "fas fa-dna",
                    "count": MolecularSequence.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Medication Knowledge",
                    "description": "Drug knowledge, ingredients, monitoring, contraindications, and classifications.",
                    "url": reverse("admin:clinical_medicationknowledge_changelist"),
                    "icon": "fas fa-book-medical",
                    "count": MedicationKnowledge.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Immunization Evaluations",
                    "description": "Dose validity evaluations for immunization events and target diseases.",
                    "url": reverse("admin:clinical_immunizationevaluation_changelist"),
                    "icon": "fas fa-check-circle",
                    "count": ImmunizationEvaluation.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Vision Prescriptions",
                    "description": "Glasses and contact lens prescriptions with lens specifications.",
                    "url": reverse("admin:clinical_visionprescription_changelist"),
                    "icon": "fas fa-glasses",
                    "count": VisionPrescription.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Request Groups",
                    "description": "Grouped or conditional care requests and planned actions.",
                    "url": reverse("admin:clinical_requestgroup_changelist"),
                    "icon": "fas fa-stream",
                    "count": RequestGroup.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Guidance Responses",
                    "description": "Decision-support responses, outputs, and data requirements.",
                    "url": reverse("admin:clinical_guidanceresponse_changelist"),
                    "icon": "fas fa-route",
                    "count": GuidanceResponse.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Supply Requests",
                    "description": "Requests for medication, device, or supply movement.",
                    "url": reverse("admin:clinical_supplyrequest_changelist"),
                    "icon": "fas fa-box-open",
                    "count": SupplyRequest.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Supply Deliveries",
                    "description": "Supply dispense or delivery events and receivers.",
                    "url": reverse("admin:clinical_supplydelivery_changelist"),
                    "icon": "fas fa-truck",
                    "count": SupplyDelivery.objects.count(),
                    "count_label": "record",
                },
            ],
        },
        {
            "title": "Quality Reporting & Testing",
            "cards": [
                {
                    "title": "Libraries",
                    "description": "Reusable logic libraries, content attachments, dependencies, and related artifacts.",
                    "url": reverse("admin:clinical_library_changelist"),
                    "icon": "fas fa-book",
                    "count": Library.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Plan Definitions",
                    "description": "Clinical protocols, order sets, workflow definitions, goals, and actions.",
                    "url": reverse("admin:clinical_plandefinition_changelist"),
                    "icon": "fas fa-project-diagram",
                    "count": PlanDefinition.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Measures",
                    "description": "Quality measure definitions, scoring, groups, populations, and stratifiers.",
                    "url": reverse("admin:clinical_measure_changelist"),
                    "icon": "fas fa-chart-bar",
                    "count": Measure.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Measure Reports",
                    "description": "Measure evaluation reports, scores, populations, and evaluated resources.",
                    "url": reverse("admin:clinical_measurereport_changelist"),
                    "icon": "fas fa-poll",
                    "count": MeasureReport.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Test Scripts",
                    "description": "FHIR test scripts, fixtures, operations, and assertions.",
                    "url": reverse("admin:clinical_testscript_changelist"),
                    "icon": "fas fa-vial",
                    "count": TestScript.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Test Reports",
                    "description": "FHIR test execution results, participants, actions, scores, and outcomes.",
                    "url": reverse("admin:clinical_testreport_changelist"),
                    "icon": "fas fa-clipboard-check",
                    "count": TestReport.objects.count(),
                    "count_label": "record",
                },
            ],
        },
        {
            "title": "Definitions & Catalogs",
            "cards": [
                {
                    "title": "Capability Statements",
                    "description": "FHIR server/app capability metadata, formats, versions, and REST interactions.",
                    "url": reverse("admin:clinical_capabilitystatement_changelist"),
                    "icon": "fas fa-server",
                    "count": CapabilityStatement.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Structure Definitions",
                    "description": "FHIR profiles, extensions, logical models, base definitions, and element summaries.",
                    "url": reverse("admin:clinical_structuredefinition_changelist"),
                    "icon": "fas fa-layer-group",
                    "count": StructureDefinition.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Implementation Guides",
                    "description": "FHIR implementation guide package metadata, targeted versions, and definitions.",
                    "url": reverse("admin:clinical_implementationguide_changelist"),
                    "icon": "fas fa-book-open",
                    "count": ImplementationGuide.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Search Parameters",
                    "description": "FHIR search parameter definitions, base resources, types, and expressions.",
                    "url": reverse("admin:clinical_searchparameter_changelist"),
                    "icon": "fas fa-search",
                    "count": SearchParameter.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Message Definitions",
                    "description": "FHIR messaging definitions, events, focus resources, and response requirements.",
                    "url": reverse("admin:clinical_messagedefinition_changelist"),
                    "icon": "fas fa-envelope-open-text",
                    "count": MessageDefinition.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Operation Definitions",
                    "description": "FHIR operations and named queries with parameters and invocation scope.",
                    "url": reverse("admin:clinical_operationdefinition_changelist"),
                    "icon": "fas fa-terminal",
                    "count": OperationDefinition.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Compartment Definitions",
                    "description": "FHIR compartment membership definitions and resource search parameters.",
                    "url": reverse("admin:clinical_compartmentdefinition_changelist"),
                    "icon": "fas fa-boxes",
                    "count": CompartmentDefinition.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Structure Maps",
                    "description": "FHIR mapping definitions, structures, groups, and transformation rules.",
                    "url": reverse("admin:clinical_structuremap_changelist"),
                    "icon": "fas fa-random",
                    "count": StructureMap.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Graph Definitions",
                    "description": "FHIR graph traversal definitions with start resources, profiles, and links.",
                    "url": reverse("admin:clinical_graphdefinition_changelist"),
                    "icon": "fas fa-project-diagram",
                    "count": GraphDefinition.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Example Scenarios",
                    "description": "FHIR documentation scenarios with actors, instances, and processes.",
                    "url": reverse("admin:clinical_examplescenario_changelist"),
                    "icon": "fas fa-theater-masks",
                    "count": ExampleScenario.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Naming Systems",
                    "description": "Identifier namespace metadata with URI, OID, UUID, and other unique IDs.",
                    "url": reverse("admin:clinical_namingsystem_changelist"),
                    "icon": "fas fa-fingerprint",
                    "count": NamingSystem.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Terminology Capabilities",
                    "description": "Terminology server capability metadata, supported code systems, and expansion behavior.",
                    "url": reverse("admin:clinical_terminologycapabilities_changelist"),
                    "icon": "fas fa-language",
                    "count": TerminologyCapabilities.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Activity Definitions",
                    "description": "Reusable activity definitions for orders, tasks, communication, and protocol logic.",
                    "url": reverse("admin:clinical_activitydefinition_changelist"),
                    "icon": "fas fa-play-circle",
                    "count": ActivityDefinition.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Event Definitions",
                    "description": "Reusable event trigger definitions used by knowledge artifacts and workflows.",
                    "url": reverse("admin:clinical_eventdefinition_changelist"),
                    "icon": "fas fa-bolt",
                    "count": EventDefinition.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Specimen Definitions",
                    "description": "Specimen collection and testing definitions, handling requirements, and type details.",
                    "url": reverse("admin:clinical_specimendefinition_changelist"),
                    "icon": "fas fa-vials",
                    "count": SpecimenDefinition.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Code Systems",
                    "description": "Terminology systems with codes, displays, definitions, and hierarchy metadata.",
                    "url": reverse("admin:clinical_codesystem_changelist"),
                    "icon": "fas fa-code-branch",
                    "count": CodeSystem.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Value Sets",
                    "description": "Terminology value set definitions, compose rules, and expansions.",
                    "url": reverse("admin:clinical_valueset_changelist"),
                    "icon": "fas fa-list-ul",
                    "count": ValueSet.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Concept Maps",
                    "description": "Mappings between source and target terminology systems or value sets.",
                    "url": reverse("admin:clinical_conceptmap_changelist"),
                    "icon": "fas fa-exchange-alt",
                    "count": ConceptMap.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Questionnaires",
                    "description": "Reusable form definitions used by questionnaire responses.",
                    "url": reverse("admin:clinical_questionnaire_changelist"),
                    "icon": "fas fa-clipboard-question",
                    "count": Questionnaire.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Device Definitions",
                    "description": "Device catalog definitions, model details, identifiers, and capabilities.",
                    "url": reverse("admin:clinical_devicedefinition_changelist"),
                    "icon": "fas fa-microchip",
                    "count": DeviceDefinition.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Observation Definitions",
                    "description": "Catalog definitions for observations, result types, methods, and intervals.",
                    "url": reverse("admin:clinical_observationdefinition_changelist"),
                    "icon": "fas fa-ruler-combined",
                    "count": ObservationDefinition.objects.count(),
                    "count_label": "record",
                },
            ],
        },
        {
            "title": "Documents & Security",
            "cards": [
                {
                    "title": "Compositions",
                    "description": "Structured clinical documents with sections, authors, attesters, and events.",
                    "url": reverse("admin:clinical_composition_changelist"),
                    "icon": "fas fa-file-alt",
                    "count": Composition.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Document Manifests",
                    "description": "Document package/index records that group document references and related material.",
                    "url": reverse("admin:clinical_documentmanifest_changelist"),
                    "icon": "fas fa-folder-open",
                    "count": DocumentManifest.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Binary Resources",
                    "description": "Raw or encoded FHIR Binary payloads used by documents, media, and attachments.",
                    "url": reverse("admin:clinical_binaryresource_changelist"),
                    "icon": "fas fa-file-code",
                    "count": BinaryResource.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Audit Events",
                    "description": "Security/system audit events, actors, outcomes, source, and referenced entities.",
                    "url": reverse("admin:clinical_auditevent_changelist"),
                    "icon": "fas fa-user-shield",
                    "count": AuditEvent.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Provenance",
                    "description": "Record source, authorship, agents, entities, and signatures for trust/history.",
                    "url": reverse("admin:clinical_provenance_changelist"),
                    "icon": "fas fa-history",
                    "count": Provenance.objects.count(),
                    "count_label": "record",
                },
            ],
        },
        {
            "title": "Workflow & Scheduling",
            "cards": [
                {
                    "title": "Tasks",
                    "description": "FHIR workflow tasks, owners, requesters, focus records, and restrictions.",
                    "url": reverse("admin:clinical_task_changelist"),
                    "icon": "fas fa-tasks",
                    "count": Task.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Appointments",
                    "description": "Planned appointments with participants, timing, service categories, and reasons.",
                    "url": reverse("admin:clinical_appointment_changelist"),
                    "icon": "fas fa-calendar-check",
                    "count": Appointment.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Appointment Responses",
                    "description": "Participant acceptance, decline, tentative, and needs-action responses.",
                    "url": reverse("admin:clinical_appointmentresponse_changelist"),
                    "icon": "fas fa-calendar-alt",
                    "count": AppointmentResponse.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Schedules",
                    "description": "Availability schedules for actors such as practitioners, locations, and services.",
                    "url": reverse("admin:clinical_schedule_changelist"),
                    "icon": "fas fa-calendar",
                    "count": Schedule.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Slots",
                    "description": "Bookable time slots attached to schedules, with status and appointment type.",
                    "url": reverse("admin:clinical_slot_changelist"),
                    "icon": "fas fa-clock",
                    "count": Slot.objects.count(),
                    "count_label": "record",
                },
            ],
        },
        {
            "title": "Directory",
            "cards": [
                {
                    "title": "Practitioners",
                    "description": "Clinicians and other people involved in care.",
                    "url": reverse("admin:clinical_practitioner_changelist"),
                    "icon": "fas fa-user-md",
                    "count": Practitioner.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Practitioner Roles",
                    "description": "Practitioner roles by organization, specialty, dates, and locations.",
                    "url": reverse("admin:clinical_practitionerrole_changelist"),
                    "icon": "fas fa-id-badge",
                    "count": PractitionerRole.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Healthcare Services",
                    "description": "Services offered by organizations and locations, including specialties and contacts.",
                    "url": reverse("admin:clinical_healthcareservice_changelist"),
                    "icon": "fas fa-clinic-medical",
                    "count": HealthcareService.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Organization Affiliations",
                    "description": "Relationships between organizations, participating organizations, and services.",
                    "url": reverse("admin:clinical_organizationaffiliation_changelist"),
                    "icon": "fas fa-handshake",
                    "count": OrganizationAffiliation.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Endpoints",
                    "description": "Technical service endpoints for exchange, messaging, or directory connectivity.",
                    "url": reverse("admin:clinical_endpoint_changelist"),
                    "icon": "fas fa-plug",
                    "count": Endpoint.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Substances",
                    "description": "Substance catalog entries used by medications, allergies, labs, and ingredients.",
                    "url": reverse("admin:clinical_substance_changelist"),
                    "icon": "fas fa-flask",
                    "count": Substance.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Device Metrics",
                    "description": "Device measurement channels, units, operational status, and calibration summaries.",
                    "url": reverse("admin:clinical_devicemetric_changelist"),
                    "icon": "fas fa-tachometer-alt",
                    "count": DeviceMetric.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Organizations",
                    "description": "Facilities, practices, departments, and care organizations.",
                    "url": reverse("admin:clinical_organization_changelist"),
                    "icon": "fas fa-hospital",
                    "count": Organization.objects.count(),
                    "count_label": "record",
                },
                {
                    "title": "Locations",
                    "description": "Clinics, hospitals, rooms, and care sites.",
                    "url": reverse("admin:clinical_location_changelist"),
                    "icon": "fas fa-map-marker-alt",
                    "count": Location.objects.count(),
                    "count_label": "record",
                },
            ],
        },
    ]

    context = {
        **admin.site.each_context(request),
        "title": "Clinical Resources",
        "directory_sections": sections,
    }
    return render(request, "admin/clinical_resource_browser.html", context)


def patient_resources_directory(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)

    def card(title, model, admin_model_name, description, icon):
        count = model.objects.filter(patient=patient).count()
        return {
            "title": title,
            "description": description,
            "url": f"{reverse(f'admin:{admin_model_name}_changelist')}?patient__id__exact={patient.pk}",
            "icon": icon,
            "count": count,
            "count_label": "record",
        }

    sections = [
        {
            "title": "Core Chart",
            "cards": [
                card(
                    "Conditions",
                    Condition,
                    "clinical_condition",
                    "Problems, diagnoses, and condition history.",
                    "fas fa-heartbeat",
                ),
                card(
                    "Allergies",
                    Allergy,
                    "clinical_allergy",
                    "Allergies, intolerances, reactions, and severity.",
                    "fas fa-exclamation-triangle",
                ),
                card(
                    "Medications",
                    Medication,
                    "clinical_medication",
                    "Medication requests/statements and dosage text.",
                    "fas fa-pills",
                ),
                card(
                    "Immunizations",
                    Immunization,
                    "clinical_immunization",
                    "Vaccines, dates, lots, and performers.",
                    "fas fa-syringe",
                ),
                card(
                    "Vitals & Labs",
                    Observation,
                    "clinical_observation",
                    "Observations, vital signs, lab values, and results.",
                    "fas fa-chart-line",
                ),
                card(
                    "Diagnostic Reports",
                    DiagnosticReport,
                    "clinical_diagnosticreport",
                    "Lab, pathology, imaging, and diagnostic reports.",
                    "fas fa-file-medical-alt",
                ),
                card(
                    "Documents",
                    ClinicalDocument,
                    "documents_clinicaldocument",
                    "Clinical documents and imported document references.",
                    "fas fa-file-pdf",
                ),
            ],
        },
        {
            "title": "Care & Events",
            "cards": [
                card(
                    "Visits & Actions",
                    Encounter,
                    "clinical_encounter",
                    "Encounters, visits, facilities, providers, and summaries.",
                    "fas fa-stethoscope",
                ),
                card(
                    "Episodes of Care",
                    EpisodeOfCare,
                    "clinical_episodeofcare",
                    "Longer care intervals and care responsibility.",
                    "fas fa-project-diagram",
                ),
                card(
                    "Care Teams",
                    CareTeam,
                    "clinical_careteam",
                    "Care teams and structured participants.",
                    "fas fa-user-friends",
                ),
                card(
                    "Care Plans",
                    CarePlan,
                    "clinical_careplan",
                    "Care plans connected to concerns and teams.",
                    "fas fa-clipboard-list",
                ),
                card(
                    "Goals",
                    Goal,
                    "clinical_goal",
                    "Care goals, targets, outcomes, and status.",
                    "fas fa-bullseye",
                ),
                card(
                    "Service Requests",
                    ServiceRequest,
                    "clinical_servicerequest",
                    "Orders, referrals, requested services, and reasons.",
                    "fas fa-tasks",
                ),
                card(
                    "Tasks",
                    Task,
                    "clinical_task",
                    "Workflow tasks, owners, focus records, and status.",
                    "fas fa-tasks",
                ),
                card(
                    "Appointments",
                    Appointment,
                    "clinical_appointment",
                    "Appointments, participants, timing, and reasons.",
                    "fas fa-calendar-check",
                ),
                card(
                    "Appointment Responses",
                    AppointmentResponse,
                    "clinical_appointmentresponse",
                    "Participant appointment responses and comments.",
                    "fas fa-calendar-alt",
                ),
                card(
                    "Schedules",
                    Schedule,
                    "clinical_schedule",
                    "Availability schedules connected to this patient when applicable.",
                    "fas fa-calendar",
                ),
                card(
                    "Procedures",
                    Procedure,
                    "clinical_procedure",
                    "Completed procedures, actions, performers, and reasons.",
                    "fas fa-procedures",
                ),
                card(
                    "Specimens",
                    Specimen,
                    "clinical_specimen",
                    "Lab specimens, collection details, and parent specimens.",
                    "fas fa-vial",
                ),
            ],
        },
        {
            "title": "Safety, Risk & Context",
            "cards": [
                card(
                    "Adverse Events",
                    AdverseEvent,
                    "clinical_adverseevent",
                    "Actual or potential harm events and suspect entities.",
                    "fas fa-exclamation-circle",
                ),
                card(
                    "Detected Issues",
                    DetectedIssue,
                    "clinical_detectedissue",
                    "Imported or entered detected-issue records.",
                    "fas fa-shield-alt",
                ),
                card(
                    "Risk Assessments",
                    RiskAssessment,
                    "clinical_riskassessment",
                    "Imported or entered risk-assessment records, basis records, and mitigation notes.",
                    "fas fa-chart-pie",
                ),
                card(
                    "Clinical Impressions",
                    ClinicalImpression,
                    "clinical_clinicalimpression",
                    "Clinical assessments, findings, and investigations.",
                    "fas fa-notes-medical",
                ),
                card(
                    "Family History",
                    FamilyMemberHistory,
                    "clinical_familymemberhistory",
                    "Family member relationships, conditions, and outcomes.",
                    "fas fa-people-arrows",
                ),
                card(
                    "Body Structures",
                    BodyStructure,
                    "clinical_bodystructure",
                    "Anatomical locations, morphology, and body-site detail.",
                    "fas fa-diagnoses",
                ),
                card(
                    "Flags",
                    Flag,
                    "clinical_flag",
                    "Patient alerts, warnings, and awareness notes.",
                    "fas fa-flag",
                ),
                card(
                    "Consents",
                    Consent,
                    "clinical_consent",
                    "Treatment, privacy, vaccine, and other consent records.",
                    "fas fa-file-signature",
                ),
            ],
        },
        {
            "title": "Insurance & Billing",
            "cards": [
                card(
                    "Coverages",
                    Coverage,
                    "clinical_coverage",
                    "Insurance coverage, subscriber IDs, payer details, and benefit classifications.",
                    "fas fa-id-card-alt",
                ),
                card(
                    "Explanations of Benefits",
                    ExplanationOfBenefit,
                    "clinical_explanationofbenefit",
                    "Adjudicated claims, payer statements, totals, and payments.",
                    "fas fa-file-invoice-dollar",
                ),
                card(
                    "Coverage Eligibility Requests",
                    CoverageEligibilityRequest,
                    "clinical_coverageeligibilityrequest",
                    "Eligibility checks and requested benefits/validation purposes.",
                    "fas fa-clipboard-check",
                ),
                card(
                    "Coverage Eligibility Responses",
                    CoverageEligibilityResponse,
                    "clinical_coverageeligibilityresponse",
                    "Eligibility outcomes, benefits, dispositions, and errors.",
                    "fas fa-clipboard-list",
                ),
                card(
                    "Enrollment Requests",
                    EnrollmentRequest,
                    "clinical_enrollmentrequest",
                    "Coverage enrollment requests and coverage links.",
                    "fas fa-user-plus",
                ),
                card(
                    "Payment Notices",
                    PaymentNotice,
                    "clinical_paymentnotice",
                    "Payment notifications tied to this patient when resolvable.",
                    "fas fa-money-check-alt",
                ),
                card(
                    "Claims",
                    Claim,
                    "clinical_claim",
                    "Submitted claims, service lines, diagnoses, and coverages.",
                    "fas fa-file-invoice",
                ),
                card(
                    "Claim Responses",
                    ClaimResponse,
                    "clinical_claimresponse",
                    "Claim adjudication responses, outcomes, totals, and payments.",
                    "fas fa-receipt",
                ),
                card(
                    "Accounts",
                    Account,
                    "clinical_account",
                    "Billing/account groupings, guarantors, balances, and coverages.",
                    "fas fa-wallet",
                ),
                card(
                    "Invoices",
                    Invoice,
                    "clinical_invoice",
                    "Invoices, line items, payment terms, and totals.",
                    "fas fa-file-invoice-dollar",
                ),
                card(
                    "Charge Items",
                    ChargeItem,
                    "clinical_chargeitem",
                    "Billable charge lines linked to visits, accounts, and services.",
                    "fas fa-tags",
                ),
            ],
        },
        {
            "title": "Devices, Nutrition & Communication",
            "cards": [
                card(
                    "Devices",
                    Device,
                    "clinical_device",
                    "Patient devices, implanted devices, and identifiers.",
                    "fas fa-laptop-medical",
                ),
                card(
                    "Device Requests",
                    DeviceRequest,
                    "clinical_devicerequest",
                    "Orders and requests for devices.",
                    "fas fa-toolbox",
                ),
                card(
                    "Device Use",
                    DeviceUseStatement,
                    "clinical_deviceusestatement",
                    "Statements that a patient uses or used a device.",
                    "fas fa-notes-medical",
                ),
                card(
                    "Medication Administrations",
                    MedicationAdministration,
                    "clinical_medicationadministration",
                    "Medication doses administered to the patient.",
                    "fas fa-prescription-bottle",
                ),
                card(
                    "Medication Dispenses",
                    MedicationDispense,
                    "clinical_medicationdispense",
                    "Medication dispensed or supplied to the patient.",
                    "fas fa-prescription-bottle-alt",
                ),
                card(
                    "Nutrition Orders",
                    NutritionOrder,
                    "clinical_nutritionorder",
                    "Diet, supplement, oral, and enteral nutrition orders.",
                    "fas fa-utensils",
                ),
                card(
                    "Communications",
                    Communication,
                    "clinical_communication",
                    "Messages or information sent about the patient.",
                    "fas fa-comments",
                ),
                card(
                    "Communication Requests",
                    CommunicationRequest,
                    "clinical_communicationrequest",
                    "Requests to convey information.",
                    "fas fa-paper-plane",
                ),
            ],
        },
        {
            "title": "Forms, Lists & FHIR",
            "cards": [
                card(
                    "Questionnaire Responses",
                    QuestionnaireResponse,
                    "clinical_questionnaireresponse",
                    "Completed forms, assessments, and patient-entered answers.",
                    "fas fa-clipboard-list",
                ),
                card(
                    "FHIR Lists",
                    FHIRList,
                    "clinical_fhirlist",
                    "Curated FHIR lists of records for this patient.",
                    "fas fa-list",
                ),
                card(
                    "Compositions",
                    Composition,
                    "clinical_composition",
                    "Structured clinical documents and sections.",
                    "fas fa-file-alt",
                ),
                card(
                    "Document Manifests",
                    DocumentManifest,
                    "clinical_documentmanifest",
                    "Document package/index records.",
                    "fas fa-folder-open",
                ),
                card(
                    "Binary Resources",
                    BinaryResource,
                    "clinical_binaryresource",
                    "Raw FHIR Binary payloads connected to this patient.",
                    "fas fa-file-code",
                ),
                card(
                    "Provenance",
                    Provenance,
                    "clinical_provenance",
                    "Source, authorship, and record trust/history.",
                    "fas fa-history",
                ),
                card(
                    "Audit Events",
                    AuditEvent,
                    "clinical_auditevent",
                    "Security/system audit events linked to this patient.",
                    "fas fa-user-shield",
                ),
                card(
                    "Immunization Recommendations",
                    ImmunizationRecommendation,
                    "clinical_immunizationrecommendation",
                    "Vaccine forecasts and recommended timing.",
                    "fas fa-calendar-check",
                ),
                card(
                    "Related People",
                    RelatedPerson,
                    "clinical_relatedperson",
                    "Family, caregivers, proxies, and patient-related contacts.",
                    "fas fa-address-book",
                ),
                card(
                    "FHIR Snapshots",
                    FHIRResourceSnapshot,
                    "fhir_fhirresourcesnapshot",
                    "Raw imported FHIR resources preserved for this patient.",
                    "fas fa-database",
                ),
                card(
                    "Measure Reports",
                    MeasureReport,
                    "clinical_measurereport",
                    "Patient-linked quality measure reports.",
                    "fas fa-poll",
                ),
                card(
                    "Research Subjects",
                    ResearchSubject,
                    "clinical_researchsubject",
                    "Research participation, study arm, period, status, and consent.",
                    "fas fa-user-graduate",
                ),
            ],
        },
        {
            "title": "Advanced Clinical",
            "cards": [
                card(
                    "Media",
                    Media,
                    "clinical_media",
                    "Clinical images, videos, audio, and attached media metadata.",
                    "fas fa-photo-video",
                ),
                card(
                    "Imaging Studies",
                    ImagingStudy,
                    "clinical_imagingstudy",
                    "DICOM study, series, instance, modality, and imaging metadata.",
                    "fas fa-x-ray",
                ),
                card(
                    "Molecular Sequences",
                    MolecularSequence,
                    "clinical_molecularsequence",
                    "Genomic sequence, variant, repository, and quality details.",
                    "fas fa-dna",
                ),
                card(
                    "Immunization Evaluations",
                    ImmunizationEvaluation,
                    "clinical_immunizationevaluation",
                    "Dose validity evaluations for immunization events.",
                    "fas fa-check-circle",
                ),
                card(
                    "Vision Prescriptions",
                    VisionPrescription,
                    "clinical_visionprescription",
                    "Glasses and contact lens prescriptions.",
                    "fas fa-glasses",
                ),
                card(
                    "Request Groups",
                    RequestGroup,
                    "clinical_requestgroup",
                    "Grouped or conditional care requests and planned actions.",
                    "fas fa-stream",
                ),
                card(
                    "Guidance Responses",
                    GuidanceResponse,
                    "clinical_guidanceresponse",
                    "Decision-support responses and outputs.",
                    "fas fa-route",
                ),
                card(
                    "Supply Requests",
                    SupplyRequest,
                    "clinical_supplyrequest",
                    "Requests for medication, device, or supply movement.",
                    "fas fa-box-open",
                ),
                card(
                    "Supply Deliveries",
                    SupplyDelivery,
                    "clinical_supplydelivery",
                    "Supply dispense or delivery events.",
                    "fas fa-truck",
                ),
            ],
        },
    ]

    context = {
        **admin.site.each_context(request),
        "title": f"{patient} Resources",
        "patient": patient,
        "directory_sections": sections,
    }
    return render(request, "admin/patient_resources_directory.html", context)


def fhir_explorer(request):
    context = {
        **admin.site.each_context(request),
        "title": "FHIR Explorer",
        "directory_sections": build_fhir_explorer_sections(),
    }
    return render(request, "admin/fhir_explorer.html", context)


def new_clinical_resources_directory(request):
    context = {
        **admin.site.each_context(request),
        "title": "All Clinical Resources",
        "directory_sections": build_personal_emr_resource_sections(),
    }
    return render(
        request, "admin/clinical_resource_browser_core_highlight.html", context
    )


def paramedic_patient_view(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)

    context = {
        **admin.site.each_context(request),
        "title": f"Paramedic View: {patient}",
        "patient": patient,
        "allergies": Allergy.objects.filter(patient=patient),
        "conditions": Condition.objects.filter(patient=patient),
        "medications": Medication.objects.filter(patient=patient),
        "observations": Observation.objects.filter(patient=patient).order_by(
            "-effective_datetime"
        )[:12],
        "encounters": Encounter.objects.filter(patient=patient).order_by("-start_time")[
            :5
        ],
        "procedures": Procedure.objects.filter(patient=patient).order_by(
            "-performed_start"
        )[:8],
        "devices": Device.objects.filter(patient=patient),
        "flags": Flag.objects.filter(patient=patient),
        "related_people": RelatedPerson.objects.filter(patient=patient),
        "documents": ClinicalDocument.objects.filter(patient=patient).order_by(
            "-created_at"
        )[:8],
    }

    return render(request, "admin/paramedic_patient_view.html", context)


def fhir_interop_hub(request):
    cards = [
        {
            "title": "FHIR Links",
            "description": "Review connections between local records and FHIR resources.",
            "url": reverse("admin:fhir_fhirlink_changelist"),
            "icon": "fas fa-link",
        },
        {
            "title": "FHIR Resource Snapshots",
            "description": "Inspect imported raw FHIR resources kept for traceability.",
            "url": reverse("admin:fhir_fhirresourcesnapshot_changelist"),
            "icon": "fas fa-database",
        },
        {
            "title": "Get Records from MyChart",
            "description": "Follow the MyChart download guide, then upload the ZIP or FHIR JSON into HolyFHIR.",
            "url": reverse("fhir_import"),
            "icon": "fas fa-question-circle",
        },
        {
            "title": "FHIR Export",
            "description": "Download saved FHIR snapshots as NDJSON files grouped by resource type.",
            "url": reverse("fhir_export"),
            "icon": "fas fa-file-export",
        },
        {
            "title": "FHIR Explorer",
            "description": "Browse FHIR resource models, profiles, and definitions available in the system.",
            "url": reverse("fhir_explorer"),
            "icon": "fas fa-search",
        },
    ]

    context = {
        **admin.site.each_context(request),
        "title": "FHIR / Interop",
        "interop_cards": cards,
    }
    return render(request, "admin/fhir_interop_hub.html", context)
