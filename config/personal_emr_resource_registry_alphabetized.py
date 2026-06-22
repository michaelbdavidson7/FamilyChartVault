"""Personal EMR resource registry for HolyFHIR admin.

Drop this into something like clinical/personal_emr_resource_registry.py.
Use it to power the human-friendly "All Clinical Resources" page.

This is intentionally a curated subset of the full FHIR Explorer. The full
FHIR Explorer can stay exhaustive, while this page focuses on resources a
family/personal EMR user is likely to understand and use.
"""

from django.apps import apps
from django.urls import NoReverseMatch, reverse


PERSONAL_EMR_GROUPS = [
    {
        "title": "Core Chart",
        "icon": "fas fa-notes-medical",
        "resources": [
            {
                "title": "Problems & Conditions",
                "resource": "Condition",
                "model": "clinical.Condition",
                "description": "Diagnoses, problem list items, and active or historical conditions.",
                "icon": "fas fa-heartbeat",
            },
            {
                "title": "Allergies & Intolerances",
                "resource": "AllergyIntolerance",
                "model": "clinical.Allergy",
                "description": "Allergies, intolerances, reactions, severity, and criticality.",
                "icon": "fas fa-exclamation-triangle",
            },
            {
                "title": "Vitals & Lab Results",
                "resource": "Observation",
                "model": "clinical.Observation",
                "description": "Vitals, lab values, measurements, surveys, and other observations.",
                "icon": "fas fa-chart-line",
            },
            {
                "title": "Diagnostic Reports",
                "resource": "DiagnosticReport",
                "model": "clinical.DiagnosticReport",
                "description": "Lab, pathology, imaging, and diagnostic reports with linked results.",
                "icon": "fas fa-file-medical-alt",
            },
            {
                "title": "Visits",
                "resource": "Encounter",
                "model": "clinical.Encounter",
                "description": "Office visits, hospital encounters, ER visits, and other care events.",
                "icon": "fas fa-stethoscope",
            },
            {
                "title": "Procedures",
                "resource": "Procedure",
                "model": "clinical.Procedure",
                "description": "Completed procedures, surgeries, therapies, and clinical actions.",
                "icon": "fas fa-procedures",
            },
            {
                "title": "Care Plans",
                "resource": "CarePlan",
                "model": "clinical.CarePlan",
                "description": "Plans of care connected to problems, goals, and care teams.",
                "icon": "fas fa-clipboard-list",
            },
            {
                "title": "Goals",
                "resource": "Goal",
                "model": "clinical.Goal",
                "description": "Patient goals, targets, outcomes, priorities, and progress.",
                "icon": "fas fa-bullseye",
            },
                        {
                "title": "Medications",
                "resource": "MedicationRequest / MedicationStatement",
                "model": "clinical.Medication",
                "description": "Current and historical medications, dosage text, route, frequency, and status.",
                "icon": "fas fa-pills",
            },
            {
                "title": "Medication Catalog",
                "resource": "Medication",
                "model": "clinical.MedicationCatalog",
                "description": "Standalone medication definitions used by orders, dispenses, and administrations.",
                "icon": "fas fa-capsules",
            },
            {
                "title": "Medication Administrations",
                "resource": "MedicationAdministration",
                "model": "clinical.MedicationAdministration",
                "description": "Medication doses administered to a patient.",
                "icon": "fas fa-prescription-bottle",
            },
            {
                "title": "Medication Dispenses",
                "resource": "MedicationDispense",
                "model": "clinical.MedicationDispense",
                "description": "Pharmacy or supply events where medication was dispensed.",
                "icon": "fas fa-prescription-bottle-alt",
            },
            {
                "title": "Immunizations",
                "resource": "Immunization",
                "model": "clinical.Immunization",
                "description": "Vaccines, dates, lots, manufacturers, and performers.",
                "icon": "fas fa-syringe",
            },
            {
                "title": "Vaccine Recommendations",
                "resource": "ImmunizationRecommendation",
                "model": "clinical.ImmunizationRecommendation",
                "description": "Vaccine forecasts, recommendations, target diseases, and timing.",
                "icon": "fas fa-calendar-check",
            },
            {
                "title": "Vaccine Evaluations",
                "resource": "ImmunizationEvaluation",
                "model": "clinical.ImmunizationEvaluation",
                "description": "Dose validity evaluations and target disease status.",
                "icon": "fas fa-check-circle",
            },
        ],
},{
        "title": "Documents, Forms & Media",
        "icon": "fas fa-folder-open",
        "resources": [
            {
                "title": "Clinical Documents",
                "resource": "DocumentReference",
                "model": "documents.ClinicalDocument",
                "description": "Imported documents, attachments, PDFs, summaries, and source files.",
                "icon": "fas fa-file-pdf",
            },
            {
                "title": "Compositions",
                "resource": "Composition",
                "model": "clinical.Composition",
                "description": "Structured clinical documents with sections, authors, and events.",
                "icon": "fas fa-file-alt",
            },
            {
                "title": "Document Manifests",
                "resource": "DocumentManifest",
                "model": "clinical.DocumentManifest",
                "description": "Document packages or indexes that group related documents.",
                "icon": "fas fa-folder-open",
            },
            {
                "title": "Questionnaire Responses",
                "resource": "QuestionnaireResponse",
                "model": "clinical.QuestionnaireResponse",
                "description": "Completed forms, assessments, screeners, and patient-entered answers.",
                "icon": "fas fa-clipboard-list",
            },
            {
                "title": "Questionnaires",
                "resource": "Questionnaire",
                "model": "clinical.Questionnaire",
                "description": "Reusable form definitions used by questionnaire responses.",
                "icon": "fas fa-clipboard-question",
            },
            {
                "title": "Media",
                "resource": "Media",
                "model": "clinical.Media",
                "description": "Clinical images, videos, audio, and attached media metadata.",
                "icon": "fas fa-photo-video",
            },
            {
                "title": "Binary Resources",
                "resource": "Binary",
                "model": "clinical.BinaryResource",
                "description": "Raw or encoded FHIR Binary payloads used by documents and media.",
                "icon": "fas fa-file-code",
            },
        ],
    },
    {
        "title": "Care, Orders & Scheduling",
        "icon": "fas fa-calendar-check",
        "resources": [
            {
                "title": "Care Teams",
                "resource": "CareTeam",
                "model": "clinical.CareTeam",
                "description": "Care teams and structured participants involved in a patient's care.",
                "icon": "fas fa-user-friends",
            },
            {
                "title": "Service Requests",
                "resource": "ServiceRequest",
                "model": "clinical.ServiceRequest",
                "description": "Orders, referrals, requested services, performers, reasons, and specimens.",
                "icon": "fas fa-tasks",
            },
            {
                "title": "Tasks",
                "resource": "Task",
                "model": "clinical.Task",
                "description": "Workflow tasks, owners, status, input, output, and due context.",
                "icon": "fas fa-tasks",
            },
            {
                "title": "Appointments",
                "resource": "Appointment",
                "model": "clinical.Appointment",
                "description": "Planned appointments with participants, timing, service type, and reasons.",
                "icon": "fas fa-calendar-check",
            },
            {
                "title": "Appointment Responses",
                "resource": "AppointmentResponse",
                "model": "clinical.AppointmentResponse",
                "description": "Accepted, declined, tentative, or needs-action appointment responses.",
                "icon": "fas fa-calendar-alt",
            },
            {
                "title": "Schedules",
                "resource": "Schedule",
                "model": "clinical.Schedule",
                "description": "Availability schedules for patients, practitioners, locations, and services.",
                "icon": "fas fa-calendar",
            },
            {
                "title": "Slots",
                "resource": "Slot",
                "model": "clinical.Slot",
                "description": "Bookable or blocked time slots attached to schedules.",
                "icon": "fas fa-clock",
            },
            {
                "title": "Episodes of Care",
                "resource": "EpisodeOfCare",
                "model": "clinical.EpisodeOfCare",
                "description": "Longer care responsibility intervals, care managers, and related teams.",
                "icon": "fas fa-project-diagram",
            },
            {
                "title": "Request Groups",
                "resource": "RequestGroup",
                "model": "clinical.RequestGroup",
                "description": "Grouped or conditional care requests and planned actions.",
                "icon": "fas fa-stream",
            },
            {
                "title": "Guidance Responses",
                "resource": "GuidanceResponse",
                "model": "clinical.GuidanceResponse",
                "description": "Decision-support responses, outputs, and data requirements.",
                "icon": "fas fa-route",
            },
        ],
    },
    {
        "title": "People & Care Directory",
        "icon": "fas fa-address-book",
        "resources": [
            {
                "title": "Practitioners",
                "resource": "Practitioner",
                "model": "clinical.Practitioner",
                "description": "Doctors, clinicians, and other people involved in care.",
                "icon": "fas fa-user-md",
            },
            {
                "title": "Practitioner Roles",
                "resource": "PractitionerRole",
                "model": "clinical.PractitionerRole",
                "description": "Practitioner roles by organization, specialty, location, and date range.",
                "icon": "fas fa-id-badge",
            },
            {
                "title": "Organizations",
                "resource": "Organization",
                "model": "clinical.Organization",
                "description": "Facilities, practices, departments, payers, and care organizations.",
                "icon": "fas fa-hospital",
            },
            {
                "title": "Locations",
                "resource": "Location",
                "model": "clinical.Location",
                "description": "Clinics, hospitals, rooms, departments, and other care sites.",
                "icon": "fas fa-map-marker-alt",
            },
            {
                "title": "Related People",
                "resource": "RelatedPerson",
                "model": "clinical.RelatedPerson",
                "description": "Family, guardians, caregivers, proxies, and other patient-related people.",
                "icon": "fas fa-address-book",
            },
            {
                "title": "People",
                "resource": "Person",
                "model": "clinical.Person",
                "description": "Identity records linking patients, practitioners, and related people.",
                "icon": "fas fa-user-circle",
            },
            {
                "title": "Healthcare Services",
                "resource": "HealthcareService",
                "model": "clinical.HealthcareService",
                "description": "Services offered by organizations and locations.",
                "icon": "fas fa-clinic-medical",
            },
            {
                "title": "Organization Affiliations",
                "resource": "OrganizationAffiliation",
                "model": "clinical.OrganizationAffiliation",
                "description": "Relationships between organizations, networks, locations, and services.",
                "icon": "fas fa-handshake",
            },
            {
                "title": "Endpoints",
                "resource": "Endpoint",
                "model": "clinical.Endpoint",
                "description": "Technical service endpoints for exchange, messaging, and connectivity.",
                "icon": "fas fa-plug",
            },
        ],
    },
    {
        "title": "Safety, Risk & Context",
        "icon": "fas fa-shield-alt",
        "resources": [
            {
                "title": "Flags",
                "resource": "Flag",
                "model": "clinical.Flag",
                "description": "Patient alerts, warnings, and awareness notes.",
                "icon": "fas fa-flag",
            },
            {
                "title": "Detected Issues",
                "resource": "DetectedIssue",
                "model": "clinical.DetectedIssue",
                "description": "Clinical safety or quality issues such as interactions or duplicate therapy.",
                "icon": "fas fa-shield-alt",
            },
            {
                "title": "Risk Assessments",
                "resource": "RiskAssessment",
                "model": "clinical.RiskAssessment",
                "description": "Risk estimates, predictions, basis records, and mitigation notes.",
                "icon": "fas fa-chart-pie",
            },
            {
                "title": "Adverse Events",
                "resource": "AdverseEvent",
                "model": "clinical.AdverseEvent",
                "description": "Actual or potential harm events, contributors, outcomes, and suspect entities.",
                "icon": "fas fa-exclamation-circle",
            },
            {
                "title": "Clinical Impressions",
                "resource": "ClinicalImpression",
                "model": "clinical.ClinicalImpression",
                "description": "Clinical assessments, summaries, findings, and supporting investigations.",
                "icon": "fas fa-notes-medical",
            },
            {
                "title": "Family History",
                "resource": "FamilyMemberHistory",
                "model": "clinical.FamilyMemberHistory",
                "description": "Family member relationships, conditions, outcomes, and notes.",
                "icon": "fas fa-people-arrows",
            },
            {
                "title": "Consents",
                "resource": "Consent",
                "model": "clinical.Consent",
                "description": "Treatment, privacy, procedure, vaccine, and other consent directives.",
                "icon": "fas fa-file-signature",
            },
            {
                "title": "Provenance",
                "resource": "Provenance",
                "model": "clinical.Provenance",
                "description": "Record source, authorship, agents, entities, signatures, and trust history.",
                "icon": "fas fa-history",
            },
            {
                "title": "Audit Events",
                "resource": "AuditEvent",
                "model": "clinical.AuditEvent",
                "description": "Security and system audit events linked to records and patients.",
                "icon": "fas fa-user-shield",
            },
        ],
    },
    {
        "title": "Devices, Supplies & Nutrition",
        "icon": "fas fa-laptop-medical",
        "resources": [
            {
                "title": "Devices",
                "resource": "Device",
                "model": "clinical.Device",
                "description": "Patient devices, implanted devices, owners, locations, and identifiers.",
                "icon": "fas fa-laptop-medical",
            },
            {
                "title": "Device Requests",
                "resource": "DeviceRequest",
                "model": "clinical.DeviceRequest",
                "description": "Orders and requests for devices, performers, reasons, and timing.",
                "icon": "fas fa-toolbox",
            },
            {
                "title": "Device Use",
                "resource": "DeviceUseStatement",
                "model": "clinical.DeviceUseStatement",
                "description": "Statements that a patient uses or used a device.",
                "icon": "fas fa-notes-medical",
            },
            {
                "title": "Device Metrics",
                "resource": "DeviceMetric",
                "model": "clinical.DeviceMetric",
                "description": "Device measurement channels, units, operational status, and calibration summaries.",
                "icon": "fas fa-tachometer-alt",
            },
            {
                "title": "Body Structures",
                "resource": "BodyStructure",
                "model": "clinical.BodyStructure",
                "description": "Anatomical locations, morphology, qualifiers, and body-site descriptions.",
                "icon": "fas fa-diagnoses",
            },
            {
                "title": "Specimens",
                "resource": "Specimen",
                "model": "clinical.Specimen",
                "description": "Lab specimens, collection details, body site, and parent specimens.",
                "icon": "fas fa-vial",
            },
            {
                "title": "Nutrition Orders",
                "resource": "NutritionOrder",
                "model": "clinical.NutritionOrder",
                "description": "Diet, supplement, oral, and enteral nutrition orders.",
                "icon": "fas fa-utensils",
            },
            {
                "title": "Supply Requests",
                "resource": "SupplyRequest",
                "model": "clinical.SupplyRequest",
                "description": "Requests for medication, device, or supply movement.",
                "icon": "fas fa-box-open",
            },
            {
                "title": "Supply Deliveries",
                "resource": "SupplyDelivery",
                "model": "clinical.SupplyDelivery",
                "description": "Supply dispense or delivery events and receivers.",
                "icon": "fas fa-truck",
            },
            {
                "title": "Substances",
                "resource": "Substance",
                "model": "clinical.Substance",
                "description": "Substance catalog entries used by allergies, medications, labs, and ingredients.",
                "icon": "fas fa-flask",
            },
        ],
    },
    {
        "title": "Insurance & Billing",
        "icon": "fas fa-file-invoice-dollar",
        "resources": [
            {
                "title": "Coverages",
                "resource": "Coverage",
                "model": "clinical.Coverage",
                "description": "Insurance coverage, subscriber IDs, payer details, and benefit classifications.",
                "icon": "fas fa-id-card-alt",
            },
            {
                "title": "Insurance Plans",
                "resource": "InsurancePlan",
                "model": "clinical.InsurancePlan",
                "description": "Payer plan/product definitions, contacts, coverage areas, and benefit summaries.",
                "icon": "fas fa-umbrella",
            },
            {
                "title": "Explanations of Benefits",
                "resource": "ExplanationOfBenefit",
                "model": "clinical.ExplanationOfBenefit",
                "description": "Adjudicated claims, payer statements, service lines, totals, and payments.",
                "icon": "fas fa-file-invoice-dollar",
            },
            {
                "title": "Claims",
                "resource": "Claim",
                "model": "clinical.Claim",
                "description": "Submitted claims, diagnoses, service lines, coverages, and totals.",
                "icon": "fas fa-file-invoice",
            },
            {
                "title": "Claim Responses",
                "resource": "ClaimResponse",
                "model": "clinical.ClaimResponse",
                "description": "Claim adjudication responses, outcomes, totals, payments, and errors.",
                "icon": "fas fa-receipt",
            },
            {
                "title": "Coverage Eligibility Requests",
                "resource": "CoverageEligibilityRequest",
                "model": "clinical.CoverageEligibilityRequest",
                "description": "Eligibility checks for benefits, validation, discovery, and authorizations.",
                "icon": "fas fa-clipboard-check",
            },
            {
                "title": "Coverage Eligibility Responses",
                "resource": "CoverageEligibilityResponse",
                "model": "clinical.CoverageEligibilityResponse",
                "description": "Eligibility outcomes, benefits, dispositions, and processing errors.",
                "icon": "fas fa-clipboard-list",
            },
            {
                "title": "Accounts",
                "resource": "Account",
                "model": "clinical.Account",
                "description": "Billing/account groupings, guarantors, balances, owners, and coverages.",
                "icon": "fas fa-wallet",
            },
            {
                "title": "Invoices",
                "resource": "Invoice",
                "model": "clinical.Invoice",
                "description": "Invoices, line items, participants, payment terms, and totals.",
                "icon": "fas fa-file-invoice-dollar",
            },
            {
                "title": "Charge Items",
                "resource": "ChargeItem",
                "model": "clinical.ChargeItem",
                "description": "Billable charge lines linked to patients, visits, accounts, and services.",
                "icon": "fas fa-tags",
            },
            {
                "title": "Payment Notices",
                "resource": "PaymentNotice",
                "model": "clinical.PaymentNotice",
                "description": "Payment notifications with recipients, statuses, amounts, and dates.",
                "icon": "fas fa-money-check-alt",
            },
            {
                "title": "Payment Reconciliations",
                "resource": "PaymentReconciliation",
                "model": "clinical.PaymentReconciliation",
                "description": "Payment reconciliation details, payment issuer, allocations, and process notes.",
                "icon": "fas fa-balance-scale",
            },
        ],
    },
    {
        "title": "Advanced Personal Records",
        "icon": "fas fa-microscope",
        "resources": [
            {
                "title": "Imaging Studies",
                "resource": "ImagingStudy",
                "model": "clinical.ImagingStudy",
                "description": "DICOM study, series, instance, modality, and imaging metadata.",
                "icon": "fas fa-x-ray",
            },
            {
                "title": "Molecular Sequences",
                "resource": "MolecularSequence",
                "model": "clinical.MolecularSequence",
                "description": "Genomic sequence, variant, repository, and quality details.",
                "icon": "fas fa-dna",
            },
            {
                "title": "Vision Prescriptions",
                "resource": "VisionPrescription",
                "model": "clinical.VisionPrescription",
                "description": "Glasses and contact lens prescriptions with lens specifications.",
                "icon": "fas fa-glasses",
            },
            {
                "title": "FHIR Lists",
                "resource": "List",
                "model": "clinical.FHIRList",
                "description": "Curated FHIR lists of problems, medications, results, or other records.",
                "icon": "fas fa-list",
            },
            {
                "title": "Groups",
                "resource": "Group",
                "model": "clinical.FHIRGroup",
                "description": "FHIR groups of people, practitioners, devices, medications, or other groups.",
                "icon": "fas fa-layer-group",
            },
            {
                "title": "Research Studies",
                "resource": "ResearchStudy",
                "model": "clinical.ResearchStudy",
                "description": "Research study definitions, sponsors, investigators, sites, and focus areas.",
                "icon": "fas fa-flask",
            },
            {
                "title": "Research Subjects",
                "resource": "ResearchSubject",
                "model": "clinical.ResearchSubject",
                "description": "Patient research participation, study arm, period, status, and consent.",
                "icon": "fas fa-user-graduate",
            },
        ],
    },
]


def _split_model_path(model_path):
    app_label, model_name = model_path.split(".", 1)
    return app_label, model_name


def _get_model(model_path):
    app_label, model_name = _split_model_path(model_path)
    return apps.get_model(app_label, model_name)


def _admin_changelist_url(model):
    route_name = f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist"
    try:
        return reverse(route_name)
    except NoReverseMatch:
        return None


def build_personal_emr_resource_sections():
    """Return directory_sections for the curated All Clinical Resources page.

    Shape matches your existing clinical_resources_directory.html and
    fhir_explorer.html templates: sections -> cards.
    """
    sections = []

    for group in PERSONAL_EMR_GROUPS:
        cards = []

        for item in group["resources"]:
            model = None
            url = None
            count = None
            app_label = None
            model_name = None
            admin_model_name = None
            has_model = False
            has_admin_url = False

            try:
                model = _get_model(item["model"])
                app_label = model._meta.app_label
                model_name = model._meta.model_name
                admin_model_name = f"{app_label}_{model_name}"
                has_model = True
                count = model.objects.count()
                url = _admin_changelist_url(model)
                has_admin_url = url is not None
            except Exception:
                pass

            cards.append(
                {
                    "title": item["title"],
                    "resource_type": item["resource"],
                    "model_path": item["model"],
                    "app_label": app_label,
                    "model_name": model_name,
                    "admin_model_name": admin_model_name,
                    "description": item["description"],
                    "url": url,
                    "icon": item.get("icon") or group["icon"],
                    "count": count,
                    "count_label": "record",
                    "has_model": has_model,
                    "has_admin_url": has_admin_url,
                    "support_status": "Personal EMR",
                }
            )

        cards.sort(key=lambda card: card["title"].casefold())

        sections.append(
            {
                "title": group["title"],
                "icon": group["icon"],
                "is_core_chart": group["title"] == "Core Chart",
                "cards": cards,
            }
        )

    sections.sort(key=lambda section: section["title"].casefold())
    return sections
