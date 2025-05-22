from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("doctor/", views.doctor_dashboard, name="doctor_dashboard"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path("inventory/", views.inventory_dashboard, name="inventory_dashboard"),
    path("patient/", views.patient_dashboard, name="patient_dashboard"),
    path("dashboard/", views.default_dashboard, name="default_dashboard"),
    path('accounts/add-patient/', views.add_patient, name='add_patient'),
]

