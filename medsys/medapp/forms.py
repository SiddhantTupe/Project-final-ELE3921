from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Patient, Prescription, PatientMedicalHistory, AdmissionRecord, ROOM_CHOICES, Message

class PatientSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['date_of_birth', 'gender', 'blood_group', 'phone']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
        
class HistoryForm(forms.ModelForm):
    class Meta:
        model = PatientMedicalHistory
        fields = ['patient', 'condition_name', 'diagnosis_date','status1', 'notes']
        widgets = {
            'diagnosis_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing, remove patient field completely
        if self.instance and self.instance.pk:
            self.fields.pop('patient')
        else:
            used_patients = list(PatientMedicalHistory.objects.values_list('patient_id', flat=True))
            self.fields['patient'].queryset = Patient.objects.exclude(id__in=used_patients)
        
class AdmissionForm(forms.ModelForm):
    assistant_doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Staff"),
        required=False,
        label="Assistant Doctor"
    )
    class Meta:
        model = AdmissionRecord
        fields = ['admission_date', 'discharge_date', 'assistant_doctor', 'room_number', 'admission_reason', 'discharge_summary', 'status']
        widgets = {
            'discharge_date': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        occupied_rooms = AdmissionRecord.objects.filter(discharge_date__isnull=True).values_list('room_number', flat=True)

        available_choices = [(num, str(num)) for num, label in ROOM_CHOICES if num not in occupied_rooms]
        
        if self.instance and self.instance.pk and self.instance.room_number:
            current_room = self.instance.room_number
            if (current_room, str(current_room)) not in available_choices:
                available_choices.append((current_room, str(current_room)))
                
        available_choices = sorted(available_choices, key=lambda x: x[0])
        
        self.fields['room_number'].choices = available_choices
        
    
class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient', 'medicine', 'dosage', 'duration_days','notes']
        
    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)  
        super().__init__(*args, **kwargs)

        if doctor:
            assigned_patient_ids = AdmissionRecord.objects.filter(
                assistant_doctor=doctor
            ).values_list('patient__id', flat=True).distinct()

            self.fields['patient'].queryset = Patient.objects.filter(id__in=assigned_patient_ids)
        
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']
