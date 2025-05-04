from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.http import HttpResponse

@login_required 
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
