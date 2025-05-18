from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
            elif user.groups.filter(name="Inventory Head").exists():
                return redirect("inventory_dashboard")
            elif user.groups.filter(name="Patients").exists():
                return redirect("patient_dashboard")
            else:
                return redirect("default_dashboard")  # fallback
        return render(request, "registration/login.html", {"username": username, "error": "Wrong password"})
    return render(request, "registration/login.html")

def logout_view(request):
    logout(request)
    return redirect("index")

@login_required
def doctor_dashboard(request):
    return render(request, 'registration/doctorgroup.html')
    

@login_required
def staff_dashboard(request):
    return render(request, 'registration/staffgroup.html')

@login_required
def inventory_dashboard(request):
    return render(request, 'registration/inventorygroup.html')

@login_required
def patient_dashboard(request):
    return render(request, 'registration/patientgroup.html')

@login_required
def default_dashboard(request):
    return render(request, 'registration/default.html')
