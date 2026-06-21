import hashlib
import json
from base64 import b64decode
from binascii import Error as BinasciiError
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.dateparse import parse_date, parse_datetime

from clinical.models import (
    Account,
    SubstanceSourceMaterial,
    SubstanceSpecification,
    SubstanceReferenceInformation,
    SubstanceProtein,
    SubstancePolymer,
    SubstanceNucleicAcid,
    MedicinalProductUndesirableEffect,
    MedicinalProductPharmaceutical,
    MedicinalProductPackaged,
    MedicinalProductManufactured,
    MedicinalProductInteraction,
    MedicinalProductIngredient,
    MedicinalProductIndication,
    MedicinalProductContraindication,
    MedicinalProductAuthorization,
    MedicinalProduct,
    RiskEvidenceSynthesis,
    EffectEvidenceSynthesis,
    EvidenceVariable,
    Evidence,
    ResearchElementDefinition,
    ResearchDefinition,
    Contract,
    ChargeItemDefinition,
    VerificationResult,
    BiologicallyDerivedProduct,
    Subscription,
    Parameters,
    OperationOutcome,
    MessageHeader,
    Linkage,
    Basic,
    CatalogEntry,
    ActivityDefinition,
    AdverseEvent,
    Allergy,
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
    BodyStructure,
    CarePlan,
    CareTeam,
    CareTeamParticipant,
    ClinicalImpression,
    ClinicalImpressionFinding,
    CodeSystem,
    ConceptMap,
    EventDefinition,
    ExampleScenario,
    Composition,
    Condition,
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
    FamilyMemberHistoryCondition,
    FHIRGroup,
    FHIRGroupMember,
    FHIRList,
    GraphDefinition,
    Flag,
    GuidanceResponse,
    Goal,
    HealthcareService,
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
    OrganizationAffiliation,
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
    Communication,
    CommunicationRequest,
    Consent,
    Coverage,
    ExplanationOfBenefit,
    InsurancePlan,
    Questionnaire,
    QuestionnaireResponse,
    Provenance,
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
)
from documents.models import ClinicalDocument
from patients.models import PatientProfile

from .models import FHIRLink, FHIRResourceSnapshot

FHIR_COMPACT_RESOURCE_MODELS = {
    "CatalogEntry": CatalogEntry,
    "Basic": Basic,
    "Linkage": Linkage,
    "MessageHeader": MessageHeader,
    "OperationOutcome": OperationOutcome,
    "Parameters": Parameters,
    "Subscription": Subscription,
    "BiologicallyDerivedProduct": BiologicallyDerivedProduct,
    "VerificationResult": VerificationResult,
    "ChargeItemDefinition": ChargeItemDefinition,
    "Contract": Contract,
    "ResearchDefinition": ResearchDefinition,
    "ResearchElementDefinition": ResearchElementDefinition,
    "Evidence": Evidence,
    "EvidenceVariable": EvidenceVariable,
    "EffectEvidenceSynthesis": EffectEvidenceSynthesis,
    "RiskEvidenceSynthesis": RiskEvidenceSynthesis,
    "MedicinalProduct": MedicinalProduct,
    "MedicinalProductAuthorization": MedicinalProductAuthorization,
    "MedicinalProductContraindication": MedicinalProductContraindication,
    "MedicinalProductIndication": MedicinalProductIndication,
    "MedicinalProductIngredient": MedicinalProductIngredient,
    "MedicinalProductInteraction": MedicinalProductInteraction,
    "MedicinalProductManufactured": MedicinalProductManufactured,
    "MedicinalProductPackaged": MedicinalProductPackaged,
    "MedicinalProductPharmaceutical": MedicinalProductPharmaceutical,
    "MedicinalProductUndesirableEffect": MedicinalProductUndesirableEffect,
    "SubstanceNucleicAcid": SubstanceNucleicAcid,
    "SubstancePolymer": SubstancePolymer,
    "SubstanceProtein": SubstanceProtein,
    "SubstanceReferenceInformation": SubstanceReferenceInformation,
    "SubstanceSpecification": SubstanceSpecification,
    "SubstanceSourceMaterial": SubstanceSourceMaterial,
}



SUPPORTED_RESOURCE_TYPES = {
    "Patient",
    "Account",
    "SubstanceSourceMaterial",
    "SubstanceSpecification",
    "SubstanceReferenceInformation",
    "SubstanceProtein",
    "SubstancePolymer",
    "SubstanceNucleicAcid",
    "MedicinalProductUndesirableEffect",
    "MedicinalProductPharmaceutical",
    "MedicinalProductPackaged",
    "MedicinalProductManufactured",
    "MedicinalProductInteraction",
    "MedicinalProductIngredient",
    "MedicinalProductIndication",
    "MedicinalProductContraindication",
    "MedicinalProductAuthorization",
    "MedicinalProduct",
    "RiskEvidenceSynthesis",
    "EffectEvidenceSynthesis",
    "EvidenceVariable",
    "ResearchElementDefinition",
    "ResearchDefinition",
    "Contract",
    "ChargeItemDefinition",
    "VerificationResult",
    "BiologicallyDerivedProduct",
    "Subscription",
    "Parameters",
    "OperationOutcome",
    "MessageHeader",
    "Linkage",
    "Basic",
    "CatalogEntry",
    "ActivityDefinition",
    "AdverseEvent",
    "Appointment",
    "AppointmentResponse",
    "AuditEvent",
    "CapabilityStatement",
    "CodeSystem",
    "CompartmentDefinition",
    "ConceptMap",
    "EventDefinition",
    "ExampleScenario",
    "CoverageEligibilityRequest",
    "CoverageEligibilityResponse",
    "EnrollmentRequest",
    "EnrollmentResponse",
    "Library",
    "Measure",
    "MeasureReport",
    "PaymentNotice",
    "PaymentReconciliation",
    "PlanDefinition",
    "TestScript",
    "TestReport",
    "TerminologyCapabilities",
    "ValueSet",
    "Binary",
    "ChargeItem",
    "Claim",
    "ClaimResponse",
    "Condition",
    "AllergyIntolerance",
    "BodyStructure",
    "ClinicalImpression",
    "DetectedIssue",
    "DeviceDefinition",
    "DiagnosticReport",
    "FamilyMemberHistory",
    "GraphDefinition",
    "Flag",
    "GuidanceResponse",
    "ImagingStudy",
    "List",
    "MedicationStatement",
    "MedicationRequest",
    "Medication",
    "MedicationAdministration",
    "MedicationDispense",
    "MedicationKnowledge",
    "Immunization",
    "ImmunizationEvaluation",
    "ImmunizationRecommendation",
    "ImplementationGuide",
    "Media",
    "MessageDefinition",
    "MolecularSequence",
    "NamingSystem",
    "NutritionOrder",
    "Observation",
    "ObservationDefinition",
    "OperationDefinition",
    "Encounter",
    "CareTeam",
    "CarePlan",
    "Communication",
    "CommunicationRequest",
    "Composition",
    "Consent",
    "Coverage",
    "TestReport",
    "TestScript",
    "PaymentReconciliation",
    "PaymentNotice",
    "MeasureReport",
    "Device",
    "DeviceMetric",
    "DeviceRequest",
    "DeviceUseStatement",
    "DocumentReference",
    "DocumentManifest",
    "Invoice",
    "EpisodeOfCare",
    "Endpoint",
    "Group",
    "Goal",
    "ExplanationOfBenefit",
    "InsurancePlan",
    "HealthcareService",
    "OrganizationAffiliation",
    "PractitionerRole",
    "Person",
    "Provenance",
    "Procedure",
    "Questionnaire",
    "QuestionnaireResponse",
    "RequestGroup",
    "RelatedPerson",
    "ResearchStudy",
    "ResearchSubject",
    "RiskAssessment",
    "Schedule",
    "SearchParameter",
    "ServiceRequest",
    "Slot",
    "Specimen",
    "SpecimenDefinition",
    "StructureDefinition",
    "StructureMap",
    "Substance",
    "SupplyDelivery",
    "SupplyRequest",
    "Task",
    "TerminologyCapabilities",
    "VisionPrescription",
    "Practitioner",
    "Organization",
    "Location",
    "Group",
    "Person",

    "Evidence",}

PATIENTLESS_RESOURCE_TYPES = {
    "Group",
    "Account",
    "SubstanceSourceMaterial",
    "SubstanceSpecification",
    "SubstanceReferenceInformation",
    "SubstanceProtein",
    "SubstancePolymer",
    "SubstanceNucleicAcid",
    "MedicinalProductUndesirableEffect",
    "MedicinalProductPharmaceutical",
    "MedicinalProductPackaged",
    "MedicinalProductManufactured",
    "MedicinalProductInteraction",
    "MedicinalProductIngredient",
    "MedicinalProductIndication",
    "MedicinalProductContraindication",
    "MedicinalProductAuthorization",
    "MedicinalProduct",
    "RiskEvidenceSynthesis",
    "EffectEvidenceSynthesis",
    "EvidenceVariable",
    "ResearchElementDefinition",
    "ResearchDefinition",
    "Contract",
    "ChargeItemDefinition",
    "VerificationResult",
    "BiologicallyDerivedProduct",
    "Subscription",
    "Parameters",
    "OperationOutcome",
    "MessageHeader",
    "Linkage",
    "Basic",
    "CatalogEntry",
    "ActivityDefinition",
    "AuditEvent",
    "CapabilityStatement",
    "CodeSystem",
    "CompartmentDefinition",
    "ConceptMap",
    "EventDefinition",
    "ExampleScenario",
    "GraphDefinition",
    "ImplementationGuide",
    "Library",
    "MessageDefinition",
    "NamingSystem",
    "Measure",
    "MeasureReport",
    "PaymentNotice",
    "PaymentReconciliation",
    "PlanDefinition",
    "TestScript",
    "TestReport",
    "TerminologyCapabilities",
    "ValueSet",
    "Binary",
    "Endpoint",
    "HealthcareService",
    "InsurancePlan",
    "MedicationKnowledge",
    "Medication",
    "OrganizationAffiliation",
    "Person",
    "Practitioner",
    "PractitionerRole",
    "Provenance",
    "Organization",
    "Location",
    "Schedule",
    "SearchParameter",
    "Slot",
    "SpecimenDefinition",
    "StructureDefinition",
    "StructureMap",
    "Substance",
    "DeviceMetric",
    "DeviceDefinition",
    "ObservationDefinition",
    "OperationDefinition",
    "Questionnaire",
    "ResearchStudy",

    "Evidence",}


@dataclass
class FHIRImportResult:
    created: int = 0
    updated: int = 0
    snapshots: int = 0
    unsupported: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def imported(self):
        return self.created + self.updated


def import_fhir_json(payload, source="imported", target_patient=None):
    return import_fhir_payloads([payload], source=source, target_patient=target_patient)


def import_fhir_payloads(payloads, source="imported", target_patient=None):
    resources = []
    for payload in payloads:
        resources.extend(_extract_resources(payload))

    result = FHIRImportResult()
    patient_by_reference = {}

    with transaction.atomic():
        for resource in resources:
            if resource.get("resourceType") == "Patient":
                patient, created = _import_patient(resource, target_patient=target_patient)
                _record_import(result, created)
                _snapshot(resource, patient, source, result)
                _link(resource, patient, "patients.PatientProfile", patient.id, "fhir_to_internal")
                patient_by_reference.update(_patient_references(resource, patient))

        for resource in resources:
            resource_type = resource.get("resourceType")
            if resource_type not in PATIENTLESS_RESOURCE_TYPES:
                continue
            if resource_type not in SUPPORTED_RESOURCE_TYPES:
                continue

            importer = {
                "CatalogEntry": _import_compact_fhir_resource,
                "Basic": _import_compact_fhir_resource,
                "Linkage": _import_compact_fhir_resource,
                "MessageHeader": _import_compact_fhir_resource,
                "OperationOutcome": _import_compact_fhir_resource,
                "Parameters": _import_compact_fhir_resource,
                "Subscription": _import_compact_fhir_resource,
                "BiologicallyDerivedProduct": _import_compact_fhir_resource,
                "VerificationResult": _import_compact_fhir_resource,
                "ChargeItemDefinition": _import_compact_fhir_resource,
                "Contract": _import_compact_fhir_resource,
                "ResearchDefinition": _import_compact_fhir_resource,
                "ResearchElementDefinition": _import_compact_fhir_resource,
                "Evidence": _import_compact_fhir_resource,
                "EvidenceVariable": _import_compact_fhir_resource,
                "EffectEvidenceSynthesis": _import_compact_fhir_resource,
                "RiskEvidenceSynthesis": _import_compact_fhir_resource,
                "MedicinalProduct": _import_compact_fhir_resource,
                "MedicinalProductAuthorization": _import_compact_fhir_resource,
                "MedicinalProductContraindication": _import_compact_fhir_resource,
                "MedicinalProductIndication": _import_compact_fhir_resource,
                "MedicinalProductIngredient": _import_compact_fhir_resource,
                "MedicinalProductInteraction": _import_compact_fhir_resource,
                "MedicinalProductManufactured": _import_compact_fhir_resource,
                "MedicinalProductPackaged": _import_compact_fhir_resource,
                "MedicinalProductPharmaceutical": _import_compact_fhir_resource,
                "MedicinalProductUndesirableEffect": _import_compact_fhir_resource,
                "SubstanceNucleicAcid": _import_compact_fhir_resource,
                "SubstancePolymer": _import_compact_fhir_resource,
                "SubstanceProtein": _import_compact_fhir_resource,
                "SubstanceReferenceInformation": _import_compact_fhir_resource,
                "SubstanceSpecification": _import_compact_fhir_resource,
                "SubstanceSourceMaterial": _import_compact_fhir_resource,
                "Account": _import_account,
                "AuditEvent": _import_audit_event,
                "ActivityDefinition": _import_activity_definition,
                "CapabilityStatement": _import_capability_statement,
                "CompartmentDefinition": _import_compartment_definition,
                "CodeSystem": _import_code_system,
                "ConceptMap": _import_concept_map,
                "EventDefinition": _import_event_definition,
                "ExampleScenario": _import_example_scenario,
                "GraphDefinition": _import_graph_definition,
                "ImplementationGuide": _import_implementation_guide,
                "Library": _import_library,
                "MessageDefinition": _import_message_definition,
                "NamingSystem": _import_naming_system,
                "OperationDefinition": _import_operation_definition,
                "Measure": _import_measure,
                "MeasureReport": _import_measure_report,
                "PaymentNotice": _import_payment_notice,
                "PaymentReconciliation": _import_payment_reconciliation,
                "PlanDefinition": _import_plan_definition,
                "SearchParameter": _import_search_parameter,
                "SpecimenDefinition": _import_specimen_definition,
                "StructureDefinition": _import_structure_definition,
                "StructureMap": _import_structure_map,
                "TestScript": _import_test_script,
                "TestReport": _import_test_report,
                "TerminologyCapabilities": _import_terminology_capabilities,
                "ValueSet": _import_value_set,
                "Binary": _import_binary_resource,
                "DeviceDefinition": _import_device_definition,
                "DeviceMetric": _import_device_metric,
                "Endpoint": _import_endpoint,
                "Group": _import_group,
                "HealthcareService": _import_healthcare_service,
                "InsurancePlan": _import_insurance_plan,
                "MedicationKnowledge": _import_medication_knowledge,
                "Medication": _import_medication_catalog,
                "OrganizationAffiliation": _import_organization_affiliation,
                "Person": _import_person,
                "Practitioner": _import_practitioner,
                "PractitionerRole": _import_practitioner_role,
                "Provenance": _import_provenance,
                "Questionnaire": _import_questionnaire,
                "ResearchStudy": _import_research_study,
                "ObservationDefinition": _import_observation_definition,
                "Organization": _import_organization,
                "Location": _import_location,
                "Schedule": _import_schedule,
                "Slot": _import_slot,
                "Substance": _import_substance,
            }[resource_type]
            patient = _resolve_patient(resource, patient_by_reference, default_patient=target_patient)
            obj, created = importer(resource, patient)
            _record_import(result, created)
            _snapshot(resource, patient, source, result)
            _link(resource, patient, _model_label(obj), obj.id, "fhir_to_internal")

        for resource in resources:
            resource_type = resource.get("resourceType")
            if resource_type == "Patient" or resource_type in PATIENTLESS_RESOURCE_TYPES:
                continue

            patient = _resolve_patient(resource, patient_by_reference, default_patient=target_patient)
            if resource_type not in SUPPORTED_RESOURCE_TYPES:
                result.unsupported += 1
                _snapshot(
                    resource,
                    patient,
                    source,
                    result,
                    import_status=FHIRResourceSnapshot.IMPORT_STATUS_SNAPSHOT_ONLY,
                )
                continue

            if not patient and resource_type not in PATIENTLESS_RESOURCE_TYPES:
                result.errors.append(f"{_resource_label(resource)} could not be linked to a patient.")
                _snapshot(
                    resource,
                    None,
                    source,
                    result,
                    is_valid=False,
                    import_status=FHIRResourceSnapshot.IMPORT_STATUS_INVALID,
                    errors=["Missing or unknown patient reference."],
                )
                continue

            importer = {
                "Condition": _import_condition,
                "AdverseEvent": _import_adverse_event,
                "AllergyIntolerance": _import_allergy,
                "Appointment": _import_appointment,
                "AppointmentResponse": _import_appointment_response,
                "ChargeItem": _import_charge_item,
                "Claim": _import_claim,
                "ClaimResponse": _import_claim_response,
                "BodyStructure": _import_body_structure,
                "ClinicalImpression": _import_clinical_impression,
                "Composition": _import_composition,
                "DetectedIssue": _import_detected_issue,
                "DeviceRequest": _import_device_request,
                "DeviceUseStatement": _import_device_use_statement,
                "DiagnosticReport": _import_diagnostic_report,
                "DocumentManifest": _import_document_manifest,
                "Invoice": _import_invoice,
                "FamilyMemberHistory": _import_family_member_history,
                "Flag": _import_flag,
                "GuidanceResponse": _import_guidance_response,
                "ImagingStudy": _import_imaging_study,
                "List": _import_fhir_list,
                "Media": _import_media,
                "MedicationAdministration": _import_medication_administration,
                "MedicationDispense": _import_medication_dispense,
                "MedicationStatement": _import_medication_statement,
                "MedicationRequest": _import_medication_request,
                "Immunization": _import_immunization,
                "ImmunizationEvaluation": _import_immunization_evaluation,
                "ImmunizationRecommendation": _import_immunization_recommendation,
                "MolecularSequence": _import_molecular_sequence,
                "NutritionOrder": _import_nutrition_order,
                "Observation": _import_observation,
                "Encounter": _import_encounter,
                "CareTeam": _import_care_team,
                "CarePlan": _import_care_plan,
                "Communication": _import_communication,
                "CommunicationRequest": _import_communication_request,
                "Consent": _import_consent,
                "Coverage": _import_coverage,
                "CoverageEligibilityRequest": _import_coverage_eligibility_request,
                "CoverageEligibilityResponse": _import_coverage_eligibility_response,
                "EnrollmentRequest": _import_enrollment_request,
                "EnrollmentResponse": _import_enrollment_response,
                "Device": _import_device,
                "DocumentReference": _import_document_reference,
                "EpisodeOfCare": _import_episode_of_care,
                "ExplanationOfBenefit": _import_explanation_of_benefit,
                "Goal": _import_goal,
                "PractitionerRole": _import_practitioner_role,
                "Procedure": _import_procedure,
                "Provenance": _import_provenance,
                "Questionnaire": _import_questionnaire,
                "ResearchStudy": _import_research_study,
                "QuestionnaireResponse": _import_questionnaire_response,
                "RequestGroup": _import_request_group,
                "RelatedPerson": _import_related_person,
                "ResearchSubject": _import_research_subject,
                "RiskAssessment": _import_risk_assessment,
                "ServiceRequest": _import_service_request,
                "Schedule": _import_schedule,
                "Slot": _import_slot,
                "Specimen": _import_specimen,
                "SupplyDelivery": _import_supply_delivery,
                "SupplyRequest": _import_supply_request,
                "Task": _import_task,
                "VisionPrescription": _import_vision_prescription,
                "Practitioner": _import_practitioner,
                "ObservationDefinition": _import_observation_definition,
                "Organization": _import_organization,
                "Location": _import_location,
            }[resource_type]
            obj, created = importer(resource, patient)
            _record_import(result, created)
            _snapshot(resource, patient, source, result)
            _link(resource, patient, _model_label(obj), obj.id, "fhir_to_internal")

        for resource in resources:
            resource_type = resource.get("resourceType")
            if resource_type == "AdverseEvent":
                _sync_adverse_event_relationships(resource)
            elif resource_type == "BodyStructure":
                pass
            elif resource_type == "ClinicalImpression":
                _sync_clinical_impression_relationships(resource)
            elif resource_type == "DetectedIssue":
                _sync_detected_issue_relationships(resource)
            elif resource_type == "DeviceRequest":
                _sync_device_request_relationships(resource)
            elif resource_type == "DeviceUseStatement":
                _sync_device_use_statement_relationships(resource)
            elif resource_type == "DiagnosticReport":
                _sync_diagnostic_report_relationships(resource)
            elif resource_type == "FamilyMemberHistory":
                _sync_family_member_history_relationships(resource)
            elif resource_type == "Flag":
                _sync_flag_relationships(resource)
            elif resource_type == "Group":
                _sync_group_relationships(resource)
            elif resource_type == "List":
                _sync_fhir_list_relationships(resource)
            elif resource_type == "MedicationAdministration":
                _sync_medication_administration_relationships(resource)
            elif resource_type == "MedicationDispense":
                _sync_medication_dispense_relationships(resource)
            elif resource_type == "Observation":
                _sync_observation_relationships(resource)
            elif resource_type == "Communication":
                _sync_communication_relationships(resource)
            elif resource_type == "CommunicationRequest":
                _sync_communication_request_relationships(resource)
            elif resource_type == "Consent":
                _sync_consent_relationships(resource)
            elif resource_type == "Coverage":
                _sync_coverage_relationships(resource)
            elif resource_type == "Person":
                _sync_person_relationships(resource)
            elif resource_type == "ImmunizationRecommendation":
                _sync_immunization_recommendation_relationships(resource)
            elif resource_type == "Goal":
                _sync_goal_relationships(resource)
            elif resource_type == "QuestionnaireResponse":
                _sync_questionnaire_response_relationships(resource)
            elif resource_type == "CarePlan":
                _sync_care_plan_relationships(resource)
            elif resource_type == "DocumentReference":
                _sync_document_reference_relationships(resource)
            elif resource_type == "Encounter":
                _sync_encounter_relationships(resource)
            elif resource_type == "EpisodeOfCare":
                _sync_episode_of_care_relationships(resource)
            elif resource_type == "ExplanationOfBenefit":
                _sync_explanation_of_benefit_relationships(resource)
            elif resource_type == "PractitionerRole":
                _sync_practitioner_role_relationships(resource)
            elif resource_type == "Procedure":
                _sync_procedure_relationships(resource)
            elif resource_type == "ServiceRequest":
                _sync_service_request_relationships(resource)
            elif resource_type == "RiskAssessment":
                _sync_risk_assessment_relationships(resource)
            elif resource_type == "Specimen":
                _sync_specimen_relationships(resource)

    return result


def loads_fhir_documents(raw, filename="FHIR JSON"):
    if _looks_like_ndjson(filename, raw):
        return _loads_ndjson(raw)
    return [loads_fhir_json(raw)]


def loads_fhir_json(raw):
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("FHIR import must be a JSON object.")
    return payload


def _looks_like_ndjson(filename, raw):
    if filename.lower().endswith(".ndjson"):
        return True
    stripped = raw.strip()
    return "\n" in stripped and not stripped.startswith(("{", "["))


def _loads_ndjson(raw):
    payloads = []
    for line_number, line in enumerate(raw.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid NDJSON on line {line_number}: {exc.msg}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"FHIR NDJSON line {line_number} must be a JSON object.")
        payloads.append(payload)
    if not payloads:
        raise ValueError("FHIR NDJSON file does not contain any resources.")
    return payloads


def _extract_resources(payload):
    resource_type = payload.get("resourceType")
    if resource_type == "Bundle":
        resources = []
        for entry in payload.get("entry", []):
            resource = entry.get("resource") if isinstance(entry, dict) else None
            if isinstance(resource, dict):
                resources.append(resource)
        if not resources:
            raise ValueError("FHIR Bundle does not contain any resources.")
        return resources
    if resource_type:
        return [payload]
    raise ValueError("FHIR JSON must include a resourceType.")


def _import_patient(resource, target_patient=None):
    defaults = _patient_defaults(resource)
    patient = target_patient or _object_for_resource(resource, "patients.PatientProfile")
    if patient:
        if target_patient:
            _fill_blank_patient_fields(patient, defaults)
        else:
            for field, value in defaults.items():
                setattr(patient, field, value)
        patient.save()
        return patient, False

    patient = PatientProfile.objects.create(**defaults)
    return patient, True


def _fill_blank_patient_fields(patient, defaults):
    for field, value in defaults.items():
        if value and not getattr(patient, field):
            setattr(patient, field, value)


def _patient_defaults(resource):
    name = _first(resource.get("name")) or {}
    given = name.get("given") or []
    address = _first(resource.get("address")) or {}
    lines = address.get("line") or []

    return {
        "first_name": _first(given) or "",
        "last_name": name.get("family") or "",
        "date_of_birth": _date(resource.get("birthDate")),
        "sex_at_birth": resource.get("gender") or "",
        "phone": _telecom(resource, "phone"),
        "email": _telecom(resource, "email"),
        "address_line_1": _first(lines) or "",
        "address_line_2": lines[1] if len(lines) > 1 else "",
        "city": address.get("city") or "",
        "state": address.get("state") or "",
        "postal_code": address.get("postalCode") or "",
        "country": address.get("country") or "USA",
    }


def _import_condition(resource, patient):
    obj = _object_for_resource(resource, "clinical.Condition") or Condition(patient=patient)
    obj.patient = patient
    obj.name = _codeable_text(resource.get("code")) or "Unknown condition"
    obj.icd10_code = _coding_code(resource.get("code"), "icd-10") or obj.icd10_code
    obj.snomed_code = _coding_code(resource.get("code"), "snomed") or obj.snomed_code
    obj.clinical_status = _codeable_text(resource.get("clinicalStatus")) or ""
    obj.onset_date = _date(resource.get("onsetDateTime") or resource.get("onsetDate") or resource.get("recordedDate"))
    obj.abatement_date = _date(resource.get("abatementDateTime") or resource.get("abatementDate"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_body_structure(resource, patient):
    obj = _object_for_resource(resource, "clinical.BodyStructure") or BodyStructure(patient=patient)
    obj.patient = patient
    obj.active = bool(resource.get("active", True))
    obj.morphology = _codeable_text(resource.get("morphology")) or ""
    obj.location = _codeable_text(resource.get("location")) or ""
    obj.location_qualifier = ", ".join(
        text for text in (_codeable_text(value) for value in resource.get("locationQualifier") or []) if text
    )
    obj.description = resource.get("description") or ""
    obj.image_summary = "\n".join(_display(image) or str(image) for image in resource.get("image") or [])
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_adverse_event(resource, patient):
    obj = _object_for_resource(resource, "clinical.AdverseEvent") or AdverseEvent(patient=patient)
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.location = _reference_as(resource.get("location"), Location)
    obj.recorder_practitioner = _reference_as(resource.get("recorder"), Practitioner)
    obj.recorder_role = _reference_as(resource.get("recorder"), PractitionerRole)
    obj.actuality = resource.get("actuality") or ""
    obj.category = _codeable_text(_first(resource.get("category"))) or ""
    obj.event = _codeable_text(resource.get("event")) or "Adverse event"
    obj.event_date = _datetime(resource.get("date"))
    obj.detected_date = _datetime(resource.get("detected"))
    obj.recorded_date = _datetime(resource.get("recordedDate"))
    obj.seriousness = _codeable_text(resource.get("seriousness")) or ""
    obj.severity = _codeable_text(resource.get("severity")) or ""
    obj.outcome = _codeable_text(resource.get("outcome")) or ""
    obj.suspect_entity_summary = _adverse_event_suspect_summary(resource)
    obj.causality_summary = _adverse_event_causality_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_adverse_event_relationships(resource, obj)
    return obj, created


def _import_allergy(resource, patient):
    obj = _object_for_resource(resource, "clinical.Allergy") or Allergy(patient=patient)
    reaction = _first(resource.get("reaction")) or {}
    obj.patient = patient
    obj.substance = _codeable_text(resource.get("code")) or "Unknown allergy"
    obj.rxnorm_code = _coding_code(resource.get("code"), "rxnorm") or obj.rxnorm_code
    obj.snomed_code = _coding_code(resource.get("code"), "snomed") or obj.snomed_code
    obj.category = _first(resource.get("category")) or ""
    obj.criticality = resource.get("criticality") or ""
    obj.reaction = _codeable_text(_first(reaction.get("manifestation"))) or ""
    obj.severity = reaction.get("severity") or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_family_member_history(resource, patient):
    obj = _object_for_resource(resource, "clinical.FamilyMemberHistory") or FamilyMemberHistory(patient=patient)
    obj.patient = patient
    obj.status = resource.get("status") or ""
    obj.relationship = _codeable_text(resource.get("relationship")) or "Family member"
    obj.sex = _codeable_text(resource.get("sex")) or ""
    obj.born_date = _date(resource.get("bornDate"))
    obj.born_text = resource.get("bornString") or _age_text(resource.get("bornAge")) or _range_text(resource.get("bornPeriod"))
    obj.age_text = resource.get("ageString") or _age_text(resource.get("ageAge")) or _range_text(resource.get("ageRange"))
    obj.estimated_age = bool(resource.get("estimatedAge", False))
    obj.deceased = resource.get("deceasedBoolean") if "deceasedBoolean" in resource else None
    obj.deceased_date = _date(resource.get("deceasedDate"))
    obj.deceased_text = (
        resource.get("deceasedString")
        or _age_text(resource.get("deceasedAge"))
        or _range_text(resource.get("deceasedRange"))
    )
    obj.reason = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_family_member_history_relationships(resource, obj)
    return obj, created


def _import_medication_statement(resource, patient):
    obj = _object_for_resource(resource, "clinical.Medication") or Medication(patient=patient)
    period = resource.get("effectivePeriod") or {}
    obj.patient = patient
    obj.name = _medication_name(resource) or "Unknown medication"
    obj.rxnorm_code = _coding_code(resource.get("medicationCodeableConcept"), "rxnorm") or obj.rxnorm_code
    obj.dosage_text = _dosage_text(resource)
    obj.status = resource.get("status") or ""
    obj.start_date = _date(period.get("start") or resource.get("effectiveDateTime"))
    obj.end_date = _date(period.get("end"))
    obj.indication = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_medication_request(resource, patient):
    obj = _object_for_resource(resource, "clinical.Medication") or Medication(patient=patient)
    obj.patient = patient
    obj.name = _medication_name(resource) or "Unknown medication"
    obj.rxnorm_code = _coding_code(resource.get("medicationCodeableConcept"), "rxnorm") or obj.rxnorm_code
    obj.dosage_text = _dosage_text(resource)
    obj.status = resource.get("status") or ""
    obj.start_date = _date(resource.get("authoredOn"))
    obj.prescriber = _display(resource.get("requester"))
    obj.indication = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_medication_catalog(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.MedicationCatalog") or MedicationCatalog()
    batch = resource.get("batch") or {}
    obj.manufacturer = _reference_as(resource.get("manufacturer"), Organization)
    obj.name = _codeable_text(resource.get("code")) or "Medication"
    obj.code = _coding_code(resource.get("code"), "") or obj.code
    obj.status = resource.get("status") or ""
    obj.form = _codeable_text(resource.get("form")) or ""
    obj.amount = _ratio_text(resource.get("amount"))
    obj.ingredient_summary = _medication_ingredient_summary(resource)
    obj.batch_lot_number = batch.get("lotNumber") or ""
    obj.batch_expiration_date = _date(batch.get("expirationDate"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_medication_knowledge(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.MedicationKnowledge") or MedicationKnowledge()
    obj.medication = _reference_as(resource.get("code"), MedicationCatalog)
    obj.status = resource.get("status") or ""
    obj.code = _codeable_text(resource.get("code")) or "Medication knowledge"
    obj.dose_form = _codeable_text(resource.get("doseForm")) or ""
    obj.amount = _age_text(resource.get("amount")) or _ratio_text(resource.get("amount"))
    obj.synonym = "\n".join(resource.get("synonym") or [])
    obj.product_type = ", ".join(text for text in (_codeable_text(v) for v in resource.get("productType") or []) if text)
    obj.ingredient_summary = _medication_knowledge_ingredient_summary(resource)
    obj.contraindication_summary = "\n".join(_display(ref) for ref in resource.get("contraindication") or [])
    obj.monitoring_summary = _medication_knowledge_monitoring_summary(resource)
    obj.medicine_classification_summary = _medication_knowledge_classification_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.associated_medications.set([o for o in (_reference_as(ref, MedicationCatalog) for ref in resource.get("associatedMedication") or []) if o])
    return obj, created


def _import_medication_administration(resource, patient):
    obj = _object_for_resource(resource, "clinical.MedicationAdministration") or MedicationAdministration(patient=patient)
    effective_period = resource.get("effectivePeriod") or {}
    dosage = resource.get("dosage") or {}
    dose = dosage.get("dose") or {}
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("context"), Encounter)
    obj.medication = _reference_as(resource.get("medicationReference"), Medication)
    obj.medication_catalog = _reference_as(resource.get("medicationReference"), MedicationCatalog)
    obj.status = resource.get("status") or ""
    obj.medication_text = _codeable_text(resource.get("medicationCodeableConcept")) or _display(resource.get("medicationReference"))
    obj.effective_start = _datetime(resource.get("effectiveDateTime") or effective_period.get("start"))
    obj.effective_end = _datetime(effective_period.get("end"))
    obj.dosage_text = dosage.get("text") or ""
    obj.route = _codeable_text(dosage.get("route")) or ""
    obj.dose_value = _decimal(dose.get("value"))
    obj.dose_unit = dose.get("unit") or dose.get("code") or ""
    obj.performer_practitioner = _reference_as(((_first(resource.get("performer")) or {}).get("actor")), Practitioner)
    obj.performer_role = _reference_as(((_first(resource.get("performer")) or {}).get("actor")), PractitionerRole)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_medication_administration_relationships(resource, obj)
    return obj, created


def _import_medication_dispense(resource, patient):
    obj = _object_for_resource(resource, "clinical.MedicationDispense") or MedicationDispense(patient=patient)
    obj.patient = patient
    obj.medication = _reference_as(resource.get("medicationReference"), Medication)
    obj.medication_catalog = _reference_as(resource.get("medicationReference"), MedicationCatalog)
    obj.performer_practitioner = _reference_as(((_first(resource.get("performer")) or {}).get("actor")), Practitioner)
    obj.performer_organization = _reference_as(((_first(resource.get("performer")) or {}).get("actor")), Organization)
    obj.status = resource.get("status") or ""
    obj.medication_text = _codeable_text(resource.get("medicationCodeableConcept")) or _display(resource.get("medicationReference"))
    obj.quantity = _age_text(resource.get("quantity"))
    obj.days_supply = _age_text(resource.get("daysSupply"))
    obj.when_prepared = _datetime(resource.get("whenPrepared"))
    obj.when_handed_over = _datetime(resource.get("whenHandedOver"))
    obj.dosage_instruction = _dosage_text(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_medication_dispense_relationships(resource, obj)
    return obj, created


def _import_immunization(resource, patient):
    obj = _object_for_resource(resource, "clinical.Immunization") or Immunization(patient=patient)
    obj.patient = patient
    obj.vaccine_name = _codeable_text(resource.get("vaccineCode")) or "Unknown vaccine"
    obj.cvx_code = _coding_code(resource.get("vaccineCode"), "cvx") or obj.cvx_code
    obj.occurrence_date = _date(resource.get("occurrenceDateTime") or resource.get("occurrenceString"))
    obj.lot_number = resource.get("lotNumber") or ""
    obj.manufacturer = _display(resource.get("manufacturer"))
    obj.performer = _display((_first(resource.get("performer")) or {}).get("actor"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_immunization_recommendation(resource, patient):
    obj = _object_for_resource(resource, "clinical.ImmunizationRecommendation") or ImmunizationRecommendation(patient=patient)
    recommendation = _first(resource.get("recommendation")) or {}
    obj.patient = patient
    obj.authority = _reference_as(resource.get("authority"), Organization)
    obj.date = _datetime(resource.get("date"))
    obj.vaccine_code = _codeable_text(_first(recommendation.get("vaccineCode"))) or ""
    obj.target_disease = _codeable_text(recommendation.get("targetDisease")) or ""
    obj.forecast_status = _codeable_text(recommendation.get("forecastStatus")) or ""
    obj.forecast_reason = _codeable_text(_first(recommendation.get("forecastReason"))) or ""
    obj.date_criterion_summary = _immunization_recommendation_date_criteria(resource)
    obj.recommendation_summary = _immunization_recommendation_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_immunization_recommendation_relationships(resource, obj)
    return obj, created


def _import_immunization_evaluation(resource, patient):
    obj = _object_for_resource(resource, "clinical.ImmunizationEvaluation") or ImmunizationEvaluation(patient=patient)
    obj.patient = patient
    obj.immunization = _reference_as(resource.get("immunizationEvent"), Immunization)
    obj.authority = _reference_as(resource.get("authority"), Organization)
    obj.status = resource.get("status") or ""
    obj.target_disease = _codeable_text(resource.get("targetDisease")) or ""
    obj.dose_status = _codeable_text(resource.get("doseStatus")) or ""
    obj.dose_status_reason = ", ".join(text for text in (_codeable_text(v) for v in resource.get("doseStatusReason") or []) if text)
    obj.description = resource.get("description") or ""
    obj.series = resource.get("series") or ""
    obj.dose_number = str(resource.get("doseNumberPositiveInt") or resource.get("doseNumberString") or "")
    obj.series_doses = str(resource.get("seriesDosesPositiveInt") or resource.get("seriesDosesString") or "")
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_observation(resource, patient):
    obj = _object_for_resource(resource, "clinical.Observation") or Observation(patient=patient)
    value_quantity = resource.get("valueQuantity") or {}
    obj.patient = patient
    obj.category = _observation_category(resource)
    obj.name = _codeable_text(resource.get("code")) or "Unknown observation"
    obj.loinc_code = _coding_code(resource.get("code"), "loinc") or obj.loinc_code
    obj.value_string = resource.get("valueString") or _codeable_text(resource.get("valueCodeableConcept")) or ""
    obj.value_quantity = _decimal(value_quantity.get("value"))
    obj.unit = value_quantity.get("unit") or value_quantity.get("code") or ""
    obj.effective_datetime = _datetime(resource.get("effectiveDateTime"))
    obj.interpretation = _codeable_text(_first(resource.get("interpretation"))) or ""
    obj.reference_range = _reference_range(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.specimen = _reference_as(resource.get("specimen"), Specimen)
    if obj.specimen_id:
        obj.save(update_fields=["specimen"])
    return obj, created


def _import_encounter(resource, patient):
    obj = _object_for_resource(resource, "clinical.Encounter") or Encounter(patient=patient)
    period = resource.get("period") or {}
    obj.patient = patient
    obj.encounter_type = _codeable_text(_first(resource.get("type"))) or _codeable_text(resource.get("class")) or ""
    obj.status = resource.get("status") or ""
    obj.start_time = _datetime(period.get("start"))
    obj.end_time = _datetime(period.get("end"))
    obj.provider_name = _display((_first(resource.get("participant")) or {}).get("individual"))
    obj.facility_name = _display(resource.get("serviceProvider"))
    obj.reason = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.summary = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_care_team(resource, patient):
    obj = _object_for_resource(resource, "clinical.CareTeam") or CareTeam(patient=patient)
    period = resource.get("period") or {}
    obj.patient = patient
    obj.name = resource.get("name") or _codeable_text(_first(resource.get("category"))) or "Care Team"
    obj.status = resource.get("status") or ""
    obj.category = _codeable_text(_first(resource.get("category"))) or ""
    obj.participants = _care_team_participants(resource)
    obj.start_date = _date(period.get("start"))
    obj.end_date = _date(period.get("end"))
    obj.reason = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.managing_organizations.set(_care_team_managing_organizations(resource))
    _sync_care_team_participants(resource, obj)
    return obj, created


def _import_care_plan(resource, patient):
    obj = _object_for_resource(resource, "clinical.CarePlan") or CarePlan(patient=patient)
    period = resource.get("period") or {}
    obj.patient = patient
    obj.title = resource.get("title") or _codeable_text(_first(resource.get("category"))) or "Care plan"
    obj.status = resource.get("status") or ""
    obj.intent = resource.get("intent") or ""
    obj.category = _codeable_text(_first(resource.get("category"))) or ""
    obj.description = resource.get("description") or ""
    obj.start_date = _date(period.get("start"))
    obj.end_date = _date(period.get("end"))
    obj.author_display = _display(resource.get("author"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_care_plan_relationships(resource, obj)
    return obj, created


def _import_nutrition_order(resource, patient):
    obj = _object_for_resource(resource, "clinical.NutritionOrder") or NutritionOrder(patient=patient)
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.orderer_practitioner = _reference_as(resource.get("orderer"), Practitioner)
    obj.status = resource.get("status") or ""
    obj.intent = resource.get("intent") or ""
    obj.date_time = _datetime(resource.get("dateTime"))
    obj.allergy_intolerance_summary = "\n".join(_display(ref) for ref in resource.get("allergyIntolerance") or [])
    obj.food_preference_summary = ", ".join(
        text for text in (_codeable_text(value) for value in resource.get("foodPreferenceModifier") or []) if text
    )
    obj.exclude_food_summary = ", ".join(
        text for text in (_codeable_text(value) for value in resource.get("excludeFoodModifier") or []) if text
    )
    obj.oral_diet_summary = _nutrition_oral_diet_summary(resource)
    obj.supplement_summary = _nutrition_supplement_summary(resource)
    obj.enteral_formula_summary = _nutrition_enteral_formula_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_communication(resource, patient):
    obj = _object_for_resource(resource, "clinical.Communication") or Communication(patient=patient)
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.sender_practitioner = _reference_as(resource.get("sender"), Practitioner)
    obj.sender_organization = _reference_as(resource.get("sender"), Organization)
    obj.sender_related_person = _reference_as(resource.get("sender"), RelatedPerson)
    obj.status = resource.get("status") or ""
    obj.category = _codeable_text(_first(resource.get("category"))) or ""
    obj.priority = resource.get("priority") or ""
    obj.medium = _codeable_text(_first(resource.get("medium"))) or ""
    obj.topic = _display(resource.get("topic"))
    obj.sent = _datetime(resource.get("sent"))
    obj.received = _datetime(resource.get("received"))
    obj.reason = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.payload_summary = _payload_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_communication_relationships(resource, obj)
    return obj, created


def _import_communication_request(resource, patient):
    obj = _object_for_resource(resource, "clinical.CommunicationRequest") or CommunicationRequest(patient=patient)
    occurrence_period = resource.get("occurrencePeriod") or {}
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.requester_practitioner = _reference_as(resource.get("requester"), Practitioner)
    obj.sender_practitioner = _reference_as(resource.get("sender"), Practitioner)
    obj.status = resource.get("status") or ""
    obj.category = _codeable_text(_first(resource.get("category"))) or ""
    obj.priority = resource.get("priority") or ""
    obj.medium = _codeable_text(_first(resource.get("medium"))) or ""
    obj.authored_on = _datetime(resource.get("authoredOn"))
    obj.occurrence_start = _datetime(resource.get("occurrenceDateTime") or occurrence_period.get("start"))
    obj.occurrence_end = _datetime(occurrence_period.get("end"))
    obj.reason = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.payload_summary = _payload_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_communication_request_relationships(resource, obj)
    return obj, created


def _import_flag(resource, patient):
    obj = _object_for_resource(resource, "clinical.Flag") or Flag(patient=patient)
    period = resource.get("period") or {}
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.author_practitioner = _reference_as(resource.get("author"), Practitioner)
    obj.author_organization = _reference_as(resource.get("author"), Organization)
    obj.status = resource.get("status") or ""
    obj.category = _codeable_text(_first(resource.get("category"))) or ""
    obj.code = _codeable_text(resource.get("code")) or "Flag"
    obj.start_date = _datetime(period.get("start"))
    obj.end_date = _datetime(period.get("end"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_flag_relationships(resource, obj)
    return obj, created


def _import_fhir_list(resource, patient):
    obj = _object_for_resource(resource, "clinical.FHIRList") or FHIRList(patient=patient)
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.source_practitioner = _reference_as(resource.get("source"), Practitioner)
    obj.source_organization = _reference_as(resource.get("source"), Organization)
    obj.status = resource.get("status") or ""
    obj.mode = resource.get("mode") or ""
    obj.title = resource.get("title") or ""
    obj.code = _codeable_text(resource.get("code")) or ""
    obj.date = _datetime(resource.get("date"))
    obj.ordered_by = _codeable_text(resource.get("orderedBy")) or ""
    obj.empty_reason = _codeable_text(resource.get("emptyReason")) or ""
    obj.entry_summary = _fhir_list_entry_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_fhir_list_relationships(resource, obj)
    return obj, created


def _import_questionnaire_response(resource, patient):
    obj = _object_for_resource(resource, "clinical.QuestionnaireResponse") or QuestionnaireResponse(patient=patient)
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.author_practitioner = _reference_as(resource.get("author"), Practitioner)
    obj.source_patient = _reference_as(resource.get("source"), PatientProfile)
    obj.source_related_person = _reference_as(resource.get("source"), RelatedPerson)
    obj.status = resource.get("status") or ""
    obj.questionnaire = resource.get("questionnaire") or ""
    obj.authored = _datetime(resource.get("authored"))
    obj.item_summary = _questionnaire_item_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_questionnaire_response_relationships(resource, obj)
    return obj, created


def _import_media(resource, patient):
    obj = _object_for_resource(resource, "clinical.Media") or Media(patient=patient)
    created_period = resource.get("createdPeriod") or {}
    content = resource.get("content") or {}
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.operator_practitioner = _reference_as(resource.get("operator"), Practitioner)
    obj.device = _reference_as(resource.get("device"), Device)
    obj.status = resource.get("status") or ""
    obj.media_type = _codeable_text(resource.get("type")) or ""
    obj.modality = _codeable_text(resource.get("modality")) or ""
    obj.view = _codeable_text(resource.get("view")) or ""
    obj.created_datetime = _datetime(resource.get("createdDateTime") or created_period.get("start"))
    obj.issued = _datetime(resource.get("issued"))
    obj.body_site = _codeable_text(resource.get("bodySite")) or ""
    obj.device_name = resource.get("deviceName") or ""
    obj.content_title = content.get("title") or ""
    obj.content_type = content.get("contentType") or ""
    obj.content_url = content.get("url") or ""
    obj.dimension_summary = _media_dimension_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.based_on_service_requests.set([o for o in (_reference_as(ref, ServiceRequest) for ref in resource.get("basedOn") or []) if o])
    return obj, created


def _import_imaging_study(resource, patient):
    obj = _object_for_resource(resource, "clinical.ImagingStudy") or ImagingStudy(patient=patient)
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.referrer_practitioner = _reference_as(resource.get("referrer"), Practitioner)
    obj.status = resource.get("status") or ""
    obj.started = _datetime(resource.get("started"))
    obj.modality_summary = ", ".join(text for text in (_codeable_text(v) for v in resource.get("modality") or []) if text)
    obj.procedure_code = _codeable_text(_first(resource.get("procedureCode"))) or ""
    obj.location_display = _display(resource.get("location"))
    obj.reason = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.description = resource.get("description") or ""
    obj.series_summary = _imaging_series_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.based_on_service_requests.set([o for o in (_reference_as(ref, ServiceRequest) for ref in resource.get("basedOn") or []) if o])
    obj.interpreter_practitioners.set([o for o in (_reference_as(ref, Practitioner) for ref in resource.get("interpreter") or []) if o])
    return obj, created


def _import_molecular_sequence(resource, patient):
    obj = _object_for_resource(resource, "clinical.MolecularSequence") or MolecularSequence(patient=patient)
    obj.patient = patient
    obj.specimen = _reference_as(resource.get("specimen"), Specimen)
    obj.device = _reference_as(resource.get("device"), Device)
    obj.performer_organization = _reference_as(resource.get("performer"), Organization)
    obj.sequence_type = resource.get("type") or ""
    obj.coordinate_system = resource.get("coordinateSystem")
    obj.observed_sequence = resource.get("observedSeq") or ""
    obj.reference_sequence_summary = _molecular_reference_summary(resource)
    obj.variant_summary = _molecular_variant_summary(resource)
    obj.repository_summary = _molecular_repository_summary(resource)
    obj.quality_summary = _molecular_quality_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_vision_prescription(resource, patient):
    obj = _object_for_resource(resource, "clinical.VisionPrescription") or VisionPrescription(patient=patient)
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.prescriber_practitioner = _reference_as(resource.get("prescriber"), Practitioner)
    obj.prescriber_role = _reference_as(resource.get("prescriber"), PractitionerRole)
    obj.status = resource.get("status") or ""
    obj.created_datetime = _datetime(resource.get("created"))
    obj.date_written = _datetime(resource.get("dateWritten"))
    obj.lens_summary = _vision_lens_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_request_group(resource, patient):
    obj = _object_for_resource(resource, "clinical.RequestGroup") or RequestGroup(patient=patient)
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.author_practitioner = _reference_as(resource.get("author"), Practitioner)
    obj.status = resource.get("status") or ""
    obj.intent = resource.get("intent") or ""
    obj.priority = resource.get("priority") or ""
    obj.code = _codeable_text(resource.get("code")) or ""
    obj.authored_on = _datetime(resource.get("authoredOn"))
    obj.reason = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.action_summary = _request_group_action_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.based_on_service_requests.set([o for o in (_reference_as(ref, ServiceRequest) for ref in resource.get("basedOn") or []) if o])
    obj.replaces.set([o for o in (_reference_as(ref, RequestGroup) for ref in resource.get("replaces") or []) if o])
    return obj, created


def _import_guidance_response(resource, patient):
    obj = _object_for_resource(resource, "clinical.GuidanceResponse") or GuidanceResponse(patient=patient)
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.performer_organization = _reference_as(resource.get("performer"), Organization)
    obj.request_identifier = (resource.get("requestIdentifier") or {}).get("value") or ""
    obj.module_uri = resource.get("moduleUri") or resource.get("moduleCanonical") or _codeable_text(resource.get("moduleCodeableConcept")) or ""
    obj.status = resource.get("status") or ""
    obj.reason = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.occurrence_datetime = _datetime(resource.get("occurrenceDateTime"))
    obj.output_parameters = _display(resource.get("outputParameters"))
    obj.result_summary = _display(resource.get("result"))
    obj.data_requirement_summary = _guidance_data_requirement_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_supply_request(resource, patient):
    obj = _object_for_resource(resource, "clinical.SupplyRequest") or SupplyRequest(patient=patient)
    occurrence_period = resource.get("occurrencePeriod") or {}
    obj.patient = patient or _reference_as(resource.get("deliverTo"), PatientProfile)
    obj.requester_practitioner = _reference_as(resource.get("requester"), Practitioner)
    obj.requester_organization = _reference_as(resource.get("requester"), Organization)
    obj.supplier_organization = _reference_as(_first(resource.get("supplier")), Organization)
    obj.deliver_to_location = _reference_as(resource.get("deliverTo"), Location)
    obj.status = resource.get("status") or ""
    obj.category = _codeable_text(resource.get("category")) or ""
    obj.priority = resource.get("priority") or ""
    obj.item = _codeable_text(resource.get("itemCodeableConcept")) or _display(resource.get("itemReference")) or "Supply request"
    obj.quantity = _age_text(resource.get("quantity"))
    obj.authored_on = _datetime(resource.get("authoredOn"))
    obj.occurrence_start = _datetime(resource.get("occurrenceDateTime") or occurrence_period.get("start"))
    obj.occurrence_end = _datetime(occurrence_period.get("end"))
    obj.reason = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.based_on_service_requests.set([o for o in (_reference_as(ref, ServiceRequest) for ref in resource.get("basedOn") or []) if o])
    return obj, created


def _import_supply_delivery(resource, patient):
    obj = _object_for_resource(resource, "clinical.SupplyDelivery") or SupplyDelivery(patient=patient)
    supplied_item = resource.get("suppliedItem") or {}
    occurrence_period = resource.get("occurrencePeriod") or {}
    obj.patient = patient
    obj.supplier_practitioner = _reference_as(resource.get("supplier"), Practitioner)
    obj.supplier_organization = _reference_as(resource.get("supplier"), Organization)
    obj.destination = _reference_as(resource.get("destination"), Location)
    obj.status = resource.get("status") or ""
    obj.delivery_type = _codeable_text(resource.get("type")) or ""
    obj.item = _codeable_text(supplied_item.get("itemCodeableConcept")) or _display(supplied_item.get("itemReference"))
    obj.quantity = _age_text(supplied_item.get("quantity"))
    obj.occurrence_start = _datetime(resource.get("occurrenceDateTime") or occurrence_period.get("start"))
    obj.occurrence_end = _datetime(occurrence_period.get("end"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.based_on_supply_requests.set([o for o in (_reference_as(ref, SupplyRequest) for ref in resource.get("basedOn") or []) if o])
    obj.part_of_deliveries.set([o for o in (_reference_as(ref, SupplyDelivery) for ref in resource.get("partOf") or []) if o])
    obj.receivers.set([o for o in (_reference_as(ref, Practitioner) for ref in resource.get("receiver") or []) if o])
    return obj, created


def _import_provenance(resource, patient):
    obj = _object_for_resource(resource, "clinical.Provenance") or Provenance(patient=patient)
    occurred_period = resource.get("occurredPeriod") or {}
    obj.patient = patient
    obj.location = _reference_as(resource.get("location"), Location)
    obj.target_summary = "\n".join(_display(ref) for ref in resource.get("target") or [])
    obj.activity = _codeable_text(resource.get("activity")) or ""
    obj.occurred_start = _datetime(resource.get("occurredDateTime") or occurred_period.get("start"))
    obj.occurred_end = _datetime(occurred_period.get("end"))
    obj.recorded = _datetime(resource.get("recorded"))
    obj.policy = "\n".join(resource.get("policy") or [])
    obj.reason = ", ".join(text for text in (_codeable_text(v) for v in resource.get("reason") or []) if text)
    obj.agent_summary = _provenance_agent_summary(resource)
    obj.entity_summary = _provenance_entity_summary(resource)
    obj.signature_summary = _signature_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_composition(resource, patient):
    obj = _object_for_resource(resource, "clinical.Composition") or Composition(patient=patient)
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.custodian = _reference_as(resource.get("custodian"), Organization)
    obj.status = resource.get("status") or ""
    obj.composition_type = _codeable_text(resource.get("type")) or ""
    obj.category = ", ".join(text for text in (_codeable_text(v) for v in resource.get("category") or []) if text)
    obj.title = resource.get("title") or obj.composition_type or "Composition"
    obj.date = _datetime(resource.get("date"))
    obj.confidentiality = resource.get("confidentiality") or ""
    obj.section_summary = _composition_section_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.authors_practitioners.set([o for o in (_reference_as(ref, Practitioner) for ref in resource.get("author") or []) if o])
    return obj, created


def _import_document_manifest(resource, patient):
    obj = _object_for_resource(resource, "clinical.DocumentManifest") or DocumentManifest(patient=patient)
    obj.patient = patient
    obj.author_practitioner = _reference_as(_first(resource.get("author")), Practitioner)
    obj.source = resource.get("source") or ""
    obj.status = resource.get("status") or ""
    obj.manifest_type = _codeable_text(resource.get("type")) or ""
    obj.created_datetime = _datetime(resource.get("created"))
    obj.description = resource.get("description") or ""
    obj.content_summary = "\n".join(_display(ref) for ref in resource.get("content") or [])
    obj.related_summary = _document_manifest_related_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_schedule(resource, patient):
    obj = _object_for_resource(resource, "clinical.Schedule") or Schedule(patient=patient)
    horizon = resource.get("planningHorizon") or {}
    obj.patient = patient
    obj.active = bool(resource.get("active", True))
    obj.service_category = _codeable_text(_first(resource.get("serviceCategory"))) or ""
    obj.service_type = _codeable_text(_first(resource.get("serviceType"))) or ""
    obj.specialty = _codeable_text(_first(resource.get("specialty"))) or ""
    obj.planning_horizon_start = _datetime(horizon.get("start"))
    obj.planning_horizon_end = _datetime(horizon.get("end"))
    obj.comment = resource.get("comment") or ""
    created = obj.pk is None
    obj.save()
    actors = resource.get("actor") or []
    obj.actors_practitioners.set([o for o in (_reference_as(ref, Practitioner) for ref in actors) if o])
    obj.actors_locations.set([o for o in (_reference_as(ref, Location) for ref in actors) if o])
    obj.actors_healthcare_services.set([o for o in (_reference_as(ref, HealthcareService) for ref in actors) if o])
    return obj, created


def _import_slot(resource, patient):
    obj = _object_for_resource(resource, "clinical.Slot") or Slot()
    obj.schedule = _reference_as(resource.get("schedule"), Schedule)
    obj.status = resource.get("status") or ""
    obj.service_category = _codeable_text(_first(resource.get("serviceCategory"))) or ""
    obj.service_type = _codeable_text(_first(resource.get("serviceType"))) or ""
    obj.specialty = _codeable_text(_first(resource.get("specialty"))) or ""
    obj.appointment_type = _codeable_text(resource.get("appointmentType")) or ""
    obj.start_time = _datetime(resource.get("start"))
    obj.end_time = _datetime(resource.get("end"))
    obj.overbooked = bool(resource.get("overbooked", False))
    obj.comment = resource.get("comment") or ""
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_appointment(resource, patient):
    obj = _object_for_resource(resource, "clinical.Appointment") or Appointment(patient=patient)
    obj.patient = patient
    obj.status = resource.get("status") or ""
    obj.cancelation_reason = _codeable_text(resource.get("cancelationReason")) or ""
    obj.service_category = _codeable_text(_first(resource.get("serviceCategory"))) or ""
    obj.service_type = _codeable_text(_first(resource.get("serviceType"))) or ""
    obj.appointment_type = _codeable_text(resource.get("appointmentType")) or ""
    obj.reason = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.description = resource.get("description") or ""
    obj.start_time = _datetime(resource.get("start"))
    obj.end_time = _datetime(resource.get("end"))
    obj.minutes_duration = resource.get("minutesDuration")
    obj.participant_summary = _appointment_participant_summary(resource)
    obj.comment = "\n".join(part for part in [resource.get("comment") or "", resource.get("patientInstruction") or ""] if part)
    created = obj.pk is None
    obj.save()
    obj.slots.set([o for o in (_reference_as(ref, Slot) for ref in resource.get("slot") or []) if o])
    obj.participants_practitioners.set([o for o in (_reference_as((p.get("actor") or {}), Practitioner) for p in resource.get("participant") or []) if o])
    obj.participants_locations.set([o for o in (_reference_as((p.get("actor") or {}), Location) for p in resource.get("participant") or []) if o])
    obj.based_on_service_requests.set([o for o in (_reference_as(ref, ServiceRequest) for ref in resource.get("basedOn") or []) if o])
    return obj, created


def _import_appointment_response(resource, patient):
    obj = _object_for_resource(resource, "clinical.AppointmentResponse") or AppointmentResponse(patient=patient)
    obj.appointment = _reference_as(resource.get("appointment"), Appointment)
    obj.patient = patient or _reference_as(resource.get("actor"), PatientProfile)
    obj.actor_practitioner = _reference_as(resource.get("actor"), Practitioner)
    obj.actor_location = _reference_as(resource.get("actor"), Location)
    obj.participant_status = resource.get("participantStatus") or ""
    obj.participant_type = ", ".join(text for text in (_codeable_text(v) for v in resource.get("participantType") or []) if text)
    obj.start_time = _datetime(resource.get("start"))
    obj.end_time = _datetime(resource.get("end"))
    obj.comment = resource.get("comment") or ""
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_task(resource, patient):
    obj = _object_for_resource(resource, "clinical.Task") or Task(patient=patient)
    execution = resource.get("executionPeriod") or {}
    obj.patient = patient or _reference_as(resource.get("for"), PatientProfile)
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.owner_practitioner = _reference_as(resource.get("owner"), Practitioner)
    obj.owner_organization = _reference_as(resource.get("owner"), Organization)
    obj.status = resource.get("status") or ""
    obj.intent = resource.get("intent") or ""
    obj.priority = resource.get("priority") or ""
    obj.code = _codeable_text(resource.get("code")) or ""
    obj.description = resource.get("description") or ""
    obj.authored_on = _datetime(resource.get("authoredOn"))
    obj.last_modified = _datetime(resource.get("lastModified"))
    obj.execution_start = _datetime(execution.get("start"))
    obj.execution_end = _datetime(execution.get("end"))
    obj.input_summary = _task_io_summary(resource, "input")
    obj.output_summary = _task_io_summary(resource, "output")
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.based_on_service_requests.set([o for o in (_reference_as(ref, ServiceRequest) for ref in resource.get("basedOn") or []) if o])
    return obj, created
def _import_audit_event(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.AuditEvent") or AuditEvent(patient=patient)
    obj.patient = patient or _audit_event_patient(resource)
    obj.recorded = _datetime(resource.get("recorded"))
    obj.audit_type = _coding_text(resource.get("type")) or "Audit event"
    obj.subtype = ", ".join(text for text in (_coding_text(value) for value in resource.get("subtype") or []) if text)
    obj.action = resource.get("action") or ""
    obj.outcome = resource.get("outcome") or ""
    obj.outcome_description = resource.get("outcomeDesc") or ""
    obj.agent_summary = _audit_event_agent_summary(resource)
    source = resource.get("source") or {}
    obj.source_observer = _display(source.get("observer"))
    obj.source_type = ", ".join(text for text in (_coding_text(value) for value in source.get("type") or []) if text)
    obj.entity_summary = _audit_event_entity_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created

def _import_account(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.Account") or Account(patient=patient)
    period = resource.get("servicePeriod") or {}
    obj.patient = patient or _reference_as(_first(resource.get("subject")), PatientProfile)
    obj.owner = _reference_as(resource.get("owner"), Organization)
    obj.status = resource.get("status") or ""
    obj.account_type = _codeable_text(resource.get("type")) or ""
    obj.name = resource.get("name") or ""
    obj.description = resource.get("description") or ""
    obj.service_period_start = _date(period.get("start"))
    obj.service_period_end = _date(period.get("end"))
    obj.guarantor_summary = _account_guarantor_summary(resource)
    obj.balance_summary = _account_balance_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    coverage_refs = [(item.get("coverage") or {}) for item in resource.get("coverage") or []]
    obj.coverages.set([o for o in (_reference_as(ref, Coverage) for ref in coverage_refs) if o])
    return obj, created


def _import_claim(resource, patient):
    obj = _object_for_resource(resource, "clinical.Claim") or Claim(patient=patient)
    billable_period = resource.get("billablePeriod") or {}
    obj.patient = patient
    obj.insurer = _reference_as(resource.get("insurer"), Organization)
    obj.provider_practitioner = _reference_as(resource.get("provider"), Practitioner)
    obj.provider_organization = _reference_as(resource.get("provider"), Organization)
    obj.status = resource.get("status") or ""
    obj.claim_type = _codeable_text(resource.get("type")) or ""
    obj.use = resource.get("use") or ""
    obj.priority = _codeable_text(resource.get("priority")) or ""
    obj.billable_period_start = _date(billable_period.get("start"))
    obj.billable_period_end = _date(billable_period.get("end"))
    obj.created_date = _date(resource.get("created"))
    obj.diagnosis_summary = _eob_diagnosis_summary(resource)
    obj.item_summary = _eob_item_summary(resource)
    obj.insurance_summary = _claim_insurance_summary(resource)
    obj.total = _money_text(resource.get("total"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    insurance = resource.get("insurance") or []
    obj.coverages.set([o for o in (_reference_as(item.get("coverage"), Coverage) for item in insurance) if o])
    return obj, created


def _import_claim_response(resource, patient):
    obj = _object_for_resource(resource, "clinical.ClaimResponse") or ClaimResponse(patient=patient)
    obj.patient = patient
    obj.request_claim = _reference_as(resource.get("request"), Claim)
    obj.insurer = _reference_as(resource.get("insurer"), Organization)
    obj.status = resource.get("status") or ""
    obj.response_type = _codeable_text(resource.get("type")) or ""
    obj.use = resource.get("use") or ""
    obj.outcome = resource.get("outcome") or ""
    obj.disposition = resource.get("disposition") or ""
    obj.created_date = _date(resource.get("created"))
    obj.item_summary = _claim_response_item_summary(resource)
    obj.total_summary = _eob_total_summary(resource)
    obj.payment_summary = _eob_payment_summary(resource)
    obj.error_summary = _claim_response_error_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_invoice(resource, patient):
    obj = _object_for_resource(resource, "clinical.Invoice") or Invoice(patient=patient)
    obj.patient = patient or _reference_as(resource.get("subject"), PatientProfile) or _reference_as(resource.get("recipient"), PatientProfile)
    obj.account = _reference_as(resource.get("account"), Account)
    obj.issuer_organization = _reference_as(resource.get("issuer"), Organization)
    obj.status = resource.get("status") or ""
    obj.invoice_type = _codeable_text(resource.get("type")) or ""
    obj.date = _datetime(resource.get("date"))
    obj.participant_summary = _invoice_participant_summary(resource)
    obj.line_item_summary = _invoice_line_item_summary(resource)
    obj.total_net = _money_text(resource.get("totalNet"))
    obj.total_gross = _money_text(resource.get("totalGross"))
    obj.payment_terms = resource.get("paymentTerms") or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_charge_item(resource, patient):
    obj = _object_for_resource(resource, "clinical.ChargeItem") or ChargeItem(patient=patient)
    occurrence_period = resource.get("occurrencePeriod") or {}
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("context"), Encounter)
    obj.account = _reference_as(_first(resource.get("account")), Account)
    obj.status = resource.get("status") or ""
    obj.code = _codeable_text(resource.get("code")) or "Charge item"
    obj.occurrence_datetime = _datetime(resource.get("occurrenceDateTime") or occurrence_period.get("start"))
    obj.quantity = _age_text(resource.get("quantity"))
    obj.factor_override = _decimal(resource.get("factorOverride"))
    obj.price_override = _money_text(resource.get("priceOverride"))
    obj.total_price_component = _charge_item_price_component_summary(resource)
    obj.reason = _codeable_text(_first(resource.get("reason"))) or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.service_requests.set([o for o in (_reference_as(ref, ServiceRequest) for ref in resource.get("service") or []) if o])
    performer_refs = [(item.get("actor") or {}) for item in resource.get("performer") or []]
    obj.performer_practitioners.set([o for o in (_reference_as(ref, Practitioner) for ref in performer_refs) if o])
    return obj, created


def _import_research_study(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.ResearchStudy") or ResearchStudy()
    period = resource.get("period") or {}
    obj.sponsor = _reference_as(resource.get("sponsor"), Organization)
    obj.principal_investigator = _reference_as(resource.get("principalInvestigator"), Practitioner)
    obj.status = resource.get("status") or ""
    obj.title = resource.get("title") or resource.get("name") or "Research study"
    obj.phase = _codeable_text(resource.get("phase")) or ""
    obj.category = ", ".join(text for text in (_codeable_text(value) for value in resource.get("category") or []) if text)
    obj.focus = ", ".join(text for text in (_codeable_text(value) for value in resource.get("focus") or []) if text)
    obj.condition = ", ".join(text for text in (_codeable_text(value) for value in resource.get("condition") or []) if text)
    obj.contact_summary = _research_contact_summary(resource)
    obj.period_start = _date(period.get("start"))
    obj.period_end = _date(period.get("end"))
    obj.description = resource.get("description") or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.sites.set([o for o in (_reference_as(ref, Location) for ref in resource.get("site") or []) if o])
    return obj, created


def _import_research_subject(resource, patient):
    obj = _object_for_resource(resource, "clinical.ResearchSubject") or ResearchSubject(patient=patient)
    period = resource.get("period") or {}
    obj.patient = patient
    obj.study = _reference_as(resource.get("study"), ResearchStudy)
    obj.consent = _reference_as(resource.get("consent"), Consent)
    obj.status = resource.get("status") or ""
    obj.period_start = _date(period.get("start"))
    obj.period_end = _date(period.get("end"))
    obj.assigned_arm = resource.get("assignedArm") or ""
    obj.actual_arm = resource.get("actualArm") or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_device_definition(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.DeviceDefinition") or DeviceDefinition()
    device_name = _first(resource.get("deviceName")) or {}
    obj.manufacturer = _reference_as(resource.get("manufacturerReference"), Organization)
    obj.device_name = device_name.get("name") or ""
    obj.device_type = _codeable_text(resource.get("type")) or ""
    obj.model_number = resource.get("modelNumber") or ""
    obj.version = ", ".join(item.get("value") or "" for item in resource.get("version") or [] if item.get("value"))
    obj.udi_device_identifier = _device_definition_udi_summary(resource)
    obj.specialization_summary = _device_definition_specialization_summary(resource)
    obj.property_summary = _device_definition_property_summary(resource)
    obj.capability_summary = _device_definition_capability_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_observation_definition(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.ObservationDefinition") or ObservationDefinition()
    obj.category = ", ".join(text for text in (_codeable_text(value) for value in resource.get("category") or []) if text)
    obj.code = _codeable_text(resource.get("code")) or "Observation definition"
    obj.permitted_data_type = ", ".join(resource.get("permittedDataType") or [])
    obj.multiple_results_allowed = bool(resource.get("multipleResultsAllowed", False))
    obj.method = _codeable_text(resource.get("method")) or ""
    obj.preferred_report_name = resource.get("preferredReportName") or ""
    obj.quantitative_details = _observation_definition_quantitative_summary(resource)
    obj.qualified_interval_summary = _observation_definition_interval_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_questionnaire(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.Questionnaire") or Questionnaire()
    period = resource.get("effectivePeriod") or {}
    obj.url = resource.get("url") or ""
    obj.version = resource.get("version") or ""
    obj.name = resource.get("name") or ""
    obj.title = resource.get("title") or resource.get("name") or "Questionnaire"
    obj.status = resource.get("status") or ""
    obj.publisher = resource.get("publisher") or ""
    obj.subject_type = ", ".join(resource.get("subjectType") or [])
    obj.approval_date = _date(resource.get("approvalDate"))
    obj.last_review_date = _date(resource.get("lastReviewDate"))
    obj.effective_start = _date(period.get("start"))
    obj.effective_end = _date(period.get("end"))
    obj.item_summary = _questionnaire_definition_item_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created

def _import_compact_fhir_resource(resource, patient=None):
    model_class = FHIR_COMPACT_RESOURCE_MODELS[resource.get("resourceType")]
    django_model = f"clinical.{model_class.__name__}"
    obj = _object_for_resource(resource, django_model) or model_class()
    obj.url = resource.get("url") or ""
    obj.version = resource.get("version") or ""
    obj.name = resource.get("name") or ""
    obj.title = _resource_title(resource)
    obj.status = resource.get("status") or resource.get("clinicalStatus", {}).get("text", "") or ""
    obj.publisher = resource.get("publisher") or ""
    obj.date = _datetime(resource.get("date") or resource.get("authoredOn") or resource.get("issued"))
    obj.description = resource.get("description") or resource.get("purpose") or ""
    obj.summary = _compact_resource_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_metadata_definition(resource, model_class, django_model, default_title, extra_fields=None):
    obj = _object_for_resource(resource, django_model) or model_class()
    if hasattr(obj, "url"):
        obj.url = resource.get("url") or ""
    if hasattr(obj, "version"):
        obj.version = resource.get("version") or ""
    if hasattr(obj, "name"):
        obj.name = resource.get("name") or ""
    if hasattr(obj, "title"):
        obj.title = resource.get("title") or resource.get("name") or default_title
    if hasattr(obj, "status"):
        obj.status = resource.get("status") or ""
    if hasattr(obj, "publisher"):
        obj.publisher = resource.get("publisher") or ""
    if hasattr(obj, "date"):
        obj.date = _datetime(resource.get("date"))
    if hasattr(obj, "description"):
        obj.description = resource.get("description") or ""
    if hasattr(obj, "notes"):
        obj.notes = _notes(resource)
    for field, value in (extra_fields or {}).items():
        setattr(obj, field, value)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_capability_statement(resource, patient=None):
    return _import_metadata_definition(resource, CapabilityStatement, "clinical.CapabilityStatement", "Capability Statement", {
        "kind": resource.get("kind") or "",
        "fhir_version": resource.get("fhirVersion") or "",
        "format_summary": ", ".join((resource.get("format") or []) + (resource.get("patchFormat") or [])),
        "rest_summary": _compact_json(resource.get("rest")),
    })


def _import_structure_definition(resource, patient=None):
    elements = ((resource.get("snapshot") or {}).get("element") or []) + ((resource.get("differential") or {}).get("element") or [])
    return _import_metadata_definition(resource, StructureDefinition, "clinical.StructureDefinition", "Structure Definition", {
        "kind": resource.get("kind") or "",
        "abstract": resource.get("abstract") if "abstract" in resource else None,
        "type_code": resource.get("type") or "",
        "base_definition": resource.get("baseDefinition") or "",
        "derivation": resource.get("derivation") or "",
        "element_summary": _compact_json(elements),
    })


def _import_implementation_guide(resource, patient=None):
    return _import_metadata_definition(resource, ImplementationGuide, "clinical.ImplementationGuide", "Implementation Guide", {
        "package_id": resource.get("packageId") or "",
        "fhir_version_summary": ", ".join(resource.get("fhirVersion") or []),
        "definition_summary": _compact_json(resource.get("definition")),
    })


def _import_search_parameter(resource, patient=None):
    return _import_metadata_definition(resource, SearchParameter, "clinical.SearchParameter", resource.get("code") or "Search Parameter", {
        "code": resource.get("code") or "",
        "base_summary": ", ".join(resource.get("base") or []),
        "search_type": resource.get("type") or "",
        "expression": resource.get("expression") or "",
    })


def _import_message_definition(resource, patient=None):
    return _import_metadata_definition(resource, MessageDefinition, "clinical.MessageDefinition", "Message Definition", {
        "event": _codeable_text(resource.get("eventCoding")) or resource.get("eventUri") or "",
        "category": resource.get("category") or "",
        "response_required": resource.get("responseRequired") or "",
        "focus_summary": _compact_json(resource.get("focus")),
    })


def _import_operation_definition(resource, patient=None):
    return _import_metadata_definition(resource, OperationDefinition, "clinical.OperationDefinition", "Operation Definition", {
        "kind": resource.get("kind") or "",
        "code": resource.get("code") or "",
        "resource_summary": ", ".join(resource.get("resource") or []),
        "system": bool(resource.get("system")),
        "type_level": bool(resource.get("type")),
        "instance": bool(resource.get("instance")),
        "parameter_summary": _compact_json(resource.get("parameter")),
    })


def _import_compartment_definition(resource, patient=None):
    return _import_metadata_definition(resource, CompartmentDefinition, "clinical.CompartmentDefinition", resource.get("code") or "Compartment Definition", {
        "code": resource.get("code") or "",
        "search": bool(resource.get("search")),
        "resource_summary": _compact_json(resource.get("resource")),
    })


def _import_structure_map(resource, patient=None):
    return _import_metadata_definition(resource, StructureMap, "clinical.StructureMap", "Structure Map", {
        "structure_summary": _compact_json(resource.get("structure")),
        "group_summary": _compact_json(resource.get("group")),
    })


def _import_graph_definition(resource, patient=None):
    return _import_metadata_definition(resource, GraphDefinition, "clinical.GraphDefinition", "Graph Definition", {
        "start": resource.get("start") or "",
        "profile": resource.get("profile") or "",
        "link_summary": _compact_json(resource.get("link")),
    })


def _import_example_scenario(resource, patient=None):
    return _import_metadata_definition(resource, ExampleScenario, "clinical.ExampleScenario", "Example Scenario", {
        "actor_summary": _compact_json(resource.get("actor")),
        "instance_summary": _compact_json(resource.get("instance")),
        "process_summary": _compact_json(resource.get("process")),
    })


def _import_naming_system(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.NamingSystem") or NamingSystem()
    obj.name = resource.get("name") or "Naming System"
    obj.status = resource.get("status") or ""
    obj.kind = resource.get("kind") or ""
    obj.publisher = resource.get("publisher") or ""
    obj.date = _datetime(resource.get("date"))
    obj.description = resource.get("description") or ""
    obj.unique_id_summary = _compact_json(resource.get("uniqueId"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_terminology_capabilities(resource, patient=None):
    return _import_metadata_definition(resource, TerminologyCapabilities, "clinical.TerminologyCapabilities", "Terminology Capabilities", {
        "kind": resource.get("kind") or "",
        "code_system_summary": _compact_json(resource.get("codeSystem")),
        "expansion_summary": _compact_json(resource.get("expansion")),
    })


def _import_activity_definition(resource, patient=None):
    return _import_metadata_definition(resource, ActivityDefinition, "clinical.ActivityDefinition", "Activity Definition", {
        "activity_kind": resource.get("kind") or "",
        "intent": resource.get("intent") or "",
        "priority": resource.get("priority") or "",
        "code": _codeable_text(resource.get("code")) or "",
        "participant_summary": _compact_json(resource.get("participant")),
    })


def _import_event_definition(resource, patient=None):
    return _import_metadata_definition(resource, EventDefinition, "clinical.EventDefinition", "Event Definition", {
        "trigger_summary": _compact_json(resource.get("trigger")),
    })


def _import_specimen_definition(resource, patient=None):
    specimen_type = _codeable_text(resource.get("typeCollected")) or resource.get("url") or "Specimen Definition"
    return _import_metadata_definition(resource, SpecimenDefinition, "clinical.SpecimenDefinition", specimen_type, {
        "specimen_type": _codeable_text(resource.get("typeCollected")) or "",
        "collection_summary": _compact_json(resource.get("collection")),
        "type_tested_summary": _compact_json(resource.get("typeTested")),
    })

def _import_code_system(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.CodeSystem") or CodeSystem()
    obj.url = resource.get("url") or ""
    obj.version = resource.get("version") or ""
    obj.name = resource.get("name") or ""
    obj.title = resource.get("title") or resource.get("name") or "Code System"
    obj.status = resource.get("status") or ""
    obj.publisher = resource.get("publisher") or ""
    obj.date = _datetime(resource.get("date"))
    obj.description = resource.get("description") or ""
    obj.content = resource.get("content") or ""
    obj.case_sensitive = resource.get("caseSensitive") if "caseSensitive" in resource else None
    obj.hierarchy_meaning = resource.get("hierarchyMeaning") or ""
    obj.concept_summary = _concept_definition_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_value_set(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.ValueSet") or ValueSet()
    obj.url = resource.get("url") or ""
    obj.version = resource.get("version") or ""
    obj.name = resource.get("name") or ""
    obj.title = resource.get("title") or resource.get("name") or "Value Set"
    obj.status = resource.get("status") or ""
    obj.publisher = resource.get("publisher") or ""
    obj.date = _datetime(resource.get("date"))
    obj.description = resource.get("description") or ""
    obj.immutable = resource.get("immutable") if "immutable" in resource else None
    obj.compose_summary = _value_set_compose_summary(resource)
    obj.expansion_summary = _value_set_expansion_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_concept_map(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.ConceptMap") or ConceptMap()
    obj.url = resource.get("url") or ""
    obj.version = resource.get("version") or ""
    obj.name = resource.get("name") or ""
    obj.title = resource.get("title") or resource.get("name") or "Concept Map"
    obj.status = resource.get("status") or ""
    obj.publisher = resource.get("publisher") or ""
    obj.date = _datetime(resource.get("date"))
    obj.description = resource.get("description") or ""
    obj.source_uri = resource.get("sourceUri") or _display(resource.get("sourceCanonical")) or ""
    obj.target_uri = resource.get("targetUri") or _display(resource.get("targetCanonical")) or ""
    obj.group_summary = _concept_map_group_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_library(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.Library") or Library()
    obj.url = resource.get("url") or ""
    obj.version = resource.get("version") or ""
    obj.name = resource.get("name") or ""
    obj.title = resource.get("title") or resource.get("name") or "Library"
    obj.status = resource.get("status") or ""
    obj.publisher = resource.get("publisher") or ""
    obj.date = _datetime(resource.get("date"))
    obj.description = resource.get("description") or ""
    obj.library_type = _codeable_text(resource.get("type")) or ""
    obj.subject = _codeable_text(resource.get("subjectCodeableConcept")) or _display(resource.get("subjectReference"))
    obj.related_artifact_summary = _related_artifact_summary(resource)
    obj.content_summary = "\n".join(_attachment_summary(item) for item in resource.get("content") or [] if _attachment_summary(item))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_plan_definition(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.PlanDefinition") or PlanDefinition()
    obj.url = resource.get("url") or ""
    obj.version = resource.get("version") or ""
    obj.name = resource.get("name") or ""
    obj.title = resource.get("title") or resource.get("name") or "Plan Definition"
    obj.status = resource.get("status") or ""
    obj.publisher = resource.get("publisher") or ""
    obj.date = _datetime(resource.get("date"))
    obj.description = resource.get("description") or ""
    obj.plan_type = _codeable_text(resource.get("type")) or ""
    obj.subject = _codeable_text(resource.get("subjectCodeableConcept")) or _display(resource.get("subjectReference"))
    obj.goal_summary = _plan_definition_goal_summary(resource)
    obj.action_summary = _plan_definition_action_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created

def _import_measure(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.Measure") or Measure()
    obj.url = resource.get("url") or ""
    obj.version = resource.get("version") or ""
    obj.name = resource.get("name") or ""
    obj.title = resource.get("title") or resource.get("name") or "Measure"
    obj.status = resource.get("status") or ""
    obj.publisher = resource.get("publisher") or ""
    obj.date = _datetime(resource.get("date"))
    obj.description = resource.get("description") or ""
    obj.scoring = _codeable_text(resource.get("scoring")) or ""
    obj.measure_type = ", ".join(text for text in (_codeable_text(value) for value in resource.get("type") or []) if text)
    obj.group_summary = _measure_group_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_measure_report(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.MeasureReport") or MeasureReport(patient=patient)
    period = resource.get("period") or {}
    obj.patient = patient or _reference_as(resource.get("subject"), PatientProfile)
    obj.measure = _reference_as({"reference": resource.get("measure") or ""}, Measure)
    obj.status = resource.get("status") or ""
    obj.report_type = resource.get("type") or ""
    obj.date = _datetime(resource.get("date"))
    obj.period_start = _date(period.get("start"))
    obj.period_end = _date(period.get("end"))
    obj.improvement_notation = _codeable_text(resource.get("improvementNotation")) or ""
    obj.group_summary = _measure_report_group_summary(resource)
    obj.evaluated_resource_summary = "\n".join(_display(ref) for ref in resource.get("evaluatedResource") or [] if _display(ref))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_test_script(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.TestScript") or TestScript()
    obj.url = resource.get("url") or ""
    obj.version = resource.get("version") or ""
    obj.name = resource.get("name") or ""
    obj.title = resource.get("title") or resource.get("name") or "Test script"
    obj.status = resource.get("status") or ""
    obj.publisher = resource.get("publisher") or ""
    obj.date = _datetime(resource.get("date"))
    obj.description = resource.get("description") or ""
    obj.fixture_summary = _test_script_fixture_summary(resource)
    obj.test_summary = _test_script_action_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_test_report(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.TestReport") or TestReport()
    obj.test_script = _reference_as(resource.get("testScript"), TestScript)
    obj.name = resource.get("name") or ""
    obj.status = resource.get("status") or ""
    obj.result = resource.get("result") or ""
    obj.score = _decimal(resource.get("score"))
    obj.tester = resource.get("tester") or ""
    obj.issued = _datetime(resource.get("issued"))
    obj.participant_summary = _test_report_participant_summary(resource)
    obj.action_summary = _test_report_action_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_coverage_eligibility_request(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.CoverageEligibilityRequest") or CoverageEligibilityRequest(patient=patient)
    serviced = resource.get("servicedPeriod") or {}
    obj.patient = patient or _reference_as(resource.get("patient"), PatientProfile)
    obj.insurer = _reference_as(resource.get("insurer"), Organization)
    obj.provider_organization = _reference_as(resource.get("provider"), Organization)
    obj.status = resource.get("status") or ""
    obj.priority = _codeable_text(resource.get("priority")) or ""
    obj.purpose = ", ".join(resource.get("purpose") or [])
    obj.created_date = _date(resource.get("created"))
    obj.serviced_start = _date(resource.get("servicedDate") or serviced.get("start"))
    obj.serviced_end = _date(serviced.get("end"))
    obj.insurance_summary = _eligibility_insurance_summary(resource)
    obj.item_summary = _eligibility_item_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_coverage_eligibility_response(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.CoverageEligibilityResponse") or CoverageEligibilityResponse(patient=patient)
    obj.patient = patient or _reference_as(resource.get("patient"), PatientProfile)
    obj.request = _reference_as(resource.get("request"), CoverageEligibilityRequest)
    obj.insurer = _reference_as(resource.get("insurer"), Organization)
    obj.status = resource.get("status") or ""
    obj.purpose = ", ".join(resource.get("purpose") or [])
    obj.outcome = resource.get("outcome") or ""
    obj.disposition = resource.get("disposition") or ""
    obj.created_date = _date(resource.get("created"))
    obj.insurance_summary = _eligibility_response_insurance_summary(resource)
    obj.error_summary = _claim_response_error_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_enrollment_request(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.EnrollmentRequest") or EnrollmentRequest(patient=patient)
    obj.patient = patient or _reference_as(resource.get("candidate"), PatientProfile)
    obj.insurer = _reference_as(resource.get("insurer"), Organization)
    obj.provider = _reference_as(resource.get("provider"), Organization)
    obj.coverage = _reference_as(resource.get("coverage"), Coverage)
    obj.status = resource.get("status") or ""
    obj.created_date = _date(resource.get("created"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_enrollment_response(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.EnrollmentResponse") or EnrollmentResponse()
    obj.request = _reference_as(resource.get("request"), EnrollmentRequest)
    obj.organization = _reference_as(resource.get("organization"), Organization)
    obj.status = resource.get("status") or ""
    obj.outcome = resource.get("outcome") or ""
    obj.disposition = resource.get("disposition") or ""
    obj.created_date = _date(resource.get("created"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_payment_notice(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.PaymentNotice") or PaymentNotice(patient=patient)
    obj.patient = patient
    obj.recipient = _reference_as(resource.get("recipient"), Organization)
    obj.status = resource.get("status") or ""
    obj.payment_status = _codeable_text(resource.get("paymentStatus")) or ""
    obj.created_date = _date(resource.get("created"))
    obj.payment_date = _date(resource.get("paymentDate"))
    obj.amount = _money_text(resource.get("amount"))
    obj.request_summary = _display(resource.get("request"))
    obj.response_summary = _display(resource.get("response"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_payment_reconciliation(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.PaymentReconciliation") or PaymentReconciliation()
    obj.payment_issuer = _reference_as(resource.get("paymentIssuer"), Organization)
    obj.status = resource.get("status") or ""
    obj.outcome = resource.get("outcome") or ""
    obj.disposition = resource.get("disposition") or ""
    obj.created_date = _date(resource.get("created"))
    obj.payment_date = _date(resource.get("paymentDate"))
    obj.payment_amount = _money_text(resource.get("paymentAmount"))
    obj.detail_summary = _payment_reconciliation_detail_summary(resource)
    obj.process_note_summary = _process_note_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created

def _import_coverage(resource, patient):
    obj = _object_for_resource(resource, "clinical.Coverage") or Coverage(patient=patient)
    period = resource.get("period") or {}
    obj.patient = patient
    obj.payor_organization = _reference_as(_first(resource.get("payor")), Organization)
    obj.policy_holder_patient = _reference_as(resource.get("policyHolder"), PatientProfile)
    obj.subscriber_patient = _reference_as(resource.get("subscriber"), PatientProfile)
    obj.status = resource.get("status") or ""
    obj.coverage_type = _codeable_text(resource.get("type")) or ""
    obj.subscriber_id = resource.get("subscriberId") or ""
    obj.dependent = resource.get("dependent") or ""
    obj.relationship = _codeable_text(resource.get("relationship")) or ""
    obj.period_start = _date(period.get("start"))
    obj.period_end = _date(period.get("end"))
    obj.order = resource.get("order")
    obj.network = resource.get("network") or ""
    obj.class_summary = _coverage_class_summary(resource)
    obj.cost_summary = _coverage_cost_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_coverage_relationships(resource, obj)
    return obj, created


def _import_explanation_of_benefit(resource, patient):
    obj = _object_for_resource(resource, "clinical.ExplanationOfBenefit") or ExplanationOfBenefit(patient=patient)
    billable_period = resource.get("billablePeriod") or {}
    obj.patient = patient
    obj.insurer = _reference_as(resource.get("insurer"), Organization)
    obj.provider_practitioner = _reference_as(resource.get("provider"), Practitioner)
    obj.provider_organization = _reference_as(resource.get("provider"), Organization)
    obj.status = resource.get("status") or ""
    obj.eob_type = _codeable_text(resource.get("type")) or ""
    obj.use = resource.get("use") or ""
    obj.outcome = resource.get("outcome") or ""
    obj.disposition = resource.get("disposition") or ""
    obj.billable_period_start = _date(billable_period.get("start"))
    obj.billable_period_end = _date(billable_period.get("end"))
    obj.created_date = _date(resource.get("created"))
    obj.total_summary = _eob_total_summary(resource)
    obj.diagnosis_summary = _eob_diagnosis_summary(resource)
    obj.item_summary = _eob_item_summary(resource)
    obj.payment_summary = _eob_payment_summary(resource)
    obj.notes = _eob_notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_explanation_of_benefit_relationships(resource, obj)
    return obj, created


def _import_consent(resource, patient):
    obj = _object_for_resource(resource, "clinical.Consent") or Consent(patient=patient)
    provision = resource.get("provision") or {}
    period = provision.get("period") or {}
    obj.patient = patient
    obj.organization = _reference_as(_first(resource.get("organization")), Organization)
    obj.status = resource.get("status") or ""
    obj.scope = _codeable_text(resource.get("scope")) or ""
    obj.category = ", ".join(text for text in (_codeable_text(value) for value in resource.get("category") or []) if text)
    obj.policy_rule = _codeable_text(resource.get("policyRule")) or ""
    obj.start_date = _datetime(period.get("start"))
    obj.end_date = _datetime(period.get("end"))
    obj.decision = provision.get("type") or ""
    obj.provision_summary = _consent_provision_summary(resource)
    obj.verification_summary = _consent_verification_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_consent_relationships(resource, obj)
    return obj, created


def _import_clinical_impression(resource, patient):
    obj = _object_for_resource(resource, "clinical.ClinicalImpression") or ClinicalImpression(patient=patient)
    effective_period = resource.get("effectivePeriod") or {}
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.assessor_practitioner = _reference_as(resource.get("assessor"), Practitioner)
    obj.assessor_role = _reference_as(resource.get("assessor"), PractitionerRole)
    obj.status = resource.get("status") or ""
    obj.description = resource.get("description") or ""
    obj.effective_datetime = _datetime(resource.get("effectiveDateTime") or effective_period.get("start"))
    obj.date = _datetime(resource.get("date"))
    obj.protocol = "\n".join(resource.get("protocol") or [])
    obj.summary = resource.get("summary") or ""
    obj.prognosis = "\n".join(
        value for value in [_codeable_text(item) for item in resource.get("prognosisCodeableConcept") or []] if value
    )
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_clinical_impression_relationships(resource, obj)
    return obj, created


def _import_diagnostic_report(resource, patient):
    obj = _object_for_resource(resource, "clinical.DiagnosticReport") or DiagnosticReport(patient=patient)
    effective_period = resource.get("effectivePeriod") or {}
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.status = resource.get("status") or ""
    obj.category = _codeable_text(_first(resource.get("category"))) or ""
    obj.code = _codeable_text(resource.get("code")) or "Diagnostic report"
    obj.effective_datetime = _datetime(resource.get("effectiveDateTime") or effective_period.get("start"))
    obj.issued = _datetime(resource.get("issued"))
    obj.conclusion = resource.get("conclusion") or ""
    obj.conclusion_code = ", ".join(
        text for text in (_codeable_text(code) for code in resource.get("conclusionCode") or []) if text
    )
    obj.presented_form_summary = _diagnostic_report_presented_form_summary(resource)
    obj.imaging_study_summary = "\n".join(_display(reference) for reference in resource.get("imagingStudy") or [])
    obj.media_summary = _diagnostic_report_media_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_diagnostic_report_relationships(resource, obj)
    return obj, created


def _import_risk_assessment(resource, patient):
    obj = _object_for_resource(resource, "clinical.RiskAssessment") or RiskAssessment(patient=patient)
    occurrence_period = resource.get("occurrencePeriod") or {}
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.performer_practitioner = _reference_as(resource.get("performer"), Practitioner)
    obj.performer_role = _reference_as(resource.get("performer"), PractitionerRole)
    obj.performer_organization = _reference_as(resource.get("performer"), Organization)
    obj.performer_device = _reference_as(resource.get("performer"), Device)
    obj.status = resource.get("status") or ""
    obj.code = _codeable_text(resource.get("code")) or "Risk assessment"
    obj.method = _codeable_text(resource.get("method")) or ""
    obj.occurrence_datetime = _datetime(resource.get("occurrenceDateTime") or occurrence_period.get("start"))
    obj.authored_on = _datetime(resource.get("authoredOn"))
    obj.prediction_summary = _risk_prediction_summary(resource)
    obj.mitigation = resource.get("mitigation") or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_risk_assessment_relationships(resource, obj)
    return obj, created


def _import_detected_issue(resource, patient):
    obj = _object_for_resource(resource, "clinical.DetectedIssue") or DetectedIssue(patient=patient)
    identified_period = resource.get("identifiedPeriod") or {}
    obj.patient = patient
    obj.author_practitioner = _reference_as(resource.get("author"), Practitioner)
    obj.author_role = _reference_as(resource.get("author"), PractitionerRole)
    obj.author_device = _reference_as(resource.get("author"), Device)
    obj.status = resource.get("status") or ""
    obj.code = _codeable_text(resource.get("code")) or "Detected issue"
    obj.severity = resource.get("severity") or ""
    obj.identified_datetime = _datetime(resource.get("identifiedDateTime") or identified_period.get("start"))
    obj.detail = resource.get("detail") or ""
    obj.reference = resource.get("reference") or ""
    obj.evidence_summary = _detected_issue_evidence_summary(resource)
    obj.mitigation_summary = _detected_issue_mitigation_summary(resource)
    obj.implicated_summary = "\n".join(_display(reference) for reference in resource.get("implicated") or [])
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_detected_issue_relationships(resource, obj)
    return obj, created


def _import_goal(resource, patient):
    obj = _object_for_resource(resource, "clinical.Goal") or Goal(patient=patient)
    obj.patient = patient
    obj.subject_group = _reference_as(resource.get("subject"), FHIRGroup)
    obj.expressed_by_practitioner = _reference_as(resource.get("expressedBy"), Practitioner)
    obj.expressed_by_role = _reference_as(resource.get("expressedBy"), PractitionerRole)
    obj.expressed_by_related_person = _reference_as(resource.get("expressedBy"), RelatedPerson)
    obj.lifecycle_status = resource.get("lifecycleStatus") or ""
    obj.achievement_status = _codeable_text(resource.get("achievementStatus")) or ""
    obj.category = ", ".join(text for text in (_codeable_text(value) for value in resource.get("category") or []) if text)
    obj.priority = _codeable_text(resource.get("priority")) or ""
    obj.description = _codeable_text(resource.get("description")) or "Goal"
    obj.start_date = _date(resource.get("startDate"))
    obj.status_date = _date(resource.get("statusDate"))
    obj.status_reason = resource.get("statusReason") or ""
    obj.target_summary = _goal_target_summary(resource)
    obj.outcome_summary = ", ".join(
        text for text in (_codeable_text(value) for value in resource.get("outcomeCode") or []) if text
    )
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_goal_relationships(resource, obj)
    return obj, created


def _import_device(resource, patient):
    obj = _object_for_resource(resource, "clinical.Device") or Device(patient=patient)
    obj.patient = patient or _reference_as(resource.get("patient"), PatientProfile)
    obj.owner = _reference_as(resource.get("owner"), Organization)
    obj.location = _reference_as(resource.get("location"), Location)
    obj.display_name = _device_display_name(resource)
    obj.device_type = _codeable_text(resource.get("type")) or ""
    obj.status = resource.get("status") or ""
    obj.manufacturer = resource.get("manufacturer") or ""
    obj.model_number = resource.get("modelNumber") or ""
    obj.serial_number = resource.get("serialNumber") or ""
    obj.lot_number = resource.get("lotNumber") or ""
    obj.distinct_identifier = resource.get("distinctIdentifier") or ""
    obj.udi_carrier = _device_udi_carrier(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_device_request(resource, patient):
    obj = _object_for_resource(resource, "clinical.DeviceRequest") or DeviceRequest(patient=patient)
    occurrence_period = resource.get("occurrencePeriod") or {}
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.requester_practitioner = _reference_as(resource.get("requester"), Practitioner)
    obj.requester_role = _reference_as(resource.get("requester"), PractitionerRole)
    obj.status = resource.get("status") or ""
    obj.intent = resource.get("intent") or ""
    obj.priority = resource.get("priority") or ""
    obj.code = (
        _codeable_text(resource.get("codeCodeableConcept"))
        or _display(resource.get("codeReference"))
        or "Device request"
    )
    obj.authored_on = _datetime(resource.get("authoredOn"))
    obj.occurrence_start = _datetime(resource.get("occurrenceDateTime") or occurrence_period.get("start"))
    obj.occurrence_end = _datetime(occurrence_period.get("end"))
    obj.reason = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_device_request_relationships(resource, obj)
    return obj, created


def _import_device_use_statement(resource, patient):
    obj = _object_for_resource(resource, "clinical.DeviceUseStatement") or DeviceUseStatement(patient=patient)
    timing_period = resource.get("timingPeriod") or {}
    obj.patient = patient
    obj.device = _reference_as(resource.get("device"), Device)
    obj.source_practitioner = _reference_as(resource.get("source"), Practitioner)
    obj.source_role = _reference_as(resource.get("source"), PractitionerRole)
    obj.source_related_person = _reference_as(resource.get("source"), RelatedPerson)
    obj.status = resource.get("status") or ""
    obj.timing_start = _datetime(resource.get("timingDateTime") or timing_period.get("start"))
    obj.timing_end = _datetime(timing_period.get("end"))
    obj.recorded_on = _datetime(resource.get("recordedOn"))
    obj.body_site = _codeable_text(resource.get("bodySite")) or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_device_use_statement_relationships(resource, obj)
    return obj, created


def _import_document_reference(resource, patient):
    obj = _object_for_resource(resource, "documents.ClinicalDocument") or ClinicalDocument(patient=patient)
    attachment = _document_reference_attachment(resource)
    document_type = _codeable_text(resource.get("type")) or _codeable_text(_first(resource.get("category"))) or ""

    obj.patient = patient
    obj.title = attachment.get("title") or document_type or resource.get("description") or "Clinical document"
    obj.document_type = document_type
    obj.description = _document_reference_description(resource)
    obj.mime_type = attachment.get("contentType") or ""
    obj.source_name = _display(_first(resource.get("author"))) or _display(resource.get("custodian"))
    obj.source_date = _date(resource.get("date") or ((resource.get("context") or {}).get("period") or {}).get("start"))

    file_content = _document_reference_file_content(resource, attachment)
    if file_content and not obj.file:
        obj.file.save(file_content[0], file_content[1], save=False)

    created = obj.pk is None
    obj.save()
    _sync_document_reference_relationships(resource, obj)
    return obj, created


def _import_episode_of_care(resource, patient):
    obj = _object_for_resource(resource, "clinical.EpisodeOfCare") or EpisodeOfCare(patient=patient)
    period = resource.get("period") or {}
    diagnosis = []
    for item in resource.get("diagnosis") or []:
        condition = _display(item.get("condition"))
        role = _codeable_text(item.get("role"))
        rank = item.get("rank")
        parts = [part for part in [condition, role, f"rank {rank}" if rank else ""] if part]
        if parts:
            diagnosis.append(" - ".join(parts))

    obj.patient = patient
    obj.status = resource.get("status") or ""
    obj.episode_type = _codeable_text(_first(resource.get("type"))) or "Episode of care"
    obj.managing_organization = _reference_as(resource.get("managingOrganization"), Organization)
    obj.care_manager_practitioner = _reference_as(resource.get("careManager"), Practitioner)
    obj.care_manager_role = _reference_as(resource.get("careManager"), PractitionerRole)
    obj.diagnosis_summary = "\n".join(diagnosis)
    obj.start_date = _date(period.get("start"))
    obj.end_date = _date(period.get("end"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_episode_of_care_relationships(resource, obj)
    return obj, created


def _import_procedure(resource, patient):
    obj = _object_for_resource(resource, "clinical.Procedure") or Procedure(patient=patient)
    performed = resource.get("performedPeriod") or {}
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.name = _codeable_text(resource.get("code")) or "Unknown procedure"
    obj.status = resource.get("status") or ""
    obj.category = _codeable_text(resource.get("category")) or ""
    obj.performed_start = _datetime(
        resource.get("performedDateTime")
        or resource.get("performedInstant")
        or resource.get("performedString")
        or performed.get("start")
    )
    obj.performed_end = _datetime(performed.get("end"))
    obj.body_site = _codeable_text(_first(resource.get("bodySite"))) or ""
    obj.outcome = _codeable_text(resource.get("outcome")) or ""
    obj.reason = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.location_display = _display(resource.get("location"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_procedure_relationships(resource, obj)
    return obj, created


def _import_service_request(resource, patient):
    obj = _object_for_resource(resource, "clinical.ServiceRequest") or ServiceRequest(patient=patient)
    occurrence = resource.get("occurrencePeriod") or {}
    obj.patient = patient
    obj.encounter = _reference_as(resource.get("encounter"), Encounter)
    obj.requester_practitioner = _reference_as(resource.get("requester"), Practitioner)
    obj.requester_role = _reference_as(resource.get("requester"), PractitionerRole)
    obj.requester_organization = _reference_as(resource.get("requester"), Organization)
    obj.requester_device = _reference_as(resource.get("requester"), Device)
    obj.name = _codeable_text(resource.get("code")) or "Service request"
    obj.status = resource.get("status") or ""
    obj.intent = resource.get("intent") or ""
    obj.category = _codeable_text(_first(resource.get("category"))) or ""
    obj.priority = resource.get("priority") or ""
    obj.do_not_perform = bool(resource.get("doNotPerform", False))
    obj.authored_on = _datetime(resource.get("authoredOn"))
    obj.occurrence_start = _datetime(resource.get("occurrenceDateTime") or occurrence.get("start"))
    obj.occurrence_end = _datetime(occurrence.get("end"))
    obj.performer_type = _codeable_text(resource.get("performerType")) or ""
    obj.location_code = _codeable_text(_first(resource.get("locationCode"))) or ""
    obj.reason = _codeable_text(_first(resource.get("reasonCode"))) or ""
    obj.patient_instruction = resource.get("patientInstruction") or ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_service_request_relationships(resource, obj)
    return obj, created


def _import_specimen(resource, patient):
    obj = _object_for_resource(resource, "clinical.Specimen") or Specimen(patient=patient)
    collection = resource.get("collection") or {}
    collected_period = collection.get("collectedPeriod") or {}
    accession = resource.get("accessionIdentifier") or {}
    obj.patient = patient
    obj.accession_identifier = accession.get("value") or obj.accession_identifier
    obj.status = resource.get("status") or ""
    obj.specimen_type = _codeable_text(resource.get("type")) or "Specimen"
    obj.received_time = _datetime(resource.get("receivedTime"))
    obj.collected_datetime = _datetime(collection.get("collectedDateTime") or collected_period.get("start"))
    obj.collection_method = _codeable_text(collection.get("method")) or ""
    obj.body_site = _codeable_text(collection.get("bodySite")) or ""
    obj.collector_display = _display(collection.get("collector"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_specimen_relationships(resource, obj)
    return obj, created


def _import_practitioner_role(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.PractitionerRole") or PractitionerRole()
    period = resource.get("period") or {}
    obj.practitioner = _reference_as(resource.get("practitioner"), Practitioner)
    obj.organization = _reference_as(resource.get("organization"), Organization)
    obj.active = bool(resource.get("active", True))
    obj.role = _codeable_text(_first(resource.get("code"))) or ""
    obj.specialty = _codeable_text(_first(resource.get("specialty"))) or ""
    obj.start_date = _date(period.get("start"))
    obj.end_date = _date(period.get("end"))
    obj.phone = _telecom(resource, "phone")
    obj.email = _telecom(resource, "email")
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_practitioner_role_relationships(resource, obj)
    return obj, created


def _import_person(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.Person") or Person()
    obj.managing_organization = _reference_as(resource.get("managingOrganization"), Organization)
    obj.active = bool(resource.get("active", True))
    obj.name = _human_name(resource) or ""
    obj.gender = resource.get("gender") or ""
    obj.birth_date = _date(resource.get("birthDate"))
    obj.phone = _telecom(resource, "phone")
    obj.email = _telecom(resource, "email")
    obj.address = _address_text(_first(resource.get("address")) or {})
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_person_relationships(resource, obj)
    return obj, created


def _import_related_person(resource, patient):
    obj = _object_for_resource(resource, "clinical.RelatedPerson") or RelatedPerson(patient=patient)
    period = resource.get("period") or {}
    communication = _first(resource.get("communication")) or {}

    obj.patient = patient
    obj.active = bool(resource.get("active", True))
    obj.name = _human_name(resource) or ""
    obj.relationship = ", ".join(
        text for text in (_codeable_text(value) for value in resource.get("relationship") or []) if text
    )
    obj.gender = resource.get("gender") or ""
    obj.birth_date = _date(resource.get("birthDate"))
    obj.phone = _telecom(resource, "phone")
    obj.email = _telecom(resource, "email")
    obj.address = _address_text(_first(resource.get("address")) or {})
    obj.language = _codeable_text(communication.get("language")) or ""
    obj.language_preferred = communication.get("preferred") if "preferred" in communication else None
    obj.period_start = _date(period.get("start"))
    obj.period_end = _date(period.get("end"))
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _ensure_person_for_related_person(obj)
    return obj, created


def _import_group(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.FHIRGroup") or FHIRGroup()
    obj.managing_organization = _reference_as(resource.get("managingEntity"), Organization)
    obj.managing_practitioner = _reference_as(resource.get("managingEntity"), Practitioner)
    obj.managing_role = _reference_as(resource.get("managingEntity"), PractitionerRole)
    obj.managing_related_person = _reference_as(resource.get("managingEntity"), RelatedPerson)
    obj.active = bool(resource.get("active", True))
    obj.group_type = resource.get("type") or ""
    obj.actual = bool(resource.get("actual", True))
    obj.code = _codeable_text(resource.get("code")) or ""
    obj.name = resource.get("name") or ""
    obj.quantity = resource.get("quantity")
    obj.characteristic_summary = _group_characteristic_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    _sync_group_relationships(resource, obj)
    return obj, created


def _import_insurance_plan(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.InsurancePlan") or InsurancePlan()
    period = resource.get("period") or {}
    obj.owned_by = _reference_as(resource.get("ownedBy"), Organization)
    obj.administered_by = _reference_as(resource.get("administeredBy"), Organization)
    obj.status = resource.get("status") or ""
    obj.name = resource.get("name") or "Insurance plan"
    obj.alias = ", ".join(resource.get("alias") or [])
    obj.plan_type = ", ".join(text for text in (_codeable_text(value) for value in resource.get("type") or []) if text)
    obj.period_start = _date(period.get("start"))
    obj.period_end = _date(period.get("end"))
    obj.coverage_area = "\n".join(_display(reference) for reference in resource.get("coverageArea") or [])
    obj.contact_summary = _insurance_plan_contact_summary(resource)
    obj.benefit_summary = _insurance_plan_benefit_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_binary_resource(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.BinaryResource") or BinaryResource(patient=patient)
    data = resource.get("data") or ""
    decoded = b""
    if data:
        try:
            decoded = b64decode(data)
        except (BinasciiError, ValueError):
            decoded = b""
    obj.patient = patient
    obj.content_type = resource.get("contentType") or "application/octet-stream"
    obj.security_context = _display(resource.get("securityContext"))
    obj.data_size = len(decoded) if decoded else None
    obj.data_hash = hashlib.sha256(decoded).hexdigest() if decoded else ""
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_endpoint(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.Endpoint") or Endpoint()
    obj.managing_organization = _reference_as(resource.get("managingOrganization"), Organization)
    obj.status = resource.get("status") or ""
    obj.connection_type = _coding_text(resource.get("connectionType")) or _codeable_text(resource.get("connectionType"))
    obj.name = resource.get("name") or ""
    obj.payload_type = ", ".join(text for text in (_codeable_text(v) for v in resource.get("payloadType") or []) if text)
    obj.payload_mime_type = ", ".join(resource.get("payloadMimeType") or [])
    obj.address = resource.get("address") or ""
    obj.header_summary = "\n".join(resource.get("header") or [])
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_healthcare_service(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.HealthcareService") or HealthcareService()
    obj.provided_by = _reference_as(resource.get("providedBy"), Organization)
    obj.active = bool(resource.get("active", True))
    obj.category = _codeable_text(_first(resource.get("category"))) or ""
    obj.service_type = _codeable_text(_first(resource.get("type"))) or ""
    obj.specialty = _codeable_text(_first(resource.get("specialty"))) or ""
    obj.name = resource.get("name") or "Healthcare service"
    obj.comment = resource.get("comment") or ""
    obj.telecom = _telecom_summary(resource)
    obj.availability_summary = _availability_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.locations.set([o for o in (_reference_as(ref, Location) for ref in resource.get("location") or []) if o])
    obj.endpoints.set([o for o in (_reference_as(ref, Endpoint) for ref in resource.get("endpoint") or []) if o])
    return obj, created


def _import_organization_affiliation(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.OrganizationAffiliation") or OrganizationAffiliation()
    period = resource.get("period") or {}
    obj.organization = _reference_as(resource.get("organization"), Organization)
    obj.participating_organization = _reference_as(resource.get("participatingOrganization"), Organization)
    obj.active = bool(resource.get("active", True))
    obj.start_date = _date(period.get("start"))
    obj.end_date = _date(period.get("end"))
    obj.role = ", ".join(text for text in (_codeable_text(v) for v in resource.get("code") or []) if text)
    obj.specialty = ", ".join(text for text in (_codeable_text(v) for v in resource.get("specialty") or []) if text)
    obj.telecom = _telecom_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    obj.networks.set([o for o in (_reference_as(ref, Organization) for ref in resource.get("network") or []) if o])
    obj.locations.set([o for o in (_reference_as(ref, Location) for ref in resource.get("location") or []) if o])
    obj.healthcare_services.set([o for o in (_reference_as(ref, HealthcareService) for ref in resource.get("healthcareService") or []) if o])
    obj.endpoints.set([o for o in (_reference_as(ref, Endpoint) for ref in resource.get("endpoint") or []) if o])
    return obj, created


def _import_substance(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.Substance") or Substance()
    obj.status = resource.get("status") or ""
    obj.category = ", ".join(text for text in (_codeable_text(v) for v in resource.get("category") or []) if text)
    obj.code = _codeable_text(resource.get("code")) or "Substance"
    obj.description = resource.get("description") or ""
    obj.instance_summary = _substance_instance_summary(resource)
    obj.ingredient_summary = _substance_ingredient_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_device_metric(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.DeviceMetric") or DeviceMetric()
    obj.source = _reference_as(resource.get("source"), Device)
    obj.parent = _reference_as(resource.get("parent"), Device)
    obj.metric_type = _codeable_text(resource.get("type")) or "Device metric"
    obj.unit = _codeable_text(resource.get("unit")) or ""
    obj.operational_status = resource.get("operationalStatus") or ""
    obj.color = resource.get("color") or ""
    obj.category = resource.get("category") or ""
    obj.calibration_summary = _device_metric_calibration_summary(resource)
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_practitioner(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.Practitioner") or Practitioner()
    obj.name = _human_name(resource) or "Unknown practitioner"
    obj.npi = _identifier_value(resource, "npi") or obj.npi
    obj.active = bool(resource.get("active", True))
    obj.qualification = _codeable_text((_first(resource.get("qualification")) or {}).get("code")) or ""
    obj.phone = _telecom(resource, "phone")
    obj.email = _telecom(resource, "email")
    obj.address = _address_text(_first(resource.get("address")) or {})
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_organization(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.Organization") or Organization()
    obj.name = resource.get("name") or "Unknown organization"
    obj.organization_type = _codeable_text(_first(resource.get("type"))) or ""
    obj.active = bool(resource.get("active", True))
    obj.phone = _telecom(resource, "phone")
    obj.email = _telecom(resource, "email")
    obj.address = _address_text(_first(resource.get("address")) or {})
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _import_location(resource, patient=None):
    obj = _object_for_resource(resource, "clinical.Location") or Location()
    obj.name = resource.get("name") or "Unknown location"
    obj.status = resource.get("status") or ""
    obj.mode = resource.get("mode") or ""
    obj.location_type = _codeable_text(_first(resource.get("type"))) or ""
    obj.managing_organization = _display(resource.get("managingOrganization"))
    obj.phone = _telecom(resource, "phone")
    obj.email = _telecom(resource, "email")
    obj.address = _address_text(resource.get("address") or {})
    obj.notes = _notes(resource)
    created = obj.pk is None
    obj.save()
    return obj, created


def _object_for_resource(resource, django_model):
    resource_id = resource.get("id")
    if not resource_id:
        return None
    link = FHIRLink.objects.filter(
        resource_type=resource.get("resourceType"),
        resource_id=resource_id,
        django_model=django_model,
    ).first()
    if not link:
        return None
    app_label, model_name = django_model.split(".")
    for model in (
        PatientProfile,
        CatalogEntry,
        Basic,
        Linkage,
        MessageHeader,
        OperationOutcome,
        Parameters,
        Subscription,
        BiologicallyDerivedProduct,
        VerificationResult,
        ChargeItemDefinition,
        Contract,
        ResearchDefinition,
        ResearchElementDefinition,
        Evidence,
        EvidenceVariable,
        EffectEvidenceSynthesis,
        RiskEvidenceSynthesis,
        MedicinalProduct,
        MedicinalProductAuthorization,
        MedicinalProductContraindication,
        MedicinalProductIndication,
        MedicinalProductIngredient,
        MedicinalProductInteraction,
        MedicinalProductManufactured,
        MedicinalProductPackaged,
        MedicinalProductPharmaceutical,
        MedicinalProductUndesirableEffect,
        SubstanceNucleicAcid,
        SubstancePolymer,
        SubstanceProtein,
        SubstanceReferenceInformation,
        SubstanceSpecification,
        SubstanceSourceMaterial,
        ActivityDefinition,
        Account,
    SubstanceSourceMaterial,
    SubstanceSpecification,
    SubstanceReferenceInformation,
    SubstanceProtein,
    SubstancePolymer,
    SubstanceNucleicAcid,
    MedicinalProductUndesirableEffect,
    MedicinalProductPharmaceutical,
    MedicinalProductPackaged,
    MedicinalProductManufactured,
    MedicinalProductInteraction,
    MedicinalProductIngredient,
    MedicinalProductIndication,
    MedicinalProductContraindication,
    MedicinalProductAuthorization,
    MedicinalProduct,
    RiskEvidenceSynthesis,
    EffectEvidenceSynthesis,
    EvidenceVariable,
    Evidence,
    ResearchElementDefinition,
    ResearchDefinition,
    Contract,
    ChargeItemDefinition,
    VerificationResult,
    BiologicallyDerivedProduct,
    Subscription,
    Parameters,
    OperationOutcome,
    MessageHeader,
    Linkage,
    Basic,
    CatalogEntry,
    ActivityDefinition,
        Appointment,
        AuditEvent,
    CapabilityStatement,
        AppointmentResponse,
    AuditEvent,
        CapabilityStatement,
    CapabilityStatement,
        ChargeItem,
    CompartmentDefinition,
        Claim,
        ClaimResponse,
        CodeSystem,
        CompartmentDefinition,
        ConceptMap,
    EventDefinition,
    ExampleScenario,
    CoverageEligibilityRequest,
    CoverageEligibilityResponse,
        BodyStructure,
        Condition,
        Account,
    SubstanceSourceMaterial,
    SubstanceSpecification,
    SubstanceReferenceInformation,
    SubstanceProtein,
    SubstancePolymer,
    SubstanceNucleicAcid,
    MedicinalProductUndesirableEffect,
    MedicinalProductPharmaceutical,
    MedicinalProductPackaged,
    MedicinalProductManufactured,
    MedicinalProductInteraction,
    MedicinalProductIngredient,
    MedicinalProductIndication,
    MedicinalProductContraindication,
    MedicinalProductAuthorization,
    MedicinalProduct,
    RiskEvidenceSynthesis,
    EffectEvidenceSynthesis,
    EvidenceVariable,
    Evidence,
    ResearchElementDefinition,
    ResearchDefinition,
    Contract,
    ChargeItemDefinition,
    VerificationResult,
    BiologicallyDerivedProduct,
    Subscription,
    Parameters,
    OperationOutcome,
    MessageHeader,
    Linkage,
    Basic,
    CatalogEntry,
    ActivityDefinition,
    AdverseEvent,
        Allergy,
        ClinicalImpression,
        ClinicalImpressionFinding,
        Composition,
        DetectedIssue,
    DeviceDefinition,
        DiagnosticReport,
        DocumentManifest,
    EnrollmentRequest,
    EnrollmentResponse,
    Invoice,
        BinaryResource,
        Endpoint,
        HealthcareService,
        OrganizationAffiliation,
        Provenance,
        DeviceRequest,
        DeviceUseStatement,
        DeviceMetric,
        FamilyMemberHistory,
        FamilyMemberHistoryCondition,
        FHIRGroup,
        FHIRGroupMember,
        FHIRList,
    GraphDefinition,
        Flag,
        GuidanceResponse,
        Goal,
        ImagingStudy,
        InsurancePlan,
        Medication,
    Library,
    Measure,
    MeasureReport,
        MedicationAdministration,
        MedicationCatalog,
        MedicationDispense,
        MedicationKnowledge,
        Immunization,
        ImmunizationEvaluation,
        ImmunizationRecommendation,
    ImplementationGuide,
        Media,
    MessageDefinition,
        MolecularSequence,
        NamingSystem,
        NutritionOrder,
    NamingSystem,
        Observation,
    ObservationDefinition,
    OperationDefinition,
        Specimen,
    SpecimenDefinition,
        Device,
        Communication,
        CommunicationRequest,
        Consent,
        Coverage,
        ExplanationOfBenefit,
        Encounter,
        EpisodeOfCare,
        CareTeam,
        CarePlan,
        CareTeamParticipant,
        ClinicalDocument,
        PaymentNotice,
    PaymentReconciliation,
    PlanDefinition,
    Person,
        PersonLink,
        Practitioner,
        PractitionerRole,
        Procedure,
        ProcedurePerformer,
        Questionnaire,
    QuestionnaireResponse,
        RequestGroup,
        RelatedPerson,
    ResearchStudy,
    ResearchSubject,
        RiskAssessment,
        Schedule,
        SearchParameter,
    SearchParameter,
        ServiceRequest,
        Slot,
        SpecimenDefinition,
        SupplyDelivery,
        SupplyRequest,
    StructureDefinition,
    StructureMap,
        Substance,
        StructureDefinition,
        StructureMap,
        Task,
        ValueSet,
        TestScript,
    TestReport,
    TerminologyCapabilities,
    VisionPrescription,
        Organization,
        Location,
    ):
        if model._meta.app_label == app_label and model.__name__ == model_name:
            return model.objects.filter(pk=link.django_object_id).first()
    return None


def _object_for_reference(reference):
    if not reference or "/" not in reference:
        return None
    resource_type, resource_id = reference.split("/", 1)
    model_by_resource_type = {
        "ActivityDefinition": "clinical.ActivityDefinition",
        "CatalogEntry": "clinical.CatalogEntry",
        "Basic": "clinical.Basic",
        "Linkage": "clinical.Linkage",
        "MessageHeader": "clinical.MessageHeader",
        "OperationOutcome": "clinical.OperationOutcome",
        "Parameters": "clinical.Parameters",
        "Subscription": "clinical.Subscription",
        "BiologicallyDerivedProduct": "clinical.BiologicallyDerivedProduct",
        "VerificationResult": "clinical.VerificationResult",
        "ChargeItemDefinition": "clinical.ChargeItemDefinition",
        "Contract": "clinical.Contract",
        "ResearchDefinition": "clinical.ResearchDefinition",
        "ResearchElementDefinition": "clinical.ResearchElementDefinition",
        "Evidence": "clinical.Evidence",
        "EvidenceVariable": "clinical.EvidenceVariable",
        "EffectEvidenceSynthesis": "clinical.EffectEvidenceSynthesis",
        "RiskEvidenceSynthesis": "clinical.RiskEvidenceSynthesis",
        "MedicinalProduct": "clinical.MedicinalProduct",
        "MedicinalProductAuthorization": "clinical.MedicinalProductAuthorization",
        "MedicinalProductContraindication": "clinical.MedicinalProductContraindication",
        "MedicinalProductIndication": "clinical.MedicinalProductIndication",
        "MedicinalProductIngredient": "clinical.MedicinalProductIngredient",
        "MedicinalProductInteraction": "clinical.MedicinalProductInteraction",
        "MedicinalProductManufactured": "clinical.MedicinalProductManufactured",
        "MedicinalProductPackaged": "clinical.MedicinalProductPackaged",
        "MedicinalProductPharmaceutical": "clinical.MedicinalProductPharmaceutical",
        "MedicinalProductUndesirableEffect": "clinical.MedicinalProductUndesirableEffect",
        "SubstanceNucleicAcid": "clinical.SubstanceNucleicAcid",
        "SubstancePolymer": "clinical.SubstancePolymer",
        "SubstanceProtein": "clinical.SubstanceProtein",
        "SubstanceReferenceInformation": "clinical.SubstanceReferenceInformation",
        "SubstanceSpecification": "clinical.SubstanceSpecification",
        "SubstanceSourceMaterial": "clinical.SubstanceSourceMaterial",
        "Account": "clinical.Account",
        "Appointment": "clinical.Appointment",
        "AppointmentResponse": "clinical.AppointmentResponse",
        "AuditEvent": "clinical.AuditEvent",
        "CapabilityStatement": "clinical.CapabilityStatement",
        "CodeSystem": "clinical.CodeSystem",
        "CompartmentDefinition": "clinical.CompartmentDefinition",
        "ConceptMap": "clinical.ConceptMap",
        "EventDefinition": "clinical.EventDefinition",
        "ExampleScenario": "clinical.ExampleScenario",
        "GraphDefinition": "clinical.GraphDefinition",
        "ImplementationGuide": "clinical.ImplementationGuide",
        "CoverageEligibilityRequest": "clinical.CoverageEligibilityRequest",
        "CoverageEligibilityResponse": "clinical.CoverageEligibilityResponse",
        "EnrollmentRequest": "clinical.EnrollmentRequest",
        "EnrollmentResponse": "clinical.EnrollmentResponse",
        "Library": "clinical.Library",
        "MessageDefinition": "clinical.MessageDefinition",
        "NamingSystem": "clinical.NamingSystem",
        "Measure": "clinical.Measure",
        "OperationDefinition": "clinical.OperationDefinition",
        "MeasureReport": "clinical.MeasureReport",
        "PaymentNotice": "clinical.PaymentNotice",
        "PaymentReconciliation": "clinical.PaymentReconciliation",
        "PlanDefinition": "clinical.PlanDefinition",
        "SearchParameter": "clinical.SearchParameter",
        "SpecimenDefinition": "clinical.SpecimenDefinition",
        "StructureDefinition": "clinical.StructureDefinition",
        "StructureMap": "clinical.StructureMap",
        "TerminologyCapabilities": "clinical.TerminologyCapabilities",
        "TestScript": "clinical.TestScript",
        "TestReport": "clinical.TestReport",
        "ValueSet": "clinical.ValueSet",
        "ChargeItem": "clinical.ChargeItem",
        "Claim": "clinical.Claim",
        "ClaimResponse": "clinical.ClaimResponse",
        "Practitioner": "clinical.Practitioner",
        "PractitionerRole": "clinical.PractitionerRole",
        "Organization": "clinical.Organization",
        "Location": "clinical.Location",
        "Encounter": "clinical.Encounter",
        "EpisodeOfCare": "clinical.EpisodeOfCare",
        "Condition": "clinical.Condition",
        "BodyStructure": "clinical.BodyStructure",
        "AdverseEvent": "clinical.AdverseEvent",
        "AllergyIntolerance": "clinical.Allergy",
        "ClinicalImpression": "clinical.ClinicalImpression",
        "Composition": "clinical.Composition",
        "DeviceDefinition": "clinical.DeviceDefinition",
        "DetectedIssue": "clinical.DetectedIssue",
        "DiagnosticReport": "clinical.DiagnosticReport",
        "DocumentManifest": "clinical.DocumentManifest",
        "Invoice": "clinical.Invoice",
        "Binary": "clinical.BinaryResource",
        "Endpoint": "clinical.Endpoint",
        "HealthcareService": "clinical.HealthcareService",
        "OrganizationAffiliation": "clinical.OrganizationAffiliation",
        "Provenance": "clinical.Provenance",
        "DeviceRequest": "clinical.DeviceRequest",
        "DeviceUseStatement": "clinical.DeviceUseStatement",
        "DeviceMetric": "clinical.DeviceMetric",
        "FamilyMemberHistory": "clinical.FamilyMemberHistory",
        "Flag": "clinical.Flag",
        "GuidanceResponse": "clinical.GuidanceResponse",
        "Group": "clinical.FHIRGroup",
        "Goal": "clinical.Goal",
        "ImagingStudy": "clinical.ImagingStudy",
        "Immunization": "clinical.Immunization",
        "ImmunizationEvaluation": "clinical.ImmunizationEvaluation",
        "ImmunizationRecommendation": "clinical.ImmunizationRecommendation",
        "List": "clinical.FHIRList",
        "Media": "clinical.Media",
        "Medication": "clinical.MedicationCatalog",
        "MedicationAdministration": "clinical.MedicationAdministration",
        "MedicationDispense": "clinical.MedicationDispense",
        "MedicationKnowledge": "clinical.MedicationKnowledge",
        "MedicationRequest": "clinical.Medication",
        "MedicationStatement": "clinical.Medication",
        "MolecularSequence": "clinical.MolecularSequence",
        "NutritionOrder": "clinical.NutritionOrder",
        "Observation": "clinical.Observation",
        "ObservationDefinition": "clinical.ObservationDefinition",
        "Communication": "clinical.Communication",
        "CommunicationRequest": "clinical.CommunicationRequest",
        "Consent": "clinical.Consent",
        "Coverage": "clinical.Coverage",
        "Person": "clinical.Person",
        "CareTeam": "clinical.CareTeam",
        "CarePlan": "clinical.CarePlan",
        "Device": "clinical.Device",
        "ExplanationOfBenefit": "clinical.ExplanationOfBenefit",
        "InsurancePlan": "clinical.InsurancePlan",
        "Procedure": "clinical.Procedure",
        "Questionnaire": "clinical.Questionnaire",
        "QuestionnaireResponse": "clinical.QuestionnaireResponse",
        "RequestGroup": "clinical.RequestGroup",
        "RelatedPerson": "clinical.RelatedPerson",
        "ResearchStudy": "clinical.ResearchStudy",
        "ResearchSubject": "clinical.ResearchSubject",
        "RiskAssessment": "clinical.RiskAssessment",
        "Schedule": "clinical.Schedule",
        "ServiceRequest": "clinical.ServiceRequest",
        "Slot": "clinical.Slot",
        "Specimen": "clinical.Specimen",
        "Substance": "clinical.Substance",
        "SupplyDelivery": "clinical.SupplyDelivery",
        "SupplyRequest": "clinical.SupplyRequest",
        "Task": "clinical.Task",
        "VisionPrescription": "clinical.VisionPrescription",
        "DocumentReference": "documents.ClinicalDocument",
        "Patient": "patients.PatientProfile",
    }
    django_model = model_by_resource_type.get(resource_type)
    if not django_model:
        return None
    return _object_for_resource({"resourceType": resource_type, "id": resource_id}, django_model)


def _resolve_patient(resource, patient_by_reference, default_patient=None):
    subject = resource.get("subject") or resource.get("patient") or resource.get("beneficiary") or resource.get("individual") or resource.get("recipient") or resource.get("candidate")
    reference = subject.get("reference") if isinstance(subject, dict) else None
    if not reference and isinstance(subject, list):
        for subject_item in subject:
            if (subject_item.get("reference") or "").startswith("Patient/"):
                reference = subject_item.get("reference")
                break
    if not reference and isinstance(resource.get("for"), dict):
        reference = resource["for"].get("reference")
    if not reference:
        for participant in resource.get("participant") or []:
            actor = participant.get("actor") or {}
            if (actor.get("reference") or "").startswith("Patient/"):
                reference = actor.get("reference")
                break
    if not reference:
        for target in resource.get("target") or []:
            if (target.get("reference") or "").startswith("Patient/"):
                reference = target.get("reference")
                break
    if not reference:
        for actor in resource.get("actor") or []:
            if (actor.get("reference") or "").startswith("Patient/"):
                reference = actor.get("reference")
                break
    if not reference and isinstance(resource.get("actor"), dict):
        actor_reference = resource["actor"].get("reference") or ""
        if actor_reference.startswith("Patient/"):
            reference = actor_reference
    if not reference and isinstance(resource.get("request"), dict):
        request_obj = _object_for_reference(resource["request"].get("reference"))
        if hasattr(request_obj, "patient"):
            return request_obj.patient
    if reference in patient_by_reference:
        return patient_by_reference[reference]
    if reference:
        resource_id = reference.split("/")[-1]
        link = FHIRLink.objects.filter(
            resource_type="Patient",
            resource_id=resource_id,
            django_model="patients.PatientProfile",
        ).first()
        if link:
            return PatientProfile.objects.filter(pk=link.django_object_id).first()
    return default_patient


def _patient_references(resource, patient):
    resource_id = resource.get("id")
    if not resource_id:
        return {}
    return {
        resource_id: patient,
        f"Patient/{resource_id}": patient,
        f"urn:uuid:{resource_id}": patient,
    }


def _reference_as(reference_value, model_class):
    reference = reference_value.get("reference") if isinstance(reference_value, dict) else reference_value
    obj = _object_for_reference(reference)
    return obj if isinstance(obj, model_class) else None


def _link(resource, patient, django_model, object_id, direction):
    resource_id = resource.get("id") or ""
    link = FHIRLink.objects.filter(
        resource_type=resource.get("resourceType"),
        resource_id=resource_id,
        django_model=django_model,
        django_object_id=object_id,
    ).first()
    if not link:
        link = FHIRLink(
            resource_type=resource.get("resourceType"),
            resource_id=resource_id,
            django_model=django_model,
            django_object_id=object_id,
        )
    link.patient = patient
    link.direction = direction
    link.save()


def _snapshot(resource, patient, source, result, is_valid=True, import_status=None, errors=None):
    FHIRResourceSnapshot.objects.create(
        patient=patient,
        resource_type=resource.get("resourceType", ""),
        resource_id=resource.get("id", ""),
        version_id=((resource.get("meta") or {}).get("versionId") or ""),
        source=source,
        raw_json=resource,
        checksum=_checksum(resource),
        import_status=import_status or FHIRResourceSnapshot.IMPORT_STATUS_IMPORTED,
        is_valid=is_valid,
        validation_errors=errors or [],
    )
    result.snapshots += 1


def _checksum(resource):
    encoded = json.dumps(resource, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _record_import(result, created):
    if created:
        result.created += 1
    else:
        result.updated += 1


def _model_label(obj):
    return f"{obj._meta.app_label}.{obj.__class__.__name__}"


def _resource_label(resource):
    return f"{resource.get('resourceType', 'Resource')}/{resource.get('id', '')}".rstrip("/")


def _first(value):
    return value[0] if isinstance(value, list) and value else None


def _telecom(resource, system):
    for telecom in resource.get("telecom") or []:
        if telecom.get("system") == system:
            return telecom.get("value") or ""
    return ""


def _telecom_summary(resource):
    lines = []
    for telecom in resource.get("telecom") or []:
        value = telecom.get("value")
        if value:
            parts = [telecom.get("system") or "", value, telecom.get("use") or ""]
            lines.append(" / ".join(part for part in parts if part))
    return "\n".join(lines)


def _identifier_value(resource, system_fragment):
    for identifier in resource.get("identifier") or []:
        system = (identifier.get("system") or "").lower()
        type_text = _codeable_text(identifier.get("type")).lower()
        if system_fragment.lower() in system or system_fragment.lower() in type_text:
            return identifier.get("value") or ""
    return ""


def _human_name(resource):
    name = _first(resource.get("name")) or {}
    text = name.get("text")
    if text:
        return text
    given = " ".join(name.get("given") or [])
    family = name.get("family") or ""
    return " ".join(part for part in [given, family] if part)


def _address_text(address):
    if not isinstance(address, dict):
        return ""
    parts = []
    parts.extend(address.get("line") or [])
    city_state_postal = " ".join(
        part for part in [address.get("city"), address.get("state"), address.get("postalCode")] if part
    )
    if city_state_postal:
        parts.append(city_state_postal)
    if address.get("country"):
        parts.append(address["country"])
    return "\n".join(parts)


def _codeable_text(value):
    if not isinstance(value, dict):
        return ""
    if value.get("text"):
        return value["text"]
    coding = _first(value.get("coding"))
    if not coding:
        return ""
    return coding.get("display") or coding.get("code") or ""


def _coding_text(value):
    if not isinstance(value, dict):
        return ""
    return value.get("display") or value.get("code") or ""


def _coding_code(value, system_fragment):
    if not isinstance(value, dict):
        return ""
    for coding in value.get("coding") or []:
        system = (coding.get("system") or "").lower()
        if system_fragment.lower() in system:
            return coding.get("code") or ""
    return ""


def _display(value):
    if not isinstance(value, dict):
        return ""
    return value.get("display") or value.get("reference") or ""


def _notes(resource):
    notes = []
    for note in resource.get("note") or []:
        text = note.get("text")
        if text:
            notes.append(text)
    return "\n".join(notes)


def _condition_by_name(name, patient):
    if not name or not patient:
        return None
    return Condition.objects.filter(patient=patient, name__iexact=name).first()


def _medication_name(resource):
    return (
        _codeable_text(resource.get("medicationCodeableConcept"))
        or _display(resource.get("medicationReference"))
    )


def _dosage_text(resource):
    dosage = _first(resource.get("dosage")) or {}
    return dosage.get("text") or ""


def _ratio_text(value):
    if not isinstance(value, dict):
        return ""
    numerator = _age_text(value.get("numerator"))
    denominator = _age_text(value.get("denominator"))
    return " / ".join(part for part in [numerator, denominator] if part)


def _medication_ingredient_summary(resource):
    lines = []
    for ingredient in resource.get("ingredient") or []:
        item = _codeable_text(ingredient.get("itemCodeableConcept")) or _display(ingredient.get("itemReference"))
        strength = _ratio_text(ingredient.get("strength"))
        active = "active" if ingredient.get("isActive") else ""
        line = " / ".join(part for part in [item, strength, active] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _payload_summary(resource):
    lines = []
    for payload in resource.get("payload") or []:
        content = (
            payload.get("contentString")
            or _display(payload.get("contentReference"))
            or _attachment_summary(payload.get("contentAttachment"))
        )
        if content:
            lines.append(content)
    return "\n".join(lines)


def _attachment_summary(attachment):
    if not isinstance(attachment, dict):
        return ""
    return " / ".join(
        part for part in [attachment.get("title"), attachment.get("contentType"), attachment.get("url")] if part
    )


def _nutrition_oral_diet_summary(resource):
    oral = resource.get("oralDiet") or {}
    parts = []
    parts.extend(_codeable_text(value) for value in oral.get("type") or [])
    parts.extend(_codeable_text(value) for value in oral.get("texture") or [])
    parts.extend(_codeable_text(value) for value in oral.get("fluidConsistencyType") or [])
    instructions = oral.get("instruction")
    if instructions:
        parts.append(instructions)
    return "\n".join(part for part in parts if part)


def _nutrition_supplement_summary(resource):
    lines = []
    for supplement in resource.get("supplement") or []:
        parts = [
            _codeable_text(supplement.get("type")),
            supplement.get("productName") or "",
            _age_text(supplement.get("quantity")),
            supplement.get("instruction") or "",
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _nutrition_enteral_formula_summary(resource):
    formula = resource.get("enteralFormula") or {}
    parts = [
        _codeable_text(formula.get("baseFormulaType")),
        formula.get("baseFormulaProductName") or "",
        _codeable_text(formula.get("additiveType")),
        formula.get("additiveProductName") or "",
        _age_text(formula.get("caloricDensity")),
        _codeable_text(formula.get("routeofAdministration")),
        formula.get("administrationInstruction") or "",
    ]
    return "\n".join(part for part in parts if part)


def _fhir_list_entry_summary(resource):
    lines = []
    for entry in resource.get("entry") or []:
        parts = [
            "deleted" if entry.get("deleted") else "",
            _display(entry.get("item")),
            entry.get("date") or "",
            _codeable_text(entry.get("flag")) or "",
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _questionnaire_item_summary(resource):
    lines = []

    def collect_items(items, depth=0):
        for item in items or []:
            answers = []
            for answer in item.get("answer") or []:
                answer_text = (
                    answer.get("valueString")
                    or str(answer.get("valueBoolean") if "valueBoolean" in answer else "")
                    or str(answer.get("valueInteger") if "valueInteger" in answer else "")
                    or str(answer.get("valueDecimal") if "valueDecimal" in answer else "")
                    or answer.get("valueDate")
                    or answer.get("valueDateTime")
                    or _coding_text(answer.get("valueCoding"))
                    or _age_text(answer.get("valueQuantity"))
                    or _display(answer.get("valueReference"))
                )
                if answer_text:
                    answers.append(answer_text)
                collect_items(answer.get("item"), depth + 1)
            question = item.get("text") or item.get("linkId") or ""
            line = ": ".join(part for part in [question, ", ".join(answers)] if part)
            if line:
                lines.append(f"{'  ' * depth}{line}")
            collect_items(item.get("item"), depth + 1)

    collect_items(resource.get("item"))
    return "\n".join(lines)


def _immunization_recommendation_date_criteria(resource):
    lines = []
    for recommendation in resource.get("recommendation") or []:
        for criterion in recommendation.get("dateCriterion") or []:
            line = " / ".join(part for part in [_codeable_text(criterion.get("code")), criterion.get("value") or ""] if part)
            if line:
                lines.append(line)
    return "\n".join(lines)


def _immunization_recommendation_summary(resource):
    lines = []
    for recommendation in resource.get("recommendation") or []:
        parts = [
            _codeable_text(_first(recommendation.get("vaccineCode"))),
            _codeable_text(recommendation.get("targetDisease")),
            _codeable_text(recommendation.get("forecastStatus")),
            recommendation.get("description") or "",
            recommendation.get("series") or "",
            f"dose {recommendation.get('doseNumberPositiveInt')}" if recommendation.get("doseNumberPositiveInt") else "",
            f"series dose {recommendation.get('seriesDosesPositiveInt')}" if recommendation.get("seriesDosesPositiveInt") else "",
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)
def _audit_event_patient(resource):
    for item in resource.get("entity") or []:
        patient = _reference_as(item.get("what"), PatientProfile)
        if patient:
            return patient
    for item in resource.get("agent") or []:
        patient = _reference_as(item.get("who"), PatientProfile)
        if patient:
            return patient
    return None


def _audit_event_agent_summary(resource):
    lines = []
    for item in resource.get("agent") or []:
        roles = ", ".join(text for text in (_codeable_text(value) for value in item.get("role") or []) if text)
        parts = ["requestor" if item.get("requestor") else "", _display(item.get("who")), _display(item.get("altId") if isinstance(item.get("altId"), dict) else {}), roles]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _audit_event_entity_summary(resource):
    lines = []
    for item in resource.get("entity") or []:
        detail = ", ".join((d.get("type") or "") for d in item.get("detail") or [] if d.get("type"))
        parts = [_display(item.get("what")), _codeable_text(item.get("type")), _codeable_text(item.get("role")), item.get("name") or "", detail]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)
def _resource_title(resource):
    code = resource.get("code")
    if isinstance(code, dict):
        code = _codeable_text(code) or code.get("text")
    return (
        resource.get("title")
        or resource.get("name")
        or resource.get("display")
        or resource.get("id")
        or code
        or resource.get("resourceType")
        or "FHIR Resource"
    )


def _compact_resource_summary(resource):
    skipped = {"resourceType", "id", "meta", "text", "contained"}
    compact = {key: value for key, value in resource.items() if key not in skipped and value not in (None, "", [], {})}
    return _compact_json(compact)
def _compact_json(value):
    if value in (None, [], {}):
        return ""
    return json.dumps(value, sort_keys=True)[:4000]

def _concept_definition_summary(resource):
    lines = []
    for concept in resource.get("concept") or []:
        line = " / ".join(part for part in [concept.get("code") or "", concept.get("display") or "", concept.get("definition") or ""] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _value_set_compose_summary(resource):
    compose = resource.get("compose") or {}
    lines = []
    for include in compose.get("include") or []:
        concepts = ", ".join(concept.get("code") or concept.get("display") or "" for concept in include.get("concept") or [] if concept.get("code") or concept.get("display"))
        filters = ", ".join(" ".join(str(part) for part in [flt.get("property"), flt.get("op"), flt.get("value")] if part) for flt in include.get("filter") or [])
        line = " / ".join(part for part in [include.get("system") or "", include.get("version") or "", concepts, filters] if part)
        if line:
            lines.append(line)
    for exclude in compose.get("exclude") or []:
        line = "exclude " + (exclude.get("system") or "")
        if line.strip() != "exclude":
            lines.append(line)
    return "\n".join(lines)


def _value_set_expansion_summary(resource):
    expansion = resource.get("expansion") or {}
    lines = []
    for item in expansion.get("contains") or []:
        line = " / ".join(part for part in [item.get("system") or "", item.get("code") or "", item.get("display") or ""] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _concept_map_group_summary(resource):
    lines = []
    for group in resource.get("group") or []:
        for element in group.get("element") or []:
            targets = ", ".join(" / ".join(part for part in [target.get("code") or "", target.get("display") or "", target.get("equivalence") or ""] if part) for target in element.get("target") or [])
            line = " / ".join(part for part in [group.get("source") or "", group.get("target") or "", element.get("code") or "", element.get("display") or "", targets] if part)
            if line:
                lines.append(line)
    return "\n".join(lines)


def _related_artifact_summary(resource):
    lines = []
    for item in resource.get("relatedArtifact") or []:
        line = " / ".join(part for part in [item.get("type") or "", item.get("label") or "", item.get("display") or "", item.get("url") or ""] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _plan_definition_goal_summary(resource):
    lines = []
    for goal in resource.get("goal") or []:
        targets = ", ".join(_codeable_text(target.get("measure")) for target in goal.get("target") or [] if _codeable_text(target.get("measure")))
        line = " / ".join(part for part in [_codeable_text(goal.get("category")), goal.get("description", {}).get("text") or _codeable_text(goal.get("description")), targets] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _plan_definition_action_summary(resource):
    lines = []
    for action in resource.get("action") or []:
        triggers = ", ".join(trigger.get("type") or "" for trigger in action.get("trigger") or [] if trigger.get("type"))
        line = " / ".join(part for part in [action.get("title") or "", action.get("description") or "", _codeable_text(action.get("code")), triggers] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)

def _measure_group_summary(resource):
    lines = []
    for group in resource.get("group") or []:
        populations = ", ".join(_codeable_text(pop.get("code")) for pop in group.get("population") or [] if _codeable_text(pop.get("code")))
        stratifiers = ", ".join(_codeable_text(strat.get("code")) for strat in group.get("stratifier") or [] if _codeable_text(strat.get("code")))
        line = " / ".join(part for part in [group.get("id") or "", populations, stratifiers] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _measure_report_group_summary(resource):
    lines = []
    for group in resource.get("group") or []:
        populations = []
        for pop in group.get("population") or []:
            populations.append(" / ".join(part for part in [_codeable_text(pop.get("code")), str(pop.get("count") or "")] if part))
        score = _age_text(group.get("measureScore"))
        line = " / ".join(part for part in [group.get("id") or "", "; ".join(filter(None, populations)), score] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _test_script_fixture_summary(resource):
    lines = []
    for fixture in resource.get("fixture") or []:
        line = " / ".join(part for part in ["autocreate" if fixture.get("autocreate") else "", "autodelete" if fixture.get("autodelete") else "", _display(fixture.get("resource"))] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _test_script_action_summary(resource):
    lines = []
    for section in [resource.get("setup") or {}] + (resource.get("test") or []) + [resource.get("teardown") or {}]:
        for action in section.get("action") or []:
            operation = action.get("operation") or {}
            assertion = action.get("assert") or {}
            line = " / ".join(part for part in [section.get("name") or "", operation.get("type", {}).get("code") if isinstance(operation.get("type"), dict) else "", assertion.get("description") or assertion.get("operator") or ""] if part)
            if line:
                lines.append(line)
    return "\n".join(lines)


def _test_report_participant_summary(resource):
    lines = []
    for item in resource.get("participant") or []:
        line = " / ".join(part for part in [item.get("type") or "", item.get("uri") or "", item.get("display") or ""] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _test_report_action_summary(resource):
    lines = []
    for section in [resource.get("setup") or {}] + (resource.get("test") or []) + [resource.get("teardown") or {}]:
        for action in section.get("action") or []:
            operation = action.get("operation") or {}
            assertion = action.get("assert") or {}
            line = " / ".join(part for part in [section.get("name") or "", operation.get("result") or "", assertion.get("result") or "", operation.get("message") or assertion.get("message") or ""] if part)
            if line:
                lines.append(line)
    return "\n".join(lines)


def _eligibility_insurance_summary(resource):
    lines = []
    for item in resource.get("insurance") or []:
        line = " / ".join(part for part in ["focal" if item.get("focal") else "", _display(item.get("coverage")), item.get("businessArrangement") or ""] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _eligibility_item_summary(resource):
    lines = []
    for item in resource.get("item") or []:
        category = _codeable_text(item.get("category")) or ""
        product = _codeable_text(item.get("productOrService")) or ""
        diagnosis = ", ".join(
            part
            for part in (_codeable_text(value.get("diagnosisCodeableConcept")) or _display(value.get("diagnosisReference")) for value in item.get("diagnosis") or [])
            if part
        )
        line = " / ".join(part for part in [category, product, _display(item.get("provider")), diagnosis] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _eligibility_response_insurance_summary(resource):
    lines = []
    for insurance in resource.get("insurance") or []:
        items = []
        for item in insurance.get("item") or []:
            benefits = ", ".join(_codeable_text(benefit.get("type")) for benefit in item.get("benefit") or [] if _codeable_text(benefit.get("type")))
            items.append(" / ".join(part for part in [_codeable_text(item.get("category")), _codeable_text(item.get("productOrService")), benefits] if part))
        line = " / ".join(part for part in [_display(insurance.get("coverage")), "in force" if insurance.get("inforce") else "", "; ".join(filter(None, items))] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _payment_reconciliation_detail_summary(resource):
    lines = []
    for item in resource.get("detail") or []:
        line = " / ".join(part for part in [_codeable_text(item.get("type")), _display(item.get("request")), _display(item.get("response")), _money_text(item.get("amount"))] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _process_note_summary(resource):
    lines = []
    for note in resource.get("processNote") or []:
        line = " / ".join(part for part in [note.get("type") or "", note.get("text") or ""] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)

def _account_guarantor_summary(resource):
    lines = []
    for item in resource.get("guarantor") or []:
        parts = [_display(item.get("party")), "on hold" if item.get("onHold") else "", item.get("period", {}).get("start") or "", item.get("period", {}).get("end") or ""]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _account_balance_summary(resource):
    lines = []
    for item in resource.get("balance") or []:
        line = " / ".join(part for part in [_codeable_text(item.get("aggregate")), _codeable_text(item.get("term")), item.get("estimate") and "estimate" or "", _money_text(item.get("amount"))] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _claim_insurance_summary(resource):
    lines = []
    for item in resource.get("insurance") or []:
        parts = [f"#{item.get('sequence')}" if item.get("sequence") else "", "focal" if item.get("focal") else "", _display(item.get("coverage")), item.get("businessArrangement") or ""]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _claim_response_item_summary(resource):
    lines = []
    for item in (resource.get("item") or []) + (resource.get("addItem") or []):
        adjudications = []
        for adjudication in item.get("adjudication") or []:
            adjudications.append(" / ".join(part for part in [_codeable_text(adjudication.get("category")), _money_text(adjudication.get("amount")), str(adjudication.get("value") or "")] if part))
        parts = [f"#{item.get('itemSequence') or item.get('sequence')}" if (item.get("itemSequence") or item.get("sequence")) else "", _codeable_text(item.get("productOrService")), "; ".join(filter(None, adjudications))]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _claim_response_error_summary(resource):
    lines = []
    for item in resource.get("error") or []:
        parts = [str(item.get("itemSequence") or ""), str(item.get("detailSequence") or ""), str(item.get("subDetailSequence") or ""), _codeable_text(item.get("code"))]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _invoice_participant_summary(resource):
    lines = []
    for item in resource.get("participant") or []:
        line = " / ".join(part for part in [_codeable_text(item.get("role")), _display(item.get("actor"))] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _invoice_line_item_summary(resource):
    lines = []
    for item in resource.get("lineItem") or []:
        charge = item.get("chargeItemCodeableConcept") or {}
        if not charge and item.get("chargeItemReference"):
            charge_text = _display(item.get("chargeItemReference"))
        else:
            charge_text = _codeable_text(charge)
        price_components = []
        for component in item.get("priceComponent") or []:
            price_components.append(" / ".join(part for part in [component.get("type") or "", _codeable_text(component.get("code")), _money_text(component.get("amount"))] if part))
        line = " / ".join(part for part in [str(item.get("sequence") or ""), charge_text, "; ".join(filter(None, price_components))] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _charge_item_price_component_summary(resource):
    lines = []
    for item in resource.get("priceComponent") or []:
        parts = [item.get("type") or "", _codeable_text(item.get("code")), str(item.get("factor") or ""), _money_text(item.get("amount"))]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _research_contact_summary(resource):
    lines = []
    for item in resource.get("contact") or []:
        telecom = ", ".join(t.get("value") or "" for t in item.get("telecom") or [] if t.get("value"))
        line = " / ".join(part for part in [_human_name({"name": [item.get("name") or {}]}) if item.get("name") else "", telecom] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _device_definition_udi_summary(resource):
    lines = []
    for item in resource.get("udiDeviceIdentifier") or []:
        line = " / ".join(part for part in [item.get("deviceIdentifier") or "", item.get("issuer") or "", item.get("jurisdiction") or ""] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _device_definition_specialization_summary(resource):
    lines = []
    for item in resource.get("specialization") or []:
        line = " / ".join(part for part in [item.get("systemType") or "", item.get("version") or ""] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _device_definition_property_summary(resource):
    lines = []
    for item in resource.get("property") or []:
        values = [_age_text(value) for value in item.get("valueQuantity") or []]
        values.extend(_codeable_text(value) for value in item.get("valueCode") or [])
        line = " / ".join(part for part in [_codeable_text(item.get("type")), ", ".join(filter(None, values))] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _device_definition_capability_summary(resource):
    lines = []
    for item in resource.get("capability") or []:
        descriptions = ", ".join(_codeable_text(value) for value in item.get("description") or [] if _codeable_text(value))
        line = " / ".join(part for part in [_codeable_text(item.get("type")), descriptions] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _observation_definition_quantitative_summary(resource):
    details = resource.get("quantitativeDetails") or {}
    return " / ".join(part for part in [_codeable_text(details.get("unit")), details.get("customaryUnit", {}).get("text") if isinstance(details.get("customaryUnit"), dict) else "", str(details.get("decimalPrecision") or ""), details.get("conversionFactor") and str(details.get("conversionFactor")) or ""] if part)


def _observation_definition_interval_summary(resource):
    lines = []
    for item in resource.get("qualifiedInterval") or []:
        parts = [_codeable_text(item.get("category")), _codeable_text(item.get("context")), _age_text(item.get("range")), item.get("gender") or ""]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _questionnaire_definition_item_summary(resource):
    lines = []

    def collect(items, depth=0):
        for item in items or []:
            line = " / ".join(part for part in ["  " * depth + (item.get("linkId") or ""), item.get("text") or "", item.get("type") or "", "required" if item.get("required") else ""] if part)
            if line.strip():
                lines.append(line)
            collect(item.get("item") or [], depth + 1)

    collect(resource.get("item") or [])
    return "\n".join(lines)

def _coverage_class_summary(resource):
    lines = []
    for item in resource.get("class") or []:
        parts = [_codeable_text(item.get("type")), item.get("value") or "", item.get("name") or ""]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _coverage_cost_summary(resource):
    lines = []
    for item in resource.get("costToBeneficiary") or []:
        value = _money_text(item.get("valueMoney")) or _age_text(item.get("valueQuantity"))
        parts = [_codeable_text(item.get("type")), value]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _money_text(value):
    if not isinstance(value, dict):
        return ""
    amount = value.get("value")
    currency = value.get("currency") or ""
    return " ".join(str(part) for part in [amount, currency] if part)


def _eob_total_summary(resource):
    lines = []
    for total in resource.get("total") or []:
        line = " / ".join(part for part in [_codeable_text(total.get("category")), _money_text(total.get("amount"))] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _eob_diagnosis_summary(resource):
    lines = []
    for diagnosis in resource.get("diagnosis") or []:
        diagnosis_text = _codeable_text(diagnosis.get("diagnosisCodeableConcept")) or _display(diagnosis.get("diagnosisReference"))
        types = ", ".join(text for text in (_codeable_text(value) for value in diagnosis.get("type") or []) if text)
        parts = [f"#{diagnosis.get('sequence')}" if diagnosis.get("sequence") else "", diagnosis_text, types]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _eob_item_summary(resource):
    lines = []
    for item in resource.get("item") or []:
        product = _codeable_text(item.get("productOrService"))
        quantity = _age_text(item.get("quantity"))
        net = _money_text(item.get("net"))
        adjudication = ", ".join(
            " / ".join(part for part in [_codeable_text(adj.get("category")), _money_text(adj.get("amount"))] if part)
            for adj in item.get("adjudication") or []
        )
        parts = [f"#{item.get('sequence')}" if item.get("sequence") else "", product, quantity, net, adjudication]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _eob_payment_summary(resource):
    payment = resource.get("payment") or {}
    return " / ".join(
        part
        for part in [
            _codeable_text(payment.get("type")),
            _money_text(payment.get("amount")),
            payment.get("date") or "",
        ]
        if part
    )


def _eob_notes(resource):
    notes = _notes(resource).splitlines() if _notes(resource) else []
    for note in resource.get("processNote") or []:
        text = note.get("text")
        if text:
            notes.append(text)
    return "\n".join(notes)


def _consent_provision_summary(resource):
    lines = []

    def collect(provision, depth=0):
        if not isinstance(provision, dict):
            return
        parts = [
            provision.get("type") or "",
            _range_text(provision.get("period")),
            ", ".join(_codeable_text(value) for value in provision.get("action") or [] if _codeable_text(value)),
            ", ".join(_codeable_text(value) for value in provision.get("purpose") or [] if _codeable_text(value)),
            ", ".join(_codeable_text(value) for value in provision.get("code") or [] if _codeable_text(value)),
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(f"{'  ' * depth}{line}")
        for child in provision.get("provision") or []:
            collect(child, depth + 1)

    collect(resource.get("provision"))
    return "\n".join(lines)


def _consent_verification_summary(resource):
    lines = []
    for verification in resource.get("verification") or []:
        parts = [
            "verified" if verification.get("verified") else "not verified",
            _display(verification.get("verifiedWith")),
            verification.get("verificationDate") or "",
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _consent_referenced_resources(resource):
    refs = []

    def collect(provision):
        if not isinstance(provision, dict):
            return
        for data in provision.get("data") or []:
            reference = data.get("reference")
            if reference:
                refs.append(reference)
        for actor in provision.get("actor") or []:
            reference = actor.get("reference")
            if reference:
                refs.append(reference)
        for child in provision.get("provision") or []:
            collect(child)

    collect(resource.get("provision"))
    return refs


def _insurance_plan_contact_summary(resource):
    lines = []
    for contact in resource.get("contact") or []:
        purpose = _codeable_text(contact.get("purpose"))
        name = _human_name({"name": [contact.get("name") or {}]}) if contact.get("name") else ""
        telecom = ", ".join(item.get("value") or "" for item in contact.get("telecom") or [] if item.get("value"))
        line = " / ".join(part for part in [purpose, name, telecom] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _insurance_plan_benefit_summary(resource):
    lines = []
    for coverage in resource.get("coverage") or []:
        coverage_type = _codeable_text(coverage.get("type"))
        benefits = []
        for benefit in coverage.get("benefit") or []:
            benefits.append(_codeable_text(benefit.get("type")))
        line = " / ".join(part for part in [coverage_type, ", ".join(filter(None, benefits))] if part)
        if line:
            lines.append(line)
    for plan in resource.get("plan") or []:
        plan_text = _codeable_text(plan.get("type")) or plan.get("name") or ""
        if plan_text:
            lines.append(plan_text)
    return "\n".join(lines)


def _media_dimension_summary(resource):
    parts = []
    for label in ("height", "width", "frames", "duration"):
        if resource.get(label) is not None:
            parts.append(f"{label}: {resource[label]}")
    return " / ".join(parts)


def _imaging_series_summary(resource):
    lines = []
    for series in resource.get("series") or []:
        parts = [
            series.get("uid") or "",
            _codeable_text(series.get("modality")),
            series.get("description") or "",
            f"{series.get('numberOfInstances')} instances" if series.get("numberOfInstances") else "",
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
        for instance in series.get("instance") or []:
            instance_line = " / ".join(part for part in [instance.get("uid"), _codeable_text(instance.get("sopClass")), instance.get("title")] if part)
            if instance_line:
                lines.append(f"  {instance_line}")
    return "\n".join(lines)


def _molecular_reference_summary(resource):
    reference = resource.get("referenceSeq") or {}
    return " / ".join(
        part
        for part in [
            _codeable_text(reference.get("chromosome")),
            reference.get("genomeBuild") or "",
            reference.get("referenceSeqId", {}).get("value") if isinstance(reference.get("referenceSeqId"), dict) else "",
            str(reference.get("windowStart") or ""),
            str(reference.get("windowEnd") or ""),
        ]
        if part
    )


def _molecular_variant_summary(resource):
    lines = []
    for variant in resource.get("variant") or []:
        parts = [
            str(variant.get("start") or ""),
            str(variant.get("end") or ""),
            variant.get("observedAllele") or "",
            variant.get("referenceAllele") or "",
            variant.get("cigar") or "",
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _molecular_repository_summary(resource):
    lines = []
    for repo in resource.get("repository") or []:
        line = " / ".join(part for part in [repo.get("type"), repo.get("url"), repo.get("name"), repo.get("datasetId"), repo.get("variantsetId")] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _molecular_quality_summary(resource):
    lines = []
    for quality in resource.get("quality") or []:
        line = " / ".join(
            part
            for part in [
                quality.get("type"),
                _codeable_text(quality.get("standardSequence")),
                str(quality.get("score", {}).get("value") if isinstance(quality.get("score"), dict) else ""),
                quality.get("method", {}).get("text") if isinstance(quality.get("method"), dict) else "",
            ]
            if part
        )
        if line:
            lines.append(line)
    return "\n".join(lines)


def _medication_knowledge_ingredient_summary(resource):
    lines = []
    for ingredient in resource.get("ingredient") or []:
        parts = [
            _codeable_text(ingredient.get("itemCodeableConcept")) or _display(ingredient.get("itemReference")),
            "active" if ingredient.get("isActive") else "",
            _ratio_text(ingredient.get("strength")),
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _medication_knowledge_monitoring_summary(resource):
    lines = []
    for program in resource.get("monitoringProgram") or []:
        line = " / ".join(part for part in [_codeable_text(program.get("type")), program.get("name") or ""] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _medication_knowledge_classification_summary(resource):
    lines = []
    for item in resource.get("medicineClassification") or []:
        classification = ", ".join(text for text in (_codeable_text(v) for v in item.get("classification") or []) if text)
        line = " / ".join(part for part in [_codeable_text(item.get("type")), classification] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _vision_lens_summary(resource):
    lines = []
    for lens in resource.get("lensSpecification") or []:
        parts = [
            _codeable_text(lens.get("product")),
            lens.get("eye") or "",
            f"sphere {lens.get('sphere')}" if lens.get("sphere") is not None else "",
            f"cylinder {lens.get('cylinder')}" if lens.get("cylinder") is not None else "",
            f"axis {lens.get('axis')}" if lens.get("axis") is not None else "",
            f"add {lens.get('add')}" if lens.get("add") is not None else "",
            lens.get("brand") or "",
            lens.get("color") or "",
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _request_group_action_summary(resource):
    lines = []

    def collect(actions, depth=0):
        for action in actions or []:
            parts = [
                action.get("title") or "",
                action.get("description") or "",
                _codeable_text(action.get("code")),
                action.get("priority") or "",
                _display(action.get("resource")),
            ]
            line = " / ".join(part for part in parts if part)
            if line:
                lines.append(f"{'  ' * depth}{line}")
            collect(action.get("action"), depth + 1)

    collect(resource.get("action"))
    return "\n".join(lines)


def _guidance_data_requirement_summary(resource):
    lines = []
    for requirement in resource.get("dataRequirement") or []:
        line = " / ".join(part for part in [requirement.get("type"), requirement.get("profile", [""])[0] if requirement.get("profile") else ""] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _availability_summary(resource):
    lines = []
    for item in resource.get("availableTime") or []:
        days = ", ".join(item.get("daysOfWeek") or [])
        times = " - ".join(part for part in [item.get("availableStartTime"), item.get("availableEndTime")] if part)
        line = " / ".join(part for part in [days, times, "all day" if item.get("allDay") else ""] if part)
        if line:
            lines.append(line)
    for item in resource.get("notAvailable") or []:
        line = " / ".join(part for part in [item.get("description"), _range_text(item.get("during"))] if part)
        if line:
            lines.append(f"Not available: {line}")
    return "\n".join(lines)


def _substance_instance_summary(resource):
    lines = []
    for item in resource.get("instance") or []:
        parts = [
            (item.get("identifier") or {}).get("value") if isinstance(item.get("identifier"), dict) else "",
            item.get("expiry") or "",
            _age_text(item.get("quantity")),
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _substance_ingredient_summary(resource):
    lines = []
    for item in resource.get("ingredient") or []:
        line = " / ".join(part for part in [_age_text(item.get("quantity")), _codeable_text(item.get("substanceCodeableConcept")) or _display(item.get("substanceReference"))] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _device_metric_calibration_summary(resource):
    lines = []
    for item in resource.get("calibration") or []:
        line = " / ".join(part for part in [item.get("type"), item.get("state"), item.get("time")] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _provenance_agent_summary(resource):
    lines = []
    for item in resource.get("agent") or []:
        parts = [_codeable_text(item.get("type")), _display(item.get("who")), _display(item.get("onBehalfOf"))]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _provenance_entity_summary(resource):
    lines = []
    for item in resource.get("entity") or []:
        line = " / ".join(part for part in [item.get("role"), _display(item.get("what"))] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _signature_summary(resource):
    lines = []
    for item in resource.get("signature") or []:
        line = " / ".join(part for part in [item.get("when"), _display(item.get("who")), item.get("sigFormat") or item.get("targetFormat") or ""] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _composition_section_summary(resource):
    lines = []
    for section in resource.get("section") or []:
        entries = ", ".join(_display(ref) for ref in section.get("entry") or [] if _display(ref))
        line = " / ".join(part for part in [section.get("title"), _codeable_text(section.get("code")), entries] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _document_manifest_related_summary(resource):
    lines = []
    for item in resource.get("related") or []:
        identifier = item.get("identifier") or {}
        line = " / ".join(part for part in [identifier.get("value") if isinstance(identifier, dict) else "", _display(item.get("ref"))] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _appointment_participant_summary(resource):
    lines = []
    for item in resource.get("participant") or []:
        parts = [_display(item.get("actor")), item.get("status") or "", _codeable_text(_first(item.get("type")))]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _task_io_summary(resource, key):
    lines = []
    for item in resource.get(key) or []:
        value = (
            _codeable_text(item.get("valueCodeableConcept"))
            or item.get("valueString")
            or _display(item.get("valueReference"))
            or _age_text(item.get("valueQuantity"))
        )
        line = " / ".join(part for part in [_codeable_text(item.get("type")), value] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _care_team_participants(resource):
    participants = []
    for participant in resource.get("participant") or []:
        role = _codeable_text(_first(participant.get("role")))
        member = _display(participant.get("member"))
        period = participant.get("period") or {}
        dates = " - ".join(value for value in [period.get("start"), period.get("end")] if value)

        parts = [part for part in [role, member] if part]
        line = ": ".join(parts) if len(parts) == 2 else "".join(parts)
        if dates:
            line = f"{line} ({dates})" if line else dates
        if line:
            participants.append(line)
    return "\n".join(participants)


def _care_team_managing_organizations(resource):
    organizations = []
    for reference in resource.get("managingOrganization") or []:
        organization = _object_for_reference(reference.get("reference"))
        if isinstance(organization, Organization):
            organizations.append(organization)
    return organizations


def _device_display_name(resource):
    device_name = _first(resource.get("deviceName")) or {}
    udi_carrier = _first(resource.get("udiCarrier")) or {}
    return (
        device_name.get("name")
        or resource.get("modelNumber")
        or resource.get("manufacturer")
        or udi_carrier.get("deviceIdentifier")
        or "Device"
    )


def _device_udi_carrier(resource):
    values = []
    for carrier in resource.get("udiCarrier") or []:
        carrier_text = carrier.get("carrierHRF") or carrier.get("carrierAIDC") or carrier.get("deviceIdentifier")
        if carrier_text:
            values.append(carrier_text)
    return "\n".join(values)


def _document_reference_attachment(resource):
    content = _first(resource.get("content")) or {}
    attachment = content.get("attachment") or {}
    return attachment if isinstance(attachment, dict) else {}


def _document_reference_description(resource):
    parts = []
    if resource.get("description"):
        parts.append(resource["description"])
    if resource.get("status"):
        parts.append(f"Status: {resource['status']}")
    custodian = _display(resource.get("custodian"))
    if custodian:
        parts.append(f"Custodian: {custodian}")
    return "\n".join(parts)


def _document_reference_file_content(resource, attachment):
    data = attachment.get("data")
    if not data:
        return None
    try:
        decoded = b64decode(data, validate=True)
    except (BinasciiError, ValueError):
        return None
    resource_id = resource.get("id") or "document"
    extension = _file_extension_for_mime_type(attachment.get("contentType"))
    filename = f"fhir-document-{resource_id}{extension}"
    return filename, ContentFile(decoded)


def _file_extension_for_mime_type(mime_type):
    mime_type = (mime_type or "").split(";", 1)[0].strip().lower()
    return {
        "application/pdf": ".pdf",
        "text/html": ".html",
        "text/plain": ".txt",
        "application/json": ".json",
        "application/xml": ".xml",
        "text/xml": ".xml",
    }.get(mime_type, ".bin")


def _age_text(value):
    if not isinstance(value, dict):
        return ""
    amount = value.get("value")
    unit = value.get("unit") or value.get("code") or ""
    return " ".join(str(part) for part in [amount, unit] if part)


def _range_text(value):
    if not isinstance(value, dict):
        return ""
    start = value.get("start")
    end = value.get("end")
    if start or end:
        return " - ".join(part for part in [start, end] if part)
    low = _age_text(value.get("low"))
    high = _age_text(value.get("high"))
    return " - ".join(part for part in [low, high] if part)


def _ensure_person_for_related_person(related_person):
    person = related_person.person or Person()
    person.active = related_person.active
    person.name = related_person.name or person.name
    person.gender = related_person.gender or person.gender
    person.birth_date = related_person.birth_date or person.birth_date
    person.phone = related_person.phone or person.phone
    person.email = related_person.email or person.email
    person.address = related_person.address or person.address
    person.notes = person.notes or "Created from RelatedPerson."
    person.save()

    if related_person.person_id != person.id:
        related_person.person = person
        related_person.save(update_fields=["person"])

    PersonLink.objects.get_or_create(
        person=person,
        related_person=related_person,
        defaults={
            "target_display": str(related_person),
            "target_reference": f"RelatedPerson/{related_person.pk}",
        },
    )
    return person


def _group_characteristic_summary(resource):
    lines = []
    for characteristic in resource.get("characteristic") or []:
        value = (
            _codeable_text(characteristic.get("valueCodeableConcept"))
            or str(characteristic.get("valueBoolean") if "valueBoolean" in characteristic else "")
            or _age_text(characteristic.get("valueQuantity"))
            or _range_text(characteristic.get("valueRange"))
            or _display(characteristic.get("valueReference"))
        )
        period = _range_text(characteristic.get("period"))
        parts = [
            "Exclude" if characteristic.get("exclude") else "Include",
            _codeable_text(characteristic.get("code")),
            value,
            period,
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _value_text(prefix, value):
    if value is None:
        return ""
    if isinstance(value, dict):
        return (
            _codeable_text(value)
            or _age_text(value)
            or _range_text(value)
            or _display(value)
            or str(value.get("value") or "")
        )
    return str(value)


def _goal_target_summary(resource):
    lines = []
    for target in resource.get("target") or []:
        detail = (
            _value_text("detail", target.get("detailQuantity"))
            or _value_text("detail", target.get("detailRange"))
            or _codeable_text(target.get("detailCodeableConcept"))
            or str(target.get("detailString") or "")
            or _value_text("detail", target.get("detailRatio"))
            or (str(target.get("detailBoolean")) if "detailBoolean" in target else "")
            or (str(target.get("detailInteger")) if "detailInteger" in target else "")
        )
        due = target.get("dueDate") or _age_text(target.get("dueDuration"))
        parts = [_codeable_text(target.get("measure")), detail, due]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _risk_prediction_summary(resource):
    lines = []
    for prediction in resource.get("prediction") or []:
        probability = (
            _value_text("probability", prediction.get("probabilityDecimal"))
            or _value_text("probability", prediction.get("probabilityRange"))
        )
        when = _range_text(prediction.get("whenPeriod")) or _age_text(prediction.get("whenRange"))
        parts = [
            _codeable_text(prediction.get("outcome")),
            probability,
            _codeable_text(prediction.get("qualitativeRisk")),
            _value_text("relativeRisk", prediction.get("relativeRisk")),
            when,
            prediction.get("rationale") or "",
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _adverse_event_suspect_summary(resource):
    lines = []
    for suspect in resource.get("suspectEntity") or []:
        instance = _display(suspect.get("instance"))
        causality_lines = []
        for causality in suspect.get("causality") or []:
            parts = [
                _codeable_text(causality.get("assessment")),
                causality.get("productRelatedness") or "",
                _codeable_text(causality.get("method")),
            ]
            line = " / ".join(part for part in parts if part)
            if line:
                causality_lines.append(line)
        if instance:
            lines.append(instance)
        lines.extend(f"  {line}" for line in causality_lines)
    return "\n".join(lines)


def _adverse_event_causality_summary(resource):
    lines = []
    for suspect in resource.get("suspectEntity") or []:
        for causality in suspect.get("causality") or []:
            parts = [
                _display(causality.get("author")),
                _codeable_text(causality.get("assessment")),
                causality.get("productRelatedness") or "",
                _codeable_text(causality.get("method")),
            ]
            line = " / ".join(part for part in parts if part)
            if line:
                lines.append(line)
    return "\n".join(lines)


def _diagnostic_report_presented_form_summary(resource):
    lines = []
    for attachment in resource.get("presentedForm") or []:
        parts = [
            attachment.get("title") or "",
            attachment.get("contentType") or "",
            attachment.get("url") or "",
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _diagnostic_report_media_summary(resource):
    lines = []
    for media in resource.get("media") or []:
        parts = [media.get("comment") or "", _display(media.get("link"))]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _diagnostic_report_attachment_content(resource, attachment, index):
    data = attachment.get("data")
    if not data:
        return None
    try:
        decoded = b64decode(data)
    except (BinasciiError, ValueError):
        return None
    resource_id = resource.get("id") or "diagnostic-report"
    extension = _file_extension_for_mime_type(attachment.get("contentType"))
    filename = f"fhir-diagnostic-report-{resource_id}-{index}{extension}"
    return filename, ContentFile(decoded)


def _sync_diagnostic_report_presented_documents(resource, diagnostic_report):
    if diagnostic_report.presented_documents.exists():
        return

    documents = []
    for index, attachment in enumerate(resource.get("presentedForm") or [], start=1):
        file_content = _diagnostic_report_attachment_content(resource, attachment, index)
        if not file_content:
            continue
        document = ClinicalDocument(
            patient=diagnostic_report.patient,
            encounter=diagnostic_report.encounter,
            title=attachment.get("title") or diagnostic_report.code or "Diagnostic report",
            document_type=diagnostic_report.category or "Diagnostic report",
            description=diagnostic_report.conclusion or "",
            mime_type=attachment.get("contentType") or "",
            source_name="FHIR DiagnosticReport.presentedForm",
            source_date=diagnostic_report.issued.date() if diagnostic_report.issued else None,
        )
        document.file.save(file_content[0], file_content[1], save=False)
        document.save()
        documents.append(document)
    diagnostic_report.presented_documents.set(documents)


def _sync_medication_administration_relationships(resource, medication_administration=None):
    medication_administration = medication_administration or _object_for_resource(resource, "clinical.MedicationAdministration")
    if not medication_administration:
        return
    changed = []
    for field, value in [
        ("encounter", _reference_as(resource.get("context"), Encounter)),
        ("medication", _reference_as(resource.get("medicationReference"), Medication)),
        ("medication_catalog", _reference_as(resource.get("medicationReference"), MedicationCatalog)),
    ]:
        if value and getattr(medication_administration, f"{field}_id") != value.id:
            setattr(medication_administration, field, value)
            changed.append(field)
    if changed:
        medication_administration.save(update_fields=changed)

    medication_administration.service_requests.set(
        [obj for obj in (_reference_as(resource.get("request"), ServiceRequest),) if obj]
    )
    medication_administration.reason_conditions.set(
        [obj for obj in (_reference_as(ref, Condition) for ref in resource.get("reasonReference") or []) if obj]
    )


def _sync_medication_dispense_relationships(resource, medication_dispense=None):
    medication_dispense = medication_dispense or _object_for_resource(resource, "clinical.MedicationDispense")
    if not medication_dispense:
        return
    changed = []
    for field, value in [
        ("medication", _reference_as(resource.get("medicationReference"), Medication)),
        ("medication_catalog", _reference_as(resource.get("medicationReference"), MedicationCatalog)),
    ]:
        if value and getattr(medication_dispense, f"{field}_id") != value.id:
            setattr(medication_dispense, field, value)
            changed.append(field)
    if changed:
        medication_dispense.save(update_fields=changed)

    medication_dispense.authorizing_requests.set(
        [obj for obj in (_reference_as(ref, ServiceRequest) for ref in resource.get("authorizingPrescription") or []) if obj]
    )


def _sync_communication_relationships(resource, communication=None):
    communication = communication or _object_for_resource(resource, "clinical.Communication")
    if not communication:
        return
    changed = []
    for field, value in [
        ("encounter", _reference_as(resource.get("encounter"), Encounter)),
        ("sender_practitioner", _reference_as(resource.get("sender"), Practitioner)),
        ("sender_organization", _reference_as(resource.get("sender"), Organization)),
        ("sender_related_person", _reference_as(resource.get("sender"), RelatedPerson)),
    ]:
        if value and getattr(communication, f"{field}_id") != value.id:
            setattr(communication, field, value)
            changed.append(field)
    if changed:
        communication.save(update_fields=changed)

    recipients = resource.get("recipient") or []
    communication.recipients_practitioners.set([obj for obj in (_reference_as(ref, Practitioner) for ref in recipients) if obj])
    communication.recipients_organizations.set([obj for obj in (_reference_as(ref, Organization) for ref in recipients) if obj])
    communication.recipients_related_people.set([obj for obj in (_reference_as(ref, RelatedPerson) for ref in recipients) if obj])
    communication.in_response_to.set(
        [obj for obj in (_reference_as(ref, Communication) for ref in resource.get("inResponseTo") or []) if obj]
    )


def _sync_communication_request_relationships(resource, communication_request=None):
    communication_request = communication_request or _object_for_resource(resource, "clinical.CommunicationRequest")
    if not communication_request:
        return
    recipients = resource.get("recipient") or []
    communication_request.recipients_practitioners.set(
        [obj for obj in (_reference_as(ref, Practitioner) for ref in recipients) if obj]
    )
    communication_request.recipients_related_people.set(
        [obj for obj in (_reference_as(ref, RelatedPerson) for ref in recipients) if obj]
    )
    communication_request.based_on_service_requests.set(
        [obj for obj in (_reference_as(ref, ServiceRequest) for ref in resource.get("basedOn") or []) if obj]
    )
    communication_request.replaces.set(
        [obj for obj in (_reference_as(ref, CommunicationRequest) for ref in resource.get("replaces") or []) if obj]
    )


def _sync_flag_relationships(resource, flag=None):
    flag = flag or _object_for_resource(resource, "clinical.Flag")
    if not flag:
        return
    changed = []
    for field, value in [
        ("encounter", _reference_as(resource.get("encounter"), Encounter)),
        ("author_practitioner", _reference_as(resource.get("author"), Practitioner)),
        ("author_organization", _reference_as(resource.get("author"), Organization)),
    ]:
        if value and getattr(flag, f"{field}_id") != value.id:
            setattr(flag, field, value)
            changed.append(field)
    if changed:
        flag.save(update_fields=changed)


def _sync_fhir_list_relationships(resource, fhir_list=None):
    fhir_list = fhir_list or _object_for_resource(resource, "clinical.FHIRList")
    if not fhir_list:
        return
    entries = [entry.get("item") for entry in resource.get("entry") or [] if entry.get("item")]
    fhir_list.conditions.set([obj for obj in (_reference_as(ref, Condition) for ref in entries) if obj])
    fhir_list.observations.set([obj for obj in (_reference_as(ref, Observation) for ref in entries) if obj])
    fhir_list.medications.set([obj for obj in (_reference_as(ref, Medication) for ref in entries) if obj])
    fhir_list.procedures.set([obj for obj in (_reference_as(ref, Procedure) for ref in entries) if obj])
    fhir_list.diagnostic_reports.set([obj for obj in (_reference_as(ref, DiagnosticReport) for ref in entries) if obj])
    fhir_list.documents.set([obj for obj in (_reference_as(ref, ClinicalDocument) for ref in entries) if obj])


def _sync_questionnaire_response_relationships(resource, questionnaire_response=None):
    questionnaire_response = questionnaire_response or _object_for_resource(resource, "clinical.QuestionnaireResponse")
    if not questionnaire_response:
        return
    questionnaire_response.based_on_service_requests.set(
        [obj for obj in (_reference_as(ref, ServiceRequest) for ref in resource.get("basedOn") or []) if obj]
    )
    part_of = resource.get("partOf") or []
    questionnaire_response.part_of_observations.set([obj for obj in (_reference_as(ref, Observation) for ref in part_of) if obj])
    questionnaire_response.part_of_procedures.set([obj for obj in (_reference_as(ref, Procedure) for ref in part_of) if obj])


def _sync_coverage_relationships(resource, coverage=None):
    coverage = coverage or _object_for_resource(resource, "clinical.Coverage")
    if not coverage:
        return
    changed = []
    for field, value in [
        ("payor_organization", _reference_as(_first(resource.get("payor")), Organization)),
        ("policy_holder_patient", _reference_as(resource.get("policyHolder"), PatientProfile)),
        ("subscriber_patient", _reference_as(resource.get("subscriber"), PatientProfile)),
    ]:
        if value and getattr(coverage, f"{field}_id") != value.id:
            setattr(coverage, field, value)
            changed.append(field)
    if changed:
        coverage.save(update_fields=changed)


def _sync_explanation_of_benefit_relationships(resource, explanation_of_benefit=None):
    explanation_of_benefit = explanation_of_benefit or _object_for_resource(resource, "clinical.ExplanationOfBenefit")
    if not explanation_of_benefit:
        return
    insurance = resource.get("insurance") or []
    explanation_of_benefit.coverages.set(
        [obj for obj in (_reference_as(item.get("coverage"), Coverage) for item in insurance) if obj]
    )
    encounter_refs = []
    for item in resource.get("item") or []:
        encounter_refs.extend(item.get("encounter") or [])
    explanation_of_benefit.encounters.set(
        [obj for obj in (_reference_as(ref, Encounter) for ref in encounter_refs) if obj]
    )


def _sync_consent_relationships(resource, consent=None):
    consent = consent or _object_for_resource(resource, "clinical.Consent")
    if not consent:
        return
    consent.performer_practitioners.set(
        [obj for obj in (_reference_as(ref, Practitioner) for ref in resource.get("performer") or []) if obj]
    )

    source_refs = []
    for key in ("sourceReference",):
        if resource.get(key):
            source_refs.append(resource[key])
    consent.source_documents.set([obj for obj in (_reference_as(ref, ClinicalDocument) for ref in source_refs) if obj])

    referenced = _consent_referenced_resources(resource)
    consent.related_immunizations.set([obj for obj in (_reference_as(ref, Immunization) for ref in referenced) if obj])
    consent.questionnaire_responses.set(
        [obj for obj in (_reference_as(ref, QuestionnaireResponse) for ref in referenced + source_refs) if obj]
    )


def _sync_immunization_recommendation_relationships(resource, immunization_recommendation=None):
    immunization_recommendation = immunization_recommendation or _object_for_resource(
        resource,
        "clinical.ImmunizationRecommendation",
    )
    if not immunization_recommendation:
        return
    recommendation = _first(resource.get("recommendation")) or {}
    supporting = recommendation.get("supportingPatientInformation") or []
    immunization_recommendation.supporting_immunizations.set(
        [obj for obj in (_reference_as(ref, Immunization) for ref in recommendation.get("supportingImmunization") or []) if obj]
    )
    immunization_recommendation.supporting_observations.set(
        [obj for obj in (_reference_as(ref, Observation) for ref in supporting) if obj]
    )
    immunization_recommendation.supporting_diagnostic_reports.set(
        [obj for obj in (_reference_as(ref, DiagnosticReport) for ref in supporting) if obj]
    )


def _detected_issue_evidence_summary(resource):
    lines = []
    for evidence in resource.get("evidence") or []:
        codes = [_codeable_text(code) for code in evidence.get("code") or []]
        details = [_display(reference) for reference in evidence.get("detail") or []]
        line = " / ".join(part for part in [", ".join(filter(None, codes)), ", ".join(filter(None, details))] if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _detected_issue_mitigation_summary(resource):
    lines = []
    for mitigation in resource.get("mitigation") or []:
        parts = [
            _codeable_text(mitigation.get("action")),
            mitigation.get("date") or "",
            _display(mitigation.get("author")),
        ]
        line = " / ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _sync_adverse_event_relationships(resource, adverse_event=None):
    adverse_event = adverse_event or _object_for_resource(resource, "clinical.AdverseEvent")
    if not adverse_event:
        return

    changed = []
    for field, value in [
        ("encounter", _reference_as(resource.get("encounter"), Encounter)),
        ("location", _reference_as(resource.get("location"), Location)),
        ("recorder_practitioner", _reference_as(resource.get("recorder"), Practitioner)),
        ("recorder_role", _reference_as(resource.get("recorder"), PractitionerRole)),
    ]:
        if value and getattr(adverse_event, f"{field}_id") != value.id:
            setattr(adverse_event, field, value)
            changed.append(field)
    if changed:
        adverse_event.save(update_fields=changed)

    adverse_event.resulting_conditions.set(
        [obj for obj in (_reference_as(reference, Condition) for reference in resource.get("resultingCondition") or []) if obj]
    )
    adverse_event.contributor_practitioners.set(
        [obj for obj in (_reference_as(reference, Practitioner) for reference in resource.get("contributor") or []) if obj]
    )
    adverse_event.contributor_roles.set(
        [obj for obj in (_reference_as(reference, PractitionerRole) for reference in resource.get("contributor") or []) if obj]
    )
    adverse_event.contributor_devices.set(
        [obj for obj in (_reference_as(reference, Device) for reference in resource.get("contributor") or []) if obj]
    )

    suspect_references = [(suspect.get("instance") or {}) for suspect in resource.get("suspectEntity") or []]
    adverse_event.suspect_immunizations.set(
        [obj for obj in (_reference_as(reference, Immunization) for reference in suspect_references) if obj]
    )
    adverse_event.suspect_procedures.set(
        [obj for obj in (_reference_as(reference, Procedure) for reference in suspect_references) if obj]
    )
    adverse_event.suspect_medications.set(
        [obj for obj in (_reference_as(reference, Medication) for reference in suspect_references) if obj]
    )
    adverse_event.suspect_devices.set(
        [obj for obj in (_reference_as(reference, Device) for reference in suspect_references) if obj]
    )

    adverse_event.reference_documents.set(
        [
            obj
            for obj in (_reference_as(reference, ClinicalDocument) for reference in resource.get("referenceDocument") or [])
            if obj
        ]
    )

    history_refs = resource.get("subjectMedicalHistory") or []
    adverse_event.subject_medical_history_conditions.set(
        [obj for obj in (_reference_as(reference, Condition) for reference in history_refs) if obj]
    )
    adverse_event.subject_medical_history_observations.set(
        [obj for obj in (_reference_as(reference, Observation) for reference in history_refs) if obj]
    )
    adverse_event.subject_medical_history_immunizations.set(
        [obj for obj in (_reference_as(reference, Immunization) for reference in history_refs) if obj]
    )
    adverse_event.subject_medical_history_procedures.set(
        [obj for obj in (_reference_as(reference, Procedure) for reference in history_refs) if obj]
    )


def _sync_family_member_history_relationships(resource, family_member_history=None):
    family_member_history = family_member_history or _object_for_resource(
        resource,
        "clinical.FamilyMemberHistory",
    )
    if not family_member_history:
        return

    conditions = []
    for reference in resource.get("reasonReference") or []:
        condition = _reference_as(reference, Condition)
        if condition:
            conditions.append(condition)
    family_member_history.conditions.set(conditions)

    family_member_history.condition_links.all().delete()
    for condition in resource.get("condition") or []:
        condition_link = FamilyMemberHistoryCondition(
            family_member_history=family_member_history,
            condition_text=_codeable_text(condition.get("code")) or "Family history condition",
            outcome=_codeable_text(condition.get("outcome")) or "",
            contributed_to_death=condition.get("contributedToDeath") if "contributedToDeath" in condition else None,
            onset_text=(
                condition.get("onsetString")
                or _age_text(condition.get("onsetAge"))
                or _range_text(condition.get("onsetRange"))
                or _range_text(condition.get("onsetPeriod"))
            ),
            notes=_notes(condition),
        )
        matched_condition = _condition_by_name(condition_link.condition_text, family_member_history.patient)
        if matched_condition:
            condition_link.condition = matched_condition
        condition_link.save()


def _sync_clinical_impression_relationships(resource, clinical_impression=None):
    clinical_impression = clinical_impression or _object_for_resource(resource, "clinical.ClinicalImpression")
    if not clinical_impression:
        return

    changed = []
    for field, value in [
        ("encounter", _reference_as(resource.get("encounter"), Encounter)),
        ("assessor_practitioner", _reference_as(resource.get("assessor"), Practitioner)),
        ("assessor_role", _reference_as(resource.get("assessor"), PractitionerRole)),
    ]:
        if value and getattr(clinical_impression, f"{field}_id") != value.id:
            setattr(clinical_impression, field, value)
            changed.append(field)
    if changed:
        clinical_impression.save(update_fields=changed)

    clinical_impression.problems.set(
        [obj for obj in (_reference_as(reference, Condition) for reference in resource.get("problem") or []) if obj]
    )

    investigation_refs = []
    for investigation in resource.get("investigation") or []:
        investigation_refs.extend(investigation.get("item") or [])
    clinical_impression.investigations_observations.set(
        [obj for obj in (_reference_as(reference, Observation) for reference in investigation_refs) if obj]
    )

    condition_refs = []
    observation_refs = []
    clinical_impression.finding_links.all().delete()
    for finding in resource.get("finding") or []:
        condition = _reference_as(finding.get("itemReference"), Condition)
        observation = _reference_as(finding.get("itemReference"), Observation)
        finding_link = ClinicalImpressionFinding(
            clinical_impression=clinical_impression,
            condition=condition,
            observation=observation,
            finding_text=_codeable_text(finding.get("itemCodeableConcept")) or _display(finding.get("itemReference")),
            basis=finding.get("basis") or "",
        )
        finding_link.save()
        if condition:
            condition_refs.append(condition)
        if observation:
            observation_refs.append(observation)
    clinical_impression.conditions.set(condition_refs)
    clinical_impression.observations.set(observation_refs)


def _sync_diagnostic_report_relationships(resource, diagnostic_report=None):
    diagnostic_report = diagnostic_report or _object_for_resource(resource, "clinical.DiagnosticReport")
    if not diagnostic_report:
        return

    encounter = _reference_as(resource.get("encounter"), Encounter)
    if encounter and diagnostic_report.encounter_id != encounter.id:
        diagnostic_report.encounter = encounter
        diagnostic_report.save(update_fields=["encounter"])

    based_on = resource.get("basedOn") or []
    diagnostic_report.care_plans.set(
        [obj for obj in (_reference_as(reference, CarePlan) for reference in based_on) if obj]
    )
    diagnostic_report.service_requests.set(
        [obj for obj in (_reference_as(reference, ServiceRequest) for reference in based_on) if obj]
    )
    diagnostic_report.specimens.set(
        [obj for obj in (_reference_as(reference, Specimen) for reference in resource.get("specimen") or []) if obj]
    )
    diagnostic_report.observations.set(
        [obj for obj in (_reference_as(reference, Observation) for reference in resource.get("result") or []) if obj]
    )

    performers = resource.get("performer") or []
    diagnostic_report.performers_practitioners.set(
        [obj for obj in (_reference_as(reference, Practitioner) for reference in performers) if obj]
    )
    diagnostic_report.performers_roles.set(
        [obj for obj in (_reference_as(reference, PractitionerRole) for reference in performers) if obj]
    )
    diagnostic_report.performers_organizations.set(
        [obj for obj in (_reference_as(reference, Organization) for reference in performers) if obj]
    )
    diagnostic_report.performers_care_teams.set(
        [obj for obj in (_reference_as(reference, CareTeam) for reference in performers) if obj]
    )

    interpreters = resource.get("resultsInterpreter") or []
    diagnostic_report.interpreter_practitioners.set(
        [obj for obj in (_reference_as(reference, Practitioner) for reference in interpreters) if obj]
    )
    diagnostic_report.interpreter_roles.set(
        [obj for obj in (_reference_as(reference, PractitionerRole) for reference in interpreters) if obj]
    )
    diagnostic_report.interpreter_organizations.set(
        [obj for obj in (_reference_as(reference, Organization) for reference in interpreters) if obj]
    )
    diagnostic_report.interpreter_care_teams.set(
        [obj for obj in (_reference_as(reference, CareTeam) for reference in interpreters) if obj]
    )

    _sync_diagnostic_report_presented_documents(resource, diagnostic_report)


def _sync_detected_issue_relationships(resource, detected_issue=None):
    detected_issue = detected_issue or _object_for_resource(resource, "clinical.DetectedIssue")
    if not detected_issue:
        return

    changed = []
    for field, value in [
        ("author_practitioner", _reference_as(resource.get("author"), Practitioner)),
        ("author_role", _reference_as(resource.get("author"), PractitionerRole)),
        ("author_device", _reference_as(resource.get("author"), Device)),
    ]:
        if value and getattr(detected_issue, f"{field}_id") != value.id:
            setattr(detected_issue, field, value)
            changed.append(field)
    if changed:
        detected_issue.save(update_fields=changed)

    implicated = resource.get("implicated") or []
    detected_issue.implicated_conditions.set(
        [obj for obj in (_reference_as(reference, Condition) for reference in implicated) if obj]
    )
    detected_issue.implicated_medications.set(
        [obj for obj in (_reference_as(reference, Medication) for reference in implicated) if obj]
    )
    detected_issue.implicated_immunizations.set(
        [obj for obj in (_reference_as(reference, Immunization) for reference in implicated) if obj]
    )
    detected_issue.implicated_observations.set(
        [obj for obj in (_reference_as(reference, Observation) for reference in implicated) if obj]
    )
    detected_issue.implicated_service_requests.set(
        [obj for obj in (_reference_as(reference, ServiceRequest) for reference in implicated) if obj]
    )
    detected_issue.implicated_procedures.set(
        [obj for obj in (_reference_as(reference, Procedure) for reference in implicated) if obj]
    )
    detected_issue.implicated_devices.set(
        [obj for obj in (_reference_as(reference, Device) for reference in implicated) if obj]
    )
    detected_issue.implicated_diagnostic_reports.set(
        [obj for obj in (_reference_as(reference, DiagnosticReport) for reference in implicated) if obj]
    )

    evidence_refs = []
    for evidence in resource.get("evidence") or []:
        evidence_refs.extend(evidence.get("detail") or [])
    detected_issue.evidence_observations.set(
        [obj for obj in (_reference_as(reference, Observation) for reference in evidence_refs) if obj]
    )
    detected_issue.evidence_conditions.set(
        [obj for obj in (_reference_as(reference, Condition) for reference in evidence_refs) if obj]
    )
    detected_issue.evidence_diagnostic_reports.set(
        [obj for obj in (_reference_as(reference, DiagnosticReport) for reference in evidence_refs) if obj]
    )


def _sync_person_relationships(resource, person=None):
    person = person or _object_for_resource(resource, "clinical.Person")
    if not person:
        return

    managing_organization = _reference_as(resource.get("managingOrganization"), Organization)
    if managing_organization and person.managing_organization_id != managing_organization.id:
        person.managing_organization = managing_organization
        person.save(update_fields=["managing_organization"])

    person.link_records.all().delete()
    for link in resource.get("link") or []:
        target = link.get("target") or {}
        target_reference = target.get("reference") or ""
        target_obj = _object_for_reference(target_reference)
        person_link = PersonLink(
            person=person,
            target_display=_display(target),
            target_reference=target_reference,
            assurance=link.get("assurance") or "",
        )
        if isinstance(target_obj, PatientProfile):
            person_link.patient = target_obj
        elif isinstance(target_obj, Practitioner):
            person_link.practitioner = target_obj
        elif isinstance(target_obj, RelatedPerson):
            old_person = target_obj.person if target_obj.person_id and target_obj.person_id != person.id else None
            person_link.related_person = target_obj
            if target_obj.person_id != person.id:
                target_obj.person = person
                target_obj.save(update_fields=["person"])
            if old_person and old_person.notes == "Created from RelatedPerson." and not old_person.related_person_roles.exists():
                old_person.delete()
        elif isinstance(target_obj, Person):
            person_link.linked_person = target_obj
        person_link.save()


def _sync_group_relationships(resource, group=None):
    group = group or _object_for_resource(resource, "clinical.FHIRGroup")
    if not group:
        return

    managing_entity = resource.get("managingEntity")
    changed = []
    for field, value in [
        ("managing_organization", _reference_as(managing_entity, Organization)),
        ("managing_practitioner", _reference_as(managing_entity, Practitioner)),
        ("managing_role", _reference_as(managing_entity, PractitionerRole)),
        ("managing_related_person", _reference_as(managing_entity, RelatedPerson)),
    ]:
        if value and getattr(group, f"{field}_id") != value.id:
            setattr(group, field, value)
            changed.append(field)
    if changed:
        group.save(update_fields=changed)

    group.member_links.all().delete()
    for member in resource.get("member") or []:
        entity = member.get("entity") or {}
        entity_reference = entity.get("reference") or ""
        period = member.get("period") or {}
        member_obj = _object_for_reference(entity_reference)
        member_link = FHIRGroupMember(
            group=group,
            entity_display=_display(entity),
            entity_reference=entity_reference,
            start_date=_date(period.get("start")),
            end_date=_date(period.get("end")),
            inactive=member.get("inactive") if "inactive" in member else None,
        )
        if isinstance(member_obj, PatientProfile):
            member_link.patient = member_obj
        elif isinstance(member_obj, Practitioner):
            member_link.practitioner = member_obj
        elif isinstance(member_obj, PractitionerRole):
            member_link.practitioner_role = member_obj
        elif isinstance(member_obj, Device):
            member_link.device = member_obj
        elif isinstance(member_obj, Medication):
            member_link.medication = member_obj
        elif isinstance(member_obj, FHIRGroup):
            member_link.member_group = member_obj
        member_link.save()


def _sync_risk_assessment_relationships(resource, risk_assessment=None):
    risk_assessment = risk_assessment or _object_for_resource(resource, "clinical.RiskAssessment")
    if not risk_assessment:
        return

    changed = []
    for field, value in [
        ("encounter", _reference_as(resource.get("encounter"), Encounter)),
        ("performer_practitioner", _reference_as(resource.get("performer"), Practitioner)),
        ("performer_role", _reference_as(resource.get("performer"), PractitionerRole)),
        ("performer_organization", _reference_as(resource.get("performer"), Organization)),
        ("performer_device", _reference_as(resource.get("performer"), Device)),
    ]:
        if value and getattr(risk_assessment, f"{field}_id") != value.id:
            setattr(risk_assessment, field, value)
            changed.append(field)
    if changed:
        risk_assessment.save(update_fields=changed)

    basis = resource.get("basis") or []
    risk_assessment.conditions.set([obj for obj in (_reference_as(ref, Condition) for ref in basis) if obj])
    risk_assessment.observations.set([obj for obj in (_reference_as(ref, Observation) for ref in basis) if obj])
    risk_assessment.diagnostic_reports.set([obj for obj in (_reference_as(ref, DiagnosticReport) for ref in basis) if obj])


def _sync_goal_relationships(resource, goal=None):
    goal = goal or _object_for_resource(resource, "clinical.Goal")
    if not goal:
        return

    changed = []
    for field, value in [
        ("subject_group", _reference_as(resource.get("subject"), FHIRGroup)),
        ("expressed_by_practitioner", _reference_as(resource.get("expressedBy"), Practitioner)),
        ("expressed_by_role", _reference_as(resource.get("expressedBy"), PractitionerRole)),
        ("expressed_by_related_person", _reference_as(resource.get("expressedBy"), RelatedPerson)),
    ]:
        if value and getattr(goal, f"{field}_id") != value.id:
            setattr(goal, field, value)
            changed.append(field)
    if changed:
        goal.save(update_fields=changed)

    addresses = resource.get("addresses") or []
    goal.addresses_conditions.set([obj for obj in (_reference_as(ref, Condition) for ref in addresses) if obj])
    goal.addresses_observations.set([obj for obj in (_reference_as(ref, Observation) for ref in addresses) if obj])
    goal.addresses_medications.set([obj for obj in (_reference_as(ref, Medication) for ref in addresses) if obj])
    goal.addresses_service_requests.set([obj for obj in (_reference_as(ref, ServiceRequest) for ref in addresses) if obj])
    goal.addresses_risk_assessments.set([obj for obj in (_reference_as(ref, RiskAssessment) for ref in addresses) if obj])
    goal.outcome_observations.set(
        [obj for obj in (_reference_as(ref, Observation) for ref in resource.get("outcomeReference") or []) if obj]
    )


def _sync_device_request_relationships(resource, device_request=None):
    device_request = device_request or _object_for_resource(resource, "clinical.DeviceRequest")
    if not device_request:
        return

    changed = []
    for field, value in [
        ("encounter", _reference_as(resource.get("encounter"), Encounter)),
        ("requester_practitioner", _reference_as(resource.get("requester"), Practitioner)),
        ("requester_role", _reference_as(resource.get("requester"), PractitionerRole)),
    ]:
        if value and getattr(device_request, f"{field}_id") != value.id:
            setattr(device_request, field, value)
            changed.append(field)
    if changed:
        device_request.save(update_fields=changed)

    code_refs = [resource.get("codeReference")] if resource.get("codeReference") else []
    device_request.devices.set([obj for obj in (_reference_as(ref, Device) for ref in code_refs) if obj])
    based_on = resource.get("basedOn") or []
    device_request.care_plans.set([obj for obj in (_reference_as(ref, CarePlan) for ref in based_on) if obj])
    device_request.service_requests.set([obj for obj in (_reference_as(ref, ServiceRequest) for ref in based_on) if obj])
    device_request.replaces.set([obj for obj in (_reference_as(ref, DeviceRequest) for ref in resource.get("replaces") or []) if obj])

    reason_refs = resource.get("reasonReference") or []
    device_request.conditions.set([obj for obj in (_reference_as(ref, Condition) for ref in reason_refs) if obj])
    device_request.observations.set([obj for obj in (_reference_as(ref, Observation) for ref in reason_refs) if obj])
    device_request.diagnostic_reports.set([obj for obj in (_reference_as(ref, DiagnosticReport) for ref in reason_refs) if obj])
    device_request.risk_assessments.set([obj for obj in (_reference_as(ref, RiskAssessment) for ref in reason_refs) if obj])

    performers = resource.get("performer") or []
    device_request.performers_practitioners.set(
        [obj for obj in (_reference_as(ref, Practitioner) for ref in performers) if obj]
    )
    device_request.performers_roles.set(
        [obj for obj in (_reference_as(ref, PractitionerRole) for ref in performers) if obj]
    )
    device_request.performers_organizations.set(
        [obj for obj in (_reference_as(ref, Organization) for ref in performers) if obj]
    )


def _sync_device_use_statement_relationships(resource, device_use_statement=None):
    device_use_statement = device_use_statement or _object_for_resource(resource, "clinical.DeviceUseStatement")
    if not device_use_statement:
        return

    changed = []
    for field, value in [
        ("device", _reference_as(resource.get("device"), Device)),
        ("source_practitioner", _reference_as(resource.get("source"), Practitioner)),
        ("source_role", _reference_as(resource.get("source"), PractitionerRole)),
        ("source_related_person", _reference_as(resource.get("source"), RelatedPerson)),
    ]:
        if value and getattr(device_use_statement, f"{field}_id") != value.id:
            setattr(device_use_statement, field, value)
            changed.append(field)
    if changed:
        device_use_statement.save(update_fields=changed)

    based_on = resource.get("basedOn") or []
    device_use_statement.based_on_service_requests.set(
        [obj for obj in (_reference_as(ref, ServiceRequest) for ref in based_on) if obj]
    )
    device_use_statement.based_on_device_requests.set(
        [obj for obj in (_reference_as(ref, DeviceRequest) for ref in based_on) if obj]
    )
    reason_refs = resource.get("reasonReference") or []
    device_use_statement.reason_conditions.set([obj for obj in (_reference_as(ref, Condition) for ref in reason_refs) if obj])
    device_use_statement.reason_observations.set([obj for obj in (_reference_as(ref, Observation) for ref in reason_refs) if obj])
    device_use_statement.reason_diagnostic_reports.set(
        [obj for obj in (_reference_as(ref, DiagnosticReport) for ref in reason_refs) if obj]
    )
    device_use_statement.reason_risk_assessments.set(
        [obj for obj in (_reference_as(ref, RiskAssessment) for ref in reason_refs) if obj]
    )


def _sync_document_reference_relationships(resource, document=None):
    document = document or _object_for_resource(resource, "documents.ClinicalDocument")
    if not document:
        return

    context = resource.get("context") or {}
    encounter = _reference_as(_first(context.get("encounter")), Encounter)
    custodian = _reference_as(resource.get("custodian"), Organization)
    changed = []
    if encounter and document.encounter_id != encounter.id:
        document.encounter = encounter
        changed.append("encounter")
    if custodian and document.custodian_id != custodian.id:
        document.custodian = custodian
        changed.append("custodian")
    if changed:
        document.save(update_fields=changed)

    authors = []
    for reference in resource.get("author") or []:
        author = _reference_as(reference, Practitioner)
        if author:
            authors.append(author)
    document.authors.set(authors)

    related_documents = []
    for related in resource.get("relatesTo") or []:
        related_document = _reference_as(related.get("target"), ClinicalDocument)
        if related_document:
            related_documents.append(related_document)
    document.related_documents.set(related_documents)


def _sync_encounter_relationships(resource, encounter=None):
    encounter = encounter or _object_for_resource(resource, "clinical.Encounter")
    if not encounter:
        return

    episodes = []
    for reference in resource.get("episodeOfCare") or []:
        episode = _reference_as(reference, EpisodeOfCare)
        if episode:
            episodes.append(episode)
    encounter.episodes_of_care.set(episodes)


def _sync_observation_relationships(resource, observation=None):
    observation = observation or _object_for_resource(resource, "clinical.Observation")
    if not observation:
        return
    specimen = _reference_as(resource.get("specimen"), Specimen)
    device = _reference_as(resource.get("device"), Device)
    changed = []
    if specimen and observation.specimen_id != specimen.id:
        observation.specimen = specimen
        changed.append("specimen")
    if device and observation.device_id != device.id:
        observation.device = device
        changed.append("device")
    if changed:
        observation.save(update_fields=changed)


def _sync_care_plan_relationships(resource, care_plan=None):
    care_plan = care_plan or _object_for_resource(resource, "clinical.CarePlan")
    if not care_plan:
        return

    conditions = []
    for reference in resource.get("addresses") or []:
        condition = _reference_as(reference, Condition)
        if condition:
            conditions.append(condition)
    care_plan.conditions.set(conditions)

    care_teams = []
    for reference in resource.get("careTeam") or []:
        care_team = _reference_as(reference, CareTeam)
        if care_team:
            care_teams.append(care_team)
    care_plan.care_teams.set(care_teams)


def _sync_procedure_relationships(resource, procedure=None):
    procedure = procedure or _object_for_resource(resource, "clinical.Procedure")
    if not procedure:
        return

    encounter = _reference_as(resource.get("encounter"), Encounter)
    if encounter and procedure.encounter_id != encounter.id:
        procedure.encounter = encounter
        procedure.save(update_fields=["encounter"])

    conditions = []
    for reference in resource.get("reasonReference") or []:
        condition = _reference_as(reference, Condition)
        if condition:
            conditions.append(condition)
    procedure.conditions.set(conditions)

    care_plans = []
    for reference in resource.get("basedOn") or []:
        care_plan = _reference_as(reference, CarePlan)
        if care_plan:
            care_plans.append(care_plan)
    procedure.care_plans.set(care_plans)

    service_requests = []
    for reference in resource.get("basedOn") or []:
        service_request = _reference_as(reference, ServiceRequest)
        if service_request:
            service_requests.append(service_request)
    procedure.service_requests.set(service_requests)

    _sync_procedure_performers(resource, procedure)


def _sync_specimen_relationships(resource, specimen=None):
    specimen = specimen or _object_for_resource(resource, "clinical.Specimen")
    if not specimen:
        return

    parent_specimens = []
    for reference in resource.get("parent") or []:
        parent_specimen = _reference_as(reference, Specimen)
        if parent_specimen:
            parent_specimens.append(parent_specimen)
    specimen.parent_specimens.set(parent_specimens)


def _sync_practitioner_role_relationships(resource, practitioner_role=None):
    practitioner_role = practitioner_role or _object_for_resource(resource, "clinical.PractitionerRole")
    if not practitioner_role:
        return

    locations = []
    for reference in resource.get("location") or []:
        location = _reference_as(reference, Location)
        if location:
            locations.append(location)
    practitioner_role.locations.set(locations)


def _sync_service_request_relationships(resource, service_request=None):
    service_request = service_request or _object_for_resource(resource, "clinical.ServiceRequest")
    if not service_request:
        return

    encounter = _reference_as(resource.get("encounter"), Encounter)
    requester_practitioner = _reference_as(resource.get("requester"), Practitioner)
    requester_role = _reference_as(resource.get("requester"), PractitionerRole)
    requester_organization = _reference_as(resource.get("requester"), Organization)
    requester_device = _reference_as(resource.get("requester"), Device)
    changed = []
    for field, value in [
        ("encounter", encounter),
        ("requester_practitioner", requester_practitioner),
        ("requester_role", requester_role),
        ("requester_organization", requester_organization),
        ("requester_device", requester_device),
    ]:
        if value and getattr(service_request, f"{field}_id") != value.id:
            setattr(service_request, field, value)
            changed.append(field)
    if changed:
        service_request.save(update_fields=changed)

    care_plans = []
    for reference in resource.get("basedOn") or []:
        care_plan = _reference_as(reference, CarePlan)
        if care_plan:
            care_plans.append(care_plan)
    service_request.care_plans.set(care_plans)

    replacements = []
    for reference in resource.get("replaces") or []:
        replacement = _reference_as(reference, ServiceRequest)
        if replacement:
            replacements.append(replacement)
    service_request.replaces.set(replacements)

    service_request.performers_practitioners.set(
        [obj for obj in (_reference_as(reference, Practitioner) for reference in resource.get("performer") or []) if obj]
    )
    service_request.performers_roles.set(
        [obj for obj in (_reference_as(reference, PractitionerRole) for reference in resource.get("performer") or []) if obj]
    )
    service_request.performers_organizations.set(
        [obj for obj in (_reference_as(reference, Organization) for reference in resource.get("performer") or []) if obj]
    )
    service_request.performers_care_teams.set(
        [obj for obj in (_reference_as(reference, CareTeam) for reference in resource.get("performer") or []) if obj]
    )
    service_request.performers_devices.set(
        [obj for obj in (_reference_as(reference, Device) for reference in resource.get("performer") or []) if obj]
    )
    service_request.locations.set(
        [
            obj
            for obj in (_reference_as(reference, Location) for reference in resource.get("locationReference") or [])
            if obj
        ]
    )
    service_request.conditions.set(
        [
            obj
            for obj in (_reference_as(reference, Condition) for reference in resource.get("reasonReference") or [])
            if obj
        ]
    )
    service_request.specimens.set(
        [obj for obj in (_reference_as(reference, Specimen) for reference in resource.get("specimen") or []) if obj]
    )


def _sync_episode_of_care_relationships(resource, episode=None):
    episode = episode or _object_for_resource(resource, "clinical.EpisodeOfCare")
    if not episode:
        return

    managing_organization = _reference_as(resource.get("managingOrganization"), Organization)
    care_manager_practitioner = _reference_as(resource.get("careManager"), Practitioner)
    care_manager_role = _reference_as(resource.get("careManager"), PractitionerRole)
    changed = []
    for field, value in [
        ("managing_organization", managing_organization),
        ("care_manager_practitioner", care_manager_practitioner),
        ("care_manager_role", care_manager_role),
    ]:
        if value and getattr(episode, f"{field}_id") != value.id:
            setattr(episode, field, value)
            changed.append(field)
    if changed:
        episode.save(update_fields=changed)

    episode.referral_requests.set(
        [
            obj
            for obj in (_reference_as(reference, ServiceRequest) for reference in resource.get("referralRequest") or [])
            if obj
        ]
    )
    episode.care_teams.set(
        [obj for obj in (_reference_as(reference, CareTeam) for reference in resource.get("team") or []) if obj]
    )


def _sync_procedure_performers(resource, procedure):
    procedure.performer_links.all().delete()
    for performer in resource.get("performer") or []:
        actor = performer.get("actor") or {}
        on_behalf_of = performer.get("onBehalfOf") or {}
        actor_reference = actor.get("reference") or ""
        on_behalf_of_reference = on_behalf_of.get("reference") or ""

        performer_link = ProcedurePerformer(
            procedure=procedure,
            role=_codeable_text(performer.get("function")) or "",
            actor_display=_display(actor),
            actor_reference=actor_reference,
            on_behalf_of_display=_display(on_behalf_of),
            on_behalf_of_reference=on_behalf_of_reference,
        )

        actor_obj = _object_for_reference(actor_reference)
        if isinstance(actor_obj, Practitioner):
            performer_link.practitioner = actor_obj
        elif isinstance(actor_obj, Organization):
            performer_link.organization = actor_obj

        on_behalf_of_obj = _object_for_reference(on_behalf_of_reference)
        if isinstance(on_behalf_of_obj, Organization) and not performer_link.organization:
            performer_link.organization = on_behalf_of_obj

        performer_link.save()


def _sync_care_team_participants(resource, care_team):
    care_team.participant_links.all().delete()
    for participant in resource.get("participant") or []:
        member = participant.get("member") or {}
        on_behalf_of = participant.get("onBehalfOf") or {}
        period = participant.get("period") or {}
        member_reference = member.get("reference") or ""
        on_behalf_of_reference = on_behalf_of.get("reference") or ""

        participant_link = CareTeamParticipant(
            care_team=care_team,
            role=_codeable_text(_first(participant.get("role"))) or "",
            member_display=_display(member),
            member_reference=member_reference,
            on_behalf_of_display=_display(on_behalf_of),
            on_behalf_of_reference=on_behalf_of_reference,
            start_date=_date(period.get("start")),
            end_date=_date(period.get("end")),
        )

        member_obj = _object_for_reference(member_reference)
        if isinstance(member_obj, Practitioner):
            participant_link.practitioner = member_obj
        elif isinstance(member_obj, Organization):
            participant_link.organization = member_obj
        elif isinstance(member_obj, Location):
            participant_link.location = member_obj
        elif isinstance(member_obj, RelatedPerson):
            participant_link.related_person = member_obj

        on_behalf_of_obj = _object_for_reference(on_behalf_of_reference)
        if isinstance(on_behalf_of_obj, Organization) and not participant_link.organization:
            participant_link.organization = on_behalf_of_obj

        participant_link.save()


def _observation_category(resource):
    category = _codeable_text(_first(resource.get("category"))).lower()
    if "vital" in category:
        return "vital"
    if "lab" in category or "laboratory" in category:
        return "lab"
    return "other"


def _reference_range(resource):
    first_range = _first(resource.get("referenceRange")) or {}
    text = first_range.get("text")
    if text:
        return text
    low = (first_range.get("low") or {}).get("value")
    high = (first_range.get("high") or {}).get("value")
    if low is not None and high is not None:
        return f"{low} - {high}"
    return ""


def _date(value):
    if not value:
        return None
    parsed = parse_date(str(value)[:10])
    if parsed:
        return parsed
    parsed_datetime = parse_datetime(str(value))
    return parsed_datetime.date() if parsed_datetime else None


def _datetime(value):
    if not value:
        return None
    return parse_datetime(str(value))


def _decimal(value):
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None



















