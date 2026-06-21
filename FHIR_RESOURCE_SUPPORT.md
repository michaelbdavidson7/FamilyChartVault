# FHIR R4 Resource Support

Source: HL7 FHIR R4 Resource Index, https://hl7.org/fhir/R4/resourcelist.html

Status legend:

- `First-class`: Imported into local Django models/admin.
- `Parser/container`: Handled structurally, but not stored as its own local model.
- `Planned`: Called out in `todo.md` as a likely first-class model or importer target.
- `Snapshot candidate`: Accepted and preserved as a valid `FHIRResourceSnapshot` with `import_status="snapshot_only"`, but probably does not need a first-class UI yet.
- `Unsupported`: No first-class importer yet.

## Current First-Class Support

- `ActivityDefinition` -> `clinical.ActivityDefinition`
- `CapabilityStatement` -> `clinical.CapabilityStatement`
- `CompartmentDefinition` -> `clinical.CompartmentDefinition`
- `EventDefinition` -> `clinical.EventDefinition`
- `ExampleScenario` -> `clinical.ExampleScenario`
- `GraphDefinition` -> `clinical.GraphDefinition`
- `ImplementationGuide` -> `clinical.ImplementationGuide`
- `MessageDefinition` -> `clinical.MessageDefinition`
- `NamingSystem` -> `clinical.NamingSystem`
- `OperationDefinition` -> `clinical.OperationDefinition`
- `SearchParameter` -> `clinical.SearchParameter`
- `SpecimenDefinition` -> `clinical.SpecimenDefinition`
- `StructureDefinition` -> `clinical.StructureDefinition`
- `StructureMap` -> `clinical.StructureMap`
- `TerminologyCapabilities` -> `clinical.TerminologyCapabilities`
- `CatalogEntry` -> `clinical.CatalogEntry`
- `Basic` -> `clinical.Basic`
- `Linkage` -> `clinical.Linkage`
- `MessageHeader` -> `clinical.MessageHeader`
- `OperationOutcome` -> `clinical.OperationOutcome`
- `Parameters` -> `clinical.Parameters`
- `Subscription` -> `clinical.Subscription`
- `BiologicallyDerivedProduct` -> `clinical.BiologicallyDerivedProduct`
- `VerificationResult` -> `clinical.VerificationResult`
- `ChargeItemDefinition` -> `clinical.ChargeItemDefinition`
- `Contract` -> `clinical.Contract`
- `ResearchDefinition` -> `clinical.ResearchDefinition`
- `ResearchElementDefinition` -> `clinical.ResearchElementDefinition`
- `Evidence` -> `clinical.Evidence`
- `EvidenceVariable` -> `clinical.EvidenceVariable`
- `EffectEvidenceSynthesis` -> `clinical.EffectEvidenceSynthesis`
- `RiskEvidenceSynthesis` -> `clinical.RiskEvidenceSynthesis`
- `MedicinalProduct` -> `clinical.MedicinalProduct`
- `MedicinalProductAuthorization` -> `clinical.MedicinalProductAuthorization`
- `MedicinalProductContraindication` -> `clinical.MedicinalProductContraindication`
- `MedicinalProductIndication` -> `clinical.MedicinalProductIndication`
- `MedicinalProductIngredient` -> `clinical.MedicinalProductIngredient`
- `MedicinalProductInteraction` -> `clinical.MedicinalProductInteraction`
- `MedicinalProductManufactured` -> `clinical.MedicinalProductManufactured`
- `MedicinalProductPackaged` -> `clinical.MedicinalProductPackaged`
- `MedicinalProductPharmaceutical` -> `clinical.MedicinalProductPharmaceutical`
- `MedicinalProductUndesirableEffect` -> `clinical.MedicinalProductUndesirableEffect`
- `SubstanceNucleicAcid` -> `clinical.SubstanceNucleicAcid`
- `SubstancePolymer` -> `clinical.SubstancePolymer`
- `SubstanceProtein` -> `clinical.SubstanceProtein`
- `SubstanceReferenceInformation` -> `clinical.SubstanceReferenceInformation`
- `SubstanceSpecification` -> `clinical.SubstanceSpecification`
- `SubstanceSourceMaterial` -> `clinical.SubstanceSourceMaterial`
- `Account` -> `clinical.Account`
- `AdverseEvent` -> `clinical.AdverseEvent`
- `AllergyIntolerance` -> `clinical.Allergy`
- `Appointment` -> `clinical.Appointment`
- `AppointmentResponse` -> `clinical.AppointmentResponse`
- `AuditEvent` -> `clinical.AuditEvent`
- `Binary` -> `clinical.BinaryResource`
- `BodyStructure` -> `clinical.BodyStructure`
- `CarePlan` -> `clinical.CarePlan`
- `CareTeam` -> `clinical.CareTeam`
- `ChargeItem` -> `clinical.ChargeItem`
- `Claim` -> `clinical.Claim`
- `ClaimResponse` -> `clinical.ClaimResponse`
- `ClinicalImpression` -> `clinical.ClinicalImpression`
- `CodeSystem` -> `clinical.CodeSystem`
- `ConceptMap` -> `clinical.ConceptMap`
- `Composition` -> `clinical.Composition`
- `Condition` -> `clinical.Condition`
- `Consent` -> `clinical.Consent`
- `CoverageEligibilityRequest` -> `clinical.CoverageEligibilityRequest`
- `CoverageEligibilityResponse` -> `clinical.CoverageEligibilityResponse`
- `EnrollmentRequest` -> `clinical.EnrollmentRequest`
- `EnrollmentResponse` -> `clinical.EnrollmentResponse`
- `Measure` -> `clinical.Measure`
- `MeasureReport` -> `clinical.MeasureReport`
- `PaymentNotice` -> `clinical.PaymentNotice`
- `PaymentReconciliation` -> `clinical.PaymentReconciliation`
- `PlanDefinition` -> `clinical.PlanDefinition`
- `TestScript` -> `clinical.TestScript`
- `TestReport` -> `clinical.TestReport`
- `Coverage` -> `clinical.Coverage`
- `DetectedIssue` -> `clinical.DetectedIssue`
- `Device` -> `clinical.Device`
- `DeviceDefinition` -> `clinical.DeviceDefinition`
- `DeviceMetric` -> `clinical.DeviceMetric`
- `DeviceRequest` -> `clinical.DeviceRequest`
- `DeviceUseStatement` -> `clinical.DeviceUseStatement`
- `DiagnosticReport` -> `clinical.DiagnosticReport`
- `DocumentManifest` -> `clinical.DocumentManifest`
- `DocumentReference` -> `documents.ClinicalDocument`
- `Encounter` -> `clinical.Encounter`
- `Endpoint` -> `clinical.Endpoint`
- `EpisodeOfCare` -> `clinical.EpisodeOfCare`
- `ExplanationOfBenefit` -> `clinical.ExplanationOfBenefit`
- `FamilyMemberHistory` -> `clinical.FamilyMemberHistory`
- `Flag` -> `clinical.Flag`
- `Goal` -> `clinical.Goal`
- `Group` -> `clinical.FHIRGroup`
- `GuidanceResponse` -> `clinical.GuidanceResponse`
- `HealthcareService` -> `clinical.HealthcareService`
- `ImagingStudy` -> `clinical.ImagingStudy`
- `Immunization` -> `clinical.Immunization`
- `ImmunizationEvaluation` -> `clinical.ImmunizationEvaluation`
- `ImmunizationRecommendation` -> `clinical.ImmunizationRecommendation`
- `InsurancePlan` -> `clinical.InsurancePlan`
- `Invoice` -> `clinical.Invoice`
- `List` -> `clinical.FHIRList`
- `Location` -> `clinical.Location`
- `Library` -> `clinical.Library`
- `Media` -> `clinical.Media`
- `Medication` -> `clinical.MedicationCatalog`
- `MedicationAdministration` -> `clinical.MedicationAdministration`
- `MedicationDispense` -> `clinical.MedicationDispense`
- `MedicationKnowledge` -> `clinical.MedicationKnowledge`
- `MedicationRequest` -> `clinical.Medication`
- `MedicationStatement` -> `clinical.Medication`
- `MolecularSequence` -> `clinical.MolecularSequence`
- `NutritionOrder` -> `clinical.NutritionOrder`
- `Observation` -> `clinical.Observation`
- `ObservationDefinition` -> `clinical.ObservationDefinition`
- `Organization` -> `clinical.Organization`
- `OrganizationAffiliation` -> `clinical.OrganizationAffiliation`
- `Patient` -> `patients.PatientProfile`
- `Person` -> `clinical.Person`
- `Practitioner` -> `clinical.Practitioner`
- `PractitionerRole` -> `clinical.PractitionerRole`
- `Procedure` -> `clinical.Procedure`
- `Provenance` -> `clinical.Provenance`
- `Questionnaire` -> `clinical.Questionnaire`
- `QuestionnaireResponse` -> `clinical.QuestionnaireResponse`
- `RelatedPerson` -> `clinical.RelatedPerson`
- `RequestGroup` -> `clinical.RequestGroup`
- `ResearchStudy` -> `clinical.ResearchStudy`
- `ResearchSubject` -> `clinical.ResearchSubject`
- `RiskAssessment` -> `clinical.RiskAssessment`
- `Schedule` -> `clinical.Schedule`
- `ServiceRequest` -> `clinical.ServiceRequest`
- `Slot` -> `clinical.Slot`
- `Specimen` -> `clinical.Specimen`
- `Substance` -> `clinical.Substance`
- `SupplyDelivery` -> `clinical.SupplyDelivery`
- `SupplyRequest` -> `clinical.SupplyRequest`
- `Task` -> `clinical.Task`
- `ValueSet` -> `clinical.ValueSet`
- `VisionPrescription` -> `clinical.VisionPrescription`

## Foundation

### Conformance

| Resource | Status | Notes |
| --- | --- | --- |
| `CapabilityStatement` | First-class | Technical server capability metadata. |
| `StructureDefinition` | First-class | Profile/extension definitions. |
| `ImplementationGuide` | First-class | IG package metadata. |
| `SearchParameter` | First-class | Search metadata. |
| `MessageDefinition` | First-class | Messaging definition. |
| `OperationDefinition` | First-class | Operation metadata. |
| `CompartmentDefinition` | First-class | Compartment metadata. |
| `StructureMap` | First-class | Mapping definition. |
| `GraphDefinition` | First-class | Resource graph definition. |
| `ExampleScenario` | First-class | Documentation/example artifact. |

### Terminology

| Resource | Status | Notes |
| --- | --- | --- |
| `CodeSystem` | First-class | Terminology definition. |
| `ValueSet` | First-class | Terminology value set. |
| `ConceptMap` | First-class | Terminology mapping. |
| `NamingSystem` | First-class | Identifier namespace metadata. |
| `TerminologyCapabilities` | First-class | Terminology server capability metadata. |

### Security

| Resource | Status | Notes |
| --- | --- | --- |
| `Provenance` | First-class | Useful for import/source trust and record history. |
| `AuditEvent` | First-class | Security/system audit event. |
| `Consent` | First-class | Privacy, treatment, procedure, vaccine, and other consent directives. |

### Documents

| Resource | Status | Notes |
| --- | --- | --- |
| `Composition` | First-class | Structured document sections; may map to ClinicalDocument/document sections. |
| `DocumentManifest` | First-class | Document package/index; link to ClinicalDocument/DocumentReference. |
| `DocumentReference` | First-class | Maps to `ClinicalDocument`; stores attachments and relationships. |

### Other

| Resource | Status | Notes |
| --- | --- | --- |
| `CatalogEntry` | First-class | Catalog metadata. |
| `Basic` | First-class | Generic extension resource. |
| `Binary` | First-class | Needed for external/inline document or media content. |
| `Bundle` | Parser/container | Extracted into contained resources; not stored as a model. |
| `Linkage` | First-class | Resource identity/linkage metadata. |
| `MessageHeader` | First-class | Messaging envelope. |
| `OperationOutcome` | First-class | Error/result payload. |
| `Parameters` | First-class | Operation parameters. |
| `Subscription` | First-class | Server subscription metadata. |

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
| `OrganizationAffiliation` | First-class | Organization-to-organization/service relationships. |
| `HealthcareService` | First-class | Services offered by organizations/locations. |
| `Endpoint` | First-class | Technical endpoint; likely interop/directory support. |
| `Location` | First-class | Directory/site resource. |

### Entities #2

| Resource | Status | Notes |
| --- | --- | --- |
| `Substance` | First-class | Useful for allergies/medications/labs; likely catalog-style. |
| `BiologicallyDerivedProduct` | First-class | Blood/tissue/product details. |
| `Device` | First-class | Patient/device inventory and references. |
| `DeviceMetric` | First-class | Device measurement channels/configuration. |

### Workflow Management

| Resource | Status | Notes |
| --- | --- | --- |
| `Task` | First-class | Workflow/reminders/imported tasks. |
| `Appointment` | First-class | Scheduling/calendar support. |
| `AppointmentResponse` | First-class | Appointment participant response. |
| `Schedule` | First-class | Availability schedule. |
| `Slot` | First-class | Bookable time slot. |
| `VerificationResult` | First-class | Verification metadata. |
| `Encounter` | First-class | Visit/action record. |
| `EpisodeOfCare` | First-class | Larger care episode grouping. |
| `Flag` | First-class | Patient warnings/alerts. |
| `List` | First-class | FHIR lists/groupings of resources. |
| `Library` | First-class | Knowledge artifact. |

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
| `Media` | First-class | Clinical images/photos/media. |
| `DiagnosticReport` | First-class | Diagnostic reports with encounter, requests, specimens, observations, performers, interpreters, and presented forms. |
| `Specimen` | First-class | Lab specimen details. |
| `BodyStructure` | First-class | Anatomical/body-site detail. |
| `ImagingStudy` | First-class | Imaging study/series/instance data. |
| `QuestionnaireResponse` | First-class | Patient-entered forms and assessments. |
| `MolecularSequence` | First-class | Genomics sequence, variant, repository, and quality details. |

### Medications

| Resource | Status | Notes |
| --- | --- | --- |
| `MedicationRequest` | First-class | Currently maps into local `Medication`. |
| `MedicationAdministration` | First-class | Administered medication event. |
| `MedicationDispense` | First-class | Pharmacy/supply dispense event. |
| `MedicationStatement` | First-class | Currently maps into local `Medication`. |
| `Medication` | First-class | Standalone medication catalog/details; maps to `MedicationCatalog`, separate from requests/statements. |
| `MedicationKnowledge` | First-class | Drug knowledge/catalog metadata, ingredients, monitoring, and classifications. |
| `Immunization` | First-class | Vaccination records. |
| `ImmunizationEvaluation` | First-class | Immunization validity/status evaluation. |
| `ImmunizationRecommendation` | First-class | Vaccine forecast/recommendations. |

### Care Provision

| Resource | Status | Notes |
| --- | --- | --- |
| `CarePlan` | First-class | Care plans with conditions/care teams. |
| `CareTeam` | First-class | Care teams and participants. |
| `Goal` | First-class | Patient/care goals with addressed concerns, targets, and outcomes. |
| `ServiceRequest` | First-class | Orders/referrals/requested services. |
| `NutritionOrder` | First-class | Dietary/oral/enteral/supplement orders. |
| `VisionPrescription` | First-class | Vision prescription details. |
| `RiskAssessment` | First-class | Risk predictions/probabilities with basis records and mitigation. |
| `RequestGroup` | First-class | Grouped/conditional requests and plans. |

### Request & Response

| Resource | Status | Notes |
| --- | --- | --- |
| `Communication` | First-class | Care communications/messages. |
| `CommunicationRequest` | First-class | Requested communication. |
| `DeviceRequest` | First-class | Device orders/requests with reasons, performers, and timing. |
| `DeviceUseStatement` | First-class | Patient/device usage history. |
| `GuidanceResponse` | First-class | Decision-support response. |
| `SupplyRequest` | First-class | Supply request. |
| `SupplyDelivery` | First-class | Supply delivery event. |

## Financial

### Support

| Resource | Status | Notes |
| --- | --- | --- |
| `Coverage` | First-class | Insurance coverage, subscriber IDs, payer details, and benefit classifications. |
| `CoverageEligibilityRequest` | First-class | Eligibility request. |
| `CoverageEligibilityResponse` | First-class | Eligibility response. |
| `EnrollmentRequest` | First-class | Enrollment request. |
| `EnrollmentResponse` | First-class | Enrollment response. |

### Billing

| Resource | Status | Notes |
| --- | --- | --- |
| `Claim` | First-class | Claims support if adding insurance/finance. |
| `ClaimResponse` | First-class | Claim adjudication response. |
| `Invoice` | First-class | Billing invoice. |

### Payment

| Resource | Status | Notes |
| --- | --- | --- |
| `PaymentNotice` | First-class | Payment notification. |
| `PaymentReconciliation` | First-class | Payment reconciliation. |

### General

| Resource | Status | Notes |
| --- | --- | --- |
| `Account` | First-class | Billing/account grouping. |
| `ChargeItem` | First-class | Charge line item. |
| `ChargeItemDefinition` | First-class | Charge item definition. |
| `Contract` | First-class | Contract/legal agreement. |
| `ExplanationOfBenefit` | First-class | EOB/claims summary; useful for personal records. |
| `InsurancePlan` | First-class | Insurance plan details. |

## Specialized

### Public Health & Research

| Resource | Status | Notes |
| --- | --- | --- |
| `ResearchStudy` | First-class | Optional research participation area. |
| `ResearchSubject` | First-class | Patient participation in a study. |

### Definitional Artifacts

| Resource | Status | Notes |
| --- | --- | --- |
| `ActivityDefinition` | First-class | Knowledge artifact. |
| `DeviceDefinition` | First-class | Device catalog/definition. |
| `EventDefinition` | First-class | Knowledge artifact. |
| `ObservationDefinition` | First-class | Observation catalog/definition. |
| `PlanDefinition` | First-class | Care plan definition/knowledge artifact. |
| `Questionnaire` | First-class | Form definitions. |
| `SpecimenDefinition` | First-class | Specimen catalog/definition. |

### Evidence-Based Medicine

| Resource | Status | Notes |
| --- | --- | --- |
| `ResearchDefinition` | First-class | Evidence/research metadata. |
| `ResearchElementDefinition` | First-class | Evidence/research metadata. |
| `Evidence` | First-class | Evidence artifact. |
| `EvidenceVariable` | First-class | Evidence variable definition. |
| `EffectEvidenceSynthesis` | First-class | Evidence synthesis. |
| `RiskEvidenceSynthesis` | First-class | Risk evidence synthesis. |

### Quality Reporting & Testing

| Resource | Status | Notes |
| --- | --- | --- |
| `Measure` | First-class | Quality measure definition. |
| `MeasureReport` | First-class | Quality measure report. |
| `TestScript` | First-class | FHIR testing artifact. |
| `TestReport` | First-class | FHIR testing artifact. |

### Medication Definition

| Resource | Status | Notes |
| --- | --- | --- |
| `MedicinalProduct` | First-class | Medication/product definition. |
| `MedicinalProductAuthorization` | First-class | Medication/product definition. |
| `MedicinalProductContraindication` | First-class | Medication/product definition. |
| `MedicinalProductIndication` | First-class | Medication/product definition. |
| `MedicinalProductIngredient` | First-class | Medication/product definition. |
| `MedicinalProductInteraction` | First-class | Medication/product definition. |
| `MedicinalProductManufactured` | First-class | Medication/product definition. |
| `MedicinalProductPackaged` | First-class | Medication/product definition. |
| `MedicinalProductPharmaceutical` | First-class | Medication/product definition. |
| `MedicinalProductUndesirableEffect` | First-class | Medication/product definition. |
| `SubstanceNucleicAcid` | First-class | Substance definition. |
| `SubstancePolymer` | First-class | Substance definition. |
| `SubstanceProtein` | First-class | Substance definition. |
| `SubstanceReferenceInformation` | First-class | Substance definition. |
| `SubstanceSpecification` | First-class | Substance definition. |
| `SubstanceSourceMaterial` | First-class | Substance definition. |

## Next Completeness Step

The app preserves unsupported but well-formed FHIR R4 resources as valid `FHIRResourceSnapshot` rows with `import_status="snapshot_only"`. First-class models can then be added selectively based on real imported data and patient-facing value.





