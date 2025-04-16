from django.db import models

# Create your models here.
# ------------------------------
# Medicine Management Models
# ------------------------------
class MedicineFormType(models.Model):
    form_id = models.AutoField(primary_key=True)
    form_name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.form_name

class MedicineCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    form_type = models.ForeignKey(MedicineFormType, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return self.category_name

class Medicine(models.Model):
    medicine_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(MedicineCategory, on_delete=models.CASCADE, related_name='medicines')
    manufacturer = models.CharField(max_length=100)
    min_stock_level = models.IntegerField()
    current_stock = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class MedicineUnit(models.Model):
    barcode = models.CharField(max_length=50, primary_key=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='units')
    batch_number = models.CharField(max_length=50)
    expiry_date = models.DateField()
    manufacturing_date = models.DateField()
    is_dispensed = models.BooleanField(default=False)

    def __str__(self):
        return self.barcode

# ------------------------------
# Staff Management Models
# ------------------------------
class DoctorField(models.Model):
    field_id = models.AutoField(primary_key=True)
    field_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.field_name

class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=20)
    field = models.ForeignKey(DoctorField, on_delete=models.SET_NULL, null=True, related_name='staff')
    role = models.CharField(max_length=50)  # e.g., Head Doctor, Assistant Doctor, Nurse, etc.
    joining_date = models.DateField()
    active = models.BooleanField(default=True)
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='assistants')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# ------------------------------
# Supplier Model
# ------------------------------
class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
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
class Patient(models.Model):
    patient_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=5)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=100)
    emergency_phone = models.CharField(max_length=20)
    insurance_provider = models.CharField(max_length=100)
    insurance_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class PatientMedicalHistory(models.Model):
    history_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_histories')
    condition_name = models.CharField(max_length=100)
    diagnosis_date = models.DateField()
    status = models.CharField(max_length=20)  # e.g., Active, Resolved, Chronic
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.condition_name} for {self.patient}"

class AdmissionRecord(models.Model):
    admission_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='admissions')
    admission_date = models.DateTimeField()
    discharge_date = models.DateTimeField(null=True, blank=True)
    room_number = models.CharField(max_length=20)
    primary_doctor = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='primary_admissions')
    assistant_doctor = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='assistant_admissions')
    admission_reason = models.TextField()
    discharge_summary = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"Admission {self.admission_id} for {self.patient}"

# ------------------------------
# Inventory & Transaction Models
# ------------------------------
class StockTransaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    transaction_type = models.CharField(max_length=20)  # e.g., 'IN' or 'OUT'
    transaction_date = models.DateTimeField(auto_now_add=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='stock_transactions')
    quantity = models.IntegerField()
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_transactions')
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='stock_transactions')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.transaction_id}"

# ------------------------------
# Prescription and Dispensing Models
# ------------------------------
class Prescription(models.Model):
    prescription_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='prescriptions')
    admission = models.ForeignKey(AdmissionRecord, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions')
    prescription_date = models.DateTimeField(auto_now_add=True)
    diagnosis = models.TextField()
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"Prescription {self.prescription_id} for {self.patient}"

class PrescriptionDetail(models.Model):
    prescription_detail_id = models.AutoField(primary_key=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='details')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='prescription_details')
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    duration = models.IntegerField()  # duration in days
    special_instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Detail {self.prescription_detail_id} for Prescription {self.prescription.prescription_id}"

class MedicineDispensing(models.Model):
    dispensing_id = models.AutoField(primary_key=True)
    prescription_detail = models.ForeignKey(PrescriptionDetail, on_delete=models.CASCADE, related_name='dispensings')
    medicine_unit = models.ForeignKey(MedicineUnit, on_delete=models.CASCADE, related_name='dispensings')
    dispensed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='dispensings')
    dispensed_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dispensing {self.dispensing_id}"

# ------------------------------
# Medication Scheduling Models
# ------------------------------
class MedicationSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    prescription_detail = models.ForeignKey(PrescriptionDetail, on_delete=models.CASCADE, related_name='schedules')
    admission = models.ForeignKey(AdmissionRecord, on_delete=models.CASCADE, related_name='schedules')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Schedule {self.schedule_id}"

class ScheduledDose(models.Model):
    dose_id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(MedicationSchedule, on_delete=models.CASCADE, related_name='doses')
    scheduled_time = models.DateTimeField()
    dose_amount = models.CharField(max_length=50)
    status = models.CharField(max_length=20)  # e.g., Scheduled, Administered, Missed, Skipped
    administered_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='administered_doses')
    administered_time = models.DateTimeField(null=True, blank=True)
    reason_if_skipped = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Dose {self.dose_id} for Schedule {self.schedule.schedule_id}"

class DoseAdministrationLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    dose = models.ForeignKey(ScheduledDose, on_delete=models.CASCADE, related_name='logs')
    medicine_unit = models.ForeignKey(MedicineUnit, on_delete=models.CASCADE, related_name='dose_logs')
    vital_signs = models.TextField(blank=True, null=True)
    patient_reaction = models.TextField(blank=True, null=True)
    logged_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='dose_logs')
    log_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log {self.log_id} for Dose {self.dose.dose_id}"

# ------------------------------
# Medication Report Model
# ------------------------------
class MedicationReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    admission = models.ForeignKey(AdmissionRecord, on_delete=models.CASCADE, related_name='reports')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reports')
    generated_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    generation_date = models.DateTimeField(auto_now_add=True)
    report_type = models.CharField(max_length=50)  # e.g., Progress, Discharge
    report_content = models.TextField()

    def __str__(self):
        return f"Report {self.report_id} for Admission {self.admission.admission_id}"
