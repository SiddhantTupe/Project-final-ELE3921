from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="custom_logout"),
    path("doctor/dashboard", views.doctor_dashboard, name="doctor_dashboard"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path('staff/inbox/', views.inbox, name='staff_inbox'),
    path('staff/add-prescription/', views.add_prescription, name='add_prescription'),
    path("patient/<int:patient_id>/", views.patient_dashboard, name="patient_dashboard"),
    path('redirect/', views.after_login_redirect, name='after_login_redirect'),
    path('patient/message/send/', views.send_message, name='send_message'),
    path("dashboard/", views.default_dashboard, name="default_dashboard"),
    path("add-patient/", views.add_patient, name='add_patient'),
    path('patients/<int:patient_id>/edit/', views.edit_patient, name='edit_patient'),
    path("add-prescription/", views.add_prescription, name='add_prescription'),
    path("signup/", views.patient_signup_view, name="patient_signup"),
]

