from django.db import models
from django.contrib.auth.models import User

# ------------------------------
# Medicine Management Models
# ------------------------------

class MedicineCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Medicine(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(MedicineCategory, on_delete=models.CASCADE, related_name='medicines')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.name


# ------------------------------
# Patient Care Models
# ------------------------------

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_user')
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=5)
    phone = models.CharField(max_length=20, null=True)
    emergency_contact = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return f"{self.user.get_full_name()}"

class PatientMedicalHistory(models.Model):
    STATUS_CHOICES1 = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('chronic', 'Chronic'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_histories')
    condition_name = models.CharField(max_length=100)
    diagnosis_date = models.DateField()
    status1 = models.CharField(max_length=20, choices=STATUS_CHOICES1, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.condition_name} for {self.patient}"

ROOM_CHOICES = [(i, str(i)) for i in range(1, 21)]

class AdmissionRecord(models.Model):
    STATUS_CHOICES = [
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged'),
        ('transferred', 'Transferred'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='admissions')
    admission_date = models.DateTimeField()
    discharge_date = models.DateTimeField(null=True, blank=True)
    room_number = models.PositiveSmallIntegerField(choices=ROOM_CHOICES)
    primary_doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='primary_admissions')
    assistant_doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assistant_doctor_admissions')
    admission_reason = models.TextField()
    discharge_summary = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return f"Admission {self.id} for {self.patient}"


# ------------------------------
# Prescription & Dosage Models
# ------------------------------

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    assistant_doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='written_prescriptions')
    created_at = models.DateTimeField(auto_now_add=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, null=True)
    dosage = models.CharField(max_length=100, default="1")
    duration_days = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Prescription for {self.patient} by {self.assistant_doctor}"

# ------------------------------
# Message
# ------------------------------

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')  
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')  
    subject = models.CharField(max_length=200)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username} - {self.subject}"