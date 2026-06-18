[ ] store database encryption key in OS keychain / credential vault
[ ] store Django SECRET_KEY in OS keychain or protected app config
[ ] recovery-key export flow for encrypted database backups
[ ] decide release-build DEBUG behavior without breaking bundled admin/static assets
[ ] export quick card for medications, allergies, and conditions 
[ ] create a full paramedic view
[ ] add more FHIR resources
    [ ] Procedure - high priority; patient-facing care history such as surgeries, imaging procedures, treatments, and completed actions
    [ ] DiagnosticReport - high priority; groups labs/imaging reports and can point to observations, documents, and specimens
    [ ] ServiceRequest - medium-high priority; orders, referrals, and requested services tied to encounters/procedures
    [ ] Specimen - medium priority; supporting data for labs and diagnostic reports
    [ ] EpisodeOfCare - medium priority; groups visits/actions into a larger care episode
    [ ] PractitionerRole - medium priority; connects practitioners to organizations, specialties, locations, and roles
    [ ] Device - lower-medium priority; implanted devices, medical equipment, and patient devices
    [ ] Binary - seen in older invalid snapshots; decide whether to import as document attachments or keep as snapshots
    [ ] Medication - seen in older invalid snapshots; decide whether to map to medication catalog/details or keep using MedicationRequest/MedicationStatement only
    [ ] AllergyIntolerance orphan strategy - parser exists, but sample allergies reference patient IDs missing from Patient.000.ndjson
    [ ] CareTeam sample coverage - importer exists, but the development sample zip has no CareTeam resources
[ ] add a dietary component
