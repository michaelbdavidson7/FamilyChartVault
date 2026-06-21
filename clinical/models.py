from django.db import models
from patients.models import PatientProfile

# Models are grouped by broad FHIR/workflow area. The ordering is intentionally
# conservative so historical migrations do not churn just to make this file prettier.

# =============================================================================
# Core Clinical Records
# Problems, allergies, medications, immunizations, observations, specimens, visits, and devices.
# =============================================================================

class Condition(models.Model):
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="conditions",
        help_text="FHIR subject: patient who has, had, or may have this condition.",
    )
    name = models.CharField(max_length=255, help_text="FHIR code: problem, diagnosis, or condition name.")
    icd10_code = models.CharField(max_length=20, blank=True, help_text="FHIR code.coding: ICD-10 diagnosis code when present.")
    snomed_code = models.CharField(max_length=30, blank=True, help_text="FHIR code.coding: SNOMED CT concept code when present.")
    clinical_status = models.CharField(max_length=30, blank=True, help_text="FHIR clinicalStatus: active, recurrence, relapse, inactive, remission, or resolved.")
    onset_date = models.DateField(null=True, blank=True, help_text="FHIR onset[x]: estimated or known start date.")
    abatement_date = models.DateField(null=True, blank=True, help_text="FHIR abatement[x]: estimated or known resolution/end date.")
    notes = models.TextField(blank=True, help_text="FHIR note: comments or clinical context for the condition.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Allergy(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="allergies", help_text="FHIR patient: person who has the allergy or intolerance.")
    substance = models.CharField(max_length=255, help_text="FHIR code: substance, product, or class that causes the reaction.")
    rxnorm_code = models.CharField(max_length=30, blank=True, help_text="FHIR code.coding: RxNorm code for medication allergies.")
    snomed_code = models.CharField(max_length=30, blank=True, help_text="FHIR code.coding: SNOMED CT code when present.")
    category = models.CharField(max_length=50, blank=True, help_text="FHIR category: food, medication, environment, or biologic.")
    criticality = models.CharField(max_length=20, blank=True, help_text="FHIR criticality: estimate of potential clinical harm.")
    reaction = models.CharField(max_length=255, blank=True, help_text="FHIR reaction.manifestation: observed or reported reaction.")
    severity = models.CharField(max_length=20, blank=True, help_text="FHIR reaction.severity: mild, moderate, or severe.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional allergy/intolerance comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Allergies"

    def __str__(self):
        return self.substance


class Medication(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="medications", help_text="FHIR subject/patient: person taking or prescribed the medication.")
    name = models.CharField(max_length=255, help_text="FHIR medication[x]: medication name or coded concept.")
    rxnorm_code = models.CharField(max_length=30, blank=True, help_text="FHIR medicationCodeableConcept.coding: RxNorm code when present.")
    dosage_text = models.CharField(max_length=255, blank=True, help_text="FHIR dosage.text: patient-facing or prescriber dosage instructions.")
    route = models.CharField(max_length=100, blank=True, help_text="FHIR dosage.route: how the medication is taken or given.")
    frequency = models.CharField(max_length=100, blank=True, help_text="FHIR dosage.timing: when or how often the medication is taken.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, completed, stopped, intended, entered-in-error, etc.")
    start_date = models.DateField(null=True, blank=True, help_text="FHIR effectivePeriod.start/authoredOn: start or authored date when known.")
    end_date = models.DateField(null=True, blank=True, help_text="FHIR effectivePeriod.end: end date when known.")
    prescriber = models.CharField(max_length=255, blank=True, help_text="FHIR requester/informationSource: prescriber or reporting source display.")
    indication = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode/reasonReference: reason or condition being treated.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional medication comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Immunization(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="immunizations", help_text="FHIR patient: person who received the vaccine.")
    vaccine_name = models.CharField(max_length=255, help_text="FHIR vaccineCode: vaccine product administered.")
    cvx_code = models.CharField(max_length=20, blank=True, help_text="FHIR vaccineCode.coding: CVX vaccine code when present.")
    occurrence_date = models.DateField(null=True, blank=True, help_text="FHIR occurrence[x]: when the vaccine was administered.")
    lot_number = models.CharField(max_length=100, blank=True, help_text="FHIR lotNumber: vaccine lot identifier.")
    manufacturer = models.CharField(max_length=255, blank=True, help_text="FHIR manufacturer: vaccine manufacturer display.")
    performer = models.CharField(max_length=255, blank=True, help_text="FHIR performer.actor: person or organization that administered or recorded the immunization.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional immunization comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vaccine_name


class Observation(models.Model):
    OBSERVATION_TYPES = [
        ("vital", "Vital"),
        ("lab", "Lab"),
        ("other", "Other"),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="observations", help_text="FHIR subject: patient the observation is about.")
    specimen = models.ForeignKey(
        "Specimen",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="observations",
        help_text="FHIR specimen: specimen used for this observation or lab result.",
    )
    device = models.ForeignKey(
        "Device",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="observations",
        help_text="FHIR device: device that generated or was used for this observation.",
    )
    category = models.CharField(max_length=20, choices=OBSERVATION_TYPES, default="other", help_text="FHIR category: vital sign, laboratory, survey, exam, or other grouping.")
    name = models.CharField(max_length=255, help_text="FHIR code: observation name or test performed.")
    loinc_code = models.CharField(max_length=30, blank=True, help_text="FHIR code.coding: LOINC code when present.")

    value_string = models.CharField(max_length=255, blank=True, help_text="FHIR valueString/valueCodeableConcept: textual result value.")
    value_quantity = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True, help_text="FHIR valueQuantity.value: numeric result value.")
    unit = models.CharField(max_length=50, blank=True, help_text="FHIR valueQuantity.unit/code: unit for numeric result values.")

    effective_datetime = models.DateTimeField(null=True, blank=True, help_text="FHIR effective[x]: clinically relevant time for the observation.")
    interpretation = models.CharField(max_length=50, blank=True, help_text="FHIR interpretation: high, low, normal, abnormal, etc.")
    reference_range = models.CharField(max_length=255, blank=True, help_text="FHIR referenceRange: expected or normal range.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional observation comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vitals & Lab Result"
        verbose_name_plural = "Vitals & Labs"

    def __str__(self):
        return self.name


class Specimen(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="specimens", help_text="FHIR subject: patient or source the specimen was collected from.")
    parent_specimens = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="child_specimens", help_text="FHIR parent: parent specimens from which this specimen was derived.")
    accession_identifier = models.CharField(max_length=100, blank=True, help_text="FHIR accessionIdentifier: identifier assigned by lab or specimen processor.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: available, unavailable, unsatisfactory, or entered-in-error.")
    specimen_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: kind of specimen, such as blood, urine, or tissue.")
    received_time = models.DateTimeField(null=True, blank=True, help_text="FHIR receivedTime: when the specimen was received for processing.")
    collected_datetime = models.DateTimeField(null=True, blank=True, help_text="FHIR collection.collected[x]: when the specimen was collected.")
    collection_method = models.CharField(max_length=255, blank=True, help_text="FHIR collection.method: how the specimen was collected.")
    body_site = models.CharField(max_length=255, blank=True, help_text="FHIR collection.bodySite: anatomical source of specimen.")
    collector_display = models.CharField(max_length=255, blank=True, help_text="FHIR collection.collector: person or organization that collected the specimen.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional specimen comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.specimen_type or self.accession_identifier or f"Specimen #{self.pk}"


class Encounter(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="encounters", help_text="FHIR subject: patient present or involved in the encounter.")
    episodes_of_care = models.ManyToManyField("EpisodeOfCare", blank=True, related_name="encounters", help_text="FHIR episodeOfCare: broader care episodes this encounter belongs to.")
    encounter_type = models.CharField(max_length=100, blank=True, help_text="FHIR class/type: setting or kind of encounter, such as office, ED, inpatient.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: planned, arrived, in-progress, finished, cancelled, etc.")
    start_time = models.DateTimeField(null=True, blank=True, help_text="FHIR period.start: encounter start time.")
    end_time = models.DateTimeField(null=True, blank=True, help_text="FHIR period.end: encounter end time.")
    provider_name = models.CharField(max_length=255, blank=True, help_text="FHIR participant.individual: provider or participant display.")
    facility_name = models.CharField(max_length=255, blank=True, help_text="FHIR location.location: facility or location display.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode/reasonReference: reason for the encounter.")
    summary = models.TextField(blank=True, help_text="FHIR text/note: encounter summary or imported narrative.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Visit"
        verbose_name_plural = "Visits"

    def __str__(self):
        return self.encounter_type or self.reason or f"Visit #{self.pk}"


class Device(models.Model):
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="devices",
        null=True,
        blank=True,
        help_text="FHIR patient: patient associated with the device when applicable.",
    )
    owner = models.ForeignKey(
        "Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
        help_text="FHIR owner: organization responsible for the device.",
    )
    location = models.ForeignKey(
        "Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
        help_text="FHIR location: where the device is found or used.",
    )
    display_name = models.CharField(max_length=255, help_text="FHIR deviceName/type: human-readable device name.")
    device_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: kind or category of device.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, inactive, entered-in-error, or unknown.")
    manufacturer = models.CharField(max_length=255, blank=True, help_text="FHIR manufacturer: device manufacturer.")
    model_number = models.CharField(max_length=255, blank=True, help_text="FHIR modelNumber: manufacturer's model number.")
    serial_number = models.CharField(max_length=255, blank=True, help_text="FHIR serialNumber: device serial number.")
    lot_number = models.CharField(max_length=255, blank=True, help_text="FHIR lotNumber: manufacturing lot number.")
    distinct_identifier = models.CharField(max_length=255, blank=True, help_text="FHIR distinctIdentifier: distinct fixed device identifier.")
    udi_carrier = models.TextField(blank=True, help_text="FHIR udiCarrier: unique device identifier carrier details.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional device comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name


# =============================================================================
# Care Planning And Coordination
# Care teams, care plans, family history, impressions, reports, detected issues, and related assessment resources.
# =============================================================================

class CareTeam(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="care_teams", help_text="FHIR subject: patient whose care team this is.")
    managing_organizations = models.ManyToManyField(
        "Organization",
        blank=True,
        related_name="managed_care_teams",
        help_text="FHIR managingOrganization: organization responsible for the care team.",
    )
    name = models.CharField(max_length=255, help_text="FHIR name: human-readable care team name.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: proposed, active, suspended, inactive, or entered-in-error.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: type of team, such as condition-specific or long-term care.")
    participants = models.TextField(blank=True, help_text="FHIR participant: imported participant summary when structured links are not available.")
    start_date = models.DateField(null=True, blank=True, help_text="FHIR period.start: when team responsibility started.")
    end_date = models.DateField(null=True, blank=True, help_text="FHIR period.end: when team responsibility ended.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode/reasonReference: why the care team exists.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional care team comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Care Team"
        verbose_name_plural = "Care Team"

    def __str__(self):
        return self.name


class CarePlan(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="care_plans", help_text="FHIR subject: patient the care plan is for.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly name for the care plan.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, on-hold, revoked, completed, etc.")
    intent = models.CharField(max_length=30, blank=True, help_text="FHIR intent: proposal, plan, order, option, etc.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: type or grouping of care plan.")
    description = models.TextField(blank=True, help_text="FHIR description: summary of the plan's scope and purpose.")
    start_date = models.DateField(null=True, blank=True, help_text="FHIR period.start: when the plan starts.")
    end_date = models.DateField(null=True, blank=True, help_text="FHIR period.end: when the plan ends.")
    author_display = models.CharField(max_length=255, blank=True, help_text="FHIR author: person or organization responsible for the plan.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional care plan comments.")
    conditions = models.ManyToManyField(Condition, blank=True, related_name="care_plans", help_text="FHIR addresses: conditions or concerns addressed by the plan.")
    care_teams = models.ManyToManyField(CareTeam, blank=True, related_name="care_plans", help_text="FHIR careTeam: teams involved in carrying out the plan.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Care Plan"
        verbose_name_plural = "Care Plans"

    def __str__(self):
        return self.title


class FamilyMemberHistory(models.Model):
    """FHIR FamilyMemberHistory: significant health conditions in a person related to the patient."""

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="family_member_histories",
        help_text="FHIR patient: the patient whose family history this record describes.",
    )
    conditions = models.ManyToManyField(
        Condition,
        blank=True,
        related_name="family_member_histories",
        help_text="FHIR condition: patient Condition records that help represent or match the family history.",
    )
    status = models.CharField(
        max_length=30,
        blank=True,
        help_text="FHIR status: partial, completed, entered-in-error, or health-unknown.",
    )
    relationship = models.CharField(max_length=255, help_text="FHIR relationship: how this relative is related to the patient.")
    sex = models.CharField(max_length=30, blank=True, help_text="FHIR sex: recorded sex of the family member.")
    born_date = models.DateField(null=True, blank=True, help_text="FHIR bornDate: actual or approximate birth date.")
    born_text = models.CharField(max_length=255, blank=True, help_text="FHIR bornString/Period: textual birth details.")
    age_text = models.CharField(max_length=255, blank=True, help_text="FHIR age[x]: age or age range at the time recorded.")
    estimated_age = models.BooleanField(default=False, help_text="FHIR estimatedAge: whether the age is approximate.")
    deceased = models.BooleanField(null=True, blank=True, help_text="FHIR deceasedBoolean: whether the relative is deceased.")
    deceased_date = models.DateField(null=True, blank=True, help_text="FHIR deceasedDate: date of death when known.")
    deceased_text = models.CharField(max_length=255, blank=True, help_text="FHIR deceased[x]: age, range, or text about death.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode/reasonReference: why this history was recorded.")
    notes = models.TextField(blank=True, help_text="FHIR note: general notes about the related person.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Family Member History"
        verbose_name_plural = "Family Member Histories"

    def __str__(self):
        return self.relationship


class FamilyMemberHistoryCondition(models.Model):
    """FHIR FamilyMemberHistory.condition: a condition the related person had."""

    family_member_history = models.ForeignKey(
        FamilyMemberHistory,
        on_delete=models.CASCADE,
        related_name="condition_links",
        help_text="The family member history record this condition belongs to.",
    )
    condition = models.ForeignKey(
        Condition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="family_history_condition_links",
        help_text="Optional matching local Condition record.",
    )
    condition_text = models.CharField(max_length=255, help_text="FHIR code: condition suffered by the family member.")
    outcome = models.CharField(max_length=255, blank=True, help_text="FHIR outcome: result such as death or disability.")
    contributed_to_death = models.BooleanField(
        null=True,
        blank=True,
        help_text="FHIR contributedToDeath: whether this condition contributed to death.",
    )
    onset_text = models.CharField(max_length=255, blank=True, help_text="FHIR onset[x]: when the condition first appeared.")
    notes = models.TextField(blank=True, help_text="FHIR note: extra notes about this specific family condition.")

    def __str__(self):
        return self.condition_text


class ClinicalImpression(models.Model):
    """FHIR ClinicalImpression: a clinician's assessment and synthesis of patient findings."""

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="clinical_impressions",
        help_text="FHIR subject: patient who was assessed.",
    )
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clinical_impressions",
        help_text="FHIR encounter: visit or encounter where the assessment occurred.",
    )
    assessor_practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clinical_impressions",
        help_text="FHIR assessor: clinician responsible for the assessment.",
    )
    assessor_role = models.ForeignKey(
        "PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clinical_impressions",
        help_text="FHIR assessor: practitioner role used when the assessor is represented by role.",
    )
    conditions = models.ManyToManyField(
        Condition,
        blank=True,
        related_name="clinical_impressions",
        help_text="FHIR finding/problem references resolved to local Condition records.",
    )
    observations = models.ManyToManyField(
        Observation,
        blank=True,
        related_name="clinical_impressions",
        help_text="FHIR finding/investigation references resolved to local Observation records.",
    )
    problems = models.ManyToManyField(
        Condition,
        blank=True,
        related_name="clinical_impression_problem_refs",
        help_text="FHIR problem: conditions or problems considered during the assessment.",
    )
    investigations_observations = models.ManyToManyField(
        Observation,
        blank=True,
        related_name="clinical_impression_investigations",
        help_text="FHIR investigation.item: observations reviewed as part of the assessment.",
    )
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: state of the assessment.")
    description = models.TextField(blank=True, help_text="FHIR description: why the assessment was performed.")
    effective_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text="FHIR effective[x]: time or period covered by the assessment.",
    )
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: when the assessment was made.")
    protocol = models.TextField(blank=True, help_text="FHIR protocol: clinical protocol or guideline followed.")
    summary = models.TextField(blank=True, help_text="FHIR summary: narrative summary of the assessment.")
    prognosis = models.TextField(blank=True, help_text="FHIR prognosisCodeableConcept/prognosisReference: expected outcome.")
    notes = models.TextField(blank=True, help_text="FHIR note: clinical notes about the impression.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Clinical Impression"
        verbose_name_plural = "Clinical Impressions"

    def __str__(self):
        return self.description or self.summary or f"Clinical Impression #{self.pk}"


class ClinicalImpressionFinding(models.Model):
    """FHIR ClinicalImpression.finding: a relevant condition, observation, or coded finding."""

    clinical_impression = models.ForeignKey(
        ClinicalImpression,
        on_delete=models.CASCADE,
        related_name="finding_links",
        help_text="The clinical impression this finding belongs to.",
    )
    condition = models.ForeignKey(
        Condition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clinical_impression_findings",
        help_text="FHIR finding.itemReference resolved to a local Condition.",
    )
    observation = models.ForeignKey(
        Observation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clinical_impression_findings",
        help_text="FHIR finding.itemReference resolved to a local Observation.",
    )
    finding_text = models.CharField(max_length=255, blank=True, help_text="FHIR finding.itemCodeableConcept or display text.")
    basis = models.TextField(blank=True, help_text="FHIR basis: reason this finding is relevant.")

    def __str__(self):
        return self.finding_text or str(self.condition or self.observation or f"Finding #{self.pk}")


class DiagnosticReport(models.Model):
    """FHIR DiagnosticReport: diagnostic report context, results, conclusions, and issued forms."""

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="diagnostic_reports",
        help_text="FHIR subject: patient who the report is about.",
    )
    encounter = models.ForeignKey(
        "Encounter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="diagnostic_reports",
        help_text="FHIR encounter: care event associated with the report.",
    )
    care_plans = models.ManyToManyField(
        "CarePlan",
        blank=True,
        related_name="diagnostic_reports",
        help_text="FHIR basedOn: care plans that requested or relate to this report.",
    )
    service_requests = models.ManyToManyField(
        "ServiceRequest",
        blank=True,
        related_name="diagnostic_reports",
        help_text="FHIR basedOn: service requests or orders this report fulfills.",
    )
    specimens = models.ManyToManyField(
        "Specimen",
        blank=True,
        related_name="diagnostic_reports",
        help_text="FHIR specimen: specimens the report is based on.",
    )
    observations = models.ManyToManyField(
        Observation,
        blank=True,
        related_name="diagnostic_reports",
        help_text="FHIR result: observations included as atomic report results.",
    )
    performers_practitioners = models.ManyToManyField(
        "Practitioner",
        blank=True,
        related_name="performed_diagnostic_reports",
        help_text="FHIR performer: practitioners responsible for issuing the report.",
    )
    performers_roles = models.ManyToManyField(
        "PractitionerRole",
        blank=True,
        related_name="performed_diagnostic_reports",
        help_text="FHIR performer: practitioner roles responsible for issuing the report.",
    )
    performers_organizations = models.ManyToManyField(
        "Organization",
        blank=True,
        related_name="performed_diagnostic_reports",
        help_text="FHIR performer: organizations responsible for issuing the report.",
    )
    performers_care_teams = models.ManyToManyField(
        "CareTeam",
        blank=True,
        related_name="performed_diagnostic_reports",
        help_text="FHIR performer: care teams responsible for issuing the report.",
    )
    interpreter_practitioners = models.ManyToManyField(
        "Practitioner",
        blank=True,
        related_name="interpreted_diagnostic_reports",
        help_text="FHIR resultsInterpreter: practitioners responsible for interpreting results.",
    )
    interpreter_roles = models.ManyToManyField(
        "PractitionerRole",
        blank=True,
        related_name="interpreted_diagnostic_reports",
        help_text="FHIR resultsInterpreter: practitioner roles responsible for interpreting results.",
    )
    interpreter_organizations = models.ManyToManyField(
        "Organization",
        blank=True,
        related_name="interpreted_diagnostic_reports",
        help_text="FHIR resultsInterpreter: organizations responsible for interpreting results.",
    )
    interpreter_care_teams = models.ManyToManyField(
        "CareTeam",
        blank=True,
        related_name="interpreted_diagnostic_reports",
        help_text="FHIR resultsInterpreter: care teams responsible for interpreting results.",
    )
    presented_documents = models.ManyToManyField(
        "documents.ClinicalDocument",
        blank=True,
        related_name="diagnostic_reports",
        help_text="FHIR presentedForm: documents created from attached issued report content.",
    )
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: registered, partial, preliminary, final, etc.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: diagnostic service section.")
    code = models.CharField(max_length=255, help_text="FHIR code: name or code for this diagnostic report.")
    effective_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text="FHIR effective[x]: clinically relevant date/time for the report.",
    )
    issued = models.DateTimeField(null=True, blank=True, help_text="FHIR issued: when this report version was released.")
    conclusion = models.TextField(blank=True, help_text="FHIR conclusion: clinical interpretation of test results.")
    conclusion_code = models.CharField(max_length=255, blank=True, help_text="FHIR conclusionCode: coded interpretation.")
    presented_form_summary = models.TextField(blank=True, help_text="FHIR presentedForm: summary of attachments that were not stored.")
    imaging_study_summary = models.TextField(blank=True, help_text="FHIR imagingStudy: unresolved imaging study references.")
    media_summary = models.TextField(blank=True, help_text="FHIR media: unresolved key image/media references.")
    notes = models.TextField(blank=True, help_text="FHIR note/text: additional imported report notes.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Diagnostic Report"
        verbose_name_plural = "Diagnostic Reports"

    def __str__(self):
        return self.code or f"Diagnostic Report #{self.pk}"


class DetectedIssue(models.Model):
    """FHIR DetectedIssue: an actual or potential clinical issue involving patient-specific actions."""

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="detected_issues",
        help_text="FHIR patient: patient whose care record contains the issue.",
    )
    author_practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="authored_detected_issues",
        help_text="FHIR author: practitioner who identified the issue.",
    )
    author_role = models.ForeignKey(
        "PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="authored_detected_issues",
        help_text="FHIR author: practitioner role that identified the issue.",
    )
    author_device = models.ForeignKey(
        "Device",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="authored_detected_issues",
        help_text="FHIR author: device or decision-support system that identified the issue.",
    )
    implicated_conditions = models.ManyToManyField(
        Condition,
        blank=True,
        related_name="detected_issue_implications",
        help_text="FHIR implicated: condition resources involved in the issue.",
    )
    implicated_medications = models.ManyToManyField(
        Medication,
        blank=True,
        related_name="detected_issue_implications",
        help_text="FHIR implicated: medication request/statement resources involved in the issue.",
    )
    implicated_immunizations = models.ManyToManyField(
        Immunization,
        blank=True,
        related_name="detected_issue_implications",
        help_text="FHIR implicated: immunizations involved in the issue.",
    )
    implicated_observations = models.ManyToManyField(
        Observation,
        blank=True,
        related_name="detected_issue_implications",
        help_text="FHIR implicated: observations involved in the issue.",
    )
    implicated_service_requests = models.ManyToManyField(
        "ServiceRequest",
        blank=True,
        related_name="detected_issue_implications",
        help_text="FHIR implicated: service requests or orders involved in the issue.",
    )
    implicated_procedures = models.ManyToManyField(
        "Procedure",
        blank=True,
        related_name="detected_issue_implications",
        help_text="FHIR implicated: procedures involved in the issue.",
    )
    implicated_devices = models.ManyToManyField(
        "Device",
        blank=True,
        related_name="detected_issue_implications",
        help_text="FHIR implicated: devices involved in the issue.",
    )
    implicated_diagnostic_reports = models.ManyToManyField(
        DiagnosticReport,
        blank=True,
        related_name="detected_issue_implications",
        help_text="FHIR implicated: diagnostic reports involved in the issue.",
    )
    evidence_observations = models.ManyToManyField(
        Observation,
        blank=True,
        related_name="detected_issue_evidence",
        help_text="FHIR evidence.detail: observations that support the detected issue.",
    )
    evidence_conditions = models.ManyToManyField(
        Condition,
        blank=True,
        related_name="detected_issue_evidence",
        help_text="FHIR evidence.detail: conditions that support the detected issue.",
    )
    evidence_diagnostic_reports = models.ManyToManyField(
        DiagnosticReport,
        blank=True,
        related_name="detected_issue_evidence",
        help_text="FHIR evidence.detail: diagnostic reports that support the detected issue.",
    )
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: registered, preliminary, final, etc.")
    code = models.CharField(max_length=255, blank=True, help_text="FHIR code: issue category such as duplicate therapy.")
    severity = models.CharField(max_length=30, blank=True, help_text="FHIR severity: high, moderate, or low.")
    identified_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text="FHIR identified[x]: when the issue was first identified.",
    )
    detail = models.TextField(blank=True, help_text="FHIR detail: description and context for the issue.")
    reference = models.URLField(blank=True, help_text="FHIR reference: authority or knowledge source for the issue.")
    evidence_summary = models.TextField(blank=True, help_text="FHIR evidence.code/detail: imported evidence summary.")
    mitigation_summary = models.TextField(blank=True, help_text="FHIR mitigation: steps taken to reduce or address the risk.")
    implicated_summary = models.TextField(blank=True, help_text="FHIR implicated: unresolved implicated resource references.")
    notes = models.TextField(blank=True, help_text="Additional imported issue notes.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Detected Issue"
        verbose_name_plural = "Detected Issues"

    def __str__(self):
        return self.code or self.detail or f"Detected Issue #{self.pk}"


# =============================================================================
# People And Groups
# FHIR Person, RelatedPerson, and Group identity/relationship resources.
# =============================================================================

class Person(models.Model):
    """FHIR Person: shared demographics and identity links across patient/practitioner/related-person roles."""

    managing_organization = models.ForeignKey(
        "Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_people",
        help_text="FHIR managingOrganization: custodian of the person record.",
    )
    active = models.BooleanField(default=True, help_text="FHIR active: whether this person record is in active use.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: name associated with the person.")
    gender = models.CharField(max_length=30, blank=True, help_text="FHIR gender: administrative gender.")
    birth_date = models.DateField(null=True, blank=True, help_text="FHIR birthDate: date the person was born.")
    phone = models.CharField(max_length=30, blank=True, help_text="FHIR telecom: phone contact.")
    email = models.EmailField(blank=True, help_text="FHIR telecom: email contact.")
    address = models.TextField(blank=True, help_text="FHIR address: one or more addresses for the person.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this person.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"

    def __str__(self):
        return self.name or f"Person #{self.pk}"


class PersonLink(models.Model):
    """FHIR Person.link: a role-specific resource believed to represent the same actual person."""

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="link_records", help_text="FHIR Person.link owner: shared Person identity record.")
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="person_identity_links",
        help_text="FHIR link.target: Patient resource believed to represent the same actual person.",
    )
    practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="person_identity_links",
        help_text="FHIR link.target: Practitioner resource believed to represent the same actual person.",
    )
    related_person = models.ForeignKey(
        "RelatedPerson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="person_identity_links",
        help_text="FHIR link.target: RelatedPerson resource believed to represent the same actual person.",
    )
    linked_person = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_from_person_records",
        help_text="FHIR link.target: another Person resource linked to this identity record.",
    )
    target_display = models.CharField(max_length=255, blank=True, help_text="FHIR link.target.display: imported display text for unresolved targets.")
    target_reference = models.CharField(max_length=255, blank=True, help_text="FHIR link.target.reference: original FHIR reference string.")
    assurance = models.CharField(max_length=30, blank=True, help_text="FHIR assurance: level1, level2, level3, or level4.")

    class Meta:
        verbose_name = "Person Link"
        verbose_name_plural = "Person Links"

    def __str__(self):
        target = self.patient or self.practitioner or self.related_person or self.linked_person or self.target_display
        return f"{self.person} -> {target or self.target_reference or 'linked resource'}"


class RelatedPerson(models.Model):
    """FHIR RelatedPerson: a person involved with a patient but not the direct target of care."""

    person = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_person_roles",
        help_text="Optional shared Person identity for this patient-specific related person role.",
    )
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="related_people",
        help_text="FHIR patient: the patient this person is related to.",
    )
    active = models.BooleanField(default=True, help_text="FHIR active: whether this related person record is in active use.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: name associated with the related person.")
    relationship = models.CharField(
        max_length=255,
        blank=True,
        help_text="FHIR relationship: spouse, parent, guardian, caregiver, friend, etc.",
    )
    gender = models.CharField(max_length=30, blank=True, help_text="FHIR gender: administrative gender.")
    birth_date = models.DateField(null=True, blank=True, help_text="FHIR birthDate: date the related person was born.")
    phone = models.CharField(max_length=30, blank=True, help_text="FHIR telecom: phone contact.")
    email = models.EmailField(blank=True, help_text="FHIR telecom: email contact.")
    address = models.TextField(blank=True, help_text="FHIR address: contact or visit address.")
    language = models.CharField(max_length=255, blank=True, help_text="FHIR communication.language: language used for health communication.")
    language_preferred = models.BooleanField(
        null=True,
        blank=True,
        help_text="FHIR communication.preferred: whether this language is preferred.",
    )
    period_start = models.DateField(null=True, blank=True, help_text="FHIR period.start: when this relationship became valid.")
    period_end = models.DateField(null=True, blank=True, help_text="FHIR period.end: when this relationship stopped being valid.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this related person.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Related Person"
        verbose_name_plural = "Related People"

    def __str__(self):
        parts = [self.name, self.relationship]
        return " - ".join(part for part in parts if part) or f"Related Person #{self.pk}"


class FHIRGroup(models.Model):
    """FHIR Group: a defined collection of people, practitioners, devices, medications, substances, or groups."""

    managing_organization = models.ForeignKey(
        "Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_groups",
        help_text="FHIR managingEntity: organization responsible for the group.",
    )
    managing_practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_groups",
        help_text="FHIR managingEntity: practitioner responsible for the group.",
    )
    managing_role = models.ForeignKey(
        "PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_groups",
        help_text="FHIR managingEntity: practitioner role responsible for the group.",
    )
    managing_related_person = models.ForeignKey(
        RelatedPerson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_groups",
        help_text="FHIR managingEntity: related person responsible for the group.",
    )
    active = models.BooleanField(default=True, help_text="FHIR active: whether this group record is in active use.")
    group_type = models.CharField(max_length=30, blank=True, help_text="FHIR type: person, practitioner, device, etc.")
    actual = models.BooleanField(default=True, help_text="FHIR actual: actual members vs intended/definitional group.")
    code = models.CharField(max_length=255, blank=True, help_text="FHIR code: kind of group members.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: human label for the group.")
    quantity = models.PositiveIntegerField(null=True, blank=True, help_text="FHIR quantity: number of members.")
    characteristic_summary = models.TextField(blank=True, help_text="FHIR characteristic: included/excluded member traits.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this group.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"

    def __str__(self):
        return self.name or self.code or f"Group #{self.pk}"


class FHIRGroupMember(models.Model):
    """FHIR Group.member: a resource that belongs or belonged to a group."""

    group = models.ForeignKey(FHIRGroup, on_delete=models.CASCADE, related_name="member_links", help_text="FHIR Group.member owner: group this member belongs to.")
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="group_memberships",
        help_text="FHIR member.entity: patient member.",
    )
    practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="group_memberships",
        help_text="FHIR member.entity: practitioner member.",
    )
    practitioner_role = models.ForeignKey(
        "PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="group_memberships",
        help_text="FHIR member.entity: practitioner role member.",
    )
    device = models.ForeignKey(
        "Device",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="group_memberships",
        help_text="FHIR member.entity: device member.",
    )
    medication = models.ForeignKey(
        Medication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="group_memberships",
        help_text="FHIR member.entity: medication member.",
    )
    member_group = models.ForeignKey(
        FHIRGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parent_group_memberships",
        help_text="FHIR member.entity: nested group member.",
    )
    entity_display = models.CharField(max_length=255, blank=True, help_text="FHIR member.entity.display: imported display text for unresolved members.")
    entity_reference = models.CharField(max_length=255, blank=True, help_text="FHIR member.entity.reference: original FHIR reference string.")
    start_date = models.DateField(null=True, blank=True, help_text="FHIR member.period.start: when group membership started.")
    end_date = models.DateField(null=True, blank=True, help_text="FHIR member.period.end: when group membership ended.")
    inactive = models.BooleanField(null=True, blank=True, help_text="FHIR member.inactive: whether this member is inactive in the group.")

    class Meta:
        verbose_name = "Group Member"
        verbose_name_plural = "Group Members"

    def __str__(self):
        member = (
            self.patient
            or self.practitioner
            or self.practitioner_role
            or self.device
            or self.medication
            or self.member_group
            or self.entity_display
        )
        return str(member or self.entity_reference or f"Group Member #{self.pk}")


# =============================================================================
# Assessment, Goals, And Requests
# Body structures, risk assessments, goals, device requests/use, and patient-facing care requests.
# =============================================================================

class BodyStructure(models.Model):
    """FHIR BodyStructure: anatomical location or structure relevant to care."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="body_structures", help_text="FHIR patient: patient this anatomical structure belongs to.")
    active = models.BooleanField(default=True, help_text="FHIR active: whether this body structure record is in active use.")
    morphology = models.CharField(max_length=255, blank=True, help_text="FHIR morphology: kind of structure or abnormality, such as tumor, wound, or surgical site.")
    location = models.CharField(max_length=255, blank=True, help_text="FHIR location: body site or anatomical location.")
    location_qualifier = models.CharField(max_length=255, blank=True, help_text="FHIR locationQualifier: laterality or relative location details.")
    description = models.TextField(blank=True, help_text="FHIR description: text description of the body structure.")
    image_summary = models.TextField(blank=True, help_text="FHIR image: summary of attached body-site images.")
    notes = models.TextField(blank=True, help_text="Additional imported body structure notes.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Body Structure"
        verbose_name_plural = "Body Structures"

    def __str__(self):
        return self.description or self.location or self.morphology or f"Body Structure #{self.pk}"


class RiskAssessment(models.Model):
    """FHIR RiskAssessment: quantified or qualitative risk estimate for a patient."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="risk_assessments", help_text="FHIR subject: patient or group whose risk is assessed.")
    encounter = models.ForeignKey(
        "Encounter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="risk_assessments",
        help_text="FHIR encounter: visit or encounter associated with the assessment.",
    )
    performer_practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_risk_assessments",
        help_text="FHIR performer: practitioner who performed the assessment.",
    )
    performer_role = models.ForeignKey(
        "PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_risk_assessments",
        help_text="FHIR performer: practitioner role that performed the assessment.",
    )
    performer_organization = models.ForeignKey(
        "Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_risk_assessments",
        help_text="FHIR performer: organization that performed the assessment.",
    )
    performer_device = models.ForeignKey(
        "Device",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_risk_assessments",
        help_text="FHIR performer: device or system that performed the assessment.",
    )
    conditions = models.ManyToManyField(Condition, blank=True, related_name="risk_assessments", help_text="FHIR basis: conditions used as evidence for the risk estimate.")
    observations = models.ManyToManyField(Observation, blank=True, related_name="risk_assessments", help_text="FHIR basis: observations used as evidence for the risk estimate.")
    diagnostic_reports = models.ManyToManyField(DiagnosticReport, blank=True, related_name="risk_assessments", help_text="FHIR basis: diagnostic reports used as evidence for the risk estimate.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: registered, preliminary, final, amended, or entered-in-error.")
    code = models.CharField(max_length=255, blank=True, help_text="FHIR code: type of risk being assessed.")
    method = models.CharField(max_length=255, blank=True, help_text="FHIR method: evaluation mechanism or algorithm used.")
    occurrence_datetime = models.DateTimeField(null=True, blank=True, help_text="FHIR occurrence[x]: when the assessment was performed.")
    authored_on = models.DateTimeField(null=True, blank=True, help_text="FHIR authoredOn: when the assessment was recorded.")
    prediction_summary = models.TextField(blank=True, help_text="FHIR prediction: outcome, probability, qualitative risk, timing, and rationale.")
    mitigation = models.TextField(blank=True, help_text="FHIR mitigation: how the risk may be reduced.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional risk assessment comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Risk Assessment"
        verbose_name_plural = "Risk Assessments"

    def __str__(self):
        return self.code or self.prediction_summary or f"Risk Assessment #{self.pk}"


class Goal(models.Model):
    """FHIR Goal: intended objective for patient, group, or care."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="goals", help_text="FHIR subject: patient this goal is for.")
    subject_group = models.ForeignKey(
        FHIRGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="goals",
        help_text="FHIR subject: group this goal is for, when not patient-specific.",
    )
    expressed_by_practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expressed_goals",
        help_text="FHIR expressedBy: practitioner who expressed or proposed the goal.",
    )
    expressed_by_role = models.ForeignKey(
        "PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expressed_goals",
        help_text="FHIR expressedBy: practitioner role that expressed or proposed the goal.",
    )
    expressed_by_related_person = models.ForeignKey(
        RelatedPerson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expressed_goals",
        help_text="FHIR expressedBy: related person who expressed or proposed the goal.",
    )
    addresses_conditions = models.ManyToManyField(Condition, blank=True, related_name="goals", help_text="FHIR addresses: conditions this goal addresses.")
    addresses_observations = models.ManyToManyField(Observation, blank=True, related_name="goals", help_text="FHIR addresses: observations this goal addresses.")
    addresses_medications = models.ManyToManyField(Medication, blank=True, related_name="goals", help_text="FHIR addresses: medications this goal addresses.")
    addresses_service_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="goals", help_text="FHIR addresses: service requests this goal addresses.")
    addresses_risk_assessments = models.ManyToManyField(RiskAssessment, blank=True, related_name="goals", help_text="FHIR addresses: risk assessments this goal addresses.")
    outcome_observations = models.ManyToManyField(Observation, blank=True, related_name="goal_outcomes", help_text="FHIR outcomeReference: observations documenting goal outcome.")
    lifecycle_status = models.CharField(max_length=30, blank=True, help_text="FHIR lifecycleStatus: proposed, planned, accepted, active, on-hold, completed, cancelled, etc.")
    achievement_status = models.CharField(max_length=255, blank=True, help_text="FHIR achievementStatus: in-progress, improving, worsening, achieved, not-achieved, etc.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: dietary, safety, behavioral, nursing, physiotherapy, etc.")
    priority = models.CharField(max_length=255, blank=True, help_text="FHIR priority: mutually agreed importance of achieving the goal.")
    description = models.CharField(max_length=255, help_text="FHIR description: desired objective or outcome.")
    start_date = models.DateField(null=True, blank=True, help_text="FHIR start[x]: when pursuit of the goal begins.")
    status_date = models.DateField(null=True, blank=True, help_text="FHIR statusDate: when the current status was established.")
    status_reason = models.TextField(blank=True, help_text="FHIR statusReason: reason for current lifecycle status.")
    target_summary = models.TextField(blank=True, help_text="FHIR target: target measure, detail, and due date/duration.")
    outcome_summary = models.TextField(blank=True, help_text="FHIR outcomeCode: coded outcome achieved or observed.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional goal comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Goal"
        verbose_name_plural = "Goals"

    def __str__(self):
        return self.description


class DeviceRequest(models.Model):
    """FHIR DeviceRequest: request/order for a device or device-related service."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="device_requests", help_text="FHIR subject: patient who needs or is prescribed the device.")
    encounter = models.ForeignKey(
        "Encounter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device_requests",
        help_text="FHIR encounter: visit or encounter where the device was requested.",
    )
    requester_practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_devices",
        help_text="FHIR requester: practitioner who initiated the device request.",
    )
    requester_role = models.ForeignKey(
        "PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_devices",
        help_text="FHIR requester: practitioner role that initiated the device request.",
    )
    devices = models.ManyToManyField("Device", blank=True, related_name="device_requests", help_text="FHIR codeReference: specific device being requested.")
    care_plans = models.ManyToManyField("CarePlan", blank=True, related_name="device_requests", help_text="FHIR basedOn: care plans this request fulfills or follows.")
    service_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="device_requests", help_text="FHIR basedOn: service requests this device request is based on.")
    replaces = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="replacement_device_requests", help_text="FHIR replaces: prior device requests replaced by this request.")
    conditions = models.ManyToManyField(Condition, blank=True, related_name="device_requests", help_text="FHIR reasonReference: conditions supporting the request.")
    observations = models.ManyToManyField(Observation, blank=True, related_name="device_requests", help_text="FHIR reasonReference: observations supporting the request.")
    diagnostic_reports = models.ManyToManyField(DiagnosticReport, blank=True, related_name="device_requests", help_text="FHIR reasonReference: diagnostic reports supporting the request.")
    risk_assessments = models.ManyToManyField(RiskAssessment, blank=True, related_name="device_requests", help_text="FHIR reasonReference: risk assessments supporting the request.")
    performers_practitioners = models.ManyToManyField(
        "Practitioner",
        blank=True,
        related_name="device_request_performances",
        help_text="FHIR performer: practitioners asked to fulfill the request.",
    )
    performers_roles = models.ManyToManyField(
        "PractitionerRole",
        blank=True,
        related_name="device_request_performances",
        help_text="FHIR performer: practitioner roles asked to fulfill the request.",
    )
    performers_organizations = models.ManyToManyField(
        "Organization",
        blank=True,
        related_name="device_request_performances",
        help_text="FHIR performer: organizations asked to fulfill the request.",
    )
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, on-hold, revoked, completed, entered-in-error, or unknown.")
    intent = models.CharField(max_length=30, blank=True, help_text="FHIR intent: proposal, plan, directive, order, original-order, etc.")
    priority = models.CharField(max_length=30, blank=True, help_text="FHIR priority: routine, urgent, asap, or stat.")
    code = models.CharField(max_length=255, help_text="FHIR code[x]: requested device, device type, or coded device request.")
    authored_on = models.DateTimeField(null=True, blank=True, help_text="FHIR authoredOn: when the request was created.")
    occurrence_start = models.DateTimeField(null=True, blank=True, help_text="FHIR occurrence[x]: requested start or occurrence time.")
    occurrence_end = models.DateTimeField(null=True, blank=True, help_text="FHIR occurrencePeriod.end: requested end time when a period is used.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode: coded reason for the device request.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional request comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Device Request"
        verbose_name_plural = "Device Requests"

    def __str__(self):
        return self.code


class DeviceUseStatement(models.Model):
    """FHIR DeviceUseStatement: record that a patient uses or used a device."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="device_use_statements", help_text="FHIR subject: patient who uses or used the device.")
    device = models.ForeignKey(
        "Device",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="use_statements",
        help_text="FHIR device: device being used.",
    )
    source_practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device_use_statements",
        help_text="FHIR source: practitioner who provided the statement.",
    )
    source_role = models.ForeignKey(
        "PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device_use_statements",
        help_text="FHIR source: practitioner role that provided the statement.",
    )
    source_related_person = models.ForeignKey(
        RelatedPerson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device_use_statements",
        help_text="FHIR source: related person who provided the statement.",
    )
    based_on_service_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="device_use_statements", help_text="FHIR basedOn: service requests this use statement fulfills or follows.")
    based_on_device_requests = models.ManyToManyField(DeviceRequest, blank=True, related_name="device_use_statements", help_text="FHIR basedOn: device requests this use statement fulfills or follows.")
    reason_conditions = models.ManyToManyField(Condition, blank=True, related_name="device_use_statements", help_text="FHIR reasonReference: conditions supporting device use.")
    reason_observations = models.ManyToManyField(Observation, blank=True, related_name="device_use_statements", help_text="FHIR reasonReference: observations supporting device use.")
    reason_diagnostic_reports = models.ManyToManyField(DiagnosticReport, blank=True, related_name="device_use_statements", help_text="FHIR reasonReference: diagnostic reports supporting device use.")
    reason_risk_assessments = models.ManyToManyField(RiskAssessment, blank=True, related_name="device_use_statements", help_text="FHIR reasonReference: risk assessments supporting device use.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, completed, entered-in-error, intended, stopped, or on-hold.")
    timing_start = models.DateTimeField(null=True, blank=True, help_text="FHIR timing[x]: when device use started or occurred.")
    timing_end = models.DateTimeField(null=True, blank=True, help_text="FHIR timingPeriod.end: when device use ended.")
    recorded_on = models.DateTimeField(null=True, blank=True, help_text="FHIR recordedOn: when the statement was recorded.")
    body_site = models.CharField(max_length=255, blank=True, help_text="FHIR bodySite: anatomical location where the device is used.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional device use comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Device Use Statement"
        verbose_name_plural = "Device Use Statements"

    def __str__(self):
        return str(self.device or f"Device Use Statement #{self.pk}")


# =============================================================================
# Medication, Nutrition, Communication, And Lists
# Medication catalog/activity resources plus nutrition orders, communications, flags, lists, and questionnaires.
# =============================================================================

class MedicationCatalog(models.Model):
    """FHIR Medication: medication definition/catalog details used by orders, statements, dispenses, and administrations."""

    manufacturer = models.ForeignKey(
        "Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="manufactured_medications",
        help_text="FHIR manufacturer: organization that manufactures the medication product.",
    )
    name = models.CharField(max_length=255, help_text="FHIR code: medication name or coded medication concept.")
    code = models.CharField(max_length=255, blank=True, help_text="FHIR code.coding: source code such as RxNorm, SNOMED CT, or local formulary code.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, inactive, or entered-in-error.")
    form = models.CharField(max_length=255, blank=True, help_text="FHIR form: powder, tablet, capsule, solution, etc.")
    amount = models.CharField(max_length=255, blank=True, help_text="FHIR amount: amount of drug in the package.")
    ingredient_summary = models.TextField(blank=True, help_text="FHIR ingredient: active/inactive ingredients and strengths.")
    batch_lot_number = models.CharField(max_length=255, blank=True, help_text="FHIR batch.lotNumber: assigned lot number.")
    batch_expiration_date = models.DateField(null=True, blank=True, help_text="FHIR batch.expirationDate: when this batch expires.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this medication definition.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Medication Catalog Item"
        verbose_name_plural = "Medication Catalog"

    def __str__(self):
        return self.name


class MedicationAdministration(models.Model):
    """FHIR MedicationAdministration: record of a medication being administered to a patient."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="medication_administrations", help_text="FHIR subject: patient who received the medication.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="medication_administrations", help_text="FHIR context: encounter associated with the administration.")
    medication = models.ForeignKey(Medication, on_delete=models.SET_NULL, null=True, blank=True, related_name="administrations", help_text="FHIR medication[x]: patient medication record when resolved locally.")
    medication_catalog = models.ForeignKey(MedicationCatalog, on_delete=models.SET_NULL, null=True, blank=True, related_name="administrations", help_text="FHIR medicationReference: catalog medication when resolved locally.")
    service_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="medication_administrations", help_text="FHIR request: medication/service request that authorized the administration.")
    reason_conditions = models.ManyToManyField(Condition, blank=True, related_name="medication_administrations", help_text="FHIR reasonReference: conditions explaining why medication was administered.")
    performer_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="medication_administrations", help_text="FHIR performer.actor: practitioner who administered or witnessed administration.")
    performer_role = models.ForeignKey("PractitionerRole", on_delete=models.SET_NULL, null=True, blank=True, related_name="medication_administrations", help_text="FHIR performer.actor: practitioner role involved in administration.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: in-progress, not-done, on-hold, completed, entered-in-error, stopped, or unknown.")
    medication_text = models.CharField(max_length=255, blank=True, help_text="FHIR medicationCodeableConcept/display: medication text when not linked.")
    effective_start = models.DateTimeField(null=True, blank=True, help_text="FHIR effective[x]: when administration started or occurred.")
    effective_end = models.DateTimeField(null=True, blank=True, help_text="FHIR effectivePeriod.end: when administration ended.")
    dosage_text = models.TextField(blank=True, help_text="FHIR dosage.text: administration dosage instructions.")
    route = models.CharField(max_length=255, blank=True, help_text="FHIR dosage.route: route of administration.")
    dose_value = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True, help_text="FHIR dosage.dose.value: amount administered.")
    dose_unit = models.CharField(max_length=50, blank=True, help_text="FHIR dosage.dose.unit/code: dose unit.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional medication administration comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Medication Administration"
        verbose_name_plural = "Medication Administrations"

    def __str__(self):
        return self.medication_text or str(self.medication or self.medication_catalog or f"Medication Administration #{self.pk}")


class MedicationDispense(models.Model):
    """FHIR MedicationDispense: record that medication was supplied or dispensed to a patient."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="medication_dispenses", help_text="FHIR subject: patient receiving the dispensed medication.")
    medication = models.ForeignKey(Medication, on_delete=models.SET_NULL, null=True, blank=True, related_name="dispenses", help_text="FHIR medication[x]: patient medication record when resolved locally.")
    medication_catalog = models.ForeignKey(MedicationCatalog, on_delete=models.SET_NULL, null=True, blank=True, related_name="dispenses", help_text="FHIR medicationReference: catalog medication when resolved locally.")
    authorizing_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="medication_dispenses", help_text="FHIR authorizingPrescription: orders authorizing the dispense.")
    performer_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="medication_dispenses", help_text="FHIR performer.actor: practitioner involved in dispensing.")
    performer_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="medication_dispenses", help_text="FHIR performer.actor: organization involved in dispensing.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: preparation, in-progress, cancelled, on-hold, completed, entered-in-error, stopped, or declined.")
    medication_text = models.CharField(max_length=255, blank=True, help_text="FHIR medicationCodeableConcept/display: medication text when not linked.")
    quantity = models.CharField(max_length=255, blank=True, help_text="FHIR quantity: amount dispensed.")
    days_supply = models.CharField(max_length=255, blank=True, help_text="FHIR daysSupply: number of days supplied.")
    when_prepared = models.DateTimeField(null=True, blank=True, help_text="FHIR whenPrepared: when medication was packaged/prepared.")
    when_handed_over = models.DateTimeField(null=True, blank=True, help_text="FHIR whenHandedOver: when medication was given to patient or representative.")
    dosage_instruction = models.TextField(blank=True, help_text="FHIR dosageInstruction: directions for patient use.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional medication dispense comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Medication Dispense"
        verbose_name_plural = "Medication Dispenses"

    def __str__(self):
        return self.medication_text or str(self.medication or self.medication_catalog or f"Medication Dispense #{self.pk}")


class NutritionOrder(models.Model):
    """FHIR NutritionOrder: diet, supplement, or enteral nutrition order for a patient."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="nutrition_orders", help_text="FHIR patient: patient who needs the nutrition order.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="nutrition_orders", help_text="FHIR encounter: encounter associated with the order.")
    orderer_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="nutrition_orders", help_text="FHIR orderer: practitioner who requested the order.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: proposed, draft, planned, requested, active, on-hold, completed, cancelled, or entered-in-error.")
    intent = models.CharField(max_length=30, blank=True, help_text="FHIR intent: proposal, plan, directive, order, etc.")
    date_time = models.DateTimeField(null=True, blank=True, help_text="FHIR dateTime: when the nutrition order was requested.")
    allergy_intolerance_summary = models.TextField(blank=True, help_text="FHIR allergyIntolerance: food or substance allergies considered by the order.")
    food_preference_summary = models.TextField(blank=True, help_text="FHIR foodPreferenceModifier: patient food preferences.")
    exclude_food_summary = models.TextField(blank=True, help_text="FHIR excludeFoodModifier: foods to exclude.")
    oral_diet_summary = models.TextField(blank=True, help_text="FHIR oralDiet: diet type, schedule, nutrients, texture, and fluid consistency.")
    supplement_summary = models.TextField(blank=True, help_text="FHIR supplement: oral nutrition supplements.")
    enteral_formula_summary = models.TextField(blank=True, help_text="FHIR enteralFormula: tube feeding formula and administration details.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional nutrition order comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Nutrition Order"
        verbose_name_plural = "Nutrition Orders"

    def __str__(self):
        return self.oral_diet_summary or self.supplement_summary or self.enteral_formula_summary or f"Nutrition Order #{self.pk}"


class Communication(models.Model):
    """FHIR Communication: record of information transmitted from sender to receiver."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="communications", help_text="FHIR subject: patient or group that is the focus of the message.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="communications", help_text="FHIR encounter: encounter associated with the communication.")
    sender_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_communications", help_text="FHIR sender: practitioner who sent the message.")
    sender_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_communications", help_text="FHIR sender: organization that sent the message.")
    sender_related_person = models.ForeignKey(RelatedPerson, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_communications", help_text="FHIR sender: related person who sent the message.")
    recipients_practitioners = models.ManyToManyField("Practitioner", blank=True, related_name="received_communications", help_text="FHIR recipient: practitioner recipients.")
    recipients_organizations = models.ManyToManyField("Organization", blank=True, related_name="received_communications", help_text="FHIR recipient: organization recipients.")
    recipients_related_people = models.ManyToManyField(RelatedPerson, blank=True, related_name="received_communications", help_text="FHIR recipient: related person recipients.")
    in_response_to = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="responses", help_text="FHIR inResponseTo: prior communications this replies to.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: preparation, in-progress, not-done, on-hold, stopped, completed, entered-in-error, or unknown.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: alert, notification, reminder, instruction, etc.")
    priority = models.CharField(max_length=30, blank=True, help_text="FHIR priority: routine, urgent, asap, or stat.")
    medium = models.CharField(max_length=255, blank=True, help_text="FHIR medium: communication channel such as phone, fax, email, or in person.")
    topic = models.CharField(max_length=255, blank=True, help_text="FHIR topic: purpose/content description.")
    sent = models.DateTimeField(null=True, blank=True, help_text="FHIR sent: when the message was sent.")
    received = models.DateTimeField(null=True, blank=True, help_text="FHIR received: when the message was received.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode: indication for the message.")
    payload_summary = models.TextField(blank=True, help_text="FHIR payload: message content or attachment/reference summary.")
    notes = models.TextField(blank=True, help_text="FHIR note: comments about the communication.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.topic or self.payload_summary[:80] or f"Communication #{self.pk}"


class CommunicationRequest(models.Model):
    """FHIR CommunicationRequest: request to convey information to one or more recipients."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="communication_requests", help_text="FHIR subject: patient or group that is the focus of the requested message.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="communication_requests", help_text="FHIR encounter: encounter associated with the request.")
    requester_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="communication_requests", help_text="FHIR requester: practitioner requesting communication.")
    sender_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="communication_requests_to_send", help_text="FHIR sender: practitioner expected to send the message.")
    recipients_practitioners = models.ManyToManyField("Practitioner", blank=True, related_name="communication_requests_to_receive", help_text="FHIR recipient: practitioner recipients.")
    recipients_related_people = models.ManyToManyField(RelatedPerson, blank=True, related_name="communication_requests_to_receive", help_text="FHIR recipient: related person recipients.")
    based_on_service_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="communication_requests", help_text="FHIR basedOn: service requests this communication request fulfills.")
    replaces = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="replacement_communication_requests", help_text="FHIR replaces: communication requests replaced by this one.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, on-hold, revoked, completed, entered-in-error, or unknown.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: message category.")
    priority = models.CharField(max_length=30, blank=True, help_text="FHIR priority: routine, urgent, asap, or stat.")
    medium = models.CharField(max_length=255, blank=True, help_text="FHIR medium: requested channel such as phone, fax, email, or in person.")
    authored_on = models.DateTimeField(null=True, blank=True, help_text="FHIR authoredOn: when the request was created.")
    occurrence_start = models.DateTimeField(null=True, blank=True, help_text="FHIR occurrence[x]: requested communication time or start.")
    occurrence_end = models.DateTimeField(null=True, blank=True, help_text="FHIR occurrencePeriod.end: requested end time when a period is used.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode: reason for requesting communication.")
    payload_summary = models.TextField(blank=True, help_text="FHIR payload: requested message content summary.")
    notes = models.TextField(blank=True, help_text="FHIR note: comments about the communication request.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.payload_summary[:80] or self.category or f"Communication Request #{self.pk}"


class Flag(models.Model):
    """FHIR Flag: warning, alert, or awareness note about a patient or record."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="flags", help_text="FHIR subject: patient this flag applies to.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="flags", help_text="FHIR encounter: encounter this flag applies to, when specific.")
    author_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="authored_flags", help_text="FHIR author: practitioner who created the flag.")
    author_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="authored_flags", help_text="FHIR author: organization that created the flag.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, inactive, or entered-in-error.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: clinical, administrative, behavioral, etc.")
    code = models.CharField(max_length=255, help_text="FHIR code: coded or textual alert/warning.")
    start_date = models.DateTimeField(null=True, blank=True, help_text="FHIR period.start: when the flag became active.")
    end_date = models.DateTimeField(null=True, blank=True, help_text="FHIR period.end: when the flag stopped being active.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this flag.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class FHIRList(models.Model):
    """FHIR List: curated or working collection of resources for a patient or workflow."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="fhir_lists", help_text="FHIR subject: patient or group that the list is about.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="fhir_lists", help_text="FHIR encounter: encounter associated with the list.")
    source_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="authored_fhir_lists", help_text="FHIR source: practitioner responsible for the list.")
    source_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="authored_fhir_lists", help_text="FHIR source: organization responsible for the list.")
    conditions = models.ManyToManyField(Condition, blank=True, related_name="fhir_lists", help_text="FHIR entry.item: condition records included in this list.")
    observations = models.ManyToManyField(Observation, blank=True, related_name="fhir_lists", help_text="FHIR entry.item: observation records included in this list.")
    medications = models.ManyToManyField(Medication, blank=True, related_name="fhir_lists", help_text="FHIR entry.item: medication request/statement records included in this list.")
    procedures = models.ManyToManyField("Procedure", blank=True, related_name="fhir_lists", help_text="FHIR entry.item: procedure records included in this list.")
    diagnostic_reports = models.ManyToManyField(DiagnosticReport, blank=True, related_name="fhir_lists", help_text="FHIR entry.item: diagnostic reports included in this list.")
    documents = models.ManyToManyField("documents.ClinicalDocument", blank=True, related_name="fhir_lists", help_text="FHIR entry.item: document references included in this list.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: current, retired, or entered-in-error.")
    mode = models.CharField(max_length=30, blank=True, help_text="FHIR mode: working, snapshot, or changes.")
    title = models.CharField(max_length=255, blank=True, help_text="FHIR title: human-readable list title.")
    code = models.CharField(max_length=255, blank=True, help_text="FHIR code: purpose of the list, such as medications, problems, or allergies.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: when the list was prepared.")
    ordered_by = models.CharField(max_length=255, blank=True, help_text="FHIR orderedBy: sort order used for list entries.")
    empty_reason = models.CharField(max_length=255, blank=True, help_text="FHIR emptyReason: why the list is empty.")
    entry_summary = models.TextField(blank=True, help_text="FHIR entry: unresolved or textual list entries.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this list.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FHIR List"
        verbose_name_plural = "FHIR Lists"

    def __str__(self):
        return self.title or self.code or f"FHIR List #{self.pk}"


class QuestionnaireResponse(models.Model):
    """FHIR QuestionnaireResponse: answers to a form, assessment, or questionnaire."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="questionnaire_responses", help_text="FHIR subject: patient or other subject the answers are about.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="questionnaire_responses", help_text="FHIR encounter: encounter associated with the response.")
    author_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="authored_questionnaire_responses", help_text="FHIR author: practitioner who recorded the answers.")
    source_patient = models.ForeignKey(PatientProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="sourced_questionnaire_responses", help_text="FHIR source: patient who supplied the answers.")
    source_related_person = models.ForeignKey(RelatedPerson, on_delete=models.SET_NULL, null=True, blank=True, related_name="sourced_questionnaire_responses", help_text="FHIR source: related person who supplied the answers.")
    based_on_service_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="questionnaire_responses", help_text="FHIR basedOn: orders or requests this response fulfills.")
    part_of_observations = models.ManyToManyField(Observation, blank=True, related_name="questionnaire_responses", help_text="FHIR partOf: observations this response is part of.")
    part_of_procedures = models.ManyToManyField("Procedure", blank=True, related_name="questionnaire_responses", help_text="FHIR partOf: procedures this response is part of.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: in-progress, completed, amended, entered-in-error, or stopped.")
    questionnaire = models.CharField(max_length=255, blank=True, help_text="FHIR questionnaire: canonical URL or identifier for the form definition.")
    authored = models.DateTimeField(null=True, blank=True, help_text="FHIR authored: when the answers were gathered.")
    item_summary = models.TextField(blank=True, help_text="FHIR item: question/answer summary.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this questionnaire response.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Questionnaire Response"
        verbose_name_plural = "Questionnaire Responses"

    def __str__(self):
        return self.questionnaire or f"Questionnaire Response #{self.pk}"


class ImmunizationRecommendation(models.Model):
    """FHIR ImmunizationRecommendation: forecast or recommendation for future immunizations."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="immunization_recommendations", help_text="FHIR patient: patient for whom vaccination is recommended.")
    authority = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="immunization_recommendations", help_text="FHIR authority: organization responsible for the recommendation.")
    supporting_immunizations = models.ManyToManyField(Immunization, blank=True, related_name="recommendations", help_text="FHIR recommendation.supportingImmunization: immunizations supporting the recommendation.")
    supporting_observations = models.ManyToManyField(Observation, blank=True, related_name="immunization_recommendations", help_text="FHIR recommendation.supportingPatientInformation: observations supporting the forecast.")
    supporting_diagnostic_reports = models.ManyToManyField(DiagnosticReport, blank=True, related_name="immunization_recommendations", help_text="FHIR recommendation.supportingPatientInformation: diagnostic reports supporting the forecast.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: when the recommendation was created.")
    vaccine_code = models.CharField(max_length=255, blank=True, help_text="FHIR recommendation.vaccineCode: vaccine product or type being recommended.")
    target_disease = models.CharField(max_length=255, blank=True, help_text="FHIR recommendation.targetDisease: disease the recommendation protects against.")
    forecast_status = models.CharField(max_length=255, blank=True, help_text="FHIR recommendation.forecastStatus: vaccination forecast status.")
    forecast_reason = models.CharField(max_length=255, blank=True, help_text="FHIR recommendation.forecastReason: reason for the forecast status.")
    date_criterion_summary = models.TextField(blank=True, help_text="FHIR recommendation.dateCriterion: dates such as earliest, recommended, overdue, or latest.")
    recommendation_summary = models.TextField(blank=True, help_text="FHIR recommendation: unresolved forecast details and dose series text.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this immunization recommendation.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Immunization Recommendation"
        verbose_name_plural = "Immunization Recommendations"

    def __str__(self):
        return self.vaccine_code or self.target_disease or f"Immunization Recommendation #{self.pk}"


# =============================================================================
# Care Directory And Clinical Activity
# Practitioner roles, service requests, episodes, adverse events, participants, practitioners, and procedures.
# =============================================================================

class PractitionerRole(models.Model):
    practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roles",
        help_text="FHIR practitioner: practitioner who can perform this role.",
    )
    organization = models.ForeignKey(
        "Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="practitioner_roles",
        help_text="FHIR organization: organization where the role applies.",
    )
    locations = models.ManyToManyField("Location", blank=True, related_name="practitioner_roles", help_text="FHIR location: locations where this role is available.")
    active = models.BooleanField(default=True, help_text="FHIR active: whether this role is active.")
    role = models.CharField(max_length=255, blank=True, help_text="FHIR code: role performed by the practitioner.")
    specialty = models.CharField(max_length=255, blank=True, help_text="FHIR specialty: specific specialty of the practitioner in this role.")
    start_date = models.DateField(null=True, blank=True, help_text="FHIR period.start: when this role became valid.")
    end_date = models.DateField(null=True, blank=True, help_text="FHIR period.end: when this role stopped being valid.")
    phone = models.CharField(max_length=30, blank=True, help_text="FHIR telecom: phone contact for this role.")
    email = models.EmailField(blank=True, help_text="FHIR telecom: email contact for this role.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this practitioner role.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Practitioner Role"
        verbose_name_plural = "Practitioner Roles"

    def __str__(self):
        parts = [str(part) for part in [self.practitioner, self.role, self.organization] if part]
        return " - ".join(parts) or f"Practitioner Role #{self.pk}"


class ServiceRequest(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="service_requests", help_text="FHIR subject: patient the service is requested for.")
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_requests",
        help_text="FHIR encounter: encounter where the request was created.",
    )
    requester_practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_services",
        help_text="FHIR requester: practitioner who requested the service.",
    )
    requester_role = models.ForeignKey(
        PractitionerRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_services",
        help_text="FHIR requester: practitioner role that requested the service.",
    )
    requester_organization = models.ForeignKey(
        "Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_services",
        help_text="FHIR requester: organization that requested the service.",
    )
    requester_device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_services",
        help_text="FHIR requester: device or system that requested the service.",
    )
    care_plans = models.ManyToManyField(CarePlan, blank=True, related_name="service_requests", help_text="FHIR basedOn: care plans this request fulfills or follows.")
    replaces = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="replacement_requests", help_text="FHIR replaces: service requests replaced by this one.")
    performers_practitioners = models.ManyToManyField(
        "Practitioner",
        blank=True,
        related_name="service_request_performances",
        help_text="FHIR performer: practitioners asked to perform the service.",
    )
    performers_roles = models.ManyToManyField(
        PractitionerRole,
        blank=True,
        related_name="service_request_performances",
        help_text="FHIR performer: practitioner roles asked to perform the service.",
    )
    performers_organizations = models.ManyToManyField(
        "Organization",
        blank=True,
        related_name="service_request_performances",
        help_text="FHIR performer: organizations asked to perform the service.",
    )
    performers_care_teams = models.ManyToManyField(CareTeam, blank=True, related_name="service_requests", help_text="FHIR performer: care teams asked to perform the service.")
    performers_devices = models.ManyToManyField(Device, blank=True, related_name="service_request_performances", help_text="FHIR performer: devices asked to perform the service.")
    locations = models.ManyToManyField("Location", blank=True, related_name="service_requests", help_text="FHIR locationReference: requested service locations.")
    conditions = models.ManyToManyField(Condition, blank=True, related_name="service_requests", help_text="FHIR reasonReference: conditions supporting the request.")
    specimens = models.ManyToManyField(Specimen, blank=True, related_name="service_requests", help_text="FHIR specimen: specimens relevant to the request.")
    name = models.CharField(max_length=255, help_text="FHIR code: service, order, procedure, or diagnostic request.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, on-hold, revoked, completed, entered-in-error, or unknown.")
    intent = models.CharField(max_length=30, blank=True, help_text="FHIR intent: proposal, plan, directive, order, original-order, etc.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: classification of service requested.")
    priority = models.CharField(max_length=30, blank=True, help_text="FHIR priority: routine, urgent, asap, or stat.")
    do_not_perform = models.BooleanField(default=False, help_text="FHIR doNotPerform: true when this is a request not to perform the service.")
    authored_on = models.DateTimeField(null=True, blank=True, help_text="FHIR authoredOn: when the request was signed or authored.")
    occurrence_start = models.DateTimeField(null=True, blank=True, help_text="FHIR occurrence[x]: requested start or occurrence time.")
    occurrence_end = models.DateTimeField(null=True, blank=True, help_text="FHIR occurrencePeriod.end: requested end time when a period is used.")
    performer_type = models.CharField(max_length=255, blank=True, help_text="FHIR performerType: requested performer type.")
    location_code = models.CharField(max_length=255, blank=True, help_text="FHIR locationCode: coded requested location.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode: coded reason for the request.")
    patient_instruction = models.TextField(blank=True, help_text="FHIR patientInstruction: instructions for the patient.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional service request comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service Request"
        verbose_name_plural = "Service Requests"

    def __str__(self):
        return self.name


class EpisodeOfCare(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="episodes_of_care", help_text="FHIR patient: patient whose care is grouped into this episode.")
    managing_organization = models.ForeignKey(
        "Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="episodes_of_care",
        help_text="FHIR managingOrganization: organization with care responsibility.",
    )
    care_manager_practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_episodes",
        help_text="FHIR careManager: practitioner coordinating the episode.",
    )
    care_manager_role = models.ForeignKey(
        PractitionerRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_episodes",
        help_text="FHIR careManager: practitioner role coordinating the episode.",
    )
    referral_requests = models.ManyToManyField(ServiceRequest, blank=True, related_name="episodes_of_care", help_text="FHIR referralRequest: referrals or requests initiating this episode.")
    care_teams = models.ManyToManyField(CareTeam, blank=True, related_name="episodes_of_care", help_text="FHIR team: care teams involved in this episode.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: planned, waitlist, active, onhold, finished, cancelled, etc.")
    episode_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: type of episode or care responsibility.")
    diagnosis_summary = models.TextField(blank=True, help_text="FHIR diagnosis: imported diagnosis/role/rank summary.")
    start_date = models.DateField(null=True, blank=True, help_text="FHIR period.start: start of episode responsibility.")
    end_date = models.DateField(null=True, blank=True, help_text="FHIR period.end: end of episode responsibility.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this episode of care.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Episode of Care"
        verbose_name_plural = "Episodes of Care"

    def __str__(self):
        return self.episode_type or f"Episode of Care #{self.pk}"


class AdverseEvent(models.Model):
    """FHIR AdverseEvent: an actual or potential harmful event involving a patient."""

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="adverse_events",
        help_text="FHIR subject: patient affected by the adverse event.",
    )
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="adverse_events",
        help_text="FHIR encounter: visit or encounter associated with the event.",
    )
    location = models.ForeignKey(
        "Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="adverse_events",
        help_text="FHIR location: where the event occurred.",
    )
    recorder_practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_adverse_events",
        help_text="FHIR recorder: person who recorded the event.",
    )
    recorder_role = models.ForeignKey(
        PractitionerRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_adverse_events",
        help_text="FHIR recorder: practitioner role used when the recorder is represented by role.",
    )
    resulting_conditions = models.ManyToManyField(
        Condition,
        blank=True,
        related_name="adverse_events",
        help_text="FHIR resultingCondition: conditions that resulted from the event.",
    )
    contributor_practitioners = models.ManyToManyField(
        "Practitioner",
        blank=True,
        related_name="adverse_event_contributions",
        help_text="FHIR contributor: practitioners involved in the event.",
    )
    contributor_roles = models.ManyToManyField(
        PractitionerRole,
        blank=True,
        related_name="adverse_event_contributions",
        help_text="FHIR contributor: practitioner roles involved in the event.",
    )
    contributor_devices = models.ManyToManyField(
        Device,
        blank=True,
        related_name="adverse_event_contributions",
        help_text="FHIR contributor: devices involved in the event.",
    )
    suspect_immunizations = models.ManyToManyField(
        Immunization,
        blank=True,
        related_name="suspected_adverse_events",
        help_text="FHIR suspectEntity.instance: immunizations suspected to have contributed.",
    )
    suspect_procedures = models.ManyToManyField(
        "Procedure",
        blank=True,
        related_name="suspected_adverse_events",
        help_text="FHIR suspectEntity.instance: procedures suspected to have contributed.",
    )
    suspect_medications = models.ManyToManyField(
        Medication,
        blank=True,
        related_name="suspected_adverse_events",
        help_text="FHIR suspectEntity.instance: medications suspected to have contributed.",
    )
    suspect_devices = models.ManyToManyField(
        Device,
        blank=True,
        related_name="suspected_adverse_events",
        help_text="FHIR suspectEntity.instance: devices suspected to have contributed.",
    )
    reference_documents = models.ManyToManyField(
        "documents.ClinicalDocument",
        blank=True,
        related_name="adverse_events",
        help_text="FHIR referenceDocument: documents relevant to the event.",
    )
    subject_medical_history_conditions = models.ManyToManyField(
        Condition,
        blank=True,
        related_name="adverse_event_medical_history_refs",
        help_text="FHIR subjectMedicalHistory: prior conditions relevant to the event.",
    )
    subject_medical_history_observations = models.ManyToManyField(
        Observation,
        blank=True,
        related_name="adverse_event_medical_history_refs",
        help_text="FHIR subjectMedicalHistory: prior observations relevant to the event.",
    )
    subject_medical_history_immunizations = models.ManyToManyField(
        Immunization,
        blank=True,
        related_name="adverse_event_medical_history_refs",
        help_text="FHIR subjectMedicalHistory: prior immunizations relevant to the event.",
    )
    subject_medical_history_procedures = models.ManyToManyField(
        "Procedure",
        blank=True,
        related_name="adverse_event_medical_history_refs",
        help_text="FHIR subjectMedicalHistory: prior procedures relevant to the event.",
    )
    actuality = models.CharField(max_length=30, blank=True, help_text="FHIR actuality: actual or potential adverse event.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: product-problem, product-quality, etc.")
    event = models.CharField(max_length=255, blank=True, help_text="FHIR event: type of adverse event.")
    event_date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: when the adverse event occurred.")
    detected_date = models.DateTimeField(null=True, blank=True, help_text="FHIR detected: when the event was detected.")
    recorded_date = models.DateTimeField(null=True, blank=True, help_text="FHIR recordedDate: when the event was recorded.")
    seriousness = models.CharField(max_length=255, blank=True, help_text="FHIR seriousness: serious, non-serious, etc.")
    severity = models.CharField(max_length=255, blank=True, help_text="FHIR severity: mild, moderate, severe, etc.")
    outcome = models.CharField(max_length=255, blank=True, help_text="FHIR outcome: result or final state of the event.")
    suspect_entity_summary = models.TextField(blank=True, help_text="FHIR suspectEntity: imported summary for unsupported suspects.")
    causality_summary = models.TextField(blank=True, help_text="FHIR causality: assessment of causality for suspect entities.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional event notes.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Adverse Event"
        verbose_name_plural = "Adverse Events"

    def __str__(self):
        return self.event or self.category or f"Adverse Event #{self.pk}"


class CareTeamParticipant(models.Model):
    care_team = models.ForeignKey(CareTeam, on_delete=models.CASCADE, related_name="participant_links", help_text="FHIR CareTeam.participant owner: care team this participant belongs to.")
    practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="care_team_participations",
        help_text="FHIR participant.member: practitioner participant.",
    )
    organization = models.ForeignKey(
        "Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="care_team_participations",
        help_text="FHIR participant.member: organization participant.",
    )
    location = models.ForeignKey(
        "Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="care_team_participations",
        help_text="FHIR participant.member: location participant.",
    )
    related_person = models.ForeignKey(
        RelatedPerson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="care_team_participations",
        help_text="FHIR participant.member: related person participant.",
    )
    role = models.CharField(max_length=255, blank=True, help_text="FHIR participant.role: role of this participant on the team.")
    member_display = models.CharField(max_length=255, blank=True, help_text="FHIR participant.member.display: imported participant display text.")
    member_reference = models.CharField(max_length=255, blank=True, help_text="FHIR participant.member.reference: original FHIR member reference.")
    on_behalf_of_display = models.CharField(max_length=255, blank=True, help_text="FHIR participant.onBehalfOf.display: organization represented by participant.")
    on_behalf_of_reference = models.CharField(max_length=255, blank=True, help_text="FHIR participant.onBehalfOf.reference: original FHIR onBehalfOf reference.")
    start_date = models.DateField(null=True, blank=True, help_text="FHIR participant.period.start: when participation started.")
    end_date = models.DateField(null=True, blank=True, help_text="FHIR participant.period.end: when participation ended.")

    class Meta:
        verbose_name = "Care Team Participant"
        verbose_name_plural = "Care Team Participants"

    def __str__(self):
        participant = self.practitioner or self.organization or self.location or self.related_person or self.member_display
        if self.role and participant:
            return f"{self.role}: {participant}"
        return str(participant or self.role or f"Participant #{self.pk}")


class Practitioner(models.Model):
    name = models.CharField(max_length=255, help_text="FHIR name: practitioner name.")
    npi = models.CharField(max_length=30, blank=True, help_text="FHIR identifier: National Provider Identifier when present.")
    active = models.BooleanField(default=True, help_text="FHIR active: whether the practitioner record is in active use.")
    qualification = models.CharField(max_length=255, blank=True, help_text="FHIR qualification.code: professional qualification or credential.")
    phone = models.CharField(max_length=30, blank=True, help_text="FHIR telecom: phone contact.")
    email = models.EmailField(blank=True, help_text="FHIR telecom: email contact.")
    address = models.TextField(blank=True, help_text="FHIR address: practitioner address.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this practitioner.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Procedure(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="procedures", help_text="FHIR subject: patient the procedure was performed on.")
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="procedures",
        help_text="FHIR encounter: encounter associated with the procedure.",
    )
    care_plans = models.ManyToManyField(CarePlan, blank=True, related_name="procedures", help_text="FHIR basedOn/partOf: care plans related to the procedure.")
    service_requests = models.ManyToManyField(ServiceRequest, blank=True, related_name="procedures", help_text="FHIR basedOn: service requests fulfilled by the procedure.")
    conditions = models.ManyToManyField(Condition, blank=True, related_name="procedures", help_text="FHIR reasonReference: conditions that explain why the procedure was performed.")
    name = models.CharField(max_length=255, help_text="FHIR code: procedure performed.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: preparation, in-progress, completed, stopped, entered-in-error, etc.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: broad classification of procedure.")
    performed_start = models.DateTimeField(null=True, blank=True, help_text="FHIR performed[x]: start or occurrence time.")
    performed_end = models.DateTimeField(null=True, blank=True, help_text="FHIR performedPeriod.end: end time when a period is used.")
    body_site = models.CharField(max_length=255, blank=True, help_text="FHIR bodySite: anatomical site where procedure was performed.")
    outcome = models.CharField(max_length=255, blank=True, help_text="FHIR outcome: result of the procedure.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode: coded reason for procedure.")
    location_display = models.CharField(max_length=255, blank=True, help_text="FHIR location: where procedure was performed.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional procedure comments.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProcedurePerformer(models.Model):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name="performer_links", help_text="FHIR Procedure.performer owner: procedure this performer belongs to.")
    practitioner = models.ForeignKey(
        Practitioner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="procedure_performances",
        help_text="FHIR performer.actor: practitioner who performed the procedure.",
    )
    organization = models.ForeignKey(
        "Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="procedure_performances",
        help_text="FHIR performer.actor/onBehalfOf: organization involved in the procedure.",
    )
    role = models.CharField(max_length=255, blank=True, help_text="FHIR performer.function: role or function of the performer.")
    actor_display = models.CharField(max_length=255, blank=True, help_text="FHIR performer.actor.display: imported performer display text.")
    actor_reference = models.CharField(max_length=255, blank=True, help_text="FHIR performer.actor.reference: original FHIR actor reference.")
    on_behalf_of_display = models.CharField(max_length=255, blank=True, help_text="FHIR performer.onBehalfOf.display: organization represented by actor.")
    on_behalf_of_reference = models.CharField(max_length=255, blank=True, help_text="FHIR performer.onBehalfOf.reference: original FHIR onBehalfOf reference.")

    class Meta:
        verbose_name = "Procedure Performer"
        verbose_name_plural = "Procedure Performers"

    def __str__(self):
        performer = self.practitioner or self.organization or self.actor_display
        if self.role and performer:
            return f"{self.role}: {performer}"
        return str(performer or self.role or f"Performer #{self.pk}")


# =============================================================================
# Insurance, Benefits, And Consent
# Insurance plans, coverages, EOBs, consents, eligibility, enrollment, payment notices, and reconciliation.
# =============================================================================

class InsurancePlan(models.Model):
    """FHIR InsurancePlan: insurer/product/plan definition offered by a payer."""

    owned_by = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_insurance_plans", help_text="FHIR ownedBy: organization that is legally responsible for the plan.")
    administered_by = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="administered_insurance_plans", help_text="FHIR administeredBy: organization that administers the plan.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    name = models.CharField(max_length=255, help_text="FHIR name: official plan or product name.")
    alias = models.CharField(max_length=255, blank=True, help_text="FHIR alias: alternate plan names.")
    plan_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: kind of insurance plan or product.")
    period_start = models.DateField(null=True, blank=True, help_text="FHIR period.start: when the plan is available or effective.")
    period_end = models.DateField(null=True, blank=True, help_text="FHIR period.end: when the plan availability/effectiveness ends.")
    coverage_area = models.TextField(blank=True, help_text="FHIR coverageArea: geographic areas covered by the plan.")
    contact_summary = models.TextField(blank=True, help_text="FHIR contact/telecom: plan contact details.")
    benefit_summary = models.TextField(blank=True, help_text="FHIR coverage/plan.specificCost/benefit: summarized benefits and plan cost details.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this insurance plan.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Insurance Plan"
        verbose_name_plural = "Insurance Plans"

    def __str__(self):
        return self.name


class Coverage(models.Model):
    """FHIR Coverage: insurance or self-pay coverage for a specific patient."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="coverages", help_text="FHIR beneficiary: patient covered by the policy or payment agreement.")
    insurer_plan = models.ForeignKey(InsurancePlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="coverages", help_text="FHIR insurancePlan extension/reference when resolved locally.")
    payor_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="coverages_as_payor", help_text="FHIR payor: insurer or organization issuing the coverage.")
    policy_holder_patient = models.ForeignKey(PatientProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="held_coverages", help_text="FHIR policyHolder: patient who owns the policy, when applicable.")
    subscriber_patient = models.ForeignKey(PatientProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="subscribed_coverages", help_text="FHIR subscriber: patient who subscribed to the policy, when applicable.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, cancelled, draft, or entered-in-error.")
    coverage_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: coverage category such as medical, dental, vision, accident, or self-pay.")
    subscriber_id = models.CharField(max_length=255, blank=True, help_text="FHIR subscriberId: insurer-assigned subscriber identifier.")
    dependent = models.CharField(max_length=255, blank=True, help_text="FHIR dependent: dependent number under the coverage.")
    relationship = models.CharField(max_length=255, blank=True, help_text="FHIR relationship: beneficiary relationship to subscriber.")
    period_start = models.DateField(null=True, blank=True, help_text="FHIR period.start: coverage start date.")
    period_end = models.DateField(null=True, blank=True, help_text="FHIR period.end: coverage end date.")
    order = models.PositiveIntegerField(null=True, blank=True, help_text="FHIR order: relative coordination order for active coverages.")
    network = models.CharField(max_length=255, blank=True, help_text="FHIR network: insurer-defined network name or identifier.")
    class_summary = models.TextField(blank=True, help_text="FHIR class: group, plan, subgroup, class, and other insurer classifications.")
    cost_summary = models.TextField(blank=True, help_text="FHIR costToBeneficiary: copay, deductible, coinsurance, and related patient cost details.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this coverage.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Coverage"
        verbose_name_plural = "Coverages"

    def __str__(self):
        return self.coverage_type or self.subscriber_id or f"Coverage #{self.pk}"


class ExplanationOfBenefit(models.Model):
    """FHIR ExplanationOfBenefit: adjudicated claim, EOB, or payer statement."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="explanation_of_benefits", help_text="FHIR patient: patient receiving products or services.")
    insurer = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="explanation_of_benefits", help_text="FHIR insurer: insurer responsible for the benefit statement.")
    provider_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="explanation_of_benefits", help_text="FHIR provider: practitioner responsible for services when resolved locally.")
    provider_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="provided_explanation_of_benefits", help_text="FHIR provider: organization responsible for services when resolved locally.")
    coverages = models.ManyToManyField(Coverage, blank=True, related_name="explanation_of_benefits", help_text="FHIR insurance.coverage: insurance coverages used in adjudication.")
    encounters = models.ManyToManyField(Encounter, blank=True, related_name="explanation_of_benefits", help_text="FHIR item.encounter: encounters associated with adjudicated line items.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, cancelled, draft, or entered-in-error.")
    eob_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: EOB/claim category such as institutional, oral, pharmacy, professional, or vision.")
    use = models.CharField(max_length=30, blank=True, help_text="FHIR use: claim, preauthorization, predetermination, or other use.")
    outcome = models.CharField(max_length=255, blank=True, help_text="FHIR outcome: queued, complete, error, partial, or other adjudication result.")
    disposition = models.TextField(blank=True, help_text="FHIR disposition: human-readable processing result.")
    billable_period_start = models.DateField(null=True, blank=True, help_text="FHIR billablePeriod.start: service billing period start.")
    billable_period_end = models.DateField(null=True, blank=True, help_text="FHIR billablePeriod.end: service billing period end.")
    created_date = models.DateField(null=True, blank=True, help_text="FHIR created: when the EOB was created.")
    total_summary = models.TextField(blank=True, help_text="FHIR total: benefit, allowed, submitted, patient responsibility, and payment totals.")
    diagnosis_summary = models.TextField(blank=True, help_text="FHIR diagnosis: diagnosis sequence, code, and package details.")
    item_summary = models.TextField(blank=True, help_text="FHIR item: adjudicated service/product line item details.")
    payment_summary = models.TextField(blank=True, help_text="FHIR payment: payment type, amount, date, and payee details.")
    notes = models.TextField(blank=True, help_text="FHIR processNote or imported source notes.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Explanation of Benefit"
        verbose_name_plural = "Explanations of Benefits"

    def __str__(self):
        return self.eob_type or self.outcome or f"Explanation of Benefit #{self.pk}"


class Consent(models.Model):
    """FHIR Consent: permission, denial, or consent directive for care, privacy, or procedures."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="consents", help_text="FHIR patient: patient or person whose consent is described.")
    organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="consents", help_text="FHIR organization: organization that manages or witnesses the consent.")
    performer_practitioners = models.ManyToManyField("Practitioner", blank=True, related_name="performed_consents", help_text="FHIR performer: practitioners who granted, acknowledged, or witnessed the consent.")
    source_documents = models.ManyToManyField("documents.ClinicalDocument", blank=True, related_name="consents", help_text="FHIR source[x]: signed or source documents for the consent.")
    related_immunizations = models.ManyToManyField(Immunization, blank=True, related_name="consents", help_text="Local link: vaccine records associated with this consent when source references can be resolved.")
    questionnaire_responses = models.ManyToManyField(QuestionnaireResponse, blank=True, related_name="consents", help_text="Local link: questionnaire responses used as consent/intake evidence.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, proposed, active, rejected, inactive, entered-in-error.")
    scope = models.CharField(max_length=255, blank=True, help_text="FHIR scope: privacy, treatment, research, advance care planning, or other consent scope.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: consent category such as treatment, information access, or procedure consent.")
    policy_rule = models.CharField(max_length=255, blank=True, help_text="FHIR policyRule: regulation or policy basis for the consent.")
    start_date = models.DateTimeField(null=True, blank=True, help_text="FHIR provision.period.start: when consent permission/denial becomes effective.")
    end_date = models.DateTimeField(null=True, blank=True, help_text="FHIR provision.period.end: when consent permission/denial ends.")
    decision = models.CharField(max_length=30, blank=True, help_text="FHIR provision.type: permit or deny.")
    provision_summary = models.TextField(blank=True, help_text="FHIR provision: actors, actions, classes, codes, purposes, and periods.")
    verification_summary = models.TextField(blank=True, help_text="FHIR verification: verification status, verifier, and verification date.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this consent.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Consent"
        verbose_name_plural = "Consents"

    def __str__(self):
        return self.category or self.scope or f"Consent #{self.pk}"


# =============================================================================
# Media, Documents, Infrastructure, And Scheduling
# Media/imaging/genomics, document/security infrastructure, endpoint/service definitions, scheduling, tasks, and audit records.
# =============================================================================

class Media(models.Model):
    """FHIR Media: clinical photo, video, audio, or imaging attachment metadata."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="media_records", help_text="FHIR subject: patient or other subject the media records.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="media_records", help_text="FHIR encounter: encounter associated with the media.")
    operator_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="operated_media", help_text="FHIR operator: practitioner who generated or collected the media.")
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, blank=True, related_name="media_records", help_text="FHIR device: observing or capture device.")
    based_on_service_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="media_records", help_text="FHIR basedOn: service requests fulfilled by the media.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: preparation, in-progress, not-done, on-hold, stopped, completed, entered-in-error, or unknown.")
    media_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: image, video, audio, or other media category.")
    modality = models.CharField(max_length=255, blank=True, help_text="FHIR modality: acquisition equipment/process or DICOM modality.")
    view = models.CharField(max_length=255, blank=True, help_text="FHIR view: imaging view/projection.")
    created_datetime = models.DateTimeField(null=True, blank=True, help_text="FHIR created[x]: when the media was collected.")
    issued = models.DateTimeField(null=True, blank=True, help_text="FHIR issued: when this media version was made available.")
    body_site = models.CharField(max_length=255, blank=True, help_text="FHIR bodySite: observed body part.")
    device_name = models.CharField(max_length=255, blank=True, help_text="FHIR deviceName: capture device/manufacturer name.")
    content_title = models.CharField(max_length=255, blank=True, help_text="FHIR content.title: attachment title.")
    content_type = models.CharField(max_length=255, blank=True, help_text="FHIR content.contentType: attachment MIME type.")
    content_url = models.TextField(blank=True, help_text="FHIR content.url: external media URL.")
    dimension_summary = models.CharField(max_length=255, blank=True, help_text="FHIR height/width/frames/duration: media dimensions or duration.")
    notes = models.TextField(blank=True, help_text="FHIR note: comments about the media.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Media"
        verbose_name_plural = "Media"

    def __str__(self):
        return self.content_title or self.media_type or f"Media #{self.pk}"


class ImagingStudy(models.Model):
    """FHIR ImagingStudy: DICOM study/series/instance imaging metadata."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="imaging_studies", help_text="FHIR subject: patient imaged in the study.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="imaging_studies", help_text="FHIR encounter: encounter associated with the imaging study.")
    endpoint_organizations = models.ManyToManyField("Organization", blank=True, related_name="imaging_studies", help_text="FHIR endpoint: organizations/endpoints associated with image access when resolved locally.")
    based_on_service_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="imaging_studies", help_text="FHIR basedOn: orders or requests that caused the study.")
    referrer_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="referred_imaging_studies", help_text="FHIR referrer: referring practitioner.")
    interpreter_practitioners = models.ManyToManyField("Practitioner", blank=True, related_name="interpreted_imaging_studies", help_text="FHIR interpreter: practitioners who interpreted the study.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: registered, available, cancelled, entered-in-error, unknown, etc.")
    started = models.DateTimeField(null=True, blank=True, help_text="FHIR started: when the study started.")
    modality_summary = models.TextField(blank=True, help_text="FHIR modality/series.modality: modalities used in the study.")
    procedure_code = models.CharField(max_length=255, blank=True, help_text="FHIR procedureCode: procedure performed for the study.")
    location_display = models.CharField(max_length=255, blank=True, help_text="FHIR location: where the study occurred.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode: reason for the study.")
    description = models.TextField(blank=True, help_text="FHIR description: study description.")
    series_summary = models.TextField(blank=True, help_text="FHIR series/instance: summarized DICOM series and image instances.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this imaging study.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Imaging Study"
        verbose_name_plural = "Imaging Studies"

    def __str__(self):
        return self.description or self.procedure_code or f"Imaging Study #{self.pk}"


class MolecularSequence(models.Model):
    """FHIR MolecularSequence: raw or interpreted DNA/RNA/protein sequence information."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="molecular_sequences", help_text="FHIR patient: patient whose sequence is described.")
    specimen = models.ForeignKey(Specimen, on_delete=models.SET_NULL, null=True, blank=True, related_name="molecular_sequences", help_text="FHIR specimen: specimen used for sequencing.")
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, blank=True, related_name="molecular_sequences", help_text="FHIR device: device used to generate sequence data.")
    performer_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="molecular_sequences", help_text="FHIR performer: organization that performed sequencing.")
    sequence_type = models.CharField(max_length=30, blank=True, help_text="FHIR type: aa, dna, or rna.")
    coordinate_system = models.PositiveIntegerField(null=True, blank=True, help_text="FHIR coordinateSystem: 0-based or 1-based coordinate system.")
    observed_sequence = models.TextField(blank=True, help_text="FHIR observedSeq: observed sequence string.")
    reference_sequence_summary = models.TextField(blank=True, help_text="FHIR referenceSeq: reference sequence details.")
    variant_summary = models.TextField(blank=True, help_text="FHIR variant: variant start/end, observed allele, reference allele, and cigar.")
    repository_summary = models.TextField(blank=True, help_text="FHIR repository: external sequence repositories.")
    quality_summary = models.TextField(blank=True, help_text="FHIR quality: sequence quality metrics.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this molecular sequence.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Molecular Sequence"
        verbose_name_plural = "Molecular Sequences"

    def __str__(self):
        return self.sequence_type or f"Molecular Sequence #{self.pk}"


class MedicationKnowledge(models.Model):
    """FHIR MedicationKnowledge: drug knowledge, monographs, costs, monitoring, and guidelines."""

    medication = models.ForeignKey(MedicationCatalog, on_delete=models.SET_NULL, null=True, blank=True, related_name="knowledge_records", help_text="FHIR code/reference: medication concept this knowledge describes when resolved locally.")
    associated_medications = models.ManyToManyField(MedicationCatalog, blank=True, related_name="associated_knowledge_records", help_text="FHIR associatedMedication: related medication definitions.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, inactive, or entered-in-error.")
    code = models.CharField(max_length=255, blank=True, help_text="FHIR code: medication or product concept.")
    dose_form = models.CharField(max_length=255, blank=True, help_text="FHIR doseForm: powder, tablet, capsule, solution, etc.")
    amount = models.CharField(max_length=255, blank=True, help_text="FHIR amount: amount of drug in package.")
    synonym = models.TextField(blank=True, help_text="FHIR synonym: alternate medication names.")
    product_type = models.CharField(max_length=255, blank=True, help_text="FHIR productType: category of medication product.")
    ingredient_summary = models.TextField(blank=True, help_text="FHIR ingredient: ingredients and strengths.")
    contraindication_summary = models.TextField(blank=True, help_text="FHIR contraindication: contraindicated conditions or use contexts.")
    monitoring_summary = models.TextField(blank=True, help_text="FHIR monitoringProgram: recommended monitoring programs.")
    medicine_classification_summary = models.TextField(blank=True, help_text="FHIR medicineClassification: drug class/category details.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this medication knowledge.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Medication Knowledge"
        verbose_name_plural = "Medication Knowledge"

    def __str__(self):
        return self.code or str(self.medication or f"Medication Knowledge #{self.pk}")


class ImmunizationEvaluation(models.Model):
    """FHIR ImmunizationEvaluation: evaluation of whether a vaccine dose is valid for a target disease."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="immunization_evaluations", help_text="FHIR patient: patient whose immunization was evaluated.")
    immunization = models.ForeignKey(Immunization, on_delete=models.SET_NULL, null=True, blank=True, related_name="evaluations", help_text="FHIR immunizationEvent: immunization being evaluated.")
    authority = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="immunization_evaluations", help_text="FHIR authority: organization responsible for the evaluation.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: completed or entered-in-error.")
    target_disease = models.CharField(max_length=255, blank=True, help_text="FHIR targetDisease: disease protected against.")
    dose_status = models.CharField(max_length=255, blank=True, help_text="FHIR doseStatus: valid or not valid dose status.")
    dose_status_reason = models.CharField(max_length=255, blank=True, help_text="FHIR doseStatusReason: reason for dose status.")
    description = models.TextField(blank=True, help_text="FHIR description: evaluation description.")
    series = models.CharField(max_length=255, blank=True, help_text="FHIR series: vaccine series name.")
    dose_number = models.CharField(max_length=50, blank=True, help_text="FHIR doseNumber[x]: dose number within the series.")
    series_doses = models.CharField(max_length=50, blank=True, help_text="FHIR seriesDoses[x]: recommended number of doses.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this immunization evaluation.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Immunization Evaluation"
        verbose_name_plural = "Immunization Evaluations"

    def __str__(self):
        return self.target_disease or self.dose_status or f"Immunization Evaluation #{self.pk}"


class VisionPrescription(models.Model):
    """FHIR VisionPrescription: authorization for glasses or contact lenses."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="vision_prescriptions", help_text="FHIR patient: patient the vision prescription is for.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="vision_prescriptions", help_text="FHIR encounter: encounter where the prescription was created.")
    prescriber_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="vision_prescriptions", help_text="FHIR prescriber: practitioner who authorized the prescription.")
    prescriber_role = models.ForeignKey("PractitionerRole", on_delete=models.SET_NULL, null=True, blank=True, related_name="vision_prescriptions", help_text="FHIR prescriber: practitioner role that authorized the prescription.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, cancelled, draft, or entered-in-error.")
    created_datetime = models.DateTimeField(null=True, blank=True, help_text="FHIR created: response creation date.")
    date_written = models.DateTimeField(null=True, blank=True, help_text="FHIR dateWritten: when the prescription was authorized.")
    lens_summary = models.TextField(blank=True, help_text="FHIR lensSpecification: product, eye, power, sphere, cylinder, axis, prism, brand, and notes.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this vision prescription.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vision Prescription"
        verbose_name_plural = "Vision Prescriptions"

    def __str__(self):
        return self.status or f"Vision Prescription #{self.pk}"


class RequestGroup(models.Model):
    """FHIR RequestGroup: coordinated collection of requests or actions."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="request_groups", help_text="FHIR subject: patient or group the request group applies to.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="request_groups", help_text="FHIR encounter: encounter associated with the request group.")
    author_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="authored_request_groups", help_text="FHIR author: practitioner who authored the request group.")
    based_on_service_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="request_groups", help_text="FHIR basedOn: requests this group fulfills or follows.")
    replaces = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="replacement_request_groups", help_text="FHIR replaces: request groups replaced by this one.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, on-hold, revoked, completed, entered-in-error, or unknown.")
    intent = models.CharField(max_length=30, blank=True, help_text="FHIR intent: proposal, plan, directive, order, etc.")
    priority = models.CharField(max_length=30, blank=True, help_text="FHIR priority: routine, urgent, asap, or stat.")
    code = models.CharField(max_length=255, blank=True, help_text="FHIR code: request group code or title.")
    authored_on = models.DateTimeField(null=True, blank=True, help_text="FHIR authoredOn: when the group was authored.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode: reason for the request group.")
    action_summary = models.TextField(blank=True, help_text="FHIR action: grouped action details, conditions, timing, participants, and resources.")
    notes = models.TextField(blank=True, help_text="FHIR note: additional request group comments.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Request Group"
        verbose_name_plural = "Request Groups"

    def __str__(self):
        return self.code or f"Request Group #{self.pk}"


class GuidanceResponse(models.Model):
    """FHIR GuidanceResponse: decision-support response for a patient or workflow."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="guidance_responses", help_text="FHIR subject: patient or group the guidance is about.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="guidance_responses", help_text="FHIR encounter: encounter associated with the guidance.")
    performer_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="guidance_responses", help_text="FHIR performer: organization or service that generated the guidance.")
    request_identifier = models.CharField(max_length=255, blank=True, help_text="FHIR requestIdentifier: identifier of the request that initiated guidance.")
    module_uri = models.TextField(blank=True, help_text="FHIR module[x]: decision support module URI/canonical/code.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: success, data-requested, data-required, in-progress, failure, or entered-in-error.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode: reason for guidance.")
    occurrence_datetime = models.DateTimeField(null=True, blank=True, help_text="FHIR occurrenceDateTime: when guidance was processed.")
    output_parameters = models.TextField(blank=True, help_text="FHIR outputParameters: output parameters or reference summary.")
    result_summary = models.TextField(blank=True, help_text="FHIR result: resulting plan, request group, or other guidance output.")
    data_requirement_summary = models.TextField(blank=True, help_text="FHIR dataRequirement: data needed by the guidance service.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this guidance response.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Guidance Response"
        verbose_name_plural = "Guidance Responses"

    def __str__(self):
        return self.module_uri or self.status or f"Guidance Response #{self.pk}"


class SupplyRequest(models.Model):
    """FHIR SupplyRequest: request for medication, device, or supply movement."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="supply_requests", help_text="FHIR deliverTo/patient context: patient associated with the supply request when known.")
    requester_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="supply_requests", help_text="FHIR requester: practitioner requesting the supply.")
    requester_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="supply_requests", help_text="FHIR requester: organization requesting the supply.")
    supplier_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="supplied_requests", help_text="FHIR supplier: requested supply organization.")
    deliver_to_location = models.ForeignKey("Location", on_delete=models.SET_NULL, null=True, blank=True, related_name="supply_requests", help_text="FHIR deliverTo: requested delivery location.")
    based_on_service_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="supply_requests", help_text="FHIR basedOn: service requests this supply request follows.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, suspended, cancelled, completed, entered-in-error, unknown.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: supply category.")
    priority = models.CharField(max_length=30, blank=True, help_text="FHIR priority: routine, urgent, asap, or stat.")
    item = models.CharField(max_length=255, help_text="FHIR item[x]: medication, substance, device, or supply item requested.")
    quantity = models.CharField(max_length=255, blank=True, help_text="FHIR quantity: amount requested.")
    authored_on = models.DateTimeField(null=True, blank=True, help_text="FHIR authoredOn: when the supply request was created.")
    occurrence_start = models.DateTimeField(null=True, blank=True, help_text="FHIR occurrence[x]: requested supply time or period start.")
    occurrence_end = models.DateTimeField(null=True, blank=True, help_text="FHIR occurrencePeriod.end: requested supply period end.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode: why the supply is requested.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this supply request.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Supply Request"
        verbose_name_plural = "Supply Requests"

    def __str__(self):
        return self.item


class SupplyDelivery(models.Model):
    """FHIR SupplyDelivery: record of supply delivery/dispense."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="supply_deliveries", help_text="FHIR patient: patient for whom the item is supplied.")
    based_on_supply_requests = models.ManyToManyField(SupplyRequest, blank=True, related_name="supply_deliveries", help_text="FHIR basedOn: supply requests fulfilled by this delivery.")
    part_of_deliveries = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="child_supply_deliveries", help_text="FHIR partOf: larger supply deliveries this delivery is part of.")
    supplier_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="supply_deliveries", help_text="FHIR supplier: practitioner responsible for delivery.")
    supplier_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="supply_deliveries", help_text="FHIR supplier: organization responsible for delivery.")
    destination = models.ForeignKey("Location", on_delete=models.SET_NULL, null=True, blank=True, related_name="supply_deliveries", help_text="FHIR destination: where the supply was sent.")
    receivers = models.ManyToManyField("Practitioner", blank=True, related_name="received_supply_deliveries", help_text="FHIR receiver: practitioners who collected the supply.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: in-progress, completed, abandoned, or entered-in-error.")
    delivery_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: category of dispense event.")
    item = models.CharField(max_length=255, blank=True, help_text="FHIR suppliedItem.item[x]: medication, substance, device, or supply delivered.")
    quantity = models.CharField(max_length=255, blank=True, help_text="FHIR suppliedItem.quantity: amount delivered.")
    occurrence_start = models.DateTimeField(null=True, blank=True, help_text="FHIR occurrence[x]: delivery time or period start.")
    occurrence_end = models.DateTimeField(null=True, blank=True, help_text="FHIR occurrencePeriod.end: delivery period end.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this supply delivery.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Supply Delivery"
        verbose_name_plural = "Supply Deliveries"

    def __str__(self):
        return self.item or f"Supply Delivery #{self.pk}"


class Provenance(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="provenance_records", help_text="FHIR patient compartment: patient associated with the provenance targets or agents, when known.")
    location = models.ForeignKey("Location", on_delete=models.SET_NULL, null=True, blank=True, related_name="provenance_records", help_text="FHIR location: where the activity occurred.")
    target_summary = models.TextField(blank=True, help_text="FHIR target: resources this provenance statement describes.")
    activity = models.CharField(max_length=255, blank=True, help_text="FHIR activity: activity that occurred.")
    occurred_start = models.DateTimeField(null=True, blank=True, help_text="FHIR occurred[x]: when the activity started or occurred.")
    occurred_end = models.DateTimeField(null=True, blank=True, help_text="FHIR occurredPeriod.end: when the activity ended.")
    recorded = models.DateTimeField(null=True, blank=True, help_text="FHIR recorded: when the activity was recorded.")
    policy = models.TextField(blank=True, help_text="FHIR policy: policies or plans defining the activity.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reason: reason the activity occurred.")
    agent_summary = models.TextField(blank=True, help_text="FHIR agent: people, organizations, systems, or devices involved.")
    entity_summary = models.TextField(blank=True, help_text="FHIR entity: source or derived entities used in the activity.")
    signature_summary = models.TextField(blank=True, help_text="FHIR signature: digital signatures on the provenance target.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this provenance record.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Provenance"
        verbose_name_plural = "Provenance"

    def __str__(self):
        return self.activity or f"Provenance #{self.pk}"


class Composition(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="compositions", help_text="FHIR subject: patient or subject of the composition.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="compositions", help_text="FHIR encounter: clinical encounter associated with the composition.")
    custodian = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="compositions", help_text="FHIR custodian: organization maintaining the composition.")
    authors_practitioners = models.ManyToManyField("Practitioner", blank=True, related_name="authored_compositions", help_text="FHIR author: practitioner authors.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: preliminary, final, amended, or entered-in-error.")
    composition_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: kind of composition/document.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: categorization of composition.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-readable composition title.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: when composition was edited.")
    confidentiality = models.CharField(max_length=30, blank=True, help_text="FHIR confidentiality: confidentiality code.")
    section_summary = models.TextField(blank=True, help_text="FHIR section: section titles, codes, text, and entries.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this composition.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class DocumentManifest(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="document_manifests", help_text="FHIR subject: patient or subject of documents in the manifest.")
    author_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="document_manifests", help_text="FHIR author: practitioner who authored the manifest.")
    source = models.CharField(max_length=255, blank=True, help_text="FHIR source: source system/application/actor.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: current, superseded, or entered-in-error.")
    manifest_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: kind of document set.")
    created_datetime = models.DateTimeField(null=True, blank=True, help_text="FHIR created: when the manifest was created.")
    description = models.TextField(blank=True, help_text="FHIR description: human-readable manifest description.")
    content_summary = models.TextField(blank=True, help_text="FHIR content: document references included in the manifest.")
    related_summary = models.TextField(blank=True, help_text="FHIR related: related identifiers or resources.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this document manifest.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description or self.manifest_type or f"Document Manifest #{self.pk}"


class BinaryResource(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="binary_resources", help_text="Local patient association when binary content can be tied to a patient.")
    content_type = models.CharField(max_length=255, help_text="FHIR contentType: MIME type of the binary content.")
    security_context = models.CharField(max_length=255, blank=True, help_text="FHIR securityContext: resource whose access rules apply.")
    data_size = models.PositiveIntegerField(null=True, blank=True, help_text="FHIR data: decoded byte count when inline data was supplied.")
    data_hash = models.CharField(max_length=64, blank=True, help_text="FHIR data: SHA-256 hash of decoded inline binary content.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this binary resource.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Binary Resource"
        verbose_name_plural = "Binary Resources"

    def __str__(self):
        return self.content_type or f"Binary #{self.pk}"


class Endpoint(models.Model):
    managing_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="endpoints", help_text="FHIR managingOrganization: organization that manages the endpoint.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, suspended, error, off, entered-in-error, or test.")
    connection_type = models.CharField(max_length=255, blank=True, help_text="FHIR connectionType: protocol/profile used by the endpoint.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: endpoint name.")
    payload_type = models.TextField(blank=True, help_text="FHIR payloadType: payload types supported.")
    payload_mime_type = models.CharField(max_length=255, blank=True, help_text="FHIR payloadMimeType: MIME types supported.")
    address = models.TextField(blank=True, help_text="FHIR address: technical endpoint address.")
    header_summary = models.TextField(blank=True, help_text="FHIR header: headers required by endpoint.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this endpoint.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.address or f"Endpoint #{self.pk}"


class HealthcareService(models.Model):
    provided_by = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="healthcare_services", help_text="FHIR providedBy: organization providing the service.")
    locations = models.ManyToManyField("Location", blank=True, related_name="healthcare_services", help_text="FHIR location: locations where service is available.")
    endpoints = models.ManyToManyField(Endpoint, blank=True, related_name="healthcare_services", help_text="FHIR endpoint: technical endpoints for the service.")
    active = models.BooleanField(default=True, help_text="FHIR active: whether this service record is active.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: broad service category.")
    service_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: specific service type.")
    specialty = models.CharField(max_length=255, blank=True, help_text="FHIR specialty: specialty that performs the service.")
    name = models.CharField(max_length=255, help_text="FHIR name: healthcare service name.")
    comment = models.TextField(blank=True, help_text="FHIR comment: extra details about the service.")
    telecom = models.TextField(blank=True, help_text="FHIR telecom: service contact details.")
    availability_summary = models.TextField(blank=True, help_text="FHIR availableTime/notAvailable: service availability.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this healthcare service.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OrganizationAffiliation(models.Model):
    organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="affiliations", help_text="FHIR organization: primary organization where role is available.")
    participating_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="participating_affiliations", help_text="FHIR participatingOrganization: organization providing/performing the role.")
    networks = models.ManyToManyField("Organization", blank=True, related_name="network_affiliations", help_text="FHIR network: provider networks for this affiliation.")
    locations = models.ManyToManyField("Location", blank=True, related_name="organization_affiliations", help_text="FHIR location: locations for this affiliation.")
    healthcare_services = models.ManyToManyField(HealthcareService, blank=True, related_name="organization_affiliations", help_text="FHIR healthcareService: services provided through this affiliation.")
    endpoints = models.ManyToManyField(Endpoint, blank=True, related_name="organization_affiliations", help_text="FHIR endpoint: technical endpoints for this affiliation.")
    active = models.BooleanField(default=True, help_text="FHIR active: whether this affiliation is active.")
    start_date = models.DateField(null=True, blank=True, help_text="FHIR period.start: affiliation start date.")
    end_date = models.DateField(null=True, blank=True, help_text="FHIR period.end: affiliation end date.")
    role = models.CharField(max_length=255, blank=True, help_text="FHIR code: role played by the participating organization.")
    specialty = models.CharField(max_length=255, blank=True, help_text="FHIR specialty: specific specialty in this role.")
    telecom = models.TextField(blank=True, help_text="FHIR telecom: contact details relevant to this affiliation.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this organization affiliation.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.role or f"Organization Affiliation #{self.pk}"


class Substance(models.Model):
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, inactive, or entered-in-error.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: substance category.")
    code = models.CharField(max_length=255, help_text="FHIR code: substance code or name.")
    description = models.TextField(blank=True, help_text="FHIR description: substance description.")
    instance_summary = models.TextField(blank=True, help_text="FHIR instance: batch, quantity, and expiry details.")
    ingredient_summary = models.TextField(blank=True, help_text="FHIR ingredient: component substances and quantities.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this substance.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class DeviceMetric(models.Model):
    source = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, blank=True, related_name="source_metrics", help_text="FHIR source: device this metric belongs to.")
    parent = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, blank=True, related_name="child_metrics", help_text="FHIR parent: parent device/component.")
    metric_type = models.CharField(max_length=255, help_text="FHIR type: metric identity, such as heart rate or PEEP setting.")
    unit = models.CharField(max_length=255, blank=True, help_text="FHIR unit: unit of measure for this metric.")
    operational_status = models.CharField(max_length=30, blank=True, help_text="FHIR operationalStatus: on, off, standby, entered-in-error.")
    color = models.CharField(max_length=30, blank=True, help_text="FHIR color: display color for the metric.")
    category = models.CharField(max_length=30, blank=True, help_text="FHIR category: measurement, setting, calculation, or unspecified.")
    calibration_summary = models.TextField(blank=True, help_text="FHIR calibration: type, state, and time of calibration.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this device metric.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.metric_type


class Schedule(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="schedules", help_text="FHIR actor: patient actor when the schedule is for a patient.")
    actors_practitioners = models.ManyToManyField("Practitioner", blank=True, related_name="schedules", help_text="FHIR actor: practitioner actors.")
    actors_locations = models.ManyToManyField("Location", blank=True, related_name="schedules", help_text="FHIR actor: location actors.")
    actors_healthcare_services = models.ManyToManyField(HealthcareService, blank=True, related_name="schedules", help_text="FHIR actor: healthcare service actors.")
    active = models.BooleanField(default=True, help_text="FHIR active: whether schedule is active.")
    service_category = models.CharField(max_length=255, blank=True, help_text="FHIR serviceCategory: broad service category.")
    service_type = models.CharField(max_length=255, blank=True, help_text="FHIR serviceType: specific service type.")
    specialty = models.CharField(max_length=255, blank=True, help_text="FHIR specialty: specialty for schedule.")
    planning_horizon_start = models.DateTimeField(null=True, blank=True, help_text="FHIR planningHorizon.start: schedule planning start.")
    planning_horizon_end = models.DateTimeField(null=True, blank=True, help_text="FHIR planningHorizon.end: schedule planning end.")
    comment = models.TextField(blank=True, help_text="FHIR comment: comments about availability.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.service_type or self.service_category or f"Schedule #{self.pk}"


class Slot(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True, related_name="slots", help_text="FHIR schedule: schedule this slot belongs to.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: busy, free, busy-unavailable, busy-tentative, entered-in-error.")
    service_category = models.CharField(max_length=255, blank=True, help_text="FHIR serviceCategory: broad service category.")
    service_type = models.CharField(max_length=255, blank=True, help_text="FHIR serviceType: specific service type.")
    specialty = models.CharField(max_length=255, blank=True, help_text="FHIR specialty: specialty for slot.")
    appointment_type = models.CharField(max_length=255, blank=True, help_text="FHIR appointmentType: style of appointment.")
    start_time = models.DateTimeField(null=True, blank=True, help_text="FHIR start: slot start instant.")
    end_time = models.DateTimeField(null=True, blank=True, help_text="FHIR end: slot end instant.")
    overbooked = models.BooleanField(default=False, help_text="FHIR overbooked: whether slot has overbooked appointments.")
    comment = models.TextField(blank=True, help_text="FHIR comment: comments on slot.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.status or 'Slot'} {self.start_time or ''}".strip()


class Appointment(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="appointments", help_text="FHIR participant.actor: patient participant when present.")
    slots = models.ManyToManyField(Slot, blank=True, related_name="appointments", help_text="FHIR slot: slots that provide availability.")
    participants_practitioners = models.ManyToManyField("Practitioner", blank=True, related_name="appointments", help_text="FHIR participant.actor: practitioner participants.")
    participants_locations = models.ManyToManyField("Location", blank=True, related_name="appointments", help_text="FHIR participant.actor: location participants.")
    based_on_service_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="appointments", help_text="FHIR basedOn: service requests fulfilled by appointment.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: proposed, pending, booked, arrived, fulfilled, cancelled, etc.")
    cancelation_reason = models.CharField(max_length=255, blank=True, help_text="FHIR cancelationReason: reason appointment was cancelled.")
    service_category = models.CharField(max_length=255, blank=True, help_text="FHIR serviceCategory: broad service category.")
    service_type = models.CharField(max_length=255, blank=True, help_text="FHIR serviceType: specific service type.")
    appointment_type = models.CharField(max_length=255, blank=True, help_text="FHIR appointmentType: type/style of appointment.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reasonCode: reason for appointment.")
    description = models.TextField(blank=True, help_text="FHIR description: appointment description.")
    start_time = models.DateTimeField(null=True, blank=True, help_text="FHIR start: appointment start instant.")
    end_time = models.DateTimeField(null=True, blank=True, help_text="FHIR end: appointment end instant.")
    minutes_duration = models.PositiveIntegerField(null=True, blank=True, help_text="FHIR minutesDuration: expected duration in minutes.")
    participant_summary = models.TextField(blank=True, help_text="FHIR participant: participant statuses and displays.")
    comment = models.TextField(blank=True, help_text="FHIR comment/patientInstruction: appointment comments or patient instructions.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description or self.appointment_type or f"Appointment #{self.pk}"


class AppointmentResponse(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name="responses", help_text="FHIR appointment: appointment being responded to.")
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="appointment_responses", help_text="FHIR actor: patient actor when patient responds.")
    actor_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="appointment_responses", help_text="FHIR actor: practitioner actor when practitioner responds.")
    actor_location = models.ForeignKey("Location", on_delete=models.SET_NULL, null=True, blank=True, related_name="appointment_responses", help_text="FHIR actor: location actor when location responds.")
    participant_status = models.CharField(max_length=30, blank=True, help_text="FHIR participantStatus: accepted, declined, tentative, needs-action.")
    participant_type = models.CharField(max_length=255, blank=True, help_text="FHIR participantType: role of participant.")
    start_time = models.DateTimeField(null=True, blank=True, help_text="FHIR start: proposed/actual participant start.")
    end_time = models.DateTimeField(null=True, blank=True, help_text="FHIR end: proposed/actual participant end.")
    comment = models.TextField(blank=True, help_text="FHIR comment: participant response comment.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.participant_status or f"Appointment Response #{self.pk}"


class Task(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="tasks", help_text="FHIR for/focus context: patient associated with the task when known.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks", help_text="FHIR encounter: healthcare event associated with the task.")
    owner_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_tasks", help_text="FHIR owner: practitioner responsible for task.")
    owner_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_tasks", help_text="FHIR owner: organization responsible for task.")
    based_on_service_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="tasks", help_text="FHIR basedOn: requests this task fulfills.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, requested, accepted, in-progress, completed, failed, etc.")
    intent = models.CharField(max_length=30, blank=True, help_text="FHIR intent: unknown, proposal, plan, order, original-order, etc.")
    priority = models.CharField(max_length=30, blank=True, help_text="FHIR priority: routine, urgent, asap, or stat.")
    code = models.CharField(max_length=255, blank=True, help_text="FHIR code: task type.")
    description = models.TextField(blank=True, help_text="FHIR description: task description.")
    authored_on = models.DateTimeField(null=True, blank=True, help_text="FHIR authoredOn: when task was created.")
    last_modified = models.DateTimeField(null=True, blank=True, help_text="FHIR lastModified: when task was last changed.")
    execution_start = models.DateTimeField(null=True, blank=True, help_text="FHIR executionPeriod.start: task execution start.")
    execution_end = models.DateTimeField(null=True, blank=True, help_text="FHIR executionPeriod.end: task execution end.")
    input_summary = models.TextField(blank=True, help_text="FHIR input: task input parameters.")
    output_summary = models.TextField(blank=True, help_text="FHIR output: task output parameters.")
    notes = models.TextField(blank=True, help_text="FHIR note: task comments.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code or self.description or f"Task #{self.pk}"
class AuditEvent(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="audit_events", help_text="Local patient association when the audit event references a patient.")
    recorded = models.DateTimeField(null=True, blank=True, help_text="FHIR recorded: when the activity was recorded.")
    audit_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: identifier for the category of event.")
    subtype = models.CharField(max_length=255, blank=True, help_text="FHIR subtype: more specific event type.")
    action = models.CharField(max_length=30, blank=True, help_text="FHIR action: create, read, update, delete, execute, etc.")
    outcome = models.CharField(max_length=30, blank=True, help_text="FHIR outcome: success, minor failure, serious failure, or major failure.")
    outcome_description = models.TextField(blank=True, help_text="FHIR outcomeDesc: description of the outcome.")
    agent_summary = models.TextField(blank=True, help_text="FHIR agent: people, systems, or organizations involved in the event.")
    source_observer = models.CharField(max_length=255, blank=True, help_text="FHIR source.observer: system or actor reporting the event.")
    source_type = models.CharField(max_length=255, blank=True, help_text="FHIR source.type: type of audit source.")
    entity_summary = models.TextField(blank=True, help_text="FHIR entity: data or objects involved in the event.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this audit event.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.audit_type or self.action or f"Audit Event #{self.pk}"

# =============================================================================
# Billing And Research
# Accounts, claims, invoices, charge items, and research resources.
# =============================================================================

class Account(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="accounts", help_text="FHIR subject: patient or other party the account tracks.")
    owner = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_accounts", help_text="FHIR owner: organization responsible for tracking the account.")
    coverages = models.ManyToManyField("Coverage", blank=True, related_name="accounts", help_text="FHIR coverage.coverage: insurance coverages associated with the account.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, inactive, entered-in-error, or on-hold.")
    account_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: categorization of the account.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: human-readable account name.")
    description = models.TextField(blank=True, help_text="FHIR description: account description.")
    service_period_start = models.DateField(null=True, blank=True, help_text="FHIR servicePeriod.start: start of account coverage/service dates.")
    service_period_end = models.DateField(null=True, blank=True, help_text="FHIR servicePeriod.end: end of account coverage/service dates.")
    guarantor_summary = models.TextField(blank=True, help_text="FHIR guarantor: parties responsible for account balances.")
    balance_summary = models.TextField(blank=True, help_text="FHIR balance: account balances by term/type.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this account.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.account_type or f"Account #{self.pk}"


class Claim(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="claims", help_text="FHIR patient: patient receiving products or services.")
    insurer = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="claims_as_insurer", help_text="FHIR insurer: target insurer for adjudication.")
    provider_practitioner = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="claims_as_provider", help_text="FHIR provider: practitioner responsible for the claim when present.")
    provider_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="claims_as_provider", help_text="FHIR provider: organization responsible for the claim when present.")
    coverages = models.ManyToManyField("Coverage", blank=True, related_name="claims", help_text="FHIR insurance.coverage: coverages used for this claim.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, cancelled, draft, or entered-in-error.")
    claim_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: category of claim, such as institutional, oral, pharmacy, or professional.")
    use = models.CharField(max_length=30, blank=True, help_text="FHIR use: claim, preauthorization, predetermination, etc.")
    priority = models.CharField(max_length=255, blank=True, help_text="FHIR priority: desired processing priority.")
    billable_period_start = models.DateField(null=True, blank=True, help_text="FHIR billablePeriod.start: beginning of service billing period.")
    billable_period_end = models.DateField(null=True, blank=True, help_text="FHIR billablePeriod.end: end of service billing period.")
    created_date = models.DateField(null=True, blank=True, help_text="FHIR created: claim creation date.")
    diagnosis_summary = models.TextField(blank=True, help_text="FHIR diagnosis: diagnosis codes or references on the claim.")
    item_summary = models.TextField(blank=True, help_text="FHIR item: claim line items, products/services, quantities, and net amounts.")
    insurance_summary = models.TextField(blank=True, help_text="FHIR insurance: claim insurance sequence, focal status, and coverage displays.")
    total = models.CharField(max_length=255, blank=True, help_text="FHIR total: total claim amount.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this claim.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.claim_type or self.use or f"Claim #{self.pk}"


class ClaimResponse(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="claim_responses", help_text="FHIR patient: patient associated with the claim response.")
    request_claim = models.ForeignKey(Claim, on_delete=models.SET_NULL, null=True, blank=True, related_name="responses", help_text="FHIR request: claim this response adjudicates.")
    insurer = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="claim_responses", help_text="FHIR insurer: party responsible for adjudication.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, cancelled, draft, or entered-in-error.")
    response_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: claim response category.")
    use = models.CharField(max_length=30, blank=True, help_text="FHIR use: claim, preauthorization, predetermination, etc.")
    outcome = models.CharField(max_length=30, blank=True, help_text="FHIR outcome: queued, complete, error, or partial.")
    disposition = models.TextField(blank=True, help_text="FHIR disposition: disposition message from adjudication.")
    created_date = models.DateField(null=True, blank=True, help_text="FHIR created: response creation date.")
    item_summary = models.TextField(blank=True, help_text="FHIR item/addItem: adjudication line summary.")
    total_summary = models.TextField(blank=True, help_text="FHIR total: adjudication totals by category.")
    payment_summary = models.TextField(blank=True, help_text="FHIR payment: payment type, amount, and date.")
    error_summary = models.TextField(blank=True, help_text="FHIR error: adjudication errors.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this claim response.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.response_type or self.outcome or f"Claim Response #{self.pk}"


class Invoice(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="invoices", help_text="FHIR subject/recipient: patient associated with the invoice when present.")
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices", help_text="FHIR account: account that tracks this invoice.")
    issuer_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="issued_invoices", help_text="FHIR issuer: organization issuing the invoice.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, issued, balanced, cancelled, or entered-in-error.")
    invoice_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: invoice type.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: when the invoice was issued.")
    participant_summary = models.TextField(blank=True, help_text="FHIR participant: parties involved in invoice creation or processing.")
    line_item_summary = models.TextField(blank=True, help_text="FHIR lineItem: charges included in the invoice.")
    total_net = models.CharField(max_length=255, blank=True, help_text="FHIR totalNet: net invoice amount.")
    total_gross = models.CharField(max_length=255, blank=True, help_text="FHIR totalGross: gross invoice amount.")
    payment_terms = models.TextField(blank=True, help_text="FHIR paymentTerms: payment timing or terms.")
    notes = models.TextField(blank=True, help_text="FHIR note: invoice notes.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_type or self.status or f"Invoice #{self.pk}"


class ChargeItem(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="charge_items", help_text="FHIR subject: patient associated with the charge.")
    encounter = models.ForeignKey("Encounter", on_delete=models.SET_NULL, null=True, blank=True, related_name="charge_items", help_text="FHIR context: encounter associated with the charge.")
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name="charge_items", help_text="FHIR account: account this charge belongs to.")
    service_requests = models.ManyToManyField("ServiceRequest", blank=True, related_name="charge_items", help_text="FHIR service: service requests represented by this charge.")
    performer_practitioners = models.ManyToManyField("Practitioner", blank=True, related_name="charge_items", help_text="FHIR performer.actor: practitioners involved with the charge.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: planned, billable, not-billable, aborted, billed, or entered-in-error.")
    code = models.CharField(max_length=255, help_text="FHIR code: charge item code.")
    occurrence_datetime = models.DateTimeField(null=True, blank=True, help_text="FHIR occurrence[x]: when charge item occurred.")
    quantity = models.CharField(max_length=255, blank=True, help_text="FHIR quantity: quantity of service/product.")
    factor_override = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True, help_text="FHIR factorOverride: multiplying factor override.")
    price_override = models.CharField(max_length=255, blank=True, help_text="FHIR priceOverride: price override.")
    total_price_component = models.TextField(blank=True, help_text="FHIR totalPriceComponent: total price components.")
    reason = models.CharField(max_length=255, blank=True, help_text="FHIR reason: coded reason for charge.")
    notes = models.TextField(blank=True, help_text="FHIR note: charge comments.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code or f"Charge Item #{self.pk}"
class ResearchStudy(models.Model):
    sponsor = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="sponsored_research_studies", help_text="FHIR sponsor: organization responsible for study initiation/management.")
    principal_investigator = models.ForeignKey("Practitioner", on_delete=models.SET_NULL, null=True, blank=True, related_name="research_studies", help_text="FHIR principalInvestigator: investigator responsible for the study.")
    sites = models.ManyToManyField("Location", blank=True, related_name="research_studies", help_text="FHIR site: locations where the study is conducted.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, administratively-completed, approved, closed-to-accrual, completed, etc.")
    title = models.CharField(max_length=255, blank=True, help_text="FHIR title: human-readable study title.")
    phase = models.CharField(max_length=255, blank=True, help_text="FHIR phase: phase of the study.")
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: study category.")
    focus = models.TextField(blank=True, help_text="FHIR focus: drugs, devices, conditions, or other focus codes.")
    condition = models.TextField(blank=True, help_text="FHIR condition: conditions being studied.")
    contact_summary = models.TextField(blank=True, help_text="FHIR contact: study contact details.")
    period_start = models.DateField(null=True, blank=True, help_text="FHIR period.start: study start date.")
    period_end = models.DateField(null=True, blank=True, help_text="FHIR period.end: study end date.")
    description = models.TextField(blank=True, help_text="FHIR description: study description.")
    notes = models.TextField(blank=True, help_text="FHIR note: study notes.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Research Study #{self.pk}"


class ResearchSubject(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="research_subjects", help_text="FHIR individual: patient participating in the research study.")
    study = models.ForeignKey(ResearchStudy, on_delete=models.SET_NULL, null=True, blank=True, related_name="subjects", help_text="FHIR study: research study this subject participates in.")
    consent = models.ForeignKey("Consent", on_delete=models.SET_NULL, null=True, blank=True, related_name="research_subjects", help_text="FHIR consent: consent record for study participation.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: candidate, eligible, follow-up, ineligible, on-study, withdrawn, etc.")
    period_start = models.DateField(null=True, blank=True, help_text="FHIR period.start: participation start date.")
    period_end = models.DateField(null=True, blank=True, help_text="FHIR period.end: participation end date.")
    assigned_arm = models.CharField(max_length=255, blank=True, help_text="FHIR assignedArm: study arm assigned to subject.")
    actual_arm = models.CharField(max_length=255, blank=True, help_text="FHIR actualArm: study arm actually followed.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this research subject.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.assigned_arm or self.status or f"Research Subject #{self.pk}"


# =============================================================================
# Definitions, Catalogs, Quality, And Testing
# FHIR definitional artifacts, terminology, quality reporting, testing, implementation metadata, and knowledge resources.
# =============================================================================

class DeviceDefinition(models.Model):
    manufacturer = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="device_definitions", help_text="FHIR manufacturer[x]: organization responsible for the device definition.")
    device_name = models.CharField(max_length=255, blank=True, help_text="FHIR deviceName.name: device name.")
    device_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: type of device.")
    model_number = models.CharField(max_length=255, blank=True, help_text="FHIR modelNumber: manufacturer model number.")
    version = models.CharField(max_length=255, blank=True, help_text="FHIR version: device version.")
    udi_device_identifier = models.CharField(max_length=255, blank=True, help_text="FHIR udiDeviceIdentifier: device identifier details.")
    specialization_summary = models.TextField(blank=True, help_text="FHIR specialization: standards/specializations supported.")
    property_summary = models.TextField(blank=True, help_text="FHIR property: device properties.")
    capability_summary = models.TextField(blank=True, help_text="FHIR capability: device capabilities.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this device definition.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.device_name or self.device_type or f"Device Definition #{self.pk}"


class ObservationDefinition(models.Model):
    category = models.CharField(max_length=255, blank=True, help_text="FHIR category: observation category.")
    code = models.CharField(max_length=255, help_text="FHIR code: type of observation being defined.")
    permitted_data_type = models.CharField(max_length=255, blank=True, help_text="FHIR permittedDataType: allowed observation value data types.")
    multiple_results_allowed = models.BooleanField(default=False, help_text="FHIR multipleResultsAllowed: whether multiple results are allowed.")
    method = models.CharField(max_length=255, blank=True, help_text="FHIR method: method used to produce the observation.")
    preferred_report_name = models.CharField(max_length=255, blank=True, help_text="FHIR preferredReportName: preferred report display name.")
    quantitative_details = models.TextField(blank=True, help_text="FHIR quantitativeDetails: measurement unit, decimal precision, and conversion details.")
    qualified_interval_summary = models.TextField(blank=True, help_text="FHIR qualifiedInterval: reference ranges/intervals.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this observation definition.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class Questionnaire(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this questionnaire.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the questionnaire.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly questionnaire name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly questionnaire title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for publication.")
    subject_type = models.CharField(max_length=255, blank=True, help_text="FHIR subjectType: resource types the questionnaire can apply to.")
    approval_date = models.DateField(null=True, blank=True, help_text="FHIR approvalDate: when questionnaire was approved.")
    last_review_date = models.DateField(null=True, blank=True, help_text="FHIR lastReviewDate: when questionnaire was last reviewed.")
    effective_start = models.DateField(null=True, blank=True, help_text="FHIR effectivePeriod.start: beginning of questionnaire effective period.")
    effective_end = models.DateField(null=True, blank=True, help_text="FHIR effectivePeriod.end: end of questionnaire effective period.")
    item_summary = models.TextField(blank=True, help_text="FHIR item: questionnaire questions/groups.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this questionnaire.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Measure(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for the measure.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the measure.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly measure name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly measure title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for the measure.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: natural language measure description.")
    scoring = models.CharField(max_length=255, blank=True, help_text="FHIR scoring: proportion, ratio, continuous-variable, cohort, etc.")
    measure_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: process, outcome, structure, patient-reported-outcome, etc.")
    group_summary = models.TextField(blank=True, help_text="FHIR group: populations, stratifiers, and supplemental data.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this measure.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class MeasureReport(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="measure_reports", help_text="FHIR subject: patient associated with the measure report when present.")
    measure = models.ForeignKey(Measure, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports", help_text="FHIR measure: measure this report is for when locally resolvable.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: complete, pending, or error.")
    report_type = models.CharField(max_length=30, blank=True, help_text="FHIR type: individual, subject-list, summary, or data-collection.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: when the report was generated.")
    period_start = models.DateField(null=True, blank=True, help_text="FHIR period.start: reporting period start.")
    period_end = models.DateField(null=True, blank=True, help_text="FHIR period.end: reporting period end.")
    improvement_notation = models.CharField(max_length=255, blank=True, help_text="FHIR improvementNotation: how improvement is calculated.")
    group_summary = models.TextField(blank=True, help_text="FHIR group: measure score, populations, and stratifiers.")
    evaluated_resource_summary = models.TextField(blank=True, help_text="FHIR evaluatedResource: resources included in evaluation.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this measure report.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.measure.title if self.measure else f"Measure Report #{self.pk}"


class TestScript(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this test script.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the test script.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly test script name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly test script title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for publication.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: test script description.")
    fixture_summary = models.TextField(blank=True, help_text="FHIR fixture: fixtures used by this script.")
    test_summary = models.TextField(blank=True, help_text="FHIR setup/test/teardown: summarized test actions and assertions.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this test script.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TestReport(models.Model):
    test_script = models.ForeignKey(TestScript, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports", help_text="FHIR testScript: test script this report executed.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: report name.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: completed, in-progress, waiting, stopped, or entered-in-error.")
    result = models.CharField(max_length=30, blank=True, help_text="FHIR result: pass, fail, or pending.")
    score = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, help_text="FHIR score: overall test score.")
    tester = models.CharField(max_length=255, blank=True, help_text="FHIR tester: name of the tester.")
    issued = models.DateTimeField(null=True, blank=True, help_text="FHIR issued: when report was generated.")
    participant_summary = models.TextField(blank=True, help_text="FHIR participant: servers/clients involved in the test.")
    action_summary = models.TextField(blank=True, help_text="FHIR setup/test/teardown.action: action results.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this test report.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.result or f"Test Report #{self.pk}"


class CoverageEligibilityRequest(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="coverage_eligibility_requests", help_text="FHIR patient: patient whose coverage eligibility is being requested.")
    insurer = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="coverage_eligibility_requests_as_insurer", help_text="FHIR insurer: target insurer for eligibility request.")
    provider_organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="coverage_eligibility_requests_as_provider", help_text="FHIR provider: organization making the request.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, cancelled, draft, or entered-in-error.")
    priority = models.CharField(max_length=255, blank=True, help_text="FHIR priority: desired processing priority.")
    purpose = models.CharField(max_length=255, blank=True, help_text="FHIR purpose: auth-requirements, benefits, discovery, validation.")
    created_date = models.DateField(null=True, blank=True, help_text="FHIR created: request creation date.")
    serviced_start = models.DateField(null=True, blank=True, help_text="FHIR serviced[x]: service date or period start.")
    serviced_end = models.DateField(null=True, blank=True, help_text="FHIR servicedPeriod.end: service period end.")
    insurance_summary = models.TextField(blank=True, help_text="FHIR insurance: coverages included in the request.")
    item_summary = models.TextField(blank=True, help_text="FHIR item: eligibility request items.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this eligibility request.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.purpose or f"Coverage Eligibility Request #{self.pk}"


class CoverageEligibilityResponse(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="coverage_eligibility_responses", help_text="FHIR patient: patient whose coverage eligibility was evaluated.")
    request = models.ForeignKey(CoverageEligibilityRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name="responses", help_text="FHIR request: eligibility request being answered.")
    insurer = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="coverage_eligibility_responses", help_text="FHIR insurer: party responsible for response.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, cancelled, draft, or entered-in-error.")
    purpose = models.CharField(max_length=255, blank=True, help_text="FHIR purpose: auth-requirements, benefits, discovery, validation.")
    outcome = models.CharField(max_length=30, blank=True, help_text="FHIR outcome: queued, complete, error, or partial.")
    disposition = models.TextField(blank=True, help_text="FHIR disposition: disposition message.")
    created_date = models.DateField(null=True, blank=True, help_text="FHIR created: response creation date.")
    insurance_summary = models.TextField(blank=True, help_text="FHIR insurance: benefits and eligibility details.")
    error_summary = models.TextField(blank=True, help_text="FHIR error: processing errors.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this eligibility response.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.outcome or self.purpose or f"Coverage Eligibility Response #{self.pk}"


class EnrollmentRequest(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="enrollment_requests", help_text="FHIR candidate: person to be enrolled when patient-resolvable.")
    insurer = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="enrollment_requests_as_insurer", help_text="FHIR insurer: target insurer.")
    provider = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="enrollment_requests_as_provider", help_text="FHIR provider: organization submitting enrollment.")
    coverage = models.ForeignKey("Coverage", on_delete=models.SET_NULL, null=True, blank=True, related_name="enrollment_requests", help_text="FHIR coverage: coverage to enroll.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, cancelled, draft, or entered-in-error.")
    created_date = models.DateField(null=True, blank=True, help_text="FHIR created: request creation date.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this enrollment request.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.status or f"Enrollment Request #{self.pk}"


class EnrollmentResponse(models.Model):
    request = models.ForeignKey(EnrollmentRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name="responses", help_text="FHIR request: enrollment request being answered.")
    organization = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="enrollment_responses", help_text="FHIR organization: organization responding.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, cancelled, draft, or entered-in-error.")
    outcome = models.CharField(max_length=30, blank=True, help_text="FHIR outcome: queued, complete, error, or partial.")
    disposition = models.TextField(blank=True, help_text="FHIR disposition: disposition message.")
    created_date = models.DateField(null=True, blank=True, help_text="FHIR created: response creation date.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this enrollment response.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.outcome or self.status or f"Enrollment Response #{self.pk}"


class PaymentNotice(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="payment_notices", help_text="Local patient association when payment references patient data.")
    recipient = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="payment_notices", help_text="FHIR recipient: party notified about payment.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, cancelled, draft, or entered-in-error.")
    payment_status = models.CharField(max_length=255, blank=True, help_text="FHIR paymentStatus: status of the payment.")
    created_date = models.DateField(null=True, blank=True, help_text="FHIR created: notice creation date.")
    payment_date = models.DateField(null=True, blank=True, help_text="FHIR paymentDate: expected or actual payment date.")
    amount = models.CharField(max_length=255, blank=True, help_text="FHIR amount: payment amount.")
    request_summary = models.CharField(max_length=255, blank=True, help_text="FHIR request: request reference this notice relates to.")
    response_summary = models.CharField(max_length=255, blank=True, help_text="FHIR response: response reference this notice relates to.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this payment notice.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.payment_status or self.amount or f"Payment Notice #{self.pk}"


class PaymentReconciliation(models.Model):
    payment_issuer = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True, related_name="payment_reconciliations", help_text="FHIR paymentIssuer: organization issuing payment.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, cancelled, draft, or entered-in-error.")
    outcome = models.CharField(max_length=30, blank=True, help_text="FHIR outcome: queued, complete, error, or partial.")
    disposition = models.TextField(blank=True, help_text="FHIR disposition: disposition message.")
    created_date = models.DateField(null=True, blank=True, help_text="FHIR created: reconciliation creation date.")
    payment_date = models.DateField(null=True, blank=True, help_text="FHIR paymentDate: date of payment.")
    payment_amount = models.CharField(max_length=255, blank=True, help_text="FHIR paymentAmount: amount paid.")
    detail_summary = models.TextField(blank=True, help_text="FHIR detail: payment allocation details.")
    process_note_summary = models.TextField(blank=True, help_text="FHIR processNote: processing notes.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this payment reconciliation.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.payment_amount or self.outcome or f"Payment Reconciliation #{self.pk}"


class CodeSystem(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this code system.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the code system.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly code system name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly code system title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this code system.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: natural language description of the code system.")
    content = models.CharField(max_length=30, blank=True, help_text="FHIR content: not-present, example, fragment, complete, or supplement.")
    case_sensitive = models.BooleanField(null=True, blank=True, help_text="FHIR caseSensitive: whether code comparison is case sensitive.")
    hierarchy_meaning = models.CharField(max_length=50, blank=True, help_text="FHIR hierarchyMeaning: meaning of parent/child concept relationships.")
    concept_summary = models.TextField(blank=True, help_text="FHIR concept: summarized code system concepts.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this code system.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ValueSet(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this value set.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the value set.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly value set name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly value set title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this value set.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: natural language description of the value set.")
    immutable = models.BooleanField(null=True, blank=True, help_text="FHIR immutable: whether the value set definition may not change.")
    compose_summary = models.TextField(blank=True, help_text="FHIR compose: include/exclude rules used to define the value set.")
    expansion_summary = models.TextField(blank=True, help_text="FHIR expansion: expanded codes when included in the resource.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this value set.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ConceptMap(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this concept map.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the concept map.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly concept map name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly concept map title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this concept map.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: natural language description of the concept map.")
    source_uri = models.CharField(max_length=500, blank=True, help_text="FHIR source[x]: source value set or structure map context.")
    target_uri = models.CharField(max_length=500, blank=True, help_text="FHIR target[x]: target value set or structure map context.")
    group_summary = models.TextField(blank=True, help_text="FHIR group: concept mappings and equivalence details.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this concept map.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Library(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this library.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the library.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly library name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly library title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this library.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: natural language description of the library.")
    library_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: logic-library, model-definition, asset-collection, module-definition, or related type.")
    subject = models.CharField(max_length=255, blank=True, help_text="FHIR subject[x]: intended subject for the library.")
    related_artifact_summary = models.TextField(blank=True, help_text="FHIR relatedArtifact: citations, dependencies, composed-of, and derived-from links.")
    content_summary = models.TextField(blank=True, help_text="FHIR content: attachments containing library logic or related files.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this library.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PlanDefinition(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this plan definition.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the plan definition.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly plan definition name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly plan definition title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this plan definition.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: natural language description of the plan definition.")
    plan_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: order-set, clinical-protocol, eca-rule, workflow-definition, or other plan type.")
    subject = models.CharField(max_length=255, blank=True, help_text="FHIR subject[x]: intended subject for the plan definition.")
    goal_summary = models.TextField(blank=True, help_text="FHIR goal: goals this plan definition supports.")
    action_summary = models.TextField(blank=True, help_text="FHIR action: actions, triggers, conditions, inputs, and outputs.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this plan definition.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class CapabilityStatement(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this capability statement.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the capability statement.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly capability statement name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly capability statement title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: natural language description of the capability statement.")
    kind = models.CharField(max_length=30, blank=True, help_text="FHIR kind: instance, capability, or requirements.")
    fhir_version = models.CharField(max_length=30, blank=True, help_text="FHIR fhirVersion: FHIR version supported.")
    format_summary = models.TextField(blank=True, help_text="FHIR format/patchFormat: supported data formats.")
    rest_summary = models.TextField(blank=True, help_text="FHIR rest: RESTful capabilities and interactions.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this capability statement.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class StructureDefinition(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this structure definition.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the structure definition.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly structure definition name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly structure definition title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: natural language profile/extension description.")
    kind = models.CharField(max_length=50, blank=True, help_text="FHIR kind: primitive-type, complex-type, resource, or logical.")
    abstract = models.BooleanField(null=True, blank=True, help_text="FHIR abstract: whether this structure is abstract.")
    type_code = models.CharField(max_length=255, blank=True, help_text="FHIR type: constrained FHIR type/resource.")
    base_definition = models.CharField(max_length=500, blank=True, help_text="FHIR baseDefinition: base structure this definition constrains.")
    derivation = models.CharField(max_length=30, blank=True, help_text="FHIR derivation: specialization or constraint.")
    element_summary = models.TextField(blank=True, help_text="FHIR snapshot/differential: summarized element definitions.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this structure definition.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ImplementationGuide(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this implementation guide.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the implementation guide.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly implementation guide name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly implementation guide title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: natural language implementation guide description.")
    package_id = models.CharField(max_length=255, blank=True, help_text="FHIR packageId: NPM package id for this guide.")
    fhir_version_summary = models.CharField(max_length=255, blank=True, help_text="FHIR fhirVersion: FHIR versions this guide targets.")
    definition_summary = models.TextField(blank=True, help_text="FHIR definition: grouped resources, pages, parameters, and templates.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this implementation guide.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class SearchParameter(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this search parameter.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the search parameter.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly search parameter name.")
    title = models.CharField(max_length=255, help_text="FHIR title/name: human-friendly search parameter label.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: search parameter purpose and behavior.")
    code = models.CharField(max_length=255, blank=True, help_text="FHIR code: code used in search URLs.")
    base_summary = models.CharField(max_length=500, blank=True, help_text="FHIR base: resource types this search parameter applies to.")
    search_type = models.CharField(max_length=50, blank=True, help_text="FHIR type: number, date, string, token, reference, composite, quantity, uri, or special.")
    expression = models.TextField(blank=True, help_text="FHIR expression: FHIRPath expression over the resource.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this search parameter.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class MessageDefinition(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this message definition.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the message definition.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly message definition name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly message definition title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: message definition behavior and use.")
    event = models.CharField(max_length=255, blank=True, help_text="FHIR event[x]: event code or canonical event definition.")
    category = models.CharField(max_length=30, blank=True, help_text="FHIR category: consequence, currency, or notification.")
    response_required = models.CharField(max_length=30, blank=True, help_text="FHIR responseRequired: always, on-error, never, or on-success.")
    focus_summary = models.TextField(blank=True, help_text="FHIR focus: resources that must be present in messages.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this message definition.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class OperationDefinition(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this operation definition.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the operation definition.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly operation definition name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly operation definition title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: operation or named query behavior.")
    kind = models.CharField(max_length=30, blank=True, help_text="FHIR kind: operation or query.")
    code = models.CharField(max_length=255, blank=True, help_text="FHIR code: name used to invoke the operation.")
    resource_summary = models.CharField(max_length=500, blank=True, help_text="FHIR resource: resource types this operation applies to.")
    system = models.BooleanField(default=False, help_text="FHIR system: whether operation can be invoked at system level.")
    type_level = models.BooleanField(default=False, help_text="FHIR type: whether operation can be invoked at resource type level.")
    instance = models.BooleanField(default=False, help_text="FHIR instance: whether operation can be invoked at instance level.")
    parameter_summary = models.TextField(blank=True, help_text="FHIR parameter: operation input/output parameters.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this operation definition.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class CompartmentDefinition(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this compartment definition.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the compartment definition.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly compartment definition name.")
    title = models.CharField(max_length=255, help_text="FHIR name/title: human-friendly compartment label.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: compartment definition description.")
    code = models.CharField(max_length=50, blank=True, help_text="FHIR code: Patient, Encounter, RelatedPerson, Practitioner, or Device.")
    search = models.BooleanField(default=False, help_text="FHIR search: whether compartment can be used for search.")
    resource_summary = models.TextField(blank=True, help_text="FHIR resource: resources and search parameters included in this compartment.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this compartment definition.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class StructureMap(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this structure map.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the structure map.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly structure map name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly structure map title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: structure mapping description.")
    structure_summary = models.TextField(blank=True, help_text="FHIR structure: source/target structures used by this map.")
    group_summary = models.TextField(blank=True, help_text="FHIR group: transformation groups and rules.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this structure map.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class GraphDefinition(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this graph definition.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the graph definition.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly graph definition name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly graph definition title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: graph traversal description.")
    start = models.CharField(max_length=255, blank=True, help_text="FHIR start: resource type where the graph starts.")
    profile = models.CharField(max_length=500, blank=True, help_text="FHIR profile: profile that describes graph instances.")
    link_summary = models.TextField(blank=True, help_text="FHIR link: graph traversal links and target resources.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this graph definition.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ExampleScenario(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this example scenario.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the example scenario.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly example scenario name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly example scenario title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: example scenario description.")
    actor_summary = models.TextField(blank=True, help_text="FHIR actor: participants in the scenario.")
    instance_summary = models.TextField(blank=True, help_text="FHIR instance: resources used in the scenario.")
    process_summary = models.TextField(blank=True, help_text="FHIR process: scenario process steps.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this example scenario.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class NamingSystem(models.Model):
    name = models.CharField(max_length=255, help_text="FHIR name: computer-friendly naming system name.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    kind = models.CharField(max_length=30, blank=True, help_text="FHIR kind: codesystem, identifier, or root.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: naming system description.")
    unique_id_summary = models.TextField(blank=True, help_text="FHIR uniqueId: unique identifiers such as URI, OID, UUID, or other ids.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this naming system.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TerminologyCapabilities(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this terminology capabilities resource.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the terminology capabilities resource.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly terminology capabilities name.")
    title = models.CharField(max_length=255, help_text="FHIR title/name: human-friendly terminology capabilities label.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: terminology server capabilities description.")
    kind = models.CharField(max_length=30, blank=True, help_text="FHIR kind: instance, capability, or requirements.")
    code_system_summary = models.TextField(blank=True, help_text="FHIR codeSystem: supported code systems and versions.")
    expansion_summary = models.TextField(blank=True, help_text="FHIR expansion: expansion behavior and parameters.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this terminology capabilities resource.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ActivityDefinition(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this activity definition.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the activity definition.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly activity definition name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly activity definition title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: activity definition description.")
    activity_kind = models.CharField(max_length=50, blank=True, help_text="FHIR kind: resource type this activity creates.")
    intent = models.CharField(max_length=50, blank=True, help_text="FHIR intent: proposal, plan, directive, order, etc.")
    priority = models.CharField(max_length=50, blank=True, help_text="FHIR priority: routine, urgent, asap, or stat.")
    code = models.CharField(max_length=255, blank=True, help_text="FHIR code: detail of the activity to perform.")
    participant_summary = models.TextField(blank=True, help_text="FHIR participant: participants expected to perform the activity.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this activity definition.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class EventDefinition(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this event definition.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the event definition.")
    name = models.CharField(max_length=255, blank=True, help_text="FHIR name: computer-friendly event definition name.")
    title = models.CharField(max_length=255, help_text="FHIR title: human-friendly event definition title.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: event definition description.")
    trigger_summary = models.TextField(blank=True, help_text="FHIR trigger: triggering events for this definition.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this event definition.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class SpecimenDefinition(models.Model):
    url = models.URLField(blank=True, help_text="FHIR url: canonical URL for this specimen definition.")
    version = models.CharField(max_length=100, blank=True, help_text="FHIR version: business version of the specimen definition.")
    title = models.CharField(max_length=255, help_text="FHIR typeCollected/title: human-friendly specimen definition label.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: draft, active, retired, or unknown.")
    publisher = models.CharField(max_length=255, blank=True, help_text="FHIR publisher: organization or individual responsible for this artifact.")
    date = models.DateTimeField(null=True, blank=True, help_text="FHIR date: publication/change date.")
    description = models.TextField(blank=True, help_text="FHIR description: specimen definition description.")
    specimen_type = models.CharField(max_length=255, blank=True, help_text="FHIR typeCollected: kind of specimen to collect.")
    collection_summary = models.TextField(blank=True, help_text="FHIR collection: preferred collection method and requirements.")
    type_tested_summary = models.TextField(blank=True, help_text="FHIR typeTested: specimen testing details and handling requirements.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this specimen definition.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# =============================================================================
# Organizations And Locations
# Core organization and location directory records used by many clinical resources.
# =============================================================================

class Organization(models.Model):
    name = models.CharField(max_length=255, help_text="FHIR name: organization name.")
    organization_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: kind of organization, such as provider, department, team, or payer.")
    active = models.BooleanField(default=True, help_text="FHIR active: whether this organization's record is active.")
    phone = models.CharField(max_length=30, blank=True, help_text="FHIR telecom: phone contact.")
    email = models.EmailField(blank=True, help_text="FHIR telecom: email contact.")
    address = models.TextField(blank=True, help_text="FHIR address: organization address.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this organization.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=255, help_text="FHIR name: location name.")
    status = models.CharField(max_length=30, blank=True, help_text="FHIR status: active, suspended, or inactive.")
    mode = models.CharField(max_length=30, blank=True, help_text="FHIR mode: instance or kind.")
    location_type = models.CharField(max_length=255, blank=True, help_text="FHIR type: kind of location, such as clinic, ward, room, or vehicle.")
    managing_organization = models.CharField(max_length=255, blank=True, help_text="FHIR managingOrganization: organization responsible for the location.")
    phone = models.CharField(max_length=30, blank=True, help_text="FHIR telecom: phone contact.")
    email = models.EmailField(blank=True, help_text="FHIR telecom: email contact.")
    address = models.TextField(blank=True, help_text="FHIR address: physical address of the location.")
    notes = models.TextField(blank=True, help_text="Imported notes or source text for this location.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

