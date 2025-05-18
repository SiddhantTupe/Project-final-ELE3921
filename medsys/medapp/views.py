from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.
from django.http import HttpResponse

@login_required 
def index(request):
    return HttpResponse("Hello, doctor. You're at the polls index.")

