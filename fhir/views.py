from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.urls import reverse

from .backups import create_pre_import_database_backup
from .forms import FHIRImportForm, QuickPatientCreateForm
from .importer import import_fhir_payloads


@staff_member_required
def import_fhir_data(request):
    can_add_patient = request.user.has_perm("patients.add_patientprofile")
    base_context = admin.site.each_context(request)

    if request.method == "POST":
        if request.POST.get("action") == "create_patient":
            patient_form = QuickPatientCreateForm(request.POST)
            if not can_add_patient:
                messages.error(request, "You do not have permission to add patients.")
            elif patient_form.is_valid():
                patient = patient_form.save()
                messages.success(request, f"Patient added: {patient}.")
                return redirect(f"{reverse('fhir_import')}?patient={patient.pk}")
            form = FHIRImportForm()
            return render(
                request,
                "admin/fhir_import.html",
                {
                    **base_context,
                    "title": "Import FHIR Data",
                    "form": form,
                    "patient_form": patient_form,
                    "can_add_patient": can_add_patient,
                    "patient_add_url": reverse("admin:patients_patientprofile_add"),
                    "show_patient_modal": True,
                },
            )

        form = FHIRImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                backup_path = create_pre_import_database_backup()
            except OSError as error:
                messages.error(request, f"FHIR import was not started because the database backup failed: {error}")
                patient_form = QuickPatientCreateForm()
                return render(
                    request,
                    "admin/fhir_import.html",
                    {
                        **base_context,
                        "title": "Import FHIR Data",
                        "form": form,
                        "patient_form": patient_form,
                        "can_add_patient": can_add_patient,
                        "patient_add_url": reverse("admin:patients_patientprofile_add"),
                        "show_patient_modal": False,
                    },
                )

            result = import_fhir_payloads(
                form.cleaned_data["payloads"],
                target_patient=form.cleaned_data.get("patient"),
            )
            if result.errors:
                for error in result.errors:
                    messages.warning(request, error)
            messages.success(
                request,
                (
                    f"FHIR import complete: {result.created} created, "
                    f"{result.updated} updated, {result.snapshots} snapshots saved, "
                    f"{result.unsupported} unsupported resources preserved as snapshots."
                ),
            )
            if backup_path:
                messages.info(request, f"Pre-import database backup created: {backup_path}")
            return redirect(reverse("admin:fhir_fhirresourcesnapshot_changelist"))
        patient_form = QuickPatientCreateForm()
    else:
        form = FHIRImportForm(initial={"patient": request.GET.get("patient") or None})
        patient_form = QuickPatientCreateForm()

    return render(
        request,
        "admin/fhir_import.html",
        {
            **base_context,
            "title": "Import FHIR Data",
            "form": form,
            "patient_form": patient_form,
            "can_add_patient": can_add_patient,
            "patient_add_url": reverse("admin:patients_patientprofile_add"),
            "show_patient_modal": False,
        },
    )
