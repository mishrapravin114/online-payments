from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def login(request):
    return render(request, 'login.html')


def detail(request):
    return render(request, 'business_detail.html')


def registration(request):
    return render(request, 'register.html')


def business_home(request):
    return render(request, 'business_home.html')


def business_transaction(request):
    return render(request, 'transaction.html')


def about(request):
    return render(request, 'about.html')


def business_profile(request):
    return render(request, 'business_profile.html')


def error_400(request, exception):
    return render(request, '400.html')


def error_403(request, exception):
    return render(request, '403.html')


def error_404(request, exception):
    return render(request, '404.html')


def error_500(request):
    return render(request, '500.html')


def e_400(request):
    return render(request, '400.html')


def e_403(request):
    return render(request, '403.html')


def e_404(request):
    return render(request, '404.html')


def e_500(request):
    return render(request, '500.html')
