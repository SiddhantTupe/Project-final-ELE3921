from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from medapp.forms import PatientForm, PrescriptionForm, PatientSignUpForm, HistoryForm, AdmissionForm, MessageForm
from medapp.models import Patient, Prescription, PatientMedicalHistory, AdmissionRecord, Message
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden
from collections import defaultdict


# Create your views here.

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name="Doctors").exists():
                return redirect("doctor_dashboard")
            elif user.groups.filter(name="Staff").exists():
                return redirect("staff_dashboard")
            elif user.groups.filter(name="Patients").exists():
                patient = get_object_or_404(Patient, user=user)
                return redirect("patient_dashboard", patient_id=patient.id)
            else:
                return redirect("default_dashboard")  # fallback
        else:
            return render(request, "registration/login.html", {
                "username": username,
                "error": "Wrong username or password"
            })
    return render(request, "registration/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

# Default Dashboard

def default_dashboard(request):
    return render(request, 'registration/default.html')

# Doctor Dashboard

def is_doctor(user):
    return user.groups.filter(name='Doctors').exists()

@login_required
@user_passes_test(is_doctor)
def doctor_dashboard(request):
    admissions = AdmissionRecord.objects.filter(
        primary_doctor=request.user,
        patient__isnull=False
    ).select_related('patient', 'patient__user')
    
    patient_records = []
    for admission in admissions:
        patient = admission.patient
        patient_records.append({
            'patient': patient,
            'created_at': admission.created_at
        })

    return render(request, 'registration/doctorgroup.html', {'patient_records': patient_records})

# Staff Dashboard

def is_staff(user):
    return user.groups.filter(name='Staff').exists()

@login_required
@user_passes_test(is_staff)
def staff_dashboard(request):
    prescriptions = Prescription.objects.filter(assistant_doctor=request.user).select_related('patient', 'medicine')

    # Group prescriptions by patient
    grouped = defaultdict(list)
    for p in prescriptions:
        grouped[p.patient].append(p)

    grouped_prescriptions = list(grouped.items())  # List of (patient, [prescriptions])
    
    assigned_patients = Patient.objects.filter(
        admissions__assistant_doctor=request.user
    ).select_related('user').distinct()
    
    return render(request, 'registration/staffgroup.html', {'grouped_prescriptions': grouped_prescriptions, 'assigned_patients': assigned_patients})

# Inventory Head Dashboard

@login_required
def inventory_dashboard(request):
    return render(request, 'registration/inventorygroup.html')

# Patient Dashboard

def is_patient_or_doctor_or_staff(user):
    return user.groups.filter(name__in=['Patients', 'Doctors', 'Staff']).exists()

@login_required
@user_passes_test(is_patient_or_doctor_or_staff)
def patient_dashboard(request, patient_id):
   
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.user.groups.filter(name='Patients').exists() and patient.user != request.user:
        return HttpResponseForbidden("You are not allowed to view this page.")
    
    history = PatientMedicalHistory.objects.filter(patient=patient).order_by('-diagnosis_date')
    admissions = AdmissionRecord.objects.filter(patient=patient).order_by('-admission_date')
    prescriptions = Prescription.objects.filter(patient=patient).select_related('medicine', 'assistant_doctor').order_by('-created_at')
    
    return render(request, 'registration/patientgroup.html', {
        'patient': patient,
        'user': request.user, 
        'history': history,
        'admissions': admissions,
        'prescriptions': prescriptions,
    })
    
@login_required
def after_login_redirect(request):
    user = request.user
    if user.groups.filter(name="Doctors").exists():
        return redirect("doctor_dashboard")
    elif user.groups.filter(name="Patients").exists():
        patient = get_object_or_404(Patient, user=user)
        print("Redirecting patient ID:", patient.id)
        return redirect("patient_dashboard", patient_id=patient.id)
    elif user.groups.filter(name="Staff").exists():
        return redirect("staff_dashboard")
    elif user.is_superuser:
        return redirect("admin:index")
    else:
        return redirect("default_dashboard")


# Form for Sign-Up 

def patient_signup_view(request):
    if request.method == "POST":
        user_form = PatientSignUpForm(request.POST)
        patient_info_form = PatientForm(request.POST)
        
        if user_form.is_valid() and patient_info_form.is_valid():
            user = user_form.save()
            patient = patient_info_form.save(commit=False)
            patient.user = user  # Link patient to the new user
            patient.save()
            
            patients_group = Group.objects.get(name="Patients")
            user.groups.add(patients_group)
            
            login(request, user)
            return redirect("patient_dashboard", patient_id=patient.id)
    else:
        user_form = PatientSignUpForm()
        patient_info_form = PatientForm()
    return render(request, "forms/signup.html", {"user_form": user_form, "patient_form": patient_info_form})


# Form for Adding Patient's Details. 

@login_required
@user_passes_test(is_doctor)
def add_patient(request):
    error = None
    if request.method == 'POST':
        history_form = HistoryForm(request.POST)
        admission_form = AdmissionForm(request.POST)
        
        if history_form.is_valid() and admission_form.is_valid():
            history = history_form.save(commit=False)
            admission = admission_form.save(commit=False)

            admission.primary_doctor = request.user

            admission.patient = history.patient

            history.save()
            admission.save()

            return redirect('doctor_dashboard')
        else:
            error = "Please correct the errors in the form."
    else:
        history_form = HistoryForm()
        admission_form = AdmissionForm()

    return render(request, 'forms/patients.html', {"history_form": history_form, "admission_form": admission_form, "error": error})

@login_required
@user_passes_test(is_doctor)
def edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    history = PatientMedicalHistory.objects.filter(patient=patient).last()
    admission = AdmissionRecord.objects.filter(patient=patient, primary_doctor=request.user).last()

    if not history or not admission:
        return HttpResponseForbidden("You don't have permission to edit this patient's records.")

    error = None

    if request.method == 'POST':
        history_form = HistoryForm(request.POST, instance=history)
        admission_form = AdmissionForm(request.POST, instance=admission)

        if history_form.is_valid() and admission_form.is_valid():
            history = history_form.save(commit=False)
            admission = admission_form.save(commit=False)
            
            history.patient = patient
            admission.patient = history.patient
            admission.primary_doctor = request.user

            # patient fields are preserved via `instance=...`, no need to reset them
            history.save()
            admission.save()

            return redirect('doctor_dashboard')
        else:
            error = "Please correct the errors."
    else:
        history_form = HistoryForm(instance=history)
        admission_form = AdmissionForm(instance=admission)

    return render(request, 'forms/patients.html', {
        'history_form': history_form,
        'admission_form': admission_form,
        'error': error,
        'edit': True,
        'patient': patient,
    })

#Form for Adding Prescription.

@login_required
@user_passes_test(is_staff)
def add_prescription(request):
    if request.method =="POST":
        form = PrescriptionForm(request.POST, doctor=request.user)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.assistant_doctor = request.user  
            prescription.save()
            return redirect(staff_dashboard)
    else:
        form = PrescriptionForm(doctor=request.user)
    return render(request, 'forms/prescription.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Staff').exists())
def inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'messaging/inbox.html', {'messages': messages})

#Form for Sending Messages.

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Patients').exists())
def send_message(request):
    patient = request.user.patient_user

    try:
        assigned = AdmissionRecord.objects.filter(patient=patient).latest('admission_date').assistant_doctor
    except AdmissionRecord.DoesNotExist:
        return HttpResponseForbidden("No assigned doctor found.")
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user  # the patient
            
            patient = request.user.patient_user
            assigned = AdmissionRecord.objects.filter(patient=patient).last().assistant_doctor
            
            message.recipient = assigned
            
            message.save()
            return redirect('patient_dashboard', patient_id=request.user.patient_user.id)
    else:
        form = MessageForm()

    return render(request, 'messaging/send_message.html', {'form': form, 'assigned_doctor': assigned})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Staff').exists())
def inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    
    grouped = defaultdict(list)
    for msg in messages:
        print(f"- From {msg.sender} | Subject: {msg.subject}")
        grouped[msg.sender].append(msg)
        
    grouped_messages = list(grouped.items())
    
    return render(request, 'messaging/inbox.html', {'grouped_messages': grouped_messages})