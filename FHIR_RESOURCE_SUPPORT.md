# FHIR R4 Resource Support

Source: HL7 FHIR R4 Resource Index, https://hl7.org/fhir/R4/resourcelist.html

Status legend:

- `First-class`: Imported into local Django models/admin.
- `Parser/container`: Handled structurally, but not stored as its own local model.
- `Planned`: Called out in `todo.md` as a likely first-class model or importer target.
- `Snapshot candidate`: Accepted and preserved as a valid `FHIRResourceSnapshot` with `import_status="snapshot_only"`, but probably does not need a first-class UI yet.
- `Unsupported`: No first-class importer yet.

## Current First-Class Support

- `AllergyIntolerance` -> `clinical.Allergy`
- `AdverseEvent` -> `clinical.AdverseEvent`
- `BodyStructure` -> `clinical.BodyStructure`
- `CarePlan` -> `clinical.CarePlan`
- `CareTeam` -> `clinical.CareTeam`
- `ClinicalImpression` -> `clinical.ClinicalImpression`
- `Condition` -> `clinical.Condition`
- `Consent` -> `clinical.Consent`
- `Coverage` -> `clinical.Coverage`
- `DetectedIssue` -> `clinical.DetectedIssue`
- `Device` -> `clinical.Device`
- `DeviceRequest` -> `clinical.DeviceRequest`
- `DeviceUseStatement` -> `clinical.DeviceUseStatement`
- `DiagnosticReport` -> `clinical.DiagnosticReport`
- `DocumentReference` -> `documents.ClinicalDocument`
- `Encounter` -> `clinical.Encounter`
- `EpisodeOfCare` -> `clinical.EpisodeOfCare`
- `ExplanationOfBenefit` -> `clinical.ExplanationOfBenefit`
- `FamilyMemberHistory` -> `clinical.FamilyMemberHistory`
- `Flag` -> `clinical.Flag`
- `Group` -> `clinical.FHIRGroup`
- `Goal` -> `clinical.Goal`
- `Immunization` -> `clinical.Immunization`
- `ImmunizationRecommendation` -> `clinical.ImmunizationRecommendation`
- `InsurancePlan` -> `clinical.InsurancePlan`
- `List` -> `clinical.FHIRList`
- `Location` -> `clinical.Location`
- `Medication` -> `clinical.MedicationCatalog`
- `MedicationAdministration` -> `clinical.MedicationAdministration`
- `MedicationDispense` -> `clinical.MedicationDispense`
- `MedicationRequest` -> `clinical.Medication`
- `MedicationStatement` -> `clinical.Medication`
- `NutritionOrder` -> `clinical.NutritionOrder`
- `Observation` -> `clinical.Observation`
- `Organization` -> `clinical.Organization`
- `Patient` -> `patients.PatientProfile`
- `Person` -> `clinical.Person`
- `Practitioner` -> `clinical.Practitioner`
- `PractitionerRole` -> `clinical.PractitionerRole`
- `Procedure` -> `clinical.Procedure`
- `QuestionnaireResponse` -> `clinical.QuestionnaireResponse`
- `RelatedPerson` -> `clinical.RelatedPerson`
- `RiskAssessment` -> `clinical.RiskAssessment`
- `ServiceRequest` -> `clinical.ServiceRequest`
- `Specimen` -> `clinical.Specimen`

## Foundation

### Conformance

| Resource | Status | Notes |
| --- | --- | --- |
| `CapabilityStatement` | Snapshot candidate | Technical server capability metadata. |
| `StructureDefinition` | Snapshot candidate | Profile/extension definitions. |
| `ImplementationGuide` | Snapshot candidate | IG package metadata. |
| `SearchParameter` | Snapshot candidate | Search metadata. |
| `MessageDefinition` | Snapshot candidate | Messaging definition. |
| `OperationDefinition` | Snapshot candidate | Operation metadata. |
| `CompartmentDefinition` | Snapshot candidate | Compartment metadata. |
| `StructureMap` | Snapshot candidate | Mapping definition. |
| `GraphDefinition` | Snapshot candidate | Resource graph definition. |
| `ExampleScenario` | Snapshot candidate | Documentation/example artifact. |

### Terminology

| Resource | Status | Notes |
| --- | --- | --- |
| `CodeSystem` | Snapshot candidate | Terminology definition. |
| `ValueSet` | Snapshot candidate | Terminology value set. |
| `ConceptMap` | Snapshot candidate | Terminology mapping. |
| `NamingSystem` | Snapshot candidate | Identifier namespace metadata. |
| `TerminologyCapabilities` | Snapshot candidate | Terminology server capability metadata. |

### Security

| Resource | Status | Notes |
| --- | --- | --- |
| `Provenance` | Planned | Useful for import/source trust and record history. |
| `AuditEvent` | Snapshot candidate | Security/system audit event. |
| `Consent` | First-class | Privacy, treatment, procedure, vaccine, and other consent directives. |

### Documents

| Resource | Status | Notes |
| --- | --- | --- |
| `Composition` | Planned | Structured document sections; may map to ClinicalDocument/document sections. |
| `DocumentManifest` | Planned | Document package/index; link to ClinicalDocument/DocumentReference. |
| `DocumentReference` | First-class | Maps to `ClinicalDocument`; stores attachments and relationships. |

### Other

| Resource | Status | Notes |
| --- | --- | --- |
| `CatalogEntry` | Snapshot candidate | Catalog metadata. |
| `Basic` | Snapshot candidate | Generic extension resource. |
| `Binary` | Planned | Needed for external/inline document or media content. |
| `Bundle` | Parser/container | Extracted into contained resources; not stored as a model. |
| `Linkage` | Snapshot candidate | Resource identity/linkage metadata. |
| `MessageHeader` | Snapshot candidate | Messaging envelope. |
| `OperationOutcome` | Snapshot candidate | Error/result payload. |
| `Parameters` | Snapshot candidate | Operation parameters. |
| `Subscription` | Snapshot candidate | Server subscription metadata. |

## Base

### Individuals

| Resource | Status | Notes |
| --- | --- | --- |
| `Patient` | First-class | Maps to `PatientProfile`. |
| `Practitioner` | First-class | Directory resource. |
| `PractitionerRole` | First-class | Links practitioner, organization, specialty, and locations. |
| `RelatedPerson` | First-class | Caregivers, family, proxies, and other patient-related people. |
| `Person` | First-class | Identity reconciliation across Patient, Practitioner, RelatedPerson, and Person records. |
| `Group` | First-class | Cohorts/groups with managing entity, characteristics, and member links. |

### Entities #1

| Resource | Status | Notes |
| --- | --- | --- |
| `Organization` | First-class | Directory resource. |
| `OrganizationAffiliation` | Planned | Organization-to-organization/service relationships. |
| `HealthcareService` | Planned | Services offered by organizations/locations. |
| `Endpoint` | Planned | Technical endpoint; likely interop/directory support. |
| `Location` | First-class | Directory/site resource. |

### Entities #2

| Resource | Status | Notes |
| --- | --- | --- |
| `Substance` | Planned | Useful for allergies/medications/labs; likely catalog-style. |
| `BiologicallyDerivedProduct` | Snapshot candidate | Blood/tissue/product details. |
| `Device` | First-class | Patient/device inventory and references. |
| `DeviceMetric` | Planned | Device measurement channels/configuration. |

### Workflow Management

| Resource | Status | Notes |
| --- | --- | --- |
| `Task` | Planned | Workflow/reminders/imported tasks. |
| `Appointment` | Planned | Scheduling/calendar support. |
| `AppointmentResponse` | Planned | Appointment participant response. |
| `Schedule` | Planned | Availability schedule. |
| `Slot` | Planned | Bookable time slot. |
| `VerificationResult` | Snapshot candidate | Verification metadata. |
| `Encounter` | First-class | Visit/action record. |
| `EpisodeOfCare` | First-class | Larger care episode grouping. |
| `Flag` | First-class | Patient warnings/alerts. |
| `List` | First-class | FHIR lists/groupings of resources. |
| `Library` | Snapshot candidate | Knowledge artifact. |

## Clinical

### Summary

| Resource | Status | Notes |
| --- | --- | --- |
| `AllergyIntolerance` | First-class | Maps to `Allergy`; orphan patient strategy still needed. |
| `AdverseEvent` | First-class | Harmful events and contributors. |
| `Condition` | First-class | Problems/diagnoses. |
| `Procedure` | First-class | Completed procedures/actions. |
| `FamilyMemberHistory` | First-class | Family history with repeating condition details. |
| `ClinicalImpression` | First-class | Clinician assessment/synthesis, findings, and investigations. |
| `DetectedIssue` | First-class | Safety/quality issues such as interactions or duplicate therapy. |

### Diagnostics

| Resource | Status | Notes |
| --- | --- | --- |
| `Observation` | First-class | Vitals/labs/results. |
| `Media` | Planned | Clinical images/photos/media. |
| `DiagnosticReport` | First-class | Diagnostic reports with encounter, requests, specimens, observations, performers, interpreters, and presented forms. |
| `Specimen` | First-class | Lab specimen details. |
| `BodyStructure` | First-class | Anatomical/body-site detail. |
| `ImagingStudy` | Planned | Imaging study/series/instance data. |
| `QuestionnaireResponse` | First-class | Patient-entered forms and assessments. |
| `MolecularSequence` | Snapshot candidate | Genomics; first-class only if genomics UI is planned. |

### Medications

| Resource | Status | Notes |
| --- | --- | --- |
| `MedicationRequest` | First-class | Currently maps into local `Medication`. |
| `MedicationAdministration` | First-class | Administered medication event. |
| `MedicationDispense` | First-class | Pharmacy/supply dispense event. |
| `MedicationStatement` | First-class | Currently maps into local `Medication`. |
| `Medication` | First-class | Standalone medication catalog/details; maps to `MedicationCatalog`, separate from requests/statements. |
| `MedicationKnowledge` | Planned | Drug knowledge/catalog metadata; probably snapshot/generic first. |
| `Immunization` | First-class | Vaccination records. |
| `ImmunizationEvaluation` | Planned | Immunization validity/status evaluation. |
| `ImmunizationRecommendation` | First-class | Vaccine forecast/recommendations. |

### Care Provision

| Resource | Status | Notes |
| --- | --- | --- |
| `CarePlan` | First-class | Care plans with conditions/care teams. |
| `CareTeam` | First-class | Care teams and participants. |
| `Goal` | First-class | Patient/care goals with addressed concerns, targets, and outcomes. |
| `ServiceRequest` | First-class | Orders/referrals/requested services. |
| `NutritionOrder` | First-class | Dietary/oral/enteral/supplement orders. |
| `VisionPrescription` | Planned | Vision prescription details. |
| `RiskAssessment` | First-class | Risk predictions/probabilities with basis records and mitigation. |
| `RequestGroup` | Planned | Grouped/conditional requests and plans. |

### Request & Response

| Resource | Status | Notes |
| --- | --- | --- |
| `Communication` | First-class | Care communications/messages. |
| `CommunicationRequest` | First-class | Requested communication. |
| `DeviceRequest` | First-class | Device orders/requests with reasons, performers, and timing. |
| `DeviceUseStatement` | First-class | Patient/device usage history. |
| `GuidanceResponse` | Planned | Decision-support response. |
| `SupplyRequest` | Planned | Supply request. |
| `SupplyDelivery` | Planned | Supply delivery event. |

## Financial

### Support

| Resource | Status | Notes |
| --- | --- | --- |
| `Coverage` | First-class | Insurance coverage, subscriber IDs, payer details, and benefit classifications. |
| `CoverageEligibilityRequest` | Snapshot candidate | Eligibility request. |
| `CoverageEligibilityResponse` | Snapshot candidate | Eligibility response. |
| `EnrollmentRequest` | Snapshot candidate | Enrollment request. |
| `EnrollmentResponse` | Snapshot candidate | Enrollment response. |

### Billing

| Resource | Status | Notes |
| --- | --- | --- |
| `Claim` | Planned | Claims support if adding insurance/finance. |
| `ClaimResponse` | Planned | Claim adjudication response. |
| `Invoice` | Planned | Billing invoice. |

### Payment

| Resource | Status | Notes |
| --- | --- | --- |
| `PaymentNotice` | Snapshot candidate | Payment notification. |
| `PaymentReconciliation` | Snapshot candidate | Payment reconciliation. |

### General

| Resource | Status | Notes |
| --- | --- | --- |
| `Account` | Planned | Billing/account grouping. |
| `ChargeItem` | Planned | Charge line item. |
| `ChargeItemDefinition` | Snapshot candidate | Charge item definition. |
| `Contract` | Snapshot candidate | Contract/legal agreement. |
| `ExplanationOfBenefit` | First-class | EOB/claims summary; useful for personal records. |
| `InsurancePlan` | First-class | Insurance plan details. |

## Specialized

### Public Health & Research

| Resource | Status | Notes |
| --- | --- | --- |
| `ResearchStudy` | Planned | Optional research participation area. |
| `ResearchSubject` | Planned | Patient participation in a study. |

### Definitional Artifacts

| Resource | Status | Notes |
| --- | --- | --- |
| `ActivityDefinition` | Snapshot candidate | Knowledge artifact. |
| `DeviceDefinition` | Planned | Device catalog/definition. |
| `EventDefinition` | Snapshot candidate | Knowledge artifact. |
| `ObservationDefinition` | Planned | Observation catalog/definition. |
| `PlanDefinition` | Snapshot candidate | Care plan definition/knowledge artifact. |
| `Questionnaire` | Planned | Form definitions. |
| `SpecimenDefinition` | Snapshot candidate | Specimen catalog/definition. |

### Evidence-Based Medicine

| Resource | Status | Notes |
| --- | --- | --- |
| `ResearchDefinition` | Snapshot candidate | Evidence/research metadata. |
| `ResearchElementDefinition` | Snapshot candidate | Evidence/research metadata. |
| `Evidence` | Snapshot candidate | Evidence artifact. |
| `EvidenceVariable` | Snapshot candidate | Evidence variable definition. |
| `EffectEvidenceSynthesis` | Snapshot candidate | Evidence synthesis. |
| `RiskEvidenceSynthesis` | Snapshot candidate | Risk evidence synthesis. |

### Quality Reporting & Testing

| Resource | Status | Notes |
| --- | --- | --- |
| `Measure` | Snapshot candidate | Quality measure definition. |
| `MeasureReport` | Snapshot candidate | Quality measure report. |
| `TestScript` | Snapshot candidate | FHIR testing artifact. |
| `TestReport` | Snapshot candidate | FHIR testing artifact. |

### Medication Definition

| Resource | Status | Notes |
| --- | --- | --- |
| `MedicinalProduct` | Snapshot candidate | Medication/product definition. |
| `MedicinalProductAuthorization` | Snapshot candidate | Medication/product definition. |
| `MedicinalProductContraindication` | Snapshot candidate | Medication/product definition. |
| `MedicinalProductIndication` | Snapshot candidate | Medication/product definition. |
| `MedicinalProductIngredient` | Snapshot candidate | Medication/product definition. |
| `MedicinalProductInteraction` | Snapshot candidate | Medication/product definition. |
| `MedicinalProductManufactured` | Snapshot candidate | Medication/product definition. |
| `MedicinalProductPackaged` | Snapshot candidate | Medication/product definition. |
| `MedicinalProductPharmaceutical` | Snapshot candidate | Medication/product definition. |
| `MedicinalProductUndesirableEffect` | Snapshot candidate | Medication/product definition. |
| `SubstanceNucleicAcid` | Snapshot candidate | Substance definition. |
| `SubstancePolymer` | Snapshot candidate | Substance definition. |
| `SubstanceProtein` | Snapshot candidate | Substance definition. |
| `SubstanceReferenceInformation` | Snapshot candidate | Substance definition. |
| `SubstanceSpecification` | Snapshot candidate | Substance definition. |
| `SubstanceSourceMaterial` | Snapshot candidate | Substance definition. |

## Next Completeness Step

The app preserves unsupported but well-formed FHIR R4 resources as valid `FHIRResourceSnapshot` rows with `import_status="snapshot_only"`. First-class models can then be added selectively based on real imported data and patient-facing value.
