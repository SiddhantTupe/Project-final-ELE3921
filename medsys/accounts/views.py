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
            return redirect(request.GET.get("next", "index"))
        return render(request, "registration/login.html", {"username": username, "error": "Wrong password"})
    return render(request, "registration/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")
