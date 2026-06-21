from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clinical.models import Condition, Observation
from documents.models import ClinicalDocument
from patients.models import PatientProfile


class SettingsBackupPageTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            username="owner",
            email="owner@example.test",
            password="correct-password",
        )
        self.client.force_login(self.user)

    def test_settings_links_to_backups_page(self):
        response = self.client.get(reverse("admin_settings"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backups")
        self.assertContains(response, reverse("admin_backups"))

    def test_backups_page_renders_manual_restore_explainer(self):
        response = self.client.get(reverse("admin_backups"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manual Restore")
        self.assertContains(response, "Close HolyFHIR completely")
        self.assertContains(response, "FHIR Import Backups")

    def test_clinical_care_team_directory_lists_directory_sections(self):
        response = self.client.get(reverse("clinical_care_team_directory"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Care Teams")
        self.assertContains(response, "Practitioners")
        self.assertContains(response, "Organizations")
        self.assertContains(response, "Locations")
        self.assertContains(response, reverse("admin:clinical_careteam_changelist"))
        self.assertContains(response, reverse("admin:clinical_practitioner_changelist"))
        self.assertContains(response, reverse("admin:clinical_organization_changelist"))
        self.assertContains(response, reverse("admin:clinical_location_changelist"))

    def test_clinical_resources_directory_lists_all_clinical_resources(self):
        response = self.client.get(reverse("clinical_resources_directory"))

        self.assertEqual(response.status_code, 200)
        expected_resources = [
            ("Conditions", "admin:clinical_condition_changelist"),
            ("Allergies", "admin:clinical_allergy_changelist"),
            ("Adverse Events", "admin:clinical_adverseevent_changelist"),
            ("Family History", "admin:clinical_familymemberhistory_changelist"),
            ("Related People", "admin:clinical_relatedperson_changelist"),
            ("People", "admin:clinical_person_changelist"),
            ("Clinical Impressions", "admin:clinical_clinicalimpression_changelist"),
            ("Detected Issues", "admin:clinical_detectedissue_changelist"),
            ("Medications", "admin:clinical_medication_changelist"),
            ("Medication Catalog", "admin:clinical_medicationcatalog_changelist"),
            ("Medication Administrations", "admin:clinical_medicationadministration_changelist"),
            ("Medication Dispenses", "admin:clinical_medicationdispense_changelist"),
            ("Medication Knowledge", "admin:clinical_medicationknowledge_changelist"),
            ("Immunizations", "admin:clinical_immunization_changelist"),
            ("Immunization Evaluations", "admin:clinical_immunizationevaluation_changelist"),
            ("Immunization Recommendations", "admin:clinical_immunizationrecommendation_changelist"),
            ("Vitals &amp; Labs", "admin:clinical_observation_changelist"),
            ("Diagnostic Reports", "admin:clinical_diagnosticreport_changelist"),
            ("Media", "admin:clinical_media_changelist"),
            ("Imaging Studies", "admin:clinical_imagingstudy_changelist"),
            ("Molecular Sequences", "admin:clinical_molecularsequence_changelist"),
            ("Flags", "admin:clinical_flag_changelist"),
            ("Consents", "admin:clinical_consent_changelist"),
            ("Communications", "admin:clinical_communication_changelist"),
            ("Questionnaire Responses", "admin:clinical_questionnaireresponse_changelist"),
            ("FHIR Lists", "admin:clinical_fhirlist_changelist"),
            ("Risk Assessments", "admin:clinical_riskassessment_changelist"),
            ("Body Structures", "admin:clinical_bodystructure_changelist"),
            ("Visits &amp; Actions", "admin:clinical_encounter_changelist"),
            ("Devices", "admin:clinical_device_changelist"),
            ("Device Use", "admin:clinical_deviceusestatement_changelist"),
            ("Groups", "admin:clinical_fhirgroup_changelist"),
            ("Care Teams", "admin:clinical_careteam_changelist"),
            ("Care Plans", "admin:clinical_careplan_changelist"),
            ("Service Requests", "admin:clinical_servicerequest_changelist"),
            ("Communication Requests", "admin:clinical_communicationrequest_changelist"),
            ("Nutrition Orders", "admin:clinical_nutritionorder_changelist"),
            ("Vision Prescriptions", "admin:clinical_visionprescription_changelist"),
            ("Request Groups", "admin:clinical_requestgroup_changelist"),
            ("Guidance Responses", "admin:clinical_guidanceresponse_changelist"),
            ("Supply Requests", "admin:clinical_supplyrequest_changelist"),
            ("Supply Deliveries", "admin:clinical_supplydelivery_changelist"),
            ("Goals", "admin:clinical_goal_changelist"),
            ("Device Requests", "admin:clinical_devicerequest_changelist"),
            ("Episodes of Care", "admin:clinical_episodeofcare_changelist"),
            ("Procedures", "admin:clinical_procedure_changelist"),
            ("Specimens", "admin:clinical_specimen_changelist"),
            ("Coverages", "admin:clinical_coverage_changelist"),
            ("Explanations of Benefits", "admin:clinical_explanationofbenefit_changelist"),
            ("Insurance Plans", "admin:clinical_insuranceplan_changelist"),
            ("Coverage Eligibility Requests", "admin:clinical_coverageeligibilityrequest_changelist"),
            ("Coverage Eligibility Responses", "admin:clinical_coverageeligibilityresponse_changelist"),
            ("Enrollment Requests", "admin:clinical_enrollmentrequest_changelist"),
            ("Enrollment Responses", "admin:clinical_enrollmentresponse_changelist"),
            ("Payment Notices", "admin:clinical_paymentnotice_changelist"),
            ("Payment Reconciliations", "admin:clinical_paymentreconciliation_changelist"),
            ("Libraries", "admin:clinical_library_changelist"),
            ("Plan Definitions", "admin:clinical_plandefinition_changelist"),
            ("Measures", "admin:clinical_measure_changelist"),
            ("Measure Reports", "admin:clinical_measurereport_changelist"),
            ("Test Scripts", "admin:clinical_testscript_changelist"),
            ("Test Reports", "admin:clinical_testreport_changelist"),
            ("Claims", "admin:clinical_claim_changelist"),
            ("Claim Responses", "admin:clinical_claimresponse_changelist"),
            ("Accounts", "admin:clinical_account_changelist"),
            ("Audit Events", "admin:clinical_auditevent_changelist"),
            ("Invoices", "admin:clinical_invoice_changelist"),
            ("Charge Items", "admin:clinical_chargeitem_changelist"),
            ("Research Studies", "admin:clinical_researchstudy_changelist"),
            ("Research Subjects", "admin:clinical_researchsubject_changelist"),
            ("Capability Statements", "admin:clinical_capabilitystatement_changelist"),
            ("Structure Definitions", "admin:clinical_structuredefinition_changelist"),
            ("Implementation Guides", "admin:clinical_implementationguide_changelist"),
            ("Search Parameters", "admin:clinical_searchparameter_changelist"),
            ("Message Definitions", "admin:clinical_messagedefinition_changelist"),
            ("Operation Definitions", "admin:clinical_operationdefinition_changelist"),
            ("Compartment Definitions", "admin:clinical_compartmentdefinition_changelist"),
            ("Structure Maps", "admin:clinical_structuremap_changelist"),
            ("Graph Definitions", "admin:clinical_graphdefinition_changelist"),
            ("Example Scenarios", "admin:clinical_examplescenario_changelist"),
            ("Naming Systems", "admin:clinical_namingsystem_changelist"),
            ("Terminology Capabilities", "admin:clinical_terminologycapabilities_changelist"),
            ("Activity Definitions", "admin:clinical_activitydefinition_changelist"),
            ("Event Definitions", "admin:clinical_eventdefinition_changelist"),
            ("Specimen Definitions", "admin:clinical_specimendefinition_changelist"),            ("Code Systems", "admin:clinical_codesystem_changelist"),
            ("Value Sets", "admin:clinical_valueset_changelist"),
            ("Concept Maps", "admin:clinical_conceptmap_changelist"),
            ("Questionnaires", "admin:clinical_questionnaire_changelist"),
            ("Device Definitions", "admin:clinical_devicedefinition_changelist"),
            ("Observation Definitions", "admin:clinical_observationdefinition_changelist"),
            ("Compositions", "admin:clinical_composition_changelist"),
            ("Document Manifests", "admin:clinical_documentmanifest_changelist"),
            ("Binary Resources", "admin:clinical_binaryresource_changelist"),
            ("Provenance", "admin:clinical_provenance_changelist"),
            ("Tasks", "admin:clinical_task_changelist"),
            ("Appointments", "admin:clinical_appointment_changelist"),
            ("Appointment Responses", "admin:clinical_appointmentresponse_changelist"),
            ("Schedules", "admin:clinical_schedule_changelist"),
            ("Slots", "admin:clinical_slot_changelist"),
            ("Practitioners", "admin:clinical_practitioner_changelist"),
            ("Practitioner Roles", "admin:clinical_practitionerrole_changelist"),
            ("Healthcare Services", "admin:clinical_healthcareservice_changelist"),
            ("Organization Affiliations", "admin:clinical_organizationaffiliation_changelist"),
            ("Endpoints", "admin:clinical_endpoint_changelist"),
            ("Substances", "admin:clinical_substance_changelist"),
            ("Device Metrics", "admin:clinical_devicemetric_changelist"),
            ("Organizations", "admin:clinical_organization_changelist"),
            ("Locations", "admin:clinical_location_changelist"),
        ]
        for label, url_name in expected_resources:
            self.assertContains(response, label)
            self.assertContains(response, reverse(url_name))

    def test_patient_profile_links_to_patient_resources_directory(self):
        patient = PatientProfile.objects.create(first_name="Maya", last_name="Rivera")

        response = self.client.get(reverse("admin:patients_patientprofile_change", args=[patient.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View all patient resources")
        self.assertContains(response, reverse("patient_resources_directory", args=[patient.pk]))

    def test_patient_resources_directory_lists_filtered_resource_links(self):
        patient = PatientProfile.objects.create(first_name="Maya", last_name="Rivera")
        other_patient = PatientProfile.objects.create(first_name="Other", last_name="Patient")
        Condition.objects.create(patient=patient, name="Asthma")
        Condition.objects.create(patient=other_patient, name="Migraine")
        Observation.objects.create(patient=patient, name="Blood pressure")
        ClinicalDocument.objects.create(patient=patient, title="Discharge summary")

        response = self.client.get(reverse("patient_resources_directory", args=[patient.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maya Rivera")
        self.assertContains(response, "Conditions")
        self.assertContains(response, "Vitals &amp; Labs")
        self.assertContains(response, "Documents")
        self.assertContains(response, "Coverages")
        self.assertContains(response, "Claims")
        self.assertContains(response, "Accounts")
        self.assertContains(response, "Research Subjects")
        self.assertContains(response, "Measure Reports")
        self.assertContains(response, "Coverage Eligibility Requests")
        self.assertContains(response, "Audit Events")
        self.assertContains(response, "Consents")
        self.assertContains(response, "Tasks")
        self.assertContains(response, "Appointments")
        self.assertContains(response, "Provenance")
        self.assertContains(response, f"{reverse('admin:clinical_condition_changelist')}?patient__id__exact={patient.pk}")
        self.assertContains(response, f"{reverse('admin:clinical_observation_changelist')}?patient__id__exact={patient.pk}")
        self.assertContains(response, f"{reverse('admin:documents_clinicaldocument_changelist')}?patient__id__exact={patient.pk}")
        self.assertContains(response, f"{reverse('admin:clinical_coverage_changelist')}?patient__id__exact={patient.pk}")
        self.assertContains(response, f"{reverse('admin:clinical_claim_changelist')}?patient__id__exact={patient.pk}")
        self.assertContains(response, f"{reverse('admin:clinical_account_changelist')}?patient__id__exact={patient.pk}")
        self.assertContains(response, f"{reverse('admin:clinical_task_changelist')}?patient__id__exact={patient.pk}")
        self.assertContains(response, "1 record")


