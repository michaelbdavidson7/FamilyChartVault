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
            ("Immunizations", "admin:clinical_immunization_changelist"),
            ("Immunization Recommendations", "admin:clinical_immunizationrecommendation_changelist"),
            ("Vitals &amp; Labs", "admin:clinical_observation_changelist"),
            ("Diagnostic Reports", "admin:clinical_diagnosticreport_changelist"),
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
            ("Goals", "admin:clinical_goal_changelist"),
            ("Device Requests", "admin:clinical_devicerequest_changelist"),
            ("Episodes of Care", "admin:clinical_episodeofcare_changelist"),
            ("Procedures", "admin:clinical_procedure_changelist"),
            ("Specimens", "admin:clinical_specimen_changelist"),
            ("Coverages", "admin:clinical_coverage_changelist"),
            ("Explanations of Benefits", "admin:clinical_explanationofbenefit_changelist"),
            ("Insurance Plans", "admin:clinical_insuranceplan_changelist"),
            ("Practitioners", "admin:clinical_practitioner_changelist"),
            ("Practitioner Roles", "admin:clinical_practitionerrole_changelist"),
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
        self.assertContains(response, "Consents")
        self.assertContains(response, f"{reverse('admin:clinical_condition_changelist')}?patient__id__exact={patient.pk}")
        self.assertContains(response, f"{reverse('admin:clinical_observation_changelist')}?patient__id__exact={patient.pk}")
        self.assertContains(response, f"{reverse('admin:documents_clinicaldocument_changelist')}?patient__id__exact={patient.pk}")
        self.assertContains(response, f"{reverse('admin:clinical_coverage_changelist')}?patient__id__exact={patient.pk}")
        self.assertContains(response, "1 record")
