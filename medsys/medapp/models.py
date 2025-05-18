from django.db import models
from django.contrib.auth.models import User

# ------------------------------
# Medicine Management Models
# ------------------------------

class MedicineFormType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name

class MedicineCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    form_type = models.ForeignKey(MedicineFormType, on_delete=models.CASCADE, related_name='categories')
    def __str__(self):
        return self.name

class Medicine(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(MedicineCategory, on_delete=models.CASCADE, related_name='medicines')
    manufacturer = models.CharField(max_length=100)
    min_stock_level = models.PositiveIntegerField()
    current_stock = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

    def stock_status(self):
        if self.current_stock < self.min_stock_level:
            return "Low Stock"
        return "OK"

class MedicineUnit(models.Model):
    barcode = models.CharField(max_length=50, unique=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='units')
    batch_number = models.CharField(max_length=50)
    expiry_date = models.DateField(db_index=True)
    manufacturing_date = models.DateField()
    is_dispensed = models.BooleanField(default=False)
    def __str__(self):
        return self.barcode

# ------------------------------
# Staff Management Models
# ------------------------------

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name

class Staff(models.Model):
    ROLE_CHOICES = [
        ('DOCTOR', 'Doctor'),
        ('NURSE', 'Nurse'),
        ('PHARMACIST', 'Pharmacist'),
        ('ADMIN', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20)
    joining_date = models.DateField()
    active = models.BooleanField(default=True)
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='assistants')
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"

# ------------------------------
# Supplier Model
# ------------------------------

class Supplier(models.Model):
    company_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.company_name

# ------------------------------
# Patient Care Models
# ------------------------------

class Allergy(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=5)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=100)
    emergency_phone = models.CharField(max_length=20)
    insurance_provider = models.CharField(max_length=100)
    insurance_id = models.CharField(max_length=50)
    allergies = models.ManyToManyField(Allergy, blank=True, related_name='patients')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.get_full_name()}"

class PatientMedicalHistory(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('RESOLVED', 'Resolved'),
        ('CHRONIC', 'Chronic'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_histories')
    condition_name = models.CharField(max_length=100)
    diagnosis_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.condition_name} for {self.patient}"

class AdmissionRecord(models.Model):
    STATUS_CHOICES = [
        ('ADMITTED', 'Admitted'),
        ('DISCHARGED', 'Discharged'),
        ('TRANSFERRED', 'Transferred'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='admissions')
    admission_date = models.DateTimeField()
    discharge_date = models.DateTimeField(null=True, blank=True)
    room_number = models.CharField(max_length=20)
    primary_doctor = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='primary_admissions')
    assistant_doctor = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='assistant_admissions')
    admission_reason = models.TextField()
    discharge_summary = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    def __str__(self):
        return f"Admission {self.id} for {self.patient}"

# ------------------------------
# Inventory & Transaction Models
# ------------------------------

class StockTransaction(models.Model):
    TRANSACTION_TYPE = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    ]
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='stock_transactions')
    quantity = models.IntegerField()
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_transactions')
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.transaction_type} - {self.medicine.name} ({self.quantity})"

# ------------------------------
# Prescription & Dosage Models
# ------------------------------

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='prescriptions')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Prescription for {self.patient} by {self.doctor}"

class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration_days = models.IntegerField()
    def __str__(self):
        return f"{self.medicine.name} for {self.prescription.patient}"

class AdministeredDose(models.Model):
    prescription_item = models.ForeignKey(PrescriptionItem, on_delete=models.CASCADE, related_name='administered_doses')
    administered_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='administered_doses')
    administered_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Dose of {self.prescription_item.medicine.name} to {self.prescription_item.prescription.patient}"

