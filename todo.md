[ ] store database encryption key in OS keychain / credential vault
[ ] store Django SECRET_KEY in OS keychain or protected app config
[ ] recovery-key export flow for encrypted database backups
[ ] decide release-build DEBUG behavior without breaking bundled admin/static assets
[ ] export quick card for medications, allergies, and conditions 
[ ] create a full paramedic view
[ ] improve FHIR snapshot retention and import history
    [ ] do not create a duplicate FHIRResourceSnapshot when resource_type/resource_id/source/checksum are unchanged
    [ ] still create a new snapshot when the raw FHIR checksum changes
    [ ] add an ImportBatch model for each upload/import run
    [ ] link snapshots to ImportBatch so repeated imports can be audited without duplicating identical JSON forever
    [ ] add admin summary for import batches: created/updated/snapshot-only/invalid counts
    [ ] add cleanup/compaction action for duplicate historical snapshots created during development imports
[ ] add more FHIR resources
    [x] CarePlan - care plans with condition/care-team relationships
    [x] Procedure - high priority; patient-facing care history such as surgeries, imaging procedures, treatments, and completed actions
    [ ] DiagnosticReport - high priority; groups labs/imaging reports and can point to observations, documents, and specimens
    [x] ServiceRequest - medium-high priority; orders, referrals, and requested services tied to encounters/procedures
    [x] Specimen - medium priority; supporting data for labs and diagnostic reports
    [x] EpisodeOfCare - medium priority; groups visits/actions into a larger care episode
    [x] PractitionerRole - medium priority; connects practitioners to organizations, specialties, locations, and roles
    [x] Device - lower-medium priority; implanted devices, medical equipment, and patient devices
    [ ] Binary - seen in older invalid snapshots; decide whether to import as document attachments or keep as snapshots
    [ ] Medication - seen in older invalid snapshots; decide whether to map to medication catalog/details or keep using MedicationRequest/MedicationStatement only
    [ ] ImagingStudy - imaging studies/series/instances; link to DiagnosticReport, Encounter, Procedure, and Media where possible
    [ ] Media - clinical photos, imaging key images, waveforms, or other captured media; link to Patient/Encounter/Procedure
    [ ] Goal - patient/care-team goals; link to CarePlan, Conditions, and lifecycle status
    [ ] RiskAssessment - risk predictions and probabilities; link to Conditions/Observations/Encounter
    [ ] ClinicalImpression - clinician assessment/synthesis; link to findings, problems, investigations, and plans
    [ ] FamilyMemberHistory - family history conditions and relationships
    [ ] AdverseEvent - harmful events and contributing products/substances/procedures
    [ ] DetectedIssue - clinical safety/quality issues such as drug interactions or duplicate therapy
    [ ] BodyStructure - body site details used by Procedure, Observation, ImagingStudy, etc.
    [ ] MedicationAdministration - administered meds; distinct from medication orders/statements
    [ ] MedicationDispense - dispensed meds; pharmacy/supply event distinct from orders/statements
    [ ] DeviceRequest - orders/requests for devices
    [ ] DeviceUseStatement - patient/device usage history
    [ ] NutritionOrder - dietary/oral/enteral/supplement orders; likely pairs with dietary component
    [ ] MedicationKnowledge - drug knowledge/catalog metadata; probably snapshot/generic first, first-class later only if needed
    [ ] Medication-related definitional resources - MedicinalProduct*, Substance*, MedicationKnowledge; probably snapshot/generic unless building a medication knowledge base
    [ ] ImmunizationEvaluation - immunization validity/status evaluation
    [ ] ImmunizationRecommendation - vaccine forecast/recommendations
    [ ] QuestionnaireResponse - patient-entered forms and assessments
    [ ] Questionnaire - form definitions for QuestionnaireResponse
    [ ] Communication - messages/communications about care
    [ ] CommunicationRequest - requested communications
    [ ] RequestGroup - grouped/conditional requests and plans
    [ ] GuidanceResponse - decision-support output
    [ ] Flag - warnings/alerts on patient records
    [ ] List - FHIR lists/groupings of clinical resources
    [ ] Composition - structured clinical documents; may map to ClinicalDocument or document sections
    [ ] DocumentManifest - document package/index; link to ClinicalDocument/DocumentReference
    [ ] RelatedPerson - caregivers/family/proxies related to patient
    [ ] Person - cross-resource person identity; probably snapshot/generic unless identity reconciliation is needed
    [ ] Group - patient/care cohorts; likely snapshot/generic for personal EMR
    [ ] HealthcareService - services offered by organizations/locations
    [ ] Endpoint - technical service endpoints; likely directory/interop support
    [ ] OrganizationAffiliation - relationships between organizations and services
    [ ] Appointment, AppointmentResponse, Schedule, Slot - scheduling resources; useful if we add appointments/calendar
    [ ] Task - workflow task tracking; useful later for reminders/to-dos/imported tasks
    [ ] Provenance - source/audit provenance; important for trust/history, can attach to snapshots/links
    [ ] Consent - patient consents/privacy choices
    [ ] AuditEvent - security/audit events; probably system-level rather than clinical UI
    [ ] Coverage, Claim, ClaimResponse, ExplanationOfBenefit, Account, Invoice - financial/insurance resources; optional personal finance/claims area
    [ ] SupplyRequest and SupplyDelivery - supplies and delivery events
    [ ] MolecularSequence - genetics/genomics; snapshot/generic unless genomics UI is planned
    [ ] ResearchStudy and ResearchSubject - research participation; optional
    [x] Generic FHIR resource fallback - accept every FHIR resourceType into valid FHIRResourceSnapshot even when no first-class model exists
    [ ] Unsupported-resource dashboard - show resource types/counts imported only as snapshots, with "promote to model later" notes
    [ ] AllergyIntolerance orphan strategy - parser exists, but sample allergies reference patient IDs missing from Patient.000.ndjson
    [ ] CareTeam sample coverage - importer exists, but the development sample zip has no CareTeam resources
[ ] add relationships between imported resources
    [ ] Observation.encounter -> Encounter
        [ ] FHIR source: Observation.encounter
        [ ] Django shape: Observation.encounter nullable FK to Encounter, related_name="observations"
        [ ] Use case: show vitals/labs/results on the visit where they happened
    [ ] Observation.performers -> Practitioner/Organization/CareTeam
        [ ] FHIR source: Observation.performer
        [ ] Django shape: likely M2M through a generic-ish participant table or separate optional text/reference fields for now
        [ ] Use case: who was responsible for a lab/vital/result
    [x] Observation.specimen -> Specimen
        [ ] FHIR source: Observation.specimen
        [x] Django shape: Observation.specimen nullable FK to Specimen
        [ ] Use case: connect lab results to specimen/source material
    [x] Observation.device -> Device
        [ ] FHIR source: Observation.device
        [x] Django shape: Observation.device nullable FK to Device
        [ ] Use case: connect readings to measuring device
    [x] ClinicalDocument.encounter -> Encounter
        [ ] FHIR source: DocumentReference.context.encounter
        [x] Django shape: ClinicalDocument.encounter nullable FK to Encounter, related_name="documents"
        [ ] Use case: show notes/documents on the visit where they were created
    [x] ClinicalDocument.authors -> Practitioner
        [ ] FHIR source: DocumentReference.author
        [x] Django shape: M2M to Practitioner, with source_name fallback
        [ ] Use case: who wrote or generated the document
    [x] ClinicalDocument.custodian -> Organization
        [ ] FHIR source: DocumentReference.custodian
        [x] Django shape: ClinicalDocument.custodian nullable FK to Organization
        [ ] Use case: organization that maintains the document
    [x] ClinicalDocument.related_documents -> ClinicalDocument
        [ ] FHIR source: DocumentReference.relatesTo
        [x] Django shape: self M2M; relationship code can be added later if needed
        [ ] Use case: preserve document version/replacement relationships
    [ ] Medication.encounter -> Encounter
        [ ] FHIR source: MedicationRequest.encounter; MedicationStatement.context can reference Encounter/EpisodeOfCare
        [ ] Django shape: Medication.encounter nullable FK to Encounter, related_name="medications"
        [ ] Use case: show prescriptions/medication changes from a visit
    [ ] Medication.prescriber -> Practitioner/Organization/Patient/RelatedPerson/PractitionerRole
        [ ] FHIR source: MedicationRequest.requester
        [ ] Django shape: start with nullable Practitioner FK plus prescriber text fallback; later support PractitionerRole/Organization
        [ ] Use case: replace prescriber text with a real directory relationship where possible
    [ ] Medication.indications -> Condition
        [ ] FHIR source: MedicationRequest.reasonReference and MedicationStatement.reasonReference
        [ ] Django shape: M2M to Condition, related_name="related_medications"
        [ ] Use case: answer "what is this medication for?"
    [ ] Medication.based_on_service_requests -> future ServiceRequest
        [ ] FHIR source: MedicationRequest.basedOn
        [ ] Django shape: M2M once ServiceRequest is supported
        [ ] Use case: connect prescriptions to originating orders/plans
    [ ] Immunization.encounter -> Encounter
        [ ] FHIR source: Immunization.encounter
        [ ] Django shape: Immunization.encounter nullable FK to Encounter, related_name="immunizations"
        [ ] Use case: show vaccines given during a visit
    [ ] Immunization.performers -> Practitioner/Organization/PractitionerRole
        [ ] FHIR source: Immunization.performer.actor
        [ ] Django shape: M2M through ImmunizationPerformer with function/role text; keep performer text fallback
        [ ] Use case: who administered, ordered, or recorded the vaccine
    [ ] Immunization.reasons -> Condition/Observation/DiagnosticReport
        [ ] FHIR source: Immunization.reasonReference
        [ ] Django shape: start with M2M to Condition; consider generic reference table later
        [ ] Use case: connect vaccines to clinical reasons when present
    [ ] Encounter.participants -> Practitioner/PractitionerRole
        [ ] FHIR source: Encounter.participant.individual
        [ ] Django shape: through model EncounterParticipant with practitioner FK, role, start/end
        [ ] Use case: replace provider_name text and show everyone involved in a visit
    [ ] Encounter.service_provider -> Organization
        [ ] FHIR source: Encounter.serviceProvider
        [ ] Django shape: Encounter.service_provider nullable FK to Organization; keep facility_name fallback
        [ ] Use case: facility or health system responsible for the visit
    [ ] Encounter.locations -> Location
        [ ] FHIR source: Encounter.location.location
        [ ] Django shape: through model EncounterLocation with location FK, status, start/end
        [ ] Use case: where the visit happened, including moves between sites/rooms
    [ ] Encounter.reason_references -> Condition/Procedure/Observation/ImmunizationRecommendation
        [ ] FHIR source: Encounter.reasonReference
        [ ] Django shape: start with M2M to Condition; expand after Procedure/Observation linking is settled
        [ ] Use case: connect visits to diagnoses/problems/reasons
    [ ] Encounter.episode_of_care -> future EpisodeOfCare
        [ ] FHIR source: Encounter.episodeOfCare
        [ ] Django shape: M2M once EpisodeOfCare is supported
        [ ] Use case: group related visits/actions into a care episode
    [ ] Encounter.based_on_service_requests -> future ServiceRequest
        [ ] FHIR source: Encounter.basedOn
        [ ] Django shape: M2M once ServiceRequest is supported
        [ ] Use case: connect visits to originating orders/referrals
    [ ] Location.managing_organization -> Organization
        [ ] FHIR source: Location.managingOrganization
        [ ] Django shape: Location.managing_organization_obj nullable FK to Organization; keep current text field during migration
        [ ] Use case: replace managing_organization text with a real organization relationship
    [ ] Location.part_of -> Location
        [ ] FHIR source: Location.partOf
        [ ] Django shape: Location.parent nullable FK to self
        [ ] Use case: model campus -> building -> clinic -> room hierarchy
    [ ] CareTeam.managing_organizations -> Organization
        [ ] FHIR source: CareTeam.managingOrganization
        [ ] Django shape: already M2M to Organization
        [ ] Use case: organization responsible for the care team
    [ ] CareTeam.participants -> Practitioner/Organization/Location
        [ ] FHIR source: CareTeam.participant.member and participant.onBehalfOf
        [ ] Django shape: already CareTeamParticipant through model for Practitioner/Organization/Location; add PractitionerRole later
        [ ] Use case: directory-backed care team membership
    [ ] CareTeam.encounter -> Encounter
        [ ] FHIR source: CareTeam.encounter
        [ ] Django shape: CareTeam.encounter nullable FK to Encounter
        [ ] Use case: care team specific to a visit/episode context
    [ ] CareTeam.reasons -> Condition
        [ ] FHIR source: CareTeam.reasonReference
        [ ] Django shape: M2M to Condition, related_name="care_teams"
        [ ] Use case: connect care teams to the problems they manage
    [ ] Condition.encounter -> Encounter
        [ ] FHIR source: Condition.encounter
        [ ] Django shape: Condition.encounter nullable FK to Encounter
        [ ] Use case: show where/when a condition was recorded
    [ ] Condition.evidence -> Observation/DiagnosticReport/etc.
        [ ] FHIR source: Condition.evidence.detail
        [ ] Django shape: defer until DiagnosticReport and richer Observation linking exist; likely generic FHIR reference table
        [ ] Use case: supporting evidence for diagnoses/problems
    [ ] Future DiagnosticReport.encounter -> Encounter
        [ ] FHIR source: DiagnosticReport.encounter
        [ ] Django shape: DiagnosticReport.encounter nullable FK once DiagnosticReport is supported
        [ ] Use case: report belongs to a visit
    [ ] Future DiagnosticReport.results -> Observation
        [ ] FHIR source: DiagnosticReport.result
        [ ] Django shape: M2M to Observation
        [ ] Use case: group atomic lab/imaging results into a report
    [ ] Future DiagnosticReport.specimens -> Specimen
        [ ] FHIR source: DiagnosticReport.specimen
        [ ] Django shape: M2M once Specimen is supported
        [ ] Use case: connect reports to specimens
    [ ] Future DiagnosticReport.media/documents -> ClinicalDocument
        [ ] FHIR source: DiagnosticReport.presentedForm and media
        [ ] Django shape: M2M or attached file/document relationship
        [ ] Use case: connect reports to PDFs/images/narrative attachments
    [ ] Future ServiceRequest.encounter -> Encounter
        [ ] FHIR source: ServiceRequest.encounter
        [ ] Django shape: nullable FK once ServiceRequest is supported
        [ ] Use case: order/referral placed during a visit
    [ ] Future ServiceRequest.requester -> Practitioner/Organization
        [ ] FHIR source: ServiceRequest.requester
        [ ] Django shape: nullable Practitioner/Organization relationship or performer-style through table
        [ ] Use case: who ordered/requested the service
    [ ] Future ServiceRequest.reason_references -> Condition/Observation/DiagnosticReport/DocumentReference
        [ ] FHIR source: ServiceRequest.reasonReference
        [ ] Django shape: start with M2M to Condition; expand with generic reference table later
        [ ] Use case: why the order/referral exists
    [x] Procedure.encounter -> Encounter
        [ ] FHIR source: Procedure.encounter
        [x] Django shape: Procedure.encounter nullable FK
        [ ] Use case: completed actions/procedures performed during a visit
    [x] Procedure.performers -> Practitioner/Organization
        [ ] FHIR source: Procedure.performer.actor and performer.onBehalfOf
        [x] Django shape: through model ProcedurePerformer with role/function
        [ ] Use case: who performed the procedure/action
    [x] Procedure.reason_references -> Condition
        [ ] FHIR source: Procedure.reasonReference
        [x] Django shape: M2M to Condition; expand later for Observation/Procedure/DiagnosticReport/DocumentReference
        [ ] Use case: why the procedure/action was done
    [ ] Future PractitionerRole -> Practitioner/Organization/Location
        [ ] FHIR source: PractitionerRole.practitioner, organization, location, specialty
        [ ] Django shape: PractitionerRole model with FKs/M2M to Practitioner, Organization, Location
        [ ] Use case: model a clinician's role at an organization/site instead of only the person
    [ ] Simplification note: keep FHIRResourceSnapshot as source of truth for full FHIR JSON even when local models intentionally flatten or omit uncommon fields
    [ ] Simplification note: keep text fallback fields during migrations so unresolved references and human-entered records still display well
[ ] add a dietary component
