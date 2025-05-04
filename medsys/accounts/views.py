from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        return render(request, "registration/login.html", {"username": username, "error": "Wrong password"})
    return render(request, "registration/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")

def homepage_role(request):
    user= request.user
    groups = user.groups.values_list('name', flat=True)
    if 'Doctors' in groups:
        return render(request, 'doctor_homepage.html', {'user': user})
    elif 'Nurses' in groups:
        return render(request, 'nurse_homepage.html', {'user': user})
    elif 'Inventory head' in groups:
        return render(request, 'inventory_head_homepage.html', {'user': user})
    elif 'Patients' in groups:
        return render(request, 'patient_homepage.html', {'user': user})
    else:
        return render(request, 'homepage.html', {'user': user})
    