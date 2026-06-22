# HolyFHIR Personal Family EMR

HolyFHIR is a private, local offline-first health-record app for people who want to keep a personal copy of their medical information.

It is meant to help you organize things like patients, medications, allergies, conditions, documents, visits, and imported FHIR records from Epic's MyChart. The app runs on your computer and does not require a cloud account.

HolyFHIR has a permanent free software license that no one can take away from you - even us. Your medical data is YOURS, it is private, and you have permission to access it forever.

![HolyFHIR Personal Family EMR screenshot](https://github.com/user-attachments/assets/a0bf0afa-3c5c-4451-89d8-ea9971fd6b9e)

## Plain-English Summary

- Your data stays on your computer.
- The Windows desktop app includes the backend it needs.
- You can keep records for yourself or family members.
- You can import some FHIR records, including MyChart requested-record exports.
- You can chart numeric observations, such as blood pressure, weight, glucose, or lab values.
- You should still keep the original records from your doctor, hospital, pharmacy, or lab.

## Latest Release

Download the latest Windows installer from the [GitHub Releases page](https://github.com/michaelbdavidson7/personal-emr/releases/latest).

## A Friendly Warning

HolyFHIR is early software. It is not a certified medical record system and should not be your only copy of important health information.

Please treat it like a personal organizer for medical records, not as a replacement for your doctor, patient portal, pharmacy records, or official chart.

HolyFHIR is not medical advice, not a medical device, and not intended for diagnosis, treatment, emergencies, clinical decision support, or medication safety checking. Imported data may be incomplete or incorrect, so always verify important information against official sources.

You are responsible for protecting your local device, password, recovery key, backups, database files, and exported records. If you use HolyFHIR with anyone else's health information, or in any professional or regulated setting, you are responsible for understanding and meeting any applicable privacy, security, consent, retention, licensing, and compliance obligations.

See [DISCLAIMER.md](DISCLAIMER.md) for the full disclaimer.

## Security And Contributions

Please report security issues privately and do not post real health information, secrets, database files, portal exports, or logs from actual use. See [SECURITY.md](SECURITY.md).

Contributions are welcome, but sample data, test fixtures, screenshots, and bug reports must use synthetic data only. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

HolyFHIR Personal EMR is licensed under the MIT License. See [LICENSE](LICENSE).

This software is provided as-is, without warranty of any kind.

## For Friends Testing The Windows App

If someone sent you a HolyFHIR installer:

1. Download the Windows setup `.exe` from the [latest release](https://github.com/michaelbdavidson7/personal-emr/releases/latest).
2. Run the installer.
3. Open **HolyFHIR Personal EMR**.
4. Create your first system user.
5. Save your password and recovery key somewhere safe.

Windows may warn you because the installer is not code-signed yet. That warning is expected for early friend builds.

Do not delete this folder unless you mean to remove local HolyFHIR data:

```text
C:\Users\<you>\AppData\Local\HolyFHIR Personal EMR
```

Useful files in that folder:

- `.env`: local app settings and generated secrets
- `holyfhir.encrypted.sqlite3`: encrypted database
- `holyfhir-desktop.log`: log file for troubleshooting
- `.env.backup.*`: automatic backups made before `.env` changes

## What You Can Track

- Patient profiles
- Conditions
- Allergies
- Medications
- Immunizations
- Vitals and lab results
- Visits, such as office visits or hospital stays
- Clinical documents, such as PDFs and reports
- Imported FHIR resources

On each patient profile, HolyFHIR shows related conditions, allergies, and medications so the most important context is easy to find.

## FHIR Import

FHIR is a healthcare data format. You do not need to understand it to use the import page.

In the app, open:

```text
FHIR / Interop > Import FHIR Data
```

Supported input:

- MyChart `Requested Record` ZIP export
- FHIR JSON Bundle
- single FHIR JSON resource
- NDJSON

Currently mapped resources:

- Patient
- Condition
- AllergyIntolerance
- MedicationStatement
- MedicationRequest
- Immunization
- Observation
- Encounter

HolyFHIR also keeps a raw copy of each imported FHIR resource for traceability.

## Health Trends

Open:

```text
Health Records > Health Trends
```

The chart page lets you:

- choose a patient
- pick up to 6 numeric vitals, labs, or other measurements
- choose a date range
- view a simple offline chart

Only numeric measurements can be charted. Text-only notes are intentionally skipped.

## Passwords And Recovery Keys

HolyFHIR is designed for local use. That means there is no cloud account where someone can reset your password for you.

Please save:

- your app password
- your recovery key
- backups of your data when backup support is finished

If the password, encryption key, and recovery material are all lost, the data may not be recoverable.

## Current Status

HolyFHIR is still early. The biggest things to finish before a wider release are:

- better backup and restore
- friendlier first-run recovery-key setup
- release-build debug/static behavior
- GitHub Actions dependency verification
- more FHIR date/time tests
- signed Windows installer

## Developer Setup

These steps are for people working on the code.

### 1. Clone

```powershell
git clone https://github.com/michaelbdavidson7/holyfhir-personal-family-emr.git
cd holyfhir-personal-family-emr
```

### 2. Create a Python virtual environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Python dependencies

```powershell
pip install -r requirements.txt
```

For desktop packaging:

```powershell
pip install -r requirements-build.txt
```

### 4. Create local secrets

```powershell
python manage.py bootstrap_secrets
```

This creates `.env`, generates the database encryption key, and generates Django's secret key.

If `.env` already exists, HolyFHIR prompts before rewriting it and creates a timestamped backup first:

```text
.env.backup.YYYYMMDD-HHMMSS
```

Do not casually rotate `DATABASE_ENCRYPTION_KEY`. Changing it can make an existing encrypted database unreadable without a migration or restore plan.

### 5. Run migrations

```powershell
python manage.py migrate
```

### 6. Start the Django app

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/admin/
```

## Desktop Development

Install Node dependencies:

```powershell
npm install
```

Install Rust and the Tauri prerequisites:

```text
https://tauri.app/start/prerequisites/
```

Run the desktop app in development:

```powershell
npm run desktop:dev
```

The desktop app starts Django on:

```text
http://127.0.0.1:8787/
```

## Building A Windows Installer

Build the backend and Windows installer:

```powershell
npm run desktop:build
```

The installer is created under:

```text
src-tauri\target\release\bundle\nsis\
```

Share the NSIS setup `.exe`, not the raw `src-tauri\target\release\holyfhir.exe`.

If the build fails with a Windows permission error for `HolyFHIRBackend.exe`, an old backend process is probably still running:

```powershell
Get-Process HolyFHIRBackend -ErrorAction SilentlyContinue | Stop-Process -Force
npm run desktop:build
```

## GitHub Actions Builds

The workflow at `.github/workflows/windows-desktop-build.yml` builds the Windows installer on GitHub Actions.

It runs when:

- pushing a branch named `release/**`
- pushing a tag named `v*`
- manually starting the workflow from the GitHub Actions tab

Branch build:

```powershell
git checkout -b release/v0.1.1
git push origin release/v0.1.1
```

Release build:

```powershell
git tag v0.1.1
git push origin v0.1.1
```

Release-tag builds upload the NSIS installer artifact and attach it to a draft GitHub Release.

## Environment Settings

`.env.example` defines the supported local settings:

- `DJANGO_SETTINGS_MODULE`: Django settings module
- `DJANGO_ENV_FILE`: environment file to load
- `DJANGO_ENV_EXAMPLE_FILE`: template used for key validation
- `SECRET_KEY`: Django secret key
- `TIME_ZONE`: local display timezone
- `DEBUG`: Django debug mode
- `ALLOWED_HOSTS`: comma-separated allowed hosts
- `DATABASE_NAME`: encrypted database path
- `DATABASE_TIMEOUT`: SQLite/SQLCipher connection timeout
- `DATABASE_ENCRYPTION_KEY`: required SQLCipher encryption key
- `DATABASE_CIPHER_PAGE_SIZE`: SQLCipher page size
- `DATABASE_KDF_ITER`: SQLCipher PBKDF iteration count
- `DATABASE_CIPHER_COMPATIBILITY`: SQLCipher compatibility mode

## Medical Date Handling

HolyFHIR stores calendar-only clinical facts, such as date of birth or medication start date, as dates. Exact moments, such as imports, lockouts, encounters, and timed observations, use timezone-aware datetimes.

That distinction matters because medical dates should not move to the previous or next day because of timezone conversion.

## License

TBD
