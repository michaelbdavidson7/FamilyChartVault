# Go-Live Todo

This app handles health data. Treat go-live as a staged launch: first private/local use, then trusted test users, then broader distribution only after the security, backup, validation, and support items are done.

## 0. Launch Decision Gates

- [ ] Define the first go-live target
  - [ ] Local-only personal use
  - [ ] Desktop app for one user
  - [ ] Small trusted beta
  - [ ] Public multi-user hosted app
- [ ] Decide whether this is a personal record viewer, a patient-held record tool, or a clinical workflow tool
- [ ] Decide whether the app will ever be used for medical decision-making
- [ ] Decide whether imported FHIR JSON snapshots are the legal/source-of-truth export, or whether model-serialized exports must become fully conformant
- [ ] Create a written "known limitations" page for users
- [ ] Create a release checklist that must be completed before every packaged release

## 1. Security & Privacy Before Go-Live

- [ ] Store database encryption key in OS keychain / credential vault
- [ ] Store Django `SECRET_KEY` in OS keychain or protected app config
- [ ] Confirm `DEBUG = False` behavior in packaged/release builds without breaking bundled admin/static assets
- [ ] Confirm production `ALLOWED_HOSTS`, CSRF trusted origins, secure cookies, and session settings
- [ ] Add a first-run secret/key generation flow for desktop/local installs
- [ ] Add a recovery-key export flow for encrypted database backups
- [ ] Add encrypted backup restore flow and test it with real sample data
- [ ] Add database backup rotation policy
- [ ] Add a user-visible "Export before upgrade" recommendation
- [ ] Confirm uploaded/imported files cannot escape expected directories
- [ ] Confirm ZIP import rejects path traversal entries
- [ ] Confirm uploaded JSON/NDJSON size limits
- [ ] Confirm PDF export size limits and timeout behavior
- [ ] Add audit logging for import, export, delete, backup, restore, and settings changes
- [ ] Hide secrets and PHI from logs, errors, and debug output
- [ ] Add explicit privacy warning before exporting ZIP/PDF files
- [ ] Add an emergency "lock app / clear session" action if relevant

## 2. Legal, Safety, and User Trust

- [ ] Review `DISCLAIMER.md` for plain-language medical/legal limitations
- [ ] Add in-app disclaimer: this is not a substitute for professional medical advice
- [ ] Add in-app disclaimer: imported/exported records may be incomplete or transformed
- [ ] Add in-app disclaimer: users should verify critical data with their clinician
- [ ] Add a "How to share with your doctor" guide
- [ ] Add a "What is included in exports" guide
- [ ] Add a "What is not included or may be simplified" guide
- [ ] Add a "Delete my data" / local data removal guide
- [ ] Decide whether HIPAA, GDPR, or state privacy obligations apply to the intended deployment
- [ ] If hosted or multi-user, complete a real legal/security review before launch

## 3. FHIR Import Readiness

- [ ] Keep `FHIRResourceSnapshot` as the raw source-of-truth copy for imported FHIR
- [ ] Validate incoming resources against local R4 schema where practical: `fhir/schema/r4/fhir.schema.json`
- [ ] Add import report that separates:
  - [ ] first-class imported resources
  - [ ] snapshot-only resources
  - [ ] invalid resources
  - [ ] unresolved references
  - [ ] duplicate resources
- [ ] Add unsupported-resource dashboard with resource type counts and example IDs
- [ ] Improve FHIR snapshot retention and import history
  - [ ] Do not create duplicate `FHIRResourceSnapshot` when `resource_type` / `resource_id` / `source` / checksum are unchanged
  - [ ] Still create a new snapshot when raw FHIR checksum changes
  - [ ] Add `ImportBatch` model for each upload/import run
  - [ ] Link snapshots to `ImportBatch`
  - [ ] Add admin summary for import batches: created / updated / snapshot-only / invalid counts
  - [ ] Add cleanup/compaction action for duplicate historical snapshots created during development imports
- [ ] Add import conflict handling for same resource ID from different sources
- [ ] Add import rollback or "delete this import batch" flow
- [ ] Add large ZIP progress/status UI if imports can take a while
- [ ] Add tests for malformed JSON, NDJSON, Bundle, ZIP, duplicate resources, and missing `resourceType`
- [ ] AllergyIntolerance orphan strategy: parser exists, but sample allergies can reference missing Patient IDs
- [ ] CareTeam sample coverage: importer exists, but current development sample zip may not contain CareTeam resources

## 4. FHIR Export Readiness

- [ ] Decide export modes clearly
  - [ ] Raw snapshot export: highest fidelity to imported data
  - [ ] Model-serialized export: app-created/edited data, currently partial
  - [ ] Medical summary PDF: human-readable, not a full FHIR export
- [ ] Make the exporter page visibly explain the difference between raw snapshots and model-serialized resources
- [ ] Add full JSON Schema validation for model-serialized exports using `fhir/schema/r4/fhir.schema.json`
- [ ] Add schema validation tests for every model-backed serializer
- [ ] Add exporter warnings when a model resource cannot be serialized as valid FHIR
- [ ] Add export manifest details for validation status and omitted/simplified fields
- [ ] Add per-resource serializer coverage beyond the current first pass
- [ ] Ensure model-created data does not silently disappear from export
- [ ] Add export tests for patient-filtered ZIPs and whole-database ZIPs
- [ ] Add export tests for resources with unresolved FK/M2M references
- [ ] Add export tests for empty optional fields so invalid empty arrays/objects are not emitted
- [ ] Add stable resource IDs for exported local models, not only database PKs if portability matters
- [ ] Add provenance/source metadata where useful
- [ ] Add user-facing "FHIR export is technical data for receiving systems" note

## 5. Current Model-Serialized Export Work

- [x] Add first model-backed FHIR serializers
- [x] Include local model resources in ZIP when requested
- [x] Add local R4 schema file: `fhir/schema/r4/fhir.schema.json`
- [x] Fix obvious R4 issues in current serializers: Encounter class, invalid plain-text narrative, enum normalization
- [x] Add focused regression tests for required fields and enum normalization
- [ ] Add real JSON Schema validation dependency or lightweight validator wrapper
- [ ] Expand serializers resource-by-resource instead of guessing all at once
- [ ] Serialize `Practitioner`, `Organization`, `Location`, `CareTeam`, `RelatedPerson`, `Person`, and `Group`
- [ ] Serialize `DocumentReference` / clinical documents correctly, including Binary attachments strategy
- [ ] Serialize relationships as real FHIR references where local FK/M2M exists
- [ ] Add a serializer conformance matrix to `FHIR_RESOURCE_SUPPORT.md`

## 6. Medical Summary PDF Readiness

- [ ] Keep PDF as human-readable summary, not "full export"
- [ ] Include actual data, not counts, for selected sections
- [ ] Keep default checked sections: allergies, medications, conditions
- [ ] Add optional sections for vitals/labs, visits/actions, immunizations, procedures, care team, documents, insurance
- [ ] Limit very large sections with "recent only" default and clear "include all" option
- [ ] Add date range controls
- [ ] Improve vitals/labs grouping by name and date
- [ ] Add doctor-friendly cover page with patient demographics, emergency contact, and generated date
- [ ] Add "source/last updated" line per section where possible
- [ ] Add PDF tests for common and large patients
- [ ] Add print/readability review

## 7. Patient Profile UX Before Go-Live

- [ ] Make patient profile usable for technology beginners
- [ ] Keep clear buttons for opening detail pages; avoid misleading patient-name links
- [ ] Make "all patient resources" page polished and easy to scan
- [ ] Ensure patient resource tiles link to filtered list pages
- [ ] Ensure all embedded patient profile views sort most recent first
- [ ] Limit visit/action rows on the profile page with link to full list
- [ ] Use human-readable dates everywhere on patient profile
- [ ] Improve empty states and "no data yet" messages
- [ ] Add clear "data came from import / entered locally" indicators
- [ ] Add quick card for medications, allergies, and conditions
- [ ] Create a paramedic/emergency view
- [ ] Add caregiver/shareable summary view if desired

## 8. Admin & Navigation Cleanup

- [x] Normal person clinical dashboard, with admin pages mostly hidden but relevant ones shown as Clinical Resources
- [x] Add FHIR Explorer / full admin area for technical resources
- [ ] Significant cleanup of admin page links needed
- [ ] Reconsider whether every model should be a first-class admin sidebar page
- [ ] Hide low-level/simple FHIR resources from primary sidebar
- [ ] Keep a complete "All FHIR Resources" explorer page for advanced use
- [ ] Fix admin links for simple/generic resources added in bulk:
  - [ ] CatalogEntry
  - [ ] Basic
  - [ ] Linkage
  - [ ] MessageHeader
  - [ ] OperationOutcome
  - [ ] Parameters
  - [ ] Subscription
  - [ ] BiologicallyDerivedProduct
  - [ ] VerificationResult
  - [ ] ChargeItemDefinition
  - [ ] Contract
  - [ ] ResearchDefinition
  - [ ] ResearchElementDefinition
  - [ ] Evidence
  - [ ] EvidenceVariable
  - [ ] EffectEvidenceSynthesis
  - [ ] RiskEvidenceSynthesis
  - [ ] MedicinalProduct* resources
  - [ ] SubstanceDefinition resources
- [ ] Audit all inlines for layout issues on small and large screens
- [ ] Keep custom admin CSS simpler; remove one-off hacks where possible

## 9. FHIR Resource Coverage

- [x] Generic FHIR resource fallback: accept every FHIR `resourceType` into valid `FHIRResourceSnapshot` even when no first-class model exists
- [x] CarePlan
- [x] Procedure
- [x] DiagnosticReport
- [x] ServiceRequest
- [x] Specimen
- [x] EpisodeOfCare
- [x] PractitionerRole
- [x] Device
- [x] DeviceMetric
- [x] Binary
- [x] Medication
- [x] ImagingStudy
- [x] Media
- [x] Goal
- [x] RiskAssessment
- [x] ClinicalImpression
- [x] FamilyMemberHistory
- [x] AdverseEvent
- [x] DetectedIssue
- [x] BodyStructure
- [x] MedicationAdministration
- [x] MedicationDispense
- [x] DeviceRequest
- [x] DeviceUseStatement
- [x] NutritionOrder
- [x] MedicationKnowledge
- [x] Substance
- [x] ImmunizationEvaluation
- [x] ImmunizationRecommendation
- [x] Questionnaire
- [x] QuestionnaireResponse
- [x] Communication
- [x] CommunicationRequest
- [x] RequestGroup
- [x] GuidanceResponse
- [x] Flag
- [x] List
- [x] Composition
- [x] DocumentManifest
- [x] RelatedPerson
- [x] Person
- [x] Group
- [x] HealthcareService
- [x] Endpoint
- [x] OrganizationAffiliation
- [x] Appointment
- [x] AppointmentResponse
- [x] Schedule
- [x] Slot
- [x] Task
- [x] Provenance
- [x] Consent
- [ ] AuditEvent: security/audit events; probably system-level rather than clinical UI
- [x] Coverage
- [x] ExplanationOfBenefit
- [x] InsurancePlan
- [x] Claim
- [x] ClaimResponse
- [x] Account
- [x] Invoice
- [x] SupplyRequest
- [x] SupplyDelivery
- [x] MolecularSequence
- [x] ResearchStudy
- [x] ResearchSubject
- [x] DeviceDefinition
- [x] ObservationDefinition
- [x] ChargeItem
- [ ] Continue reviewing `FHIR_RESOURCE_SUPPORT.md` against official R4 categories
- [ ] Add another clarifying pass through every FHIR resource documentation page
- [ ] Decide which low-value definitional resources stay snapshot-only forever

## 10. Resource Relationships To Add or Verify

- [ ] Simplification rule: keep `FHIRResourceSnapshot` as source of truth for full JSON even when local models flatten uncommon fields
- [ ] Simplification rule: keep text fallback fields during migrations so unresolved references and human-entered records still display well
- [ ] Observation relationships
  - [ ] `Observation.encounter` -> `Encounter`
  - [x] `Observation.specimen` -> `Specimen`
  - [x] `Observation.device` -> `Device`
  - [ ] `Observation.performers` -> Practitioner / Organization / CareTeam
- [ ] Document relationships
  - [x] `ClinicalDocument.encounter` -> `Encounter`
  - [x] `ClinicalDocument.authors` -> `Practitioner`
  - [x] `ClinicalDocument.custodian` -> `Organization`
  - [x] `ClinicalDocument.related_documents` -> `ClinicalDocument`
- [ ] Medication relationships
  - [ ] `Medication.encounter` -> `Encounter`
  - [ ] `Medication.prescriber` -> Practitioner / Organization / Patient / RelatedPerson / PractitionerRole
  - [ ] `Medication.indications` -> `Condition`
  - [ ] `Medication.based_on_service_requests` -> `ServiceRequest`
- [ ] Immunization relationships
  - [ ] `Immunization.encounter` -> `Encounter`
  - [ ] `Immunization.performers` -> Practitioner / Organization / PractitionerRole
  - [ ] `Immunization.reasons` -> Condition / Observation / DiagnosticReport
  - [ ] Decide where vaccine consent is represented: likely `Consent` referencing Immunization / ServiceRequest / Patient
- [ ] Encounter relationships
  - [ ] `Encounter.participants` -> Practitioner / PractitionerRole
  - [ ] `Encounter.service_provider` -> `Organization`
  - [ ] `Encounter.locations` -> `Location`
  - [ ] `Encounter.reason_references` -> Condition / Procedure / Observation / ImmunizationRecommendation
  - [ ] `Encounter.episode_of_care` -> `EpisodeOfCare`
  - [ ] `Encounter.based_on_service_requests` -> `ServiceRequest`
- [ ] Directory relationships
  - [ ] `Location.managing_organization` -> `Organization`
  - [ ] `Location.part_of` -> `Location`
  - [ ] `PractitionerRole` -> Practitioner / Organization / Location
  - [ ] `RelatedPerson.person` -> `Person` where appropriate, without forcing every RelatedPerson to be a Person
- [ ] Care team relationships
  - [x] `CareTeam.managing_organizations` -> `Organization`
  - [x] `CareTeam.participants` -> Practitioner / Organization / Location
  - [ ] Add PractitionerRole support to CareTeam participants
  - [ ] `CareTeam.encounter` -> `Encounter`
  - [ ] `CareTeam.reasons` -> `Condition`
- [ ] Condition relationships
  - [ ] `Condition.encounter` -> `Encounter`
  - [ ] `Condition.evidence` -> Observation / DiagnosticReport / etc.
- [ ] DiagnosticReport relationships
  - [x] `DiagnosticReport.encounter` -> `Encounter`
  - [x] `DiagnosticReport.results` -> `Observation`
  - [x] `DiagnosticReport.specimens` -> `Specimen`
  - [x] `DiagnosticReport.presentedForm` -> `ClinicalDocument`
- [ ] ServiceRequest relationships
  - [ ] `ServiceRequest.encounter` -> `Encounter`
  - [ ] `ServiceRequest.requester` -> Practitioner / Organization / PractitionerRole
  - [ ] `ServiceRequest.reason_references` -> Condition / Observation / DiagnosticReport / DocumentReference
- [ ] Procedure relationships
  - [x] `Procedure.encounter` -> `Encounter`
  - [x] `Procedure.performers` -> Practitioner / Organization
  - [x] `Procedure.reason_references` -> `Condition`
  - [ ] Expand Procedure reasons to Observation / Procedure / DiagnosticReport / DocumentReference

## 11. Data Quality & Clinical Safety

- [ ] Add duplicate detection for imported patients/resources
- [ ] Add patient matching review UI when imported Patient does not clearly match existing profile
- [ ] Add unresolved-reference report per patient
- [ ] Add missing/unknown value handling that is visible to users
- [ ] Add data source labels for imported vs local records
- [ ] Add last-imported timestamp per patient/resource
- [ ] Add "this record may be incomplete" warning for snapshot-only resources
- [ ] Add unit normalization strategy for vitals/labs only if it can be done safely
- [ ] Avoid silently converting clinical codes without retaining original coding
- [ ] Keep original FHIR coding/system/display wherever possible

## 12. Testing Before Go-Live

- [ ] Run full Django test suite
- [ ] Add test coverage for patient profile resource page
- [ ] Add test coverage for FHIR import page
- [ ] Add test coverage for FHIR export page
- [ ] Add test coverage for medical summary PDF options
- [ ] Add tests for encrypted DB behavior if available in test env
- [ ] Add tests for backup/restore
- [ ] Add Playwright or screenshot checks for core admin/profile pages if practical
- [ ] Test tiny viewport, laptop viewport, and wide desktop viewport
- [ ] Test import/export with Synthea sample patients
- [ ] Test import/export with the real development ZIP after removing/avoiding PHI in test artifacts
- [ ] Test app startup from a clean install
- [ ] Test app upgrade with an existing database
- [ ] Test app behavior when schema migrations are pending
- [ ] Test no-network/local-only mode if this is a desktop app

## 13. Deployment / Desktop Packaging

- [ ] Decide exact release packaging path: Django local server, Tauri desktop, hosted web app, or both
- [ ] Verify static files in release build
- [ ] Verify migrations run safely on startup or through an explicit upgrade step
- [ ] Verify database location, media location, and backup location in packaged app
- [ ] Verify app does not depend on dev-only files like `.env`, local schema downloads, or test data
- [ ] Add version display in the UI
- [ ] Add release notes/changelog process
- [ ] Add crash/error report strategy that does not leak PHI
- [ ] Add "export all data before uninstall" instructions

## 14. Documentation

- [ ] Update `README.md` for install/run/import/export basics
- [ ] Update `SECURITY.md` with local-data and encryption notes
- [ ] Update `CONTRIBUTING.md` with FHIR serializer/schema expectations
- [ ] Update `FHIR_RESOURCE_SUPPORT.md` after every resource support change
- [ ] Add short user docs for:
  - [ ] Importing FHIR files
  - [ ] Viewing patient records
  - [ ] Exporting FHIR ZIP
  - [ ] Exporting medical summary PDF
  - [ ] Sharing data with a doctor
  - [ ] Backing up and restoring data
  - [ ] Understanding limitations

## 15. Nice-To-Have After First Go-Live

- [ ] Add dietary component
- [ ] Add medication/allergy/condition quick emergency card
- [ ] Add richer consent workflows, including vaccine/procedure consent
- [ ] Add insurance-focused summary page for Coverage / EOB / Claims
- [ ] Add import preview before committing data
- [ ] Add resource diff viewer between import batches
- [ ] Add patient timeline view
- [ ] Add smarter search across all patient resources
- [ ] Add accessibility pass for keyboard/screen-reader use
- [ ] Add localization/date-format settings
