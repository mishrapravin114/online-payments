from django.shortcuts import render

def main_all(request):
    if request.method == "POST":
        return render(request, 'main.html')
    return render(request, 'main.html')