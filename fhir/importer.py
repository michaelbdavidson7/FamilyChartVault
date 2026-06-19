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
    Allergy,
    CarePlan,
    CareTeam,
    CareTeamParticipant,
    Condition,
    Device,
    Encounter,
    EpisodeOfCare,
    Immunization,
    Location,
    Medication,
    Observation,
    Organization,
    Practitioner,
    PractitionerRole,
    Procedure,
    ProcedurePerformer,
    ServiceRequest,
    Specimen,
)
from documents.models import ClinicalDocument
from patients.models import PatientProfile

from .models import FHIRLink, FHIRResourceSnapshot


SUPPORTED_RESOURCE_TYPES = {
    "Patient",
    "Condition",
    "AllergyIntolerance",
    "MedicationStatement",
    "MedicationRequest",
    "Immunization",
    "Observation",
    "Encounter",
    "CareTeam",
    "CarePlan",
    "Device",
    "DocumentReference",
    "EpisodeOfCare",
    "PractitionerRole",
    "Procedure",
    "ServiceRequest",
    "Specimen",
    "Practitioner",
    "Organization",
    "Location",
}

PATIENTLESS_RESOURCE_TYPES = {
    "Practitioner",
    "PractitionerRole",
    "Organization",
    "Location",
}


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
                "Practitioner": _import_practitioner,
                "PractitionerRole": _import_practitioner_role,
                "Organization": _import_organization,
                "Location": _import_location,
            }[resource_type]
            obj, created = importer(resource, None)
            _record_import(result, created)
            _snapshot(resource, None, source, result)
            _link(resource, None, _model_label(obj), obj.id, "fhir_to_internal")

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
                "AllergyIntolerance": _import_allergy,
                "MedicationStatement": _import_medication_statement,
                "MedicationRequest": _import_medication_request,
                "Immunization": _import_immunization,
                "Observation": _import_observation,
                "Encounter": _import_encounter,
                "CareTeam": _import_care_team,
                "CarePlan": _import_care_plan,
                "Device": _import_device,
                "DocumentReference": _import_document_reference,
                "EpisodeOfCare": _import_episode_of_care,
                "PractitionerRole": _import_practitioner_role,
                "Procedure": _import_procedure,
                "ServiceRequest": _import_service_request,
                "Specimen": _import_specimen,
                "Practitioner": _import_practitioner,
                "Organization": _import_organization,
                "Location": _import_location,
            }[resource_type]
            obj, created = importer(resource, patient)
            _record_import(result, created)
            _snapshot(resource, patient, source, result)
            _link(resource, patient, _model_label(obj), obj.id, "fhir_to_internal")

        for resource in resources:
            resource_type = resource.get("resourceType")
            if resource_type == "Observation":
                _sync_observation_relationships(resource)
            elif resource_type == "CarePlan":
                _sync_care_plan_relationships(resource)
            elif resource_type == "DocumentReference":
                _sync_document_reference_relationships(resource)
            elif resource_type == "Encounter":
                _sync_encounter_relationships(resource)
            elif resource_type == "EpisodeOfCare":
                _sync_episode_of_care_relationships(resource)
            elif resource_type == "PractitionerRole":
                _sync_practitioner_role_relationships(resource)
            elif resource_type == "Procedure":
                _sync_procedure_relationships(resource)
            elif resource_type == "ServiceRequest":
                _sync_service_request_relationships(resource)
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
        Condition,
        Allergy,
        Medication,
        Immunization,
        Observation,
        Specimen,
        Device,
        Encounter,
        EpisodeOfCare,
        CareTeam,
        CarePlan,
        CareTeamParticipant,
        ClinicalDocument,
        Practitioner,
        PractitionerRole,
        Procedure,
        ProcedurePerformer,
        ServiceRequest,
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
        "Practitioner": "clinical.Practitioner",
        "PractitionerRole": "clinical.PractitionerRole",
        "Organization": "clinical.Organization",
        "Location": "clinical.Location",
        "Encounter": "clinical.Encounter",
        "EpisodeOfCare": "clinical.EpisodeOfCare",
        "Condition": "clinical.Condition",
        "CareTeam": "clinical.CareTeam",
        "CarePlan": "clinical.CarePlan",
        "Device": "clinical.Device",
        "Procedure": "clinical.Procedure",
        "ServiceRequest": "clinical.ServiceRequest",
        "Specimen": "clinical.Specimen",
        "DocumentReference": "documents.ClinicalDocument",
    }
    django_model = model_by_resource_type.get(resource_type)
    if not django_model:
        return None
    return _object_for_resource({"resourceType": resource_type, "id": resource_id}, django_model)


def _resolve_patient(resource, patient_by_reference, default_patient=None):
    subject = resource.get("subject") or resource.get("patient")
    reference = subject.get("reference") if isinstance(subject, dict) else None
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


def _medication_name(resource):
    return (
        _codeable_text(resource.get("medicationCodeableConcept"))
        or _display(resource.get("medicationReference"))
    )


def _dosage_text(resource):
    dosage = _first(resource.get("dosage")) or {}
    return dosage.get("text") or ""


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
