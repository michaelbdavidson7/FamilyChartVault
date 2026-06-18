from io import BytesIO
from pathlib import PurePosixPath
from zipfile import BadZipFile, ZipFile

from django import forms

from patients.models import PatientProfile

from .importer import loads_fhir_documents


FHIR_ZIP_SIDECAR_FILENAMES = {
    "log.ndjson",
}


class FHIRImportForm(forms.Form):
    patient = forms.ModelChoiceField(
        label="Attach to patient",
        queryset=PatientProfile.objects.order_by("last_name", "first_name", "id"),
        required=False,
        empty_label="Select a Patient",
        widget=forms.Select(attrs={"class": "form-select"}),
        help_text="Choose an existing profile to attach this import to. Leave blank to create or update from the FHIR Patient resource.",
    )
    fhir_file = forms.FileField(
        label="FHIR JSON file",
        required=False,
        help_text="Upload a MyChart ZIP export, NDJSON file, FHIR Bundle, or single FHIR resource JSON.",
    )
    fhir_json = forms.CharField(
        label="FHIR JSON",
        widget=forms.Textarea(attrs={"rows": 14}),
        required=False,
        help_text="Paste a FHIR Bundle, NDJSON, or single resource when you do not have a file.",
    )

    def clean(self):
        cleaned_data = super().clean()
        uploaded_file = cleaned_data.get("fhir_file")
        pasted_json = cleaned_data.get("fhir_json", "").strip()

        if not uploaded_file and not pasted_json:
            raise forms.ValidationError("Upload a FHIR ZIP/JSON/NDJSON file or paste FHIR JSON.")

        if uploaded_file and pasted_json:
            raise forms.ValidationError("Use either a file upload or pasted JSON, not both.")

        if uploaded_file:
            cleaned_data["payloads"] = self._payloads_from_upload(uploaded_file)
        else:
            try:
                cleaned_data["payloads"] = loads_fhir_documents(pasted_json, "pasted FHIR JSON")
            except ValueError as exc:
                raise forms.ValidationError(str(exc)) from exc

        return cleaned_data

    def _payloads_from_upload(self, uploaded_file):
        filename = uploaded_file.name or ""
        content = uploaded_file.read()
        if filename.lower().endswith(".zip"):
            return self._payloads_from_zip(content)

        try:
            raw = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise forms.ValidationError("FHIR file must be UTF-8 encoded JSON/NDJSON or a ZIP export.") from exc

        try:
            return loads_fhir_documents(raw, filename)
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc

    def _payloads_from_zip(self, content):
        payloads = []
        try:
            with ZipFile(BytesIO(content)) as archive:
                for name in archive.namelist():
                    path = PurePosixPath(name)
                    if path.name.startswith(".") or not path.name:
                        continue
                    if path.name.lower() in FHIR_ZIP_SIDECAR_FILENAMES:
                        continue
                    if path.suffix.lower() not in {".json", ".ndjson"}:
                        continue
                    try:
                        raw = archive.read(name).decode("utf-8-sig")
                    except UnicodeDecodeError as exc:
                        raise forms.ValidationError(f"{name} must be UTF-8 encoded.") from exc
                    try:
                        payloads.extend(loads_fhir_documents(raw, path.name))
                    except ValueError as exc:
                        raise forms.ValidationError(f"{name}: {exc}") from exc
        except BadZipFile as exc:
            raise forms.ValidationError("Uploaded ZIP file could not be opened.") from exc

        if not payloads:
            raise forms.ValidationError("ZIP file did not contain any FHIR JSON or NDJSON files.")
        return payloads


class QuickPatientCreateForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ("first_name", "last_name", "date_of_birth")
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "date_of_birth": "Date of birth",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
