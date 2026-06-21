import json
import tempfile
from base64 import b64encode
from datetime import date
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch
from zipfile import ZipFile

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse

from clinical.models import (
    AdverseEvent,
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
    BodyStructure,
    CarePlan,
    CareTeam,
    CareTeamParticipant,
    ClinicalImpression,
    ClinicalImpressionFinding,
    CodeSystem,
    ConceptMap,
    Condition,
    DetectedIssue,
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
    Flag,
    Goal,
    Immunization,
    ImmunizationRecommendation,
    Location,
    Library,
    MedicationAdministration,
    MedicationCatalog,
    MedicationDispense,
    Medication,
    Measure,
    MeasureReport,
    NutritionOrder,
    Observation,
    Organization,
    Person,
    PersonLink,
    PaymentNotice,
    PaymentReconciliation,
    PlanDefinition,
    Practitioner,
    PractitionerRole,
    Procedure,
    ProcedurePerformer,
    RelatedPerson,
    RiskAssessment,
    ServiceRequest,
    Specimen,
    TestReport,
    TestScript,
    ValueSet,
    Communication,
    CommunicationRequest,
    Consent,
    Coverage,
    CoverageEligibilityRequest,
    CoverageEligibilityResponse,
    EnrollmentRequest,
    EnrollmentResponse,
    ExplanationOfBenefit,
    InsurancePlan,
    QuestionnaireResponse,
)
from documents.models import ClinicalDocument
from patients.models import PatientProfile

from .backups import create_pre_import_database_backup, list_fhir_import_database_backups
from .forms import FHIRImportForm
from .importer import import_fhir_json, import_fhir_payloads, loads_fhir_documents, loads_fhir_json
from .models import FHIRLink, FHIRResourceSnapshot


class FHIRImportTests(TestCase):
    def test_imports_bundle_patient_and_clinical_resources(self):
        payload = {
            "resourceType": "Bundle",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "pat-1",
                        "name": [{"family": "Rivera", "given": ["Maya"]}],
                        "birthDate": "1980-04-12",
                        "gender": "female",
                        "telecom": [
                            {"system": "phone", "value": "555-0100"},
                            {"system": "email", "value": "maya@example.test"},
                        ],
                        "address": [{"line": ["1 Main St"], "city": "Boston", "state": "MA"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Condition",
                        "id": "cond-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "code": {
                            "text": "Asthma",
                            "coding": [{"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "J45.909"}],
                        },
                        "clinicalStatus": {"coding": [{"code": "active", "display": "Active"}]},
                        "onsetDateTime": "2020-01-02",
                    }
                },
                {
                    "resource": {
                        "resourceType": "MedicationStatement",
                        "id": "med-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "active",
                        "medicationCodeableConcept": {"text": "Albuterol inhaler"},
                        "dosage": [{"text": "2 puffs as needed"}],
                        "effectivePeriod": {"start": "2021-02-03"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "obs-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "category": [{"text": "Vital Signs"}],
                        "code": {"text": "Body weight"},
                        "valueQuantity": {"value": 72.5, "unit": "kg"},
                        "effectiveDateTime": "2022-03-04T10:15:00Z",
                    }
                },
            ],
        }

        result = import_fhir_json(payload)

        self.assertEqual(result.created, 4)
        self.assertEqual(result.updated, 0)
        self.assertEqual(result.snapshots, 4)
        self.assertEqual(result.errors, [])

        patient = PatientProfile.objects.get()
        self.assertEqual(patient.first_name, "Maya")
        self.assertEqual(patient.last_name, "Rivera")
        self.assertEqual(patient.date_of_birth, date(1980, 4, 12))
        self.assertEqual(patient.email, "maya@example.test")

        condition = Condition.objects.get()
        self.assertEqual(condition.patient, patient)
        self.assertEqual(condition.name, "Asthma")
        self.assertEqual(condition.icd10_code, "J45.909")

        medication = Medication.objects.get()
        self.assertEqual(medication.name, "Albuterol inhaler")
        self.assertEqual(medication.dosage_text, "2 puffs as needed")

        observation = Observation.objects.get()
        self.assertEqual(observation.category, "vital")
        self.assertEqual(observation.value_quantity, 72.5)
        self.assertEqual(observation.unit, "kg")

        self.assertEqual(FHIRResourceSnapshot.objects.count(), 4)
        self.assertEqual(FHIRLink.objects.count(), 4)

    def test_imports_extended_clinical_resource_batch(self):
        payload = {
            "resourceType": "Bundle",
            "entry": [
                {"resource": {"resourceType": "Patient", "id": "pat-extended", "name": [{"family": "Chen", "given": ["Ari"]}]}},
                {"resource": {"resourceType": "Organization", "id": "org-1", "name": "Good Health"}},
                {"resource": {"resourceType": "Practitioner", "id": "prac-1", "name": [{"text": "Dr. Stone"}]}},
                {
                    "resource": {
                        "resourceType": "Medication",
                        "id": "medcat-1",
                        "code": {"text": "Acetaminophen 325 MG Oral Tablet"},
                        "status": "active",
                        "manufacturer": {"reference": "Organization/org-1"},
                        "form": {"text": "Tablet"},
                        "ingredient": [{"itemCodeableConcept": {"text": "Acetaminophen"}, "isActive": True}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Condition",
                        "id": "cond-ext",
                        "subject": {"reference": "Patient/pat-extended"},
                        "code": {"text": "Fever"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "obs-ext",
                        "subject": {"reference": "Patient/pat-extended"},
                        "code": {"text": "Temperature"},
                        "valueQuantity": {"value": 38.2, "unit": "C"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Immunization",
                        "id": "imm-ext",
                        "patient": {"reference": "Patient/pat-extended"},
                        "vaccineCode": {"text": "Influenza vaccine"},
                        "occurrenceDateTime": "2024-10-01",
                    }
                },
                {
                    "resource": {
                        "resourceType": "ServiceRequest",
                        "id": "sr-ext",
                        "subject": {"reference": "Patient/pat-extended"},
                        "status": "active",
                        "intent": "order",
                        "code": {"text": "Follow up call"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "MedicationAdministration",
                        "id": "medadmin-1",
                        "subject": {"reference": "Patient/pat-extended"},
                        "status": "completed",
                        "medicationReference": {"reference": "Medication/medcat-1", "display": "Acetaminophen"},
                        "request": {"reference": "ServiceRequest/sr-ext"},
                        "effectiveDateTime": "2024-01-02T10:00:00Z",
                        "performer": [{"actor": {"reference": "Practitioner/prac-1"}}],
                        "dosage": {"text": "One tablet", "dose": {"value": 325, "unit": "mg"}},
                    }
                },
                {
                    "resource": {
                        "resourceType": "MedicationDispense",
                        "id": "meddisp-1",
                        "subject": {"reference": "Patient/pat-extended"},
                        "status": "completed",
                        "medicationReference": {"reference": "Medication/medcat-1", "display": "Acetaminophen"},
                        "performer": [{"actor": {"reference": "Organization/org-1"}}],
                        "quantity": {"value": 30, "unit": "tablet"},
                        "whenHandedOver": "2024-01-02T11:00:00Z",
                    }
                },
                {
                    "resource": {
                        "resourceType": "NutritionOrder",
                        "id": "nutrition-1",
                        "patient": {"reference": "Patient/pat-extended"},
                        "status": "active",
                        "intent": "order",
                        "dateTime": "2024-01-03T09:00:00Z",
                        "orderer": {"reference": "Practitioner/prac-1"},
                        "oralDiet": {"type": [{"text": "Low sodium diet"}]},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Communication",
                        "id": "comm-1",
                        "subject": {"reference": "Patient/pat-extended"},
                        "status": "completed",
                        "sender": {"reference": "Practitioner/prac-1"},
                        "recipient": [{"reference": "Organization/org-1"}],
                        "sent": "2024-01-04T09:00:00Z",
                        "payload": [{"contentString": "Patient instructions sent."}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "CommunicationRequest",
                        "id": "commreq-1",
                        "subject": {"reference": "Patient/pat-extended"},
                        "status": "active",
                        "requester": {"reference": "Practitioner/prac-1"},
                        "recipient": [{"reference": "Practitioner/prac-1"}],
                        "basedOn": [{"reference": "ServiceRequest/sr-ext"}],
                        "payload": [{"contentString": "Call patient tomorrow."}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Flag",
                        "id": "flag-1",
                        "subject": {"reference": "Patient/pat-extended"},
                        "status": "active",
                        "author": {"reference": "Organization/org-1"},
                        "code": {"text": "Interpreter requested"},
                        "period": {"start": "2024-01-01T00:00:00Z"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "List",
                        "id": "list-1",
                        "subject": {"reference": "Patient/pat-extended"},
                        "status": "current",
                        "mode": "working",
                        "title": "Problem and result list",
                        "entry": [
                            {"item": {"reference": "Condition/cond-ext"}},
                            {"item": {"reference": "Observation/obs-ext"}},
                        ],
                    }
                },
                {
                    "resource": {
                        "resourceType": "QuestionnaireResponse",
                        "id": "qr-1",
                        "subject": {"reference": "Patient/pat-extended"},
                        "status": "completed",
                        "questionnaire": "http://example.test/forms/intake",
                        "authored": "2024-01-05T09:00:00Z",
                        "basedOn": [{"reference": "ServiceRequest/sr-ext"}],
                        "item": [{"linkId": "symptoms", "text": "Symptoms", "answer": [{"valueString": "Fever"}]}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "ImmunizationRecommendation",
                        "id": "immrec-1",
                        "patient": {"reference": "Patient/pat-extended"},
                        "date": "2024-01-06T09:00:00Z",
                        "authority": {"reference": "Organization/org-1"},
                        "recommendation": [
                            {
                                "vaccineCode": [{"text": "COVID-19 vaccine"}],
                                "targetDisease": {"text": "COVID-19"},
                                "forecastStatus": {"text": "Due"},
                                "supportingImmunization": [{"reference": "Immunization/imm-ext"}],
                                "supportingPatientInformation": [{"reference": "Observation/obs-ext"}],
                            }
                        ],
                    }
                },
            ],
        }

        result = import_fhir_json(payload)

        self.assertEqual(result.errors, [])
        self.assertEqual(MedicationCatalog.objects.get().manufacturer.name, "Good Health")
        self.assertEqual(MedicationAdministration.objects.get().medication_catalog.name, "Acetaminophen 325 MG Oral Tablet")
        self.assertEqual(MedicationDispense.objects.get().performer_organization.name, "Good Health")
        self.assertEqual(NutritionOrder.objects.get().oral_diet_summary, "Low sodium diet")
        self.assertEqual(Communication.objects.get().recipients_organizations.get().name, "Good Health")
        self.assertEqual(CommunicationRequest.objects.get().based_on_service_requests.get().name, "Follow up call")
        self.assertEqual(Flag.objects.get().code, "Interpreter requested")
        self.assertEqual(FHIRList.objects.get().conditions.get().name, "Fever")
        self.assertEqual(QuestionnaireResponse.objects.get().based_on_service_requests.get().name, "Follow up call")
        self.assertEqual(ImmunizationRecommendation.objects.get().supporting_immunizations.get().vaccine_name, "Influenza vaccine")

    def test_imports_insurance_and_consent_resources(self):
        payload = {
            "resourceType": "Bundle",
            "entry": [
                {"resource": {"resourceType": "Patient", "id": "pat-fin", "name": [{"family": "Rivera", "given": ["Maya"]}]}},
                {"resource": {"resourceType": "Organization", "id": "payer-1", "name": "Acme Health Plan"}},
                {
                    "resource": {
                        "resourceType": "InsurancePlan",
                        "id": "plan-1",
                        "status": "active",
                        "name": "Acme Gold",
                        "ownedBy": {"reference": "Organization/payer-1"},
                        "type": [{"text": "Medical"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Coverage",
                        "id": "coverage-1",
                        "status": "active",
                        "beneficiary": {"reference": "Patient/pat-fin"},
                        "payor": [{"reference": "Organization/payer-1"}],
                        "type": {"text": "Medical"},
                        "subscriberId": "SUB123",
                        "period": {"start": "2024-01-01"},
                        "class": [{"type": {"text": "plan"}, "value": "Gold", "name": "Gold Plan"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Encounter",
                        "id": "enc-fin",
                        "subject": {"reference": "Patient/pat-fin"},
                        "status": "finished",
                        "class": {"display": "ambulatory"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "ExplanationOfBenefit",
                        "id": "eob-1",
                        "status": "active",
                        "patient": {"reference": "Patient/pat-fin"},
                        "insurer": {"reference": "Organization/payer-1"},
                        "provider": {"reference": "Organization/payer-1"},
                        "type": {"text": "Professional"},
                        "use": "claim",
                        "outcome": "complete",
                        "created": "2024-02-01",
                        "insurance": [{"coverage": {"reference": "Coverage/coverage-1"}}],
                        "item": [{"sequence": 1, "encounter": [{"reference": "Encounter/enc-fin"}], "productOrService": {"text": "Office visit"}}],
                        "total": [{"category": {"text": "Submitted"}, "amount": {"value": 100, "currency": "USD"}}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Immunization",
                        "id": "imm-consent",
                        "patient": {"reference": "Patient/pat-fin"},
                        "vaccineCode": {"text": "Influenza vaccine"},
                        "occurrenceDateTime": "2024-10-01",
                    }
                },
                {
                    "resource": {
                        "resourceType": "QuestionnaireResponse",
                        "id": "qr-consent",
                        "subject": {"reference": "Patient/pat-fin"},
                        "status": "completed",
                        "questionnaire": "http://example.test/vaccine-consent",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Consent",
                        "id": "consent-1",
                        "status": "active",
                        "scope": {"text": "Treatment"},
                        "category": [{"text": "Vaccine consent"}],
                        "patient": {"reference": "Patient/pat-fin"},
                        "organization": [{"reference": "Organization/payer-1"}],
                        "sourceReference": {"reference": "QuestionnaireResponse/qr-consent"},
                        "provision": {
                            "type": "permit",
                            "period": {"start": "2024-10-01T09:00:00Z"},
                            "data": [{"reference": {"reference": "Immunization/imm-consent"}}],
                        },
                    }
                },
            ],
        }

        result = import_fhir_json(payload)

        self.assertEqual(result.errors, [])
        self.assertEqual(InsurancePlan.objects.get().owned_by.name, "Acme Health Plan")
        self.assertEqual(Coverage.objects.get().subscriber_id, "SUB123")
        self.assertEqual(ExplanationOfBenefit.objects.get().coverages.get(), Coverage.objects.get())
        self.assertEqual(ExplanationOfBenefit.objects.get().encounters.get(), Encounter.objects.get())
        self.assertEqual(Consent.objects.get().related_immunizations.get().vaccine_name, "Influenza vaccine")
        self.assertEqual(Consent.objects.get().questionnaire_responses.get().questionnaire, "http://example.test/vaccine-consent")

    def test_reimport_updates_linked_resources(self):
        payload = {
            "resourceType": "Bundle",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "pat-1",
                        "name": [{"family": "Rivera", "given": ["Maya"]}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Condition",
                        "id": "cond-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "code": {"text": "Asthma"},
                    }
                },
            ],
        }

        import_fhir_json(payload)
        payload["entry"][1]["resource"]["code"]["text"] = "Resolved asthma"
        result = import_fhir_json(payload)

        self.assertEqual(result.created, 0)
        self.assertEqual(result.updated, 2)
        self.assertEqual(PatientProfile.objects.count(), 1)
        self.assertEqual(Condition.objects.count(), 1)
        self.assertEqual(Condition.objects.get().name, "Resolved asthma")
        self.assertEqual(FHIRResourceSnapshot.objects.count(), 4)

    def test_import_can_attach_to_existing_patient(self):
        existing_patient = PatientProfile.objects.create(
            first_name="Mike",
            last_name="Davidson",
            email="existing@example.test",
        )
        payload = {
            "resourceType": "Bundle",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "epic-patient-id",
                        "name": [{"family": "Davidson", "given": ["Michael"]}],
                        "telecom": [{"system": "phone", "value": "555-0199"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Condition",
                        "id": "cond-1",
                        "subject": {"reference": "Patient/epic-patient-id"},
                        "code": {"text": "Asthma"},
                    }
                },
            ],
        }

        result = import_fhir_json(payload, target_patient=existing_patient)

        self.assertEqual(result.created, 1)
        self.assertEqual(result.updated, 1)
        self.assertEqual(PatientProfile.objects.count(), 1)

        existing_patient.refresh_from_db()
        self.assertEqual(existing_patient.first_name, "Mike")
        self.assertEqual(existing_patient.email, "existing@example.test")
        self.assertEqual(existing_patient.phone, "555-0199")
        self.assertEqual(Condition.objects.get().patient, existing_patient)
        self.assertTrue(
            FHIRLink.objects.filter(
                resource_type="Patient",
                resource_id="epic-patient-id",
                django_object_id=existing_patient.id,
            ).exists()
        )

    def test_imports_care_team(self):
        patient = PatientProfile.objects.create(first_name="Maya", last_name="Rivera")
        payload = {
            "resourceType": "CareTeam",
            "id": "careteam-1",
            "subject": {"reference": "Patient/pat-1"},
            "status": "active",
            "name": "Primary care team",
            "category": [{"text": "Longitudinal care team"}],
            "participant": [
                {
                    "role": [{"text": "Primary care physician"}],
                    "member": {"display": "Dr. Ada Lovelace"},
                    "period": {"start": "2021-01-01"},
                },
                {
                    "role": [{"text": "Cardiology"}],
                    "member": {"reference": "Practitioner/prac-1"},
                },
            ],
            "period": {"start": "2021-01-01", "end": "2023-12-31"},
            "reasonCode": [{"text": "Ongoing care coordination"}],
            "note": [{"text": "Call office before medication changes."}],
        }

        result = import_fhir_json(payload, target_patient=patient)

        self.assertEqual(result.created, 1)
        self.assertEqual(result.snapshots, 1)
        care_team = CareTeam.objects.get()
        self.assertEqual(care_team.patient, patient)
        self.assertEqual(care_team.name, "Primary care team")
        self.assertEqual(care_team.status, "active")
        self.assertEqual(care_team.category, "Longitudinal care team")
        self.assertEqual(care_team.start_date, date(2021, 1, 1))
        self.assertEqual(care_team.end_date, date(2023, 12, 31))
        self.assertEqual(care_team.reason, "Ongoing care coordination")
        self.assertEqual(care_team.notes, "Call office before medication changes.")
        self.assertIn("Primary care physician: Dr. Ada Lovelace (2021-01-01)", care_team.participants)
        self.assertIn("Cardiology: Practitioner/prac-1", care_team.participants)
        self.assertEqual(care_team.participant_links.count(), 2)
        unresolved_participant = CareTeamParticipant.objects.get(member_reference="Practitioner/prac-1")
        self.assertEqual(unresolved_participant.care_team, care_team)
        self.assertEqual(unresolved_participant.role, "Cardiology")
        self.assertIsNone(unresolved_participant.practitioner)
        self.assertTrue(
            FHIRLink.objects.filter(
                resource_type="CareTeam",
                resource_id="careteam-1",
                django_model="clinical.CareTeam",
                django_object_id=care_team.id,
            ).exists()
        )

    def test_imports_directory_resources_without_patient_reference(self):
        payload = {
            "resourceType": "Bundle",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Practitioner",
                        "id": "prac-1",
                        "identifier": [
                            {
                                "system": "http://hl7.org/fhir/sid/us-npi",
                                "value": "1234567890",
                            }
                        ],
                        "active": True,
                        "name": [{"text": "Dr. Ada Lovelace"}],
                        "qualification": [{"code": {"text": "MD"}}],
                        "telecom": [
                            {"system": "phone", "value": "555-0101"},
                            {"system": "email", "value": "ada@example.test"},
                        ],
                        "address": [{"line": ["1 Clinic Way"], "city": "Boston", "state": "MA"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Organization",
                        "id": "org-1",
                        "active": True,
                        "name": "Example Health",
                        "type": [{"text": "Hospital"}],
                        "telecom": [{"system": "phone", "value": "555-0102"}],
                        "address": [{"line": ["2 Hospital Ave"], "city": "Boston", "state": "MA"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Location",
                        "id": "loc-1",
                        "status": "active",
                        "mode": "instance",
                        "name": "Example Health Main Campus",
                        "type": [{"text": "Campus"}],
                        "managingOrganization": {"reference": "Organization/org-1"},
                        "telecom": [{"system": "phone", "value": "555-0103"}],
                        "address": {"line": ["3 Care St"], "city": "Boston", "state": "MA"},
                    }
                },
            ],
        }

        result = import_fhir_json(payload)

        self.assertEqual(result.created, 3)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.snapshots, 3)

        practitioner = Practitioner.objects.get()
        self.assertEqual(practitioner.name, "Dr. Ada Lovelace")
        self.assertEqual(practitioner.npi, "1234567890")
        self.assertEqual(practitioner.qualification, "MD")
        self.assertEqual(practitioner.phone, "555-0101")
        self.assertEqual(practitioner.email, "ada@example.test")
        self.assertIn("1 Clinic Way", practitioner.address)

        organization = Organization.objects.get()
        self.assertEqual(organization.name, "Example Health")
        self.assertEqual(organization.organization_type, "Hospital")
        self.assertEqual(organization.phone, "555-0102")

        location = Location.objects.get()
        self.assertEqual(location.name, "Example Health Main Campus")
        self.assertEqual(location.status, "active")
        self.assertEqual(location.mode, "instance")
        self.assertEqual(location.location_type, "Campus")
        self.assertEqual(location.managing_organization, "Organization/org-1")
        self.assertEqual(location.phone, "555-0103")

        self.assertEqual(
            set(FHIRLink.objects.values_list("django_model", flat=True)),
            {"clinical.Practitioner", "clinical.Organization", "clinical.Location"},
        )

    def test_imports_care_team_directory_relationships(self):
        payload = {
            "resourceType": "Bundle",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "pat-1",
                        "name": [{"family": "Rivera", "given": ["Maya"]}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "CareTeam",
                        "id": "careteam-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "name": "Specialty care team",
                        "participant": [
                            {
                                "role": [{"text": "Endocrinologist"}],
                                "member": {"reference": "Practitioner/prac-1", "display": "Dr. Grace Hopper"},
                                "onBehalfOf": {"reference": "Organization/org-1", "display": "Example Health"},
                                "period": {"start": "2022-01-01", "end": "2024-01-01"},
                            },
                            {
                                "role": [{"text": "Clinic"}],
                                "member": {"reference": "Location/loc-1", "display": "Main Clinic"},
                            },
                        ],
                        "managingOrganization": [{"reference": "Organization/org-1"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Practitioner",
                        "id": "prac-1",
                        "name": [{"text": "Dr. Grace Hopper"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Organization",
                        "id": "org-1",
                        "name": "Example Health",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Location",
                        "id": "loc-1",
                        "name": "Main Clinic",
                    }
                },
            ],
        }

        result = import_fhir_json(payload)

        self.assertEqual(result.created, 5)
        self.assertEqual(result.errors, [])

        care_team = CareTeam.objects.get()
        practitioner = Practitioner.objects.get()
        organization = Organization.objects.get()
        location = Location.objects.get()

        self.assertEqual(list(care_team.managing_organizations.all()), [organization])

        practitioner_participant = CareTeamParticipant.objects.get(role="Endocrinologist")
        self.assertEqual(practitioner_participant.care_team, care_team)
        self.assertEqual(practitioner_participant.practitioner, practitioner)
        self.assertEqual(practitioner_participant.organization, organization)
        self.assertEqual(practitioner_participant.member_reference, "Practitioner/prac-1")
        self.assertEqual(practitioner_participant.on_behalf_of_reference, "Organization/org-1")
        self.assertEqual(practitioner_participant.start_date, date(2022, 1, 1))
        self.assertEqual(practitioner_participant.end_date, date(2024, 1, 1))

        location_participant = CareTeamParticipant.objects.get(role="Clinic")
        self.assertEqual(location_participant.location, location)

    def test_imports_document_reference_as_clinical_document(self):
        patient = PatientProfile.objects.create(first_name="Maya", last_name="Rivera")
        encoded_document = b64encode(b"Visit summary").decode("ascii")
        payload = {
            "resourceType": "DocumentReference",
            "id": "doc-1",
            "status": "current",
            "subject": {"reference": "Patient/pat-1"},
            "type": {"coding": [{"display": "History and physical note"}]},
            "date": "2024-01-02T03:04:05Z",
            "author": [{"display": "Dr. Ada Lovelace"}],
            "content": [
                {
                    "attachment": {
                        "contentType": "text/plain; charset=utf-8",
                        "title": "Visit summary",
                        "data": encoded_document,
                    }
                }
            ],
        }

        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            result = import_fhir_json(payload, target_patient=patient)
            document = ClinicalDocument.objects.get()

            self.assertEqual(result.created, 1)
            self.assertEqual(result.errors, [])
            self.assertEqual(document.patient, patient)
            self.assertEqual(document.title, "Visit summary")
            self.assertEqual(document.document_type, "History and physical note")
            self.assertEqual(document.mime_type, "text/plain; charset=utf-8")
            self.assertEqual(document.source_name, "Dr. Ada Lovelace")
            self.assertEqual(document.source_date, date(2024, 1, 2))
            with document.file.open("rb") as imported_file:
                self.assertEqual(imported_file.read(), b"Visit summary")
            self.assertTrue(
                FHIRLink.objects.filter(
                    resource_type="DocumentReference",
                    resource_id="doc-1",
                    django_model="documents.ClinicalDocument",
                    django_object_id=document.id,
                ).exists()
            )

    def test_imports_care_plan_procedure_and_specimen_relationships(self):
        payload = {
            "resourceType": "Bundle",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "pat-1",
                        "name": [{"family": "Rivera", "given": ["Maya"]}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Practitioner",
                        "id": "prac-1",
                        "name": [{"text": "Dr. Ada Lovelace"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Organization",
                        "id": "org-1",
                        "name": "Example Health",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Condition",
                        "id": "cond-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "code": {"text": "Wrist fracture"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Encounter",
                        "id": "enc-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "finished",
                        "type": [{"text": "Office visit"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "CareTeam",
                        "id": "team-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "name": "Orthopedic care team",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "obs-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "specimen": {"reference": "Specimen/spec-1"},
                        "code": {"text": "Culture result"},
                        "valueString": "No growth",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Procedure",
                        "id": "proc-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "encounter": {"reference": "Encounter/enc-1"},
                        "basedOn": [{"reference": "CarePlan/plan-1"}],
                        "status": "completed",
                        "code": {"text": "Bone immobilization"},
                        "performedDateTime": "2024-01-02T10:30:00Z",
                        "reasonReference": [{"reference": "Condition/cond-1"}],
                        "performer": [
                            {
                                "function": {"text": "Surgeon"},
                                "actor": {"reference": "Practitioner/prac-1", "display": "Dr. Ada Lovelace"},
                                "onBehalfOf": {"reference": "Organization/org-1", "display": "Example Health"},
                            }
                        ],
                    }
                },
                {
                    "resource": {
                        "resourceType": "CarePlan",
                        "id": "plan-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "active",
                        "intent": "plan",
                        "title": "Fracture recovery plan",
                        "category": [{"text": "Orthopedics"}],
                        "period": {"start": "2024-01-01", "end": "2024-02-01"},
                        "addresses": [{"reference": "Condition/cond-1"}],
                        "careTeam": [{"reference": "CareTeam/team-1"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Specimen",
                        "id": "parent-spec",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "available",
                        "type": {"text": "Parent specimen"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Specimen",
                        "id": "spec-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "available",
                        "type": {"text": "Blood specimen"},
                        "accessionIdentifier": {"value": "A-123"},
                        "receivedTime": "2024-01-02T11:00:00Z",
                        "collection": {
                            "collectedDateTime": "2024-01-02T10:45:00Z",
                            "method": {"text": "Venipuncture"},
                            "bodySite": {"text": "Left arm"},
                            "collector": {"display": "Lab Tech"},
                        },
                        "parent": [{"reference": "Specimen/parent-spec"}],
                    }
                },
            ],
        }

        result = import_fhir_json(payload)

        self.assertEqual(result.errors, [])
        self.assertEqual(CarePlan.objects.count(), 1)
        self.assertEqual(Procedure.objects.count(), 1)
        self.assertEqual(Specimen.objects.count(), 2)

        care_plan = CarePlan.objects.get()
        condition = Condition.objects.get()
        care_team = CareTeam.objects.get()
        self.assertEqual(care_plan.title, "Fracture recovery plan")
        self.assertEqual(care_plan.conditions.get(), condition)
        self.assertEqual(care_plan.care_teams.get(), care_team)

        procedure = Procedure.objects.get()
        self.assertEqual(procedure.encounter, Encounter.objects.get())
        self.assertEqual(procedure.care_plans.get(), care_plan)
        self.assertEqual(procedure.conditions.get(), condition)
        self.assertEqual(procedure.performer_links.count(), 1)

        performer = ProcedurePerformer.objects.get()
        self.assertEqual(performer.role, "Surgeon")
        self.assertEqual(performer.practitioner, Practitioner.objects.get())
        self.assertEqual(performer.organization, Organization.objects.get())

        specimen = Specimen.objects.get(accession_identifier="A-123")
        self.assertEqual(specimen.specimen_type, "Blood specimen")
        self.assertEqual(specimen.collection_method, "Venipuncture")
        self.assertEqual(specimen.parent_specimens.get().specimen_type, "Parent specimen")
        self.assertEqual(Observation.objects.get().specimen, specimen)

        self.assertTrue(FHIRLink.objects.filter(resource_type="CarePlan", django_model="clinical.CarePlan").exists())
        self.assertTrue(FHIRLink.objects.filter(resource_type="Procedure", django_model="clinical.Procedure").exists())
        self.assertTrue(FHIRLink.objects.filter(resource_type="Specimen", django_model="clinical.Specimen").exists())

    def test_imports_service_request_episode_device_and_practitioner_role_relationships(self):
        payload = {
            "resourceType": "Bundle",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "pat-1",
                        "name": [{"family": "Rivera", "given": ["Maya"]}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Organization",
                        "id": "org-1",
                        "name": "Example Health",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Location",
                        "id": "loc-1",
                        "name": "Main Clinic",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Practitioner",
                        "id": "prac-1",
                        "name": [{"text": "Dr. Ada Lovelace"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "PractitionerRole",
                        "id": "role-1",
                        "active": True,
                        "practitioner": {"reference": "Practitioner/prac-1"},
                        "organization": {"reference": "Organization/org-1"},
                        "code": [{"text": "Ordering clinician"}],
                        "specialty": [{"text": "Family Medicine"}],
                        "location": [{"reference": "Location/loc-1"}],
                        "period": {"start": "2024-01-01", "end": "2024-12-31"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Encounter",
                        "id": "enc-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "finished",
                        "type": [{"text": "Office visit"}],
                        "episodeOfCare": [{"reference": "EpisodeOfCare/episode-1"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Condition",
                        "id": "cond-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "code": {"text": "Knee pain"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "CarePlan",
                        "id": "plan-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "active",
                        "intent": "plan",
                        "title": "Knee care plan",
                    }
                },
                {
                    "resource": {
                        "resourceType": "CareTeam",
                        "id": "team-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "name": "Primary care team",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Device",
                        "id": "device-1",
                        "patient": {"reference": "Patient/pat-1"},
                        "owner": {"reference": "Organization/org-1"},
                        "location": {"reference": "Location/loc-1"},
                        "status": "active",
                        "type": {"text": "Blood pressure cuff"},
                        "deviceName": [{"name": "Home BP cuff"}],
                        "manufacturer": "Example Devices",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Specimen",
                        "id": "spec-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "type": {"text": "Blood specimen"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "obs-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "code": {"text": "Blood pressure"},
                        "device": {"reference": "Device/device-1"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "ServiceRequest",
                        "id": "sr-2",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "completed",
                        "intent": "order",
                        "code": {"text": "Old order"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "ServiceRequest",
                        "id": "sr-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "encounter": {"reference": "Encounter/enc-1"},
                        "basedOn": [{"reference": "CarePlan/plan-1"}],
                        "replaces": [{"reference": "ServiceRequest/sr-2"}],
                        "status": "active",
                        "intent": "order",
                        "category": [{"text": "Imaging"}],
                        "priority": "routine",
                        "code": {"text": "Knee x-ray"},
                        "authoredOn": "2024-01-02T10:00:00Z",
                        "requester": {"reference": "PractitionerRole/role-1"},
                        "performer": [
                            {"reference": "Practitioner/prac-1"},
                            {"reference": "Organization/org-1"},
                            {"reference": "CareTeam/team-1"},
                            {"reference": "Device/device-1"},
                        ],
                        "locationReference": [{"reference": "Location/loc-1"}],
                        "reasonReference": [{"reference": "Condition/cond-1"}],
                        "specimen": [{"reference": "Specimen/spec-1"}],
                        "patientInstruction": "Please schedule this week.",
                    }
                },
                {
                    "resource": {
                        "resourceType": "EpisodeOfCare",
                        "id": "episode-1",
                        "patient": {"reference": "Patient/pat-1"},
                        "status": "active",
                        "type": [{"text": "Orthopedic episode"}],
                        "managingOrganization": {"reference": "Organization/org-1"},
                        "careManager": {"reference": "PractitionerRole/role-1"},
                        "team": [{"reference": "CareTeam/team-1"}],
                        "referralRequest": [{"reference": "ServiceRequest/sr-1"}],
                        "period": {"start": "2024-01-02", "end": "2024-03-02"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "DocumentReference",
                        "id": "doc-1",
                        "status": "current",
                        "subject": {"reference": "Patient/pat-1"},
                        "type": {"text": "Progress note"},
                        "author": [{"reference": "Practitioner/prac-1"}],
                        "custodian": {"reference": "Organization/org-1"},
                        "context": {"encounter": [{"reference": "Encounter/enc-1"}]},
                        "content": [{"attachment": {"contentType": "text/plain", "title": "Progress note"}}],
                    }
                },
            ],
        }

        result = import_fhir_json(payload)

        self.assertEqual(result.errors, [])
        self.assertEqual(PractitionerRole.objects.count(), 1)
        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(ServiceRequest.objects.count(), 2)
        self.assertEqual(EpisodeOfCare.objects.count(), 1)

        role = PractitionerRole.objects.get()
        self.assertEqual(role.practitioner, Practitioner.objects.get())
        self.assertEqual(role.organization, Organization.objects.get())
        self.assertEqual(role.role, "Ordering clinician")
        self.assertEqual(role.specialty, "Family Medicine")
        self.assertEqual(role.locations.get(), Location.objects.get())

        device = Device.objects.get()
        self.assertEqual(device.patient, PatientProfile.objects.get())
        self.assertEqual(device.owner, Organization.objects.get())
        self.assertEqual(device.location, Location.objects.get())
        self.assertEqual(Observation.objects.get().device, device)

        service_request = ServiceRequest.objects.get(name="Knee x-ray")
        self.assertEqual(service_request.encounter, Encounter.objects.get())
        self.assertEqual(service_request.requester_role, role)
        self.assertEqual(service_request.care_plans.get(), CarePlan.objects.get())
        self.assertEqual(service_request.replaces.get().name, "Old order")
        self.assertEqual(service_request.performers_practitioners.get(), Practitioner.objects.get())
        self.assertEqual(service_request.performers_organizations.get(), Organization.objects.get())
        self.assertEqual(service_request.performers_care_teams.get(), CareTeam.objects.get())
        self.assertEqual(service_request.performers_devices.get(), device)
        self.assertEqual(service_request.locations.get(), Location.objects.get())
        self.assertEqual(service_request.conditions.get(), Condition.objects.get())
        self.assertEqual(service_request.specimens.get(), Specimen.objects.get())

        episode = EpisodeOfCare.objects.get()
        self.assertEqual(episode.managing_organization, Organization.objects.get())
        self.assertEqual(episode.care_manager_role, role)
        self.assertEqual(episode.referral_requests.get(), service_request)
        self.assertEqual(episode.care_teams.get(), CareTeam.objects.get())
        self.assertEqual(Encounter.objects.get().episodes_of_care.get(), episode)

        document = ClinicalDocument.objects.get()
        self.assertEqual(document.encounter, Encounter.objects.get())
        self.assertEqual(document.custodian, Organization.objects.get())
        self.assertEqual(document.authors.get(), Practitioner.objects.get())

    def test_imports_adverse_event_family_history_and_clinical_impression(self):
        payload = {
            "resourceType": "Bundle",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "pat-1",
                        "name": [{"family": "Rivera", "given": ["Maya"]}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Practitioner",
                        "id": "prac-1",
                        "name": [{"text": "Dr. Ada Lovelace"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Organization",
                        "id": "org-1",
                        "name": "Example Health",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Location",
                        "id": "loc-1",
                        "name": "Main Clinic",
                    }
                },
                {
                    "resource": {
                        "resourceType": "PractitionerRole",
                        "id": "role-1",
                        "practitioner": {"reference": "Practitioner/prac-1"},
                        "organization": {"reference": "Organization/org-1"},
                        "code": [{"text": "Attending"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Encounter",
                        "id": "enc-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "finished",
                        "type": [{"text": "Office visit"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Condition",
                        "id": "cond-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "code": {"text": "Asthma"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "obs-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "code": {"text": "Wheezing"},
                        "valueString": "Mild",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Immunization",
                        "id": "imm-1",
                        "patient": {"reference": "Patient/pat-1"},
                        "status": "completed",
                        "vaccineCode": {"text": "Influenza vaccine"},
                        "occurrenceDateTime": "2024-01-02",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Procedure",
                        "id": "proc-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "completed",
                        "code": {"text": "Nebulizer treatment"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Device",
                        "id": "device-1",
                        "patient": {"reference": "Patient/pat-1"},
                        "type": {"text": "Nebulizer"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "DocumentReference",
                        "id": "doc-1",
                        "status": "current",
                        "subject": {"reference": "Patient/pat-1"},
                        "type": {"text": "Adverse event note"},
                        "content": [{"attachment": {"contentType": "text/plain", "title": "Adverse event note"}}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "FamilyMemberHistory",
                        "id": "fmh-1",
                        "patient": {"reference": "Patient/pat-1"},
                        "status": "completed",
                        "relationship": {"text": "Mother"},
                        "sex": {"text": "female"},
                        "ageAge": {"value": 67, "unit": "years"},
                        "reasonReference": [{"reference": "Condition/cond-1"}],
                        "condition": [
                            {
                                "code": {"text": "Asthma"},
                                "outcome": {"text": "ongoing"},
                                "onsetAge": {"value": 30, "unit": "years"},
                                "contributedToDeath": False,
                                "note": [{"text": "Mild family history."}],
                            }
                        ],
                    }
                },
                {
                    "resource": {
                        "resourceType": "ClinicalImpression",
                        "id": "ci-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "encounter": {"reference": "Encounter/enc-1"},
                        "assessor": {"reference": "PractitionerRole/role-1"},
                        "status": "completed",
                        "description": "Asthma assessment",
                        "effectiveDateTime": "2024-01-02T10:00:00Z",
                        "date": "2024-01-02T10:30:00Z",
                        "problem": [{"reference": "Condition/cond-1"}],
                        "investigation": [{"item": [{"reference": "Observation/obs-1"}]}],
                        "finding": [
                            {
                                "itemReference": {"reference": "Condition/cond-1"},
                                "basis": "Symptoms and exam.",
                            },
                            {
                                "itemReference": {"reference": "Observation/obs-1"},
                                "basis": "Observation supports finding.",
                            },
                        ],
                        "summary": "Likely mild exacerbation.",
                        "prognosisCodeableConcept": [{"text": "Good"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "AdverseEvent",
                        "id": "ae-1",
                        "actuality": "actual",
                        "subject": {"reference": "Patient/pat-1"},
                        "encounter": {"reference": "Encounter/enc-1"},
                        "event": {"text": "Medication reaction"},
                        "date": "2024-01-02T11:00:00Z",
                        "location": {"reference": "Location/loc-1"},
                        "resultingCondition": [{"reference": "Condition/cond-1"}],
                        "seriousness": {"text": "Non-serious"},
                        "severity": {"text": "mild"},
                        "outcome": {"text": "resolved"},
                        "recorder": {"reference": "Practitioner/prac-1"},
                        "contributor": [
                            {"reference": "PractitionerRole/role-1"},
                            {"reference": "Device/device-1"},
                        ],
                        "suspectEntity": [
                            {
                                "instance": {"reference": "Procedure/proc-1"},
                                "causality": [{"assessment": {"text": "Possible"}}],
                            },
                            {"instance": {"reference": "Immunization/imm-1"}},
                            {"instance": {"reference": "Device/device-1"}},
                        ],
                        "subjectMedicalHistory": [
                            {"reference": "Condition/cond-1"},
                            {"reference": "Observation/obs-1"},
                            {"reference": "Immunization/imm-1"},
                            {"reference": "Procedure/proc-1"},
                        ],
                        "referenceDocument": [{"reference": "DocumentReference/doc-1"}],
                    }
                },
            ],
        }

        result = import_fhir_json(payload)

        self.assertEqual(result.errors, [])
        family_history = FamilyMemberHistory.objects.get()
        self.assertEqual(family_history.relationship, "Mother")
        self.assertEqual(family_history.conditions.get(), Condition.objects.get())
        family_condition = FamilyMemberHistoryCondition.objects.get()
        self.assertEqual(family_condition.condition, Condition.objects.get())
        self.assertEqual(family_condition.condition_text, "Asthma")
        self.assertEqual(family_condition.onset_text, "30 years")

        clinical_impression = ClinicalImpression.objects.get()
        self.assertEqual(clinical_impression.encounter, Encounter.objects.get())
        self.assertEqual(clinical_impression.assessor_role, PractitionerRole.objects.get())
        self.assertEqual(clinical_impression.problems.get(), Condition.objects.get())
        self.assertEqual(clinical_impression.investigations_observations.get(), Observation.objects.get())
        self.assertEqual(ClinicalImpressionFinding.objects.count(), 2)
        self.assertEqual(clinical_impression.conditions.get(), Condition.objects.get())
        self.assertEqual(clinical_impression.observations.get(), Observation.objects.get())

        adverse_event = AdverseEvent.objects.get()
        self.assertEqual(adverse_event.encounter, Encounter.objects.get())
        self.assertEqual(adverse_event.location, Location.objects.get())
        self.assertEqual(adverse_event.recorder_practitioner, Practitioner.objects.get())
        self.assertEqual(adverse_event.resulting_conditions.get(), Condition.objects.get())
        self.assertEqual(adverse_event.contributor_roles.get(), PractitionerRole.objects.get())
        self.assertEqual(adverse_event.contributor_devices.get(), Device.objects.get())
        self.assertEqual(adverse_event.suspect_procedures.get(), Procedure.objects.get())
        self.assertEqual(adverse_event.suspect_immunizations.get(), Immunization.objects.get())
        self.assertEqual(adverse_event.suspect_devices.get(), Device.objects.get())
        self.assertEqual(adverse_event.reference_documents.get(), ClinicalDocument.objects.get())
        self.assertEqual(adverse_event.subject_medical_history_conditions.get(), Condition.objects.get())
        self.assertEqual(adverse_event.subject_medical_history_observations.get(), Observation.objects.get())
        self.assertEqual(adverse_event.subject_medical_history_immunizations.get(), Immunization.objects.get())
        self.assertEqual(adverse_event.subject_medical_history_procedures.get(), Procedure.objects.get())

    def test_imports_diagnostic_report_and_detected_issue_relationships(self):
        report_text = b64encode(b"diagnostic report").decode("ascii")
        payload = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "pat-1",
                        "name": [{"family": "Rivera", "given": ["Maya"]}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Organization",
                        "id": "org-1",
                        "name": "Example Lab",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Practitioner",
                        "id": "prac-1",
                        "name": [{"family": "Nguyen", "given": ["Ari"]}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "PractitionerRole",
                        "id": "role-1",
                        "practitioner": {"reference": "Practitioner/prac-1"},
                        "organization": {"reference": "Organization/org-1"},
                        "code": [{"text": "Pathologist"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Encounter",
                        "id": "enc-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "class": {"display": "Outpatient"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Condition",
                        "id": "cond-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "code": {"text": "Anemia"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Specimen",
                        "id": "spec-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "type": {"text": "Blood"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "obs-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "specimen": {"reference": "Specimen/spec-1"},
                        "code": {"text": "Hemoglobin"},
                        "valueQuantity": {"value": 11.2, "unit": "g/dL"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "CarePlan",
                        "id": "cp-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "active",
                        "intent": "plan",
                        "title": "Anemia workup",
                    }
                },
                {
                    "resource": {
                        "resourceType": "ServiceRequest",
                        "id": "sr-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "completed",
                        "intent": "order",
                        "code": {"text": "CBC"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Device",
                        "id": "device-1",
                        "patient": {"reference": "Patient/pat-1"},
                        "type": {"text": "Decision support system"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "DiagnosticReport",
                        "id": "dr-1",
                        "status": "final",
                        "category": [{"text": "Laboratory"}],
                        "code": {"text": "CBC report"},
                        "subject": {"reference": "Patient/pat-1"},
                        "encounter": {"reference": "Encounter/enc-1"},
                        "basedOn": [
                            {"reference": "CarePlan/cp-1"},
                            {"reference": "ServiceRequest/sr-1"},
                        ],
                        "effectiveDateTime": "2024-01-03T09:00:00Z",
                        "issued": "2024-01-03T10:00:00Z",
                        "performer": [
                            {"reference": "Organization/org-1"},
                            {"reference": "PractitionerRole/role-1"},
                        ],
                        "resultsInterpreter": [{"reference": "Practitioner/prac-1"}],
                        "specimen": [{"reference": "Specimen/spec-1"}],
                        "result": [{"reference": "Observation/obs-1"}],
                        "conclusion": "Mild anemia.",
                        "conclusionCode": [{"text": "Abnormal"}],
                        "presentedForm": [
                            {
                                "contentType": "text/plain",
                                "title": "CBC report text",
                                "data": report_text,
                            }
                        ],
                    }
                },
                {
                    "resource": {
                        "resourceType": "DetectedIssue",
                        "id": "issue-1",
                        "status": "final",
                        "code": {"text": "Duplicate therapy"},
                        "severity": "moderate",
                        "patient": {"reference": "Patient/pat-1"},
                        "identifiedDateTime": "2024-01-03T11:00:00Z",
                        "author": {"reference": "Device/device-1"},
                        "implicated": [
                            {"reference": "ServiceRequest/sr-1"},
                            {"reference": "DiagnosticReport/dr-1"},
                            {"reference": "Condition/cond-1"},
                        ],
                        "evidence": [
                            {
                                "code": [{"text": "Low hemoglobin"}],
                                "detail": [
                                    {"reference": "Observation/obs-1"},
                                    {"reference": "DiagnosticReport/dr-1"},
                                ],
                            }
                        ],
                        "detail": "Possible duplicate lab order.",
                        "mitigation": [
                            {
                                "action": {"text": "Reviewed by clinician"},
                                "date": "2024-01-03T11:15:00Z",
                                "author": {"reference": "PractitionerRole/role-1"},
                            }
                        ],
                    }
                },
            ],
        }

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                result = import_fhir_json(payload)

            self.assertEqual(result.errors, [])
            diagnostic_report = DiagnosticReport.objects.get()
            self.assertEqual(diagnostic_report.encounter, Encounter.objects.get())
            self.assertEqual(diagnostic_report.care_plans.get(), CarePlan.objects.get())
            self.assertEqual(diagnostic_report.service_requests.get(), ServiceRequest.objects.get())
            self.assertEqual(diagnostic_report.specimens.get(), Specimen.objects.get())
            self.assertEqual(diagnostic_report.observations.get(), Observation.objects.get())
            self.assertEqual(diagnostic_report.performers_roles.get(), PractitionerRole.objects.get())
            self.assertEqual(diagnostic_report.performers_organizations.get(), Organization.objects.get())
            self.assertEqual(diagnostic_report.interpreter_practitioners.get(), Practitioner.objects.get())
            self.assertEqual(diagnostic_report.presented_documents.count(), 1)
            self.assertEqual(ClinicalDocument.objects.get().title, "CBC report text")

            detected_issue = DetectedIssue.objects.get()
            self.assertEqual(detected_issue.author_device, Device.objects.get())
            self.assertEqual(detected_issue.implicated_service_requests.get(), ServiceRequest.objects.get())
            self.assertEqual(detected_issue.implicated_diagnostic_reports.get(), diagnostic_report)
            self.assertEqual(detected_issue.implicated_conditions.get(), Condition.objects.get())
            self.assertEqual(detected_issue.evidence_observations.get(), Observation.objects.get())
        self.assertEqual(detected_issue.evidence_diagnostic_reports.get(), diagnostic_report)
        self.assertIn("Reviewed by clinician", detected_issue.mitigation_summary)

    def test_imports_related_person(self):
        result = import_fhir_json(
            {
                "resourceType": "Bundle",
                "type": "collection",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "Patient",
                            "id": "pat-1",
                            "name": [{"family": "Rivera", "given": ["Maya"]}],
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "RelatedPerson",
                            "id": "rp-1",
                            "patient": {"reference": "Patient/pat-1"},
                            "active": True,
                            "relationship": [{"text": "Guardian"}, {"text": "Emergency contact"}],
                            "name": [{"family": "Rivera", "given": ["Alex"]}],
                            "telecom": [
                                {"system": "phone", "value": "555-1212"},
                                {"system": "email", "value": "alex@example.test"},
                            ],
                            "gender": "other",
                            "birthDate": "1980-04-05",
                            "address": [{"line": ["100 Main St"], "city": "Boston", "state": "MA"}],
                            "period": {"start": "2020-01-01"},
                            "communication": [
                                {
                                    "language": {"text": "English"},
                                    "preferred": True,
                                }
                            ],
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "CareTeam",
                            "id": "team-1",
                            "subject": {"reference": "Patient/pat-1"},
                            "status": "active",
                            "name": "Home support",
                            "participant": [
                                {
                                    "role": [{"text": "Caregiver"}],
                                    "member": {"reference": "RelatedPerson/rp-1"},
                                }
                            ],
                        }
                    },
                ],
            }
        )

        self.assertEqual(result.errors, [])
        related_person = RelatedPerson.objects.get()
        self.assertEqual(related_person.patient, PatientProfile.objects.get())
        self.assertEqual(related_person.name, "Alex Rivera")
        self.assertEqual(related_person.relationship, "Guardian, Emergency contact")
        self.assertEqual(related_person.phone, "555-1212")
        self.assertEqual(related_person.email, "alex@example.test")
        self.assertEqual(related_person.language, "English")
        self.assertTrue(related_person.language_preferred)
        self.assertIsNotNone(related_person.person)
        self.assertEqual(related_person.person.name, "Alex Rivera")
        self.assertEqual(PersonLink.objects.get(related_person=related_person).person, related_person.person)
        self.assertEqual(CareTeamParticipant.objects.get().related_person, related_person)

    def test_imports_person_and_group(self):
        result = import_fhir_json(
            {
                "resourceType": "Bundle",
                "type": "collection",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "Patient",
                            "id": "pat-1",
                            "name": [{"family": "Rivera", "given": ["Maya"]}],
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "Organization",
                            "id": "org-1",
                            "name": "Example Registry",
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "Practitioner",
                            "id": "prac-1",
                            "name": [{"family": "Nguyen", "given": ["Ari"]}],
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "RelatedPerson",
                            "id": "rp-1",
                            "patient": {"reference": "Patient/pat-1"},
                            "relationship": [{"text": "Guardian"}],
                            "name": [{"family": "Rivera", "given": ["Alex"]}],
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "Device",
                            "id": "device-1",
                            "patient": {"reference": "Patient/pat-1"},
                            "type": {"text": "Monitor"},
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "Person",
                            "id": "person-1",
                            "name": [{"family": "Rivera", "given": ["Alex"]}],
                            "telecom": [{"system": "phone", "value": "555-1212"}],
                            "gender": "other",
                            "birthDate": "1980-04-05",
                            "managingOrganization": {"reference": "Organization/org-1"},
                            "link": [
                                {"target": {"reference": "RelatedPerson/rp-1"}, "assurance": "level3"},
                                {"target": {"reference": "Practitioner/prac-1"}, "assurance": "level1"},
                            ],
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "Group",
                            "id": "group-1",
                            "active": True,
                            "type": "person",
                            "actual": True,
                            "code": {"text": "Household"},
                            "name": "Rivera household",
                            "quantity": 2,
                            "managingEntity": {"reference": "RelatedPerson/rp-1"},
                            "characteristic": [
                                {
                                    "code": {"text": "Lives together"},
                                    "valueBoolean": True,
                                    "exclude": False,
                                }
                            ],
                            "member": [
                                {"entity": {"reference": "Patient/pat-1"}},
                                {"entity": {"reference": "Device/device-1"}, "inactive": False},
                            ],
                        }
                    },
                ],
            }
        )

        self.assertEqual(result.errors, [])
        person = Person.objects.get(name="Alex Rivera")
        related_person = RelatedPerson.objects.get()
        self.assertEqual(related_person.person, person)
        self.assertEqual(person.managing_organization, Organization.objects.get())
        self.assertEqual(person.link_records.count(), 2)
        self.assertEqual(PersonLink.objects.get(related_person=related_person).assurance, "level3")
        self.assertEqual(PersonLink.objects.get(practitioner=Practitioner.objects.get()).assurance, "level1")

        group = FHIRGroup.objects.get()
        self.assertEqual(group.name, "Rivera household")
        self.assertEqual(group.managing_related_person, related_person)
        self.assertIn("Lives together", group.characteristic_summary)
        self.assertEqual(group.member_links.count(), 2)
        self.assertEqual(FHIRGroupMember.objects.get(patient=PatientProfile.objects.get()).group, group)
        self.assertEqual(FHIRGroupMember.objects.get(device=Device.objects.get()).group, group)

    def test_imports_goal_risk_body_structure_and_device_resources(self):
        payload = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {"resource": {"resourceType": "Patient", "id": "pat-1", "name": [{"family": "Rivera", "given": ["Maya"]}]}},
                {"resource": {"resourceType": "Practitioner", "id": "prac-1", "name": [{"family": "Nguyen", "given": ["Ari"]}]}},
                {"resource": {"resourceType": "Organization", "id": "org-1", "name": "Example Clinic"}},
                {"resource": {"resourceType": "Encounter", "id": "enc-1", "subject": {"reference": "Patient/pat-1"}}},
                {"resource": {"resourceType": "Condition", "id": "cond-1", "subject": {"reference": "Patient/pat-1"}, "code": {"text": "Fall risk"}}},
                {"resource": {"resourceType": "Observation", "id": "obs-1", "subject": {"reference": "Patient/pat-1"}, "code": {"text": "Gait score"}, "valueString": "Unsteady"}},
                {"resource": {"resourceType": "Device", "id": "device-1", "patient": {"reference": "Patient/pat-1"}, "type": {"text": "Walker"}}},
                {"resource": {"resourceType": "ServiceRequest", "id": "sr-1", "subject": {"reference": "Patient/pat-1"}, "status": "active", "intent": "order", "code": {"text": "PT evaluation"}}},
                {
                    "resource": {
                        "resourceType": "DiagnosticReport",
                        "id": "dr-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "final",
                        "code": {"text": "Mobility report"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "RiskAssessment",
                        "id": "risk-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "encounter": {"reference": "Encounter/enc-1"},
                        "status": "final",
                        "code": {"text": "Fall risk assessment"},
                        "performer": {"reference": "Practitioner/prac-1"},
                        "basis": [
                            {"reference": "Condition/cond-1"},
                            {"reference": "Observation/obs-1"},
                            {"reference": "DiagnosticReport/dr-1"},
                        ],
                        "prediction": [{"outcome": {"text": "Fall"}, "probabilityDecimal": 0.2, "qualitativeRisk": {"text": "moderate"}}],
                        "mitigation": "Use walker.",
                    }
                },
                {
                    "resource": {
                        "resourceType": "Goal",
                        "id": "goal-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "lifecycleStatus": "active",
                        "achievementStatus": {"text": "in progress"},
                        "description": {"text": "Walk safely at home"},
                        "expressedBy": {"reference": "Practitioner/prac-1"},
                        "addresses": [
                            {"reference": "Condition/cond-1"},
                            {"reference": "Observation/obs-1"},
                            {"reference": "RiskAssessment/risk-1"},
                        ],
                        "target": [{"measure": {"text": "Falls"}, "detailInteger": 0, "dueDate": "2024-05-01"}],
                        "outcomeReference": [{"reference": "Observation/obs-1"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "BodyStructure",
                        "id": "body-1",
                        "patient": {"reference": "Patient/pat-1"},
                        "active": True,
                        "location": {"text": "Left knee"},
                        "morphology": {"text": "Surgical site"},
                        "description": "Left knee surgical site",
                    }
                },
                {
                    "resource": {
                        "resourceType": "DeviceRequest",
                        "id": "devreq-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "encounter": {"reference": "Encounter/enc-1"},
                        "status": "active",
                        "intent": "order",
                        "codeReference": {"reference": "Device/device-1"},
                        "requester": {"reference": "Practitioner/prac-1"},
                        "basedOn": [{"reference": "ServiceRequest/sr-1"}],
                        "reasonReference": [
                            {"reference": "Condition/cond-1"},
                            {"reference": "RiskAssessment/risk-1"},
                        ],
                        "performer": [{"reference": "Organization/org-1"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "DeviceUseStatement",
                        "id": "devuse-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "status": "active",
                        "device": {"reference": "Device/device-1"},
                        "source": {"reference": "Practitioner/prac-1"},
                        "basedOn": [
                            {"reference": "ServiceRequest/sr-1"},
                            {"reference": "DeviceRequest/devreq-1"},
                        ],
                        "reasonReference": [
                            {"reference": "Condition/cond-1"},
                            {"reference": "RiskAssessment/risk-1"},
                        ],
                        "bodySite": {"text": "Left hand"},
                    }
                },
            ],
        }

        result = import_fhir_json(payload)

        self.assertEqual(result.errors, [])
        risk = RiskAssessment.objects.get()
        self.assertEqual(risk.encounter, Encounter.objects.get())
        self.assertEqual(risk.performer_practitioner, Practitioner.objects.get())
        self.assertEqual(risk.conditions.get(), Condition.objects.get())
        self.assertEqual(risk.observations.get(), Observation.objects.get())
        self.assertEqual(risk.diagnostic_reports.get(), DiagnosticReport.objects.get())

        goal = Goal.objects.get()
        self.assertEqual(goal.expressed_by_practitioner, Practitioner.objects.get())
        self.assertEqual(goal.addresses_conditions.get(), Condition.objects.get())
        self.assertEqual(goal.addresses_observations.get(), Observation.objects.get())
        self.assertEqual(goal.addresses_risk_assessments.get(), risk)
        self.assertEqual(goal.outcome_observations.get(), Observation.objects.get())

        self.assertEqual(BodyStructure.objects.get().description, "Left knee surgical site")

        device_request = DeviceRequest.objects.get()
        self.assertEqual(device_request.devices.get(), Device.objects.get())
        self.assertEqual(device_request.service_requests.get(), ServiceRequest.objects.get())
        self.assertEqual(device_request.conditions.get(), Condition.objects.get())
        self.assertEqual(device_request.risk_assessments.get(), risk)
        self.assertEqual(device_request.performers_organizations.get(), Organization.objects.get())

        device_use = DeviceUseStatement.objects.get()
        self.assertEqual(device_use.device, Device.objects.get())
        self.assertEqual(device_use.source_practitioner, Practitioner.objects.get())
        self.assertEqual(device_use.based_on_service_requests.get(), ServiceRequest.objects.get())
        self.assertEqual(device_use.based_on_device_requests.get(), device_request)
        self.assertEqual(device_use.reason_conditions.get(), Condition.objects.get())
        self.assertEqual(device_use.reason_risk_assessments.get(), risk)

    def test_imports_quality_reporting_and_payment_resources(self):
        payload = {
            "resourceType": "Bundle",
            "entry": [
                {"resource": {"resourceType": "Patient", "id": "pat-quality", "name": [{"family": "Rivera", "given": ["Maya"]}]}},
                {"resource": {"resourceType": "Organization", "id": "payer-1", "name": "Acme Health Plan"}},
                {"resource": {"resourceType": "Coverage", "id": "coverage-1", "beneficiary": {"reference": "Patient/pat-quality"}, "payor": [{"reference": "Organization/payer-1"}], "status": "active"}},
                {"resource": {"resourceType": "Measure", "id": "measure-1", "title": "Screening Measure", "status": "active", "scoring": {"text": "proportion"}}},
                {"resource": {"resourceType": "MeasureReport", "id": "measure-report-1", "status": "complete", "type": "individual", "subject": {"reference": "Patient/pat-quality"}, "measure": "Measure/measure-1"}},
                {"resource": {"resourceType": "TestScript", "id": "testscript-1", "title": "FHIR Smoke Test", "status": "active"}},
                {"resource": {"resourceType": "TestReport", "id": "testreport-1", "name": "FHIR Smoke Report", "status": "completed", "result": "pass", "testScript": {"reference": "TestScript/testscript-1"}}},
                {"resource": {"resourceType": "CoverageEligibilityRequest", "id": "eligibility-request-1", "status": "active", "purpose": ["benefits"], "patient": {"reference": "Patient/pat-quality"}, "insurer": {"reference": "Organization/payer-1"}, "insurance": [{"coverage": {"reference": "Coverage/coverage-1"}}], "item": [{"category": {"text": "medical"}, "productOrService": {"text": "office visit"}}]}},
                {"resource": {"resourceType": "CoverageEligibilityResponse", "id": "eligibility-response-1", "status": "active", "purpose": ["benefits"], "outcome": "complete", "patient": {"reference": "Patient/pat-quality"}, "request": {"reference": "CoverageEligibilityRequest/eligibility-request-1"}, "insurer": {"reference": "Organization/payer-1"}}},
                {"resource": {"resourceType": "EnrollmentRequest", "id": "enrollment-request-1", "status": "active", "candidate": {"reference": "Patient/pat-quality"}, "insurer": {"reference": "Organization/payer-1"}, "coverage": {"reference": "Coverage/coverage-1"}}},
                {"resource": {"resourceType": "EnrollmentResponse", "id": "enrollment-response-1", "status": "active", "outcome": "complete", "request": {"reference": "EnrollmentRequest/enrollment-request-1"}, "organization": {"reference": "Organization/payer-1"}}},
                {"resource": {"resourceType": "PaymentNotice", "id": "payment-notice-1", "status": "active", "recipient": {"reference": "Organization/payer-1"}, "amount": {"value": 10, "currency": "USD"}, "request": {"reference": "CoverageEligibilityRequest/eligibility-request-1"}}},
                {"resource": {"resourceType": "PaymentReconciliation", "id": "payment-reconciliation-1", "status": "active", "outcome": "complete", "paymentIssuer": {"reference": "Organization/payer-1"}, "paymentAmount": {"value": 10, "currency": "USD"}}},
            ],
        }

        result = import_fhir_json(payload)

        self.assertEqual(result.errors, [])
        self.assertEqual(Measure.objects.get().title, "Screening Measure")
        self.assertEqual(MeasureReport.objects.get().patient, PatientProfile.objects.get())
        self.assertEqual(TestReport.objects.get().test_script, TestScript.objects.get())
        self.assertEqual(CoverageEligibilityRequest.objects.get().patient, PatientProfile.objects.get())
        self.assertEqual(CoverageEligibilityResponse.objects.get().request, CoverageEligibilityRequest.objects.get())
        self.assertEqual(EnrollmentRequest.objects.get().coverage, Coverage.objects.get())
        self.assertEqual(EnrollmentResponse.objects.get().request, EnrollmentRequest.objects.get())
        self.assertEqual(PaymentNotice.objects.get().recipient, Organization.objects.get())
        self.assertEqual(PaymentReconciliation.objects.get().payment_issuer, Organization.objects.get())

    def test_imports_terminology_and_knowledge_resources(self):
        payload = {
            "resourceType": "Bundle",
            "entry": [
                {"resource": {"resourceType": "CodeSystem", "id": "codesystem-1", "title": "Local Codes", "status": "active", "content": "complete", "concept": [{"code": "abc", "display": "ABC"}]}},
                {"resource": {"resourceType": "ValueSet", "id": "valueset-1", "title": "Local Value Set", "status": "active", "compose": {"include": [{"system": "http://example.test/codes", "concept": [{"code": "abc"}]}]}}},
                {"resource": {"resourceType": "ConceptMap", "id": "conceptmap-1", "title": "Local Map", "status": "active", "sourceUri": "http://example.test/source", "targetUri": "http://example.test/target", "group": [{"source": "source", "target": "target", "element": [{"code": "abc", "target": [{"code": "xyz", "equivalence": "equivalent"}]}]}]}},
                {"resource": {"resourceType": "Library", "id": "library-1", "title": "Logic Library", "status": "active", "type": {"text": "logic-library"}, "content": [{"contentType": "text/cql", "title": "logic.cql"}]}},
                {"resource": {"resourceType": "PlanDefinition", "id": "plandefinition-1", "title": "Care Protocol", "status": "active", "type": {"text": "clinical-protocol"}, "action": [{"title": "Review chart", "description": "Review relevant records"}]}},
            ],
        }

        result = import_fhir_json(payload)

        self.assertEqual(result.errors, [])
        self.assertEqual(CodeSystem.objects.get().title, "Local Codes")
        self.assertIn("abc", CodeSystem.objects.get().concept_summary)
        self.assertEqual(ValueSet.objects.get().title, "Local Value Set")
        self.assertIn("http://example.test/codes", ValueSet.objects.get().compose_summary)
        self.assertEqual(ConceptMap.objects.get().source_uri, "http://example.test/source")
        self.assertEqual(Library.objects.get().library_type, "logic-library")
        self.assertIn("logic.cql", Library.objects.get().content_summary)
        self.assertEqual(PlanDefinition.objects.get().plan_type, "clinical-protocol")
        self.assertIn("Review chart", PlanDefinition.objects.get().action_summary)
    def test_imports_metadata_definition_resources(self):
        payload = {
            "resourceType": "Bundle",
            "entry": [
                {"resource": {"resourceType": "CapabilityStatement", "id": "capability-1", "title": "Server Capabilities", "status": "active", "kind": "capability", "fhirVersion": "4.0.1", "format": ["json"]}},
                {"resource": {"resourceType": "StructureDefinition", "id": "structure-1", "title": "Patient Profile", "status": "active", "kind": "resource", "type": "Patient", "abstract": False}},
                {"resource": {"resourceType": "ImplementationGuide", "id": "ig-1", "title": "Local IG", "status": "active", "packageId": "local.fhir", "fhirVersion": ["4.0.1"]}},
                {"resource": {"resourceType": "SearchParameter", "id": "search-1", "name": "PatientName", "status": "active", "code": "name", "base": ["Patient"], "type": "string", "expression": "Patient.name"}},
                {"resource": {"resourceType": "MessageDefinition", "id": "message-1", "title": "ADT Message", "status": "active", "eventUri": "http://example.test/event", "category": "notification"}},
                {"resource": {"resourceType": "OperationDefinition", "id": "operation-1", "title": "Everything", "status": "active", "kind": "operation", "code": "everything", "system": True}},
                {"resource": {"resourceType": "CompartmentDefinition", "id": "compartment-1", "name": "Patient", "status": "active", "code": "Patient", "search": True}},
                {"resource": {"resourceType": "StructureMap", "id": "map-1", "title": "Patient Map", "status": "active", "structure": [{"url": "StructureDefinition/Patient", "mode": "source"}]}},
                {"resource": {"resourceType": "GraphDefinition", "id": "graph-1", "title": "Patient Graph", "status": "active", "start": "Patient", "link": [{"path": "Patient.generalPractitioner"}]}},
                {"resource": {"resourceType": "ExampleScenario", "id": "scenario-1", "title": "Scheduling Scenario", "status": "active", "actor": [{"actorId": "patient", "name": "Patient"}]}},
                {"resource": {"resourceType": "NamingSystem", "id": "naming-1", "name": "Local IDs", "status": "active", "kind": "identifier", "uniqueId": [{"type": "uri", "value": "http://example.test/ids"}]}},
                {"resource": {"resourceType": "TerminologyCapabilities", "id": "termcap-1", "title": "Terminology Capabilities", "status": "active", "kind": "capability", "codeSystem": [{"uri": "http://loinc.org"}]}},
                {"resource": {"resourceType": "ActivityDefinition", "id": "activity-1", "title": "Order Lab", "status": "active", "kind": "ServiceRequest", "intent": "order", "code": {"text": "CBC"}}},
                {"resource": {"resourceType": "EventDefinition", "id": "event-1", "title": "Patient Arrived", "status": "active", "trigger": [{"type": "named-event", "name": "patient-arrived"}]}},
                {"resource": {"resourceType": "SpecimenDefinition", "id": "specdef-1", "url": "http://example.test/specimen", "status": "active", "typeCollected": {"text": "Blood"}}},
            ],
        }

        result = import_fhir_json(payload)

        self.assertEqual(result.errors, [])
        self.assertEqual(CapabilityStatement.objects.get().kind, "capability")
        self.assertEqual(StructureDefinition.objects.get().type_code, "Patient")
        self.assertEqual(ImplementationGuide.objects.get().package_id, "local.fhir")
        self.assertEqual(SearchParameter.objects.get().code, "name")
        self.assertEqual(MessageDefinition.objects.get().event, "http://example.test/event")
        self.assertEqual(OperationDefinition.objects.get().code, "everything")
        self.assertEqual(CompartmentDefinition.objects.get().code, "Patient")
        self.assertIn("StructureDefinition/Patient", StructureMap.objects.get().structure_summary)
        self.assertEqual(GraphDefinition.objects.get().start, "Patient")
        self.assertIn("patient", ExampleScenario.objects.get().actor_summary)
        self.assertEqual(NamingSystem.objects.get().kind, "identifier")
        self.assertEqual(TerminologyCapabilities.objects.get().kind, "capability")
        self.assertEqual(ActivityDefinition.objects.get().activity_kind, "ServiceRequest")
        self.assertIn("patient-arrived", EventDefinition.objects.get().trigger_summary)
        self.assertEqual(SpecimenDefinition.objects.get().specimen_type, "Blood")
    def test_missing_patient_reference_is_snapshotted_as_invalid(self):
        result = import_fhir_json(
            {
                "resourceType": "Condition",
                "id": "orphan",
                "subject": {"reference": "Patient/missing"},
                "code": {"text": "Asthma"},
            }
        )

        self.assertEqual(result.created, 0)
        self.assertEqual(len(result.errors), 1)
        snapshot = FHIRResourceSnapshot.objects.get()
        self.assertFalse(snapshot.is_valid)
        self.assertEqual(snapshot.import_status, FHIRResourceSnapshot.IMPORT_STATUS_INVALID)
        self.assertEqual(snapshot.validation_errors, ["Missing or unknown patient reference."])

    def test_unsupported_resource_is_preserved_as_valid_snapshot_only(self):
        result = import_fhir_json(
            {
                "resourceType": "OperationOutcome",
                "id": "operation-outcome-1",
                "issue": [{"severity": "information", "code": "informational"}],
            }
        )

        self.assertEqual(result.created, 0)
        self.assertEqual(result.updated, 0)
        self.assertEqual(result.unsupported, 1)
        self.assertEqual(result.errors, [])
        snapshot = FHIRResourceSnapshot.objects.get()
        self.assertTrue(snapshot.is_valid)
        self.assertEqual(snapshot.import_status, FHIRResourceSnapshot.IMPORT_STATUS_SNAPSHOT_ONLY)
        self.assertEqual(snapshot.validation_errors, [])
        self.assertEqual(snapshot.resource_type, "OperationOutcome")

    def test_loads_fhir_json_rejects_invalid_json(self):
        with self.assertRaises(ValueError):
            loads_fhir_json("{not-json")

    def test_loads_ndjson_resources(self):
        payloads = loads_fhir_documents(
            "\n".join(
                [
                    json.dumps({"resourceType": "Patient", "id": "pat-1"}),
                    json.dumps({"resourceType": "Condition", "id": "cond-1"}),
                ]
            ),
            "export.ndjson",
        )

        self.assertEqual([payload["resourceType"] for payload in payloads], ["Patient", "Condition"])

    def test_form_accepts_mychart_zip_export(self):
        archive_content = BytesIO()
        with ZipFile(archive_content, "w") as archive:
            archive.writestr(
                "Requested Record/FHIR/Patient11694.NDJSON",
                json.dumps(
                    {
                        "resourceType": "Patient",
                        "id": "pat-1",
                        "name": [{"family": "Rivera", "given": ["Maya"]}],
                    }
                )
                + "\n",
            )
            archive.writestr(
                "Requested Record/FHIR/condition1168.NDJSON",
                json.dumps(
                    {
                        "resourceType": "Condition",
                        "id": "cond-1",
                        "subject": {"reference": "Patient/pat-1"},
                        "code": {"text": "Asthma"},
                    }
                )
                + "\n",
            )
            archive.writestr("Requested Record/readme.txt", "not fhir")

        uploaded_file = SimpleUploadedFile(
            "Requested Record.zip",
            archive_content.getvalue(),
            content_type="application/zip",
        )
        form = FHIRImportForm(data={}, files={"fhir_file": uploaded_file})

        self.assertTrue(form.is_valid(), form.errors)
        result = import_fhir_payloads(form.cleaned_data["payloads"])

        self.assertEqual(result.created, 2)
        self.assertEqual(PatientProfile.objects.count(), 1)
        self.assertEqual(Condition.objects.count(), 1)

    def test_form_ignores_bulk_fhir_zip_log_sidecar(self):
        archive_content = BytesIO()
        with ZipFile(archive_content, "w") as archive:
            archive.writestr(
                "bulk-export/Patient.000.ndjson",
                json.dumps(
                    {
                        "resourceType": "Patient",
                        "id": "pat-1",
                        "name": [{"family": "Rivera", "given": ["Maya"]}],
                    }
                )
                + "\n",
            )
            archive.writestr(
                "bulk-export/log.ndjson",
                json.dumps(
                    {
                        "exportId": "export-1",
                        "timestamp": "2026-06-18T10:00:00Z",
                        "eventId": "complete",
                        "eventDetail": "Bulk export completed.",
                    }
                )
                + "\n",
            )

        uploaded_file = SimpleUploadedFile(
            "sample-bulk-fhir-datasets-10-patients.zip",
            archive_content.getvalue(),
            content_type="application/zip",
        )
        form = FHIRImportForm(data={}, files={"fhir_file": uploaded_file})

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(len(form.cleaned_data["payloads"]), 1)
        self.assertEqual(form.cleaned_data["payloads"][0]["resourceType"], "Patient")

    def test_import_page_can_quick_add_patient(self):
        User = get_user_model()
        user = User.objects.create_superuser(
            username="owner",
            email="owner@example.test",
            password="correct-password",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("fhir_import"),
            {
                "action": "create_patient",
                "first_name": "Ada",
                "last_name": "Lovelace",
                "date_of_birth": "1815-12-10",
            },
            follow=True,
        )

        patient = PatientProfile.objects.get(first_name="Ada", last_name="Lovelace")
        self.assertRedirects(response, f"{reverse('fhir_import')}?patient={patient.pk}")
        self.assertEqual(patient.date_of_birth, date(1815, 12, 10))
        self.assertEqual(response.context["form"].initial["patient"], str(patient.pk))

    def test_import_page_includes_admin_sidebar_context(self):
        User = get_user_model()
        user = User.objects.create_superuser(
            username="owner",
            email="owner@example.test",
            password="correct-password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("fhir_import"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("available_apps", response.context)
        self.assertContains(response, "jazzy-navigation")

    def test_pre_import_backup_copies_database_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "holyfhir.encrypted.sqlite3"
            database_path.write_bytes(b"encrypted database bytes")
            fake_connections = {"default": Mock()}

            with patch("fhir.backups.settings.DATABASES", {"default": {"NAME": str(database_path)}}):
                with patch("fhir.backups.connections", fake_connections):
                    backup_path = create_pre_import_database_backup()

            self.assertIsNotNone(backup_path)
            self.assertTrue(backup_path.exists())
            self.assertEqual(backup_path.read_bytes(), b"encrypted database bytes")
            self.assertEqual(backup_path.parent, database_path.parent / "backups" / "fhir-imports")
            self.assertIn(".pre-fhir-import.", backup_path.name)
            fake_connections["default"].close.assert_called_once()

    def test_lists_fhir_import_backups_newest_first(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "holyfhir.encrypted.sqlite3"
            database_path.write_bytes(b"live")
            backup_dir = Path(temp_dir) / "backups" / "fhir-imports"
            backup_dir.mkdir(parents=True)
            older = backup_dir / "holyfhir.encrypted.pre-fhir-import.20260426-120000.sqlite3"
            newer = backup_dir / "holyfhir.encrypted.pre-fhir-import.20260426-130000.sqlite3"
            ignored = backup_dir / "notes.txt"
            older.write_bytes(b"older")
            newer.write_bytes(b"newer")
            ignored.write_text("not a backup")

            with patch("fhir.backups.settings.DATABASES", {"default": {"NAME": str(database_path)}}):
                backups = list_fhir_import_database_backups()

            self.assertEqual([backup.name for backup in backups], [newer.name, older.name])
            self.assertEqual(backups[0].size_bytes, 5)

    def test_import_page_creates_pre_import_backup(self):
        User = get_user_model()
        user = User.objects.create_superuser(
            username="owner",
            email="owner@example.test",
            password="correct-password",
        )
        self.client.force_login(user)
        payload = {
            "resourceType": "Patient",
            "id": "pat-1",
            "name": [{"family": "Rivera", "given": ["Maya"]}],
        }

        with patch("fhir.views.create_pre_import_database_backup", return_value=Path("backup.sqlite3")) as backup:
            response = self.client.post(
                reverse("fhir_import"),
                {"action": "import_fhir", "fhir_json": json.dumps(payload)},
                follow=True,
            )

        self.assertEqual(response.status_code, 200)
        backup.assert_called_once()
        self.assertEqual(PatientProfile.objects.filter(first_name="Maya", last_name="Rivera").count(), 1)
        messages = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertTrue(any("Pre-import database backup created: backup.sqlite3" in message for message in messages))

    def test_import_page_stops_if_pre_import_backup_fails(self):
        User = get_user_model()
        user = User.objects.create_superuser(
            username="owner",
            email="owner@example.test",
            password="correct-password",
        )
        self.client.force_login(user)
        payload = {
            "resourceType": "Patient",
            "id": "pat-1",
            "name": [{"family": "Rivera", "given": ["Maya"]}],
        }

        with patch("fhir.views.create_pre_import_database_backup", side_effect=OSError("disk is full")):
            response = self.client.post(
                reverse("fhir_import"),
                {"action": "import_fhir", "fhir_json": json.dumps(payload)},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PatientProfile.objects.filter(first_name="Maya", last_name="Rivera").count(), 0)
        messages = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertTrue(any("database backup failed" in message for message in messages))





