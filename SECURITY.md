# Security Policy

HolyFHIR Personal EMR handles sensitive health information. Please report security issues privately and do not include personal health information, real medical records, database files, recovery keys, passwords, access tokens, logs with secrets, screenshots with identifiable information, or portal exports in public issues, pull requests, discussions, or commits.

## Reporting A Vulnerability

If you find a security vulnerability, please contact the maintainer privately before opening a public issue.

Preferred contact:

- GitHub Security Advisory for this repository, if available
- Otherwise, contact the maintainer through the most direct private channel available from the repository owner profile

Please include:

- A short description of the issue
- Steps to reproduce using synthetic data only
- The affected version, commit, or build
- Any relevant logs with secrets and health information removed
- Your assessment of the impact

Please do not publicly disclose the issue until there has been a reasonable opportunity to investigate and release a fix.

## Sensitive Data

Do not share real patient data when reporting bugs or security issues. This includes:

- Names, dates of birth, addresses, phone numbers, email addresses, identifiers, account numbers, or MRNs
- Medical conditions, medications, allergies, immunizations, lab results, observations, encounters, documents, or notes
- FHIR bundles, MyChart exports, PDFs, images, database files, backups, or logs from real use
- Passwords, recovery keys, `.env` files, encryption keys, access tokens, cookies, or session data

Use synthetic examples that cannot be linked to a real person.

## Supported Versions

HolyFHIR is early open-source software. Security fixes are generally made on the main development branch unless release branches are explicitly published.

## User Responsibilities

HolyFHIR is intended for local, personal recordkeeping and is not represented as HIPAA-compliant, certified, audited, or appropriate for regulated use. Users are responsible for protecting their devices, passwords, recovery keys, backups, exports, database files, and any sensitive health information they store or share.
