from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.decorators import login_required
from .models import Profile, Service, BusinessProfile, Transaction
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from random import randint
from django.utils import timezone
from decimal import Decimal
import csv
from django.http import JsonResponse
from django.views.generic import TemplateView
import plotly.express as px
from plotly.offline import plot
from plotly.graph_objs import Scatter

User = get_user_model()

otp=0

def home(request):
    return render(request, 'home.html')

def business_index(request):
    return render(request, 'index.html')

def registration(request):   

    if request.method == "POST":
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname'] 
        email =  request.POST['email'] 
        phone = request.POST['phone']
        profile_type = request.POST['profile_type']

        if len(username)<5:
            messages.error(request, "Length of username  must be of atleast 5 Digit")
            return render(request, 'register.html')   

        if User.objects.filter(username=username).exists():
            messages.success(request, "Account already exists! Please try again!")
            return render(request, 'login.html')

        user = User.objects.create_user(username=username, password=request.POST.get('password'), \
                                    email=email, first_name=first_name, \
                                    last_name=last_name, phone=phone, profile_type=profile_type)

        user.save()  

        global otp
        otp = randint(100000, 999999)          
        send_mail('django_test',str(otp),'mishrapravin214@gmail.com', [email], fail_silently=False)
        
        login(request, user)
        return render(request, 'otp.html', {'user':request.user})

    return render(request, 'register.html')


def otp_verification(request):

    if request.method == "POST":
        userotp = request.POST['otp']
        if str(otp) == userotp:
            if request.user.profile_type == "Individual":
                return render(request, 'individual_home.html')
            else:
                service = Service.objects.all()
                return render(request, 'business_signup.html', {'service':service})    
        else:
            messages.error(request, "Invalid OTP! Please try again!")
            return render(request, "register.html")
            
    return render(request, "otp.html")



def business_signup(request):

    if request.method == "POST":
        print('dddd')
        business_profile = BusinessProfile(business_name=request.POST.get("business_name"),
                                        pan_number=request.POST.get("pan_number"),
                                        pan_name=request.POST.get("pan_name"),
                                        address=request.POST.get("address"),
                                        pincode=request.POST.get("pincode"),
                                        city=request.POST.get("city"),
                                        state=request.POST.get("state"))

        service_name = request.POST.get("service")
        
        business_profile.user=request.user
        business_profile.save()

        service =  Service.objects.filter(name=service_name).first()
        service.save()
        business_profile_service_list = []
        services = Service.objects.prefetch_related('business_profile').filter(business_profile__user=request.user)
        for index, current_service in enumerate(services):
            if current_service in business_profile_service_list :
                messages.success(request, "You Service already exists!")
                service = Service.objects.all()
                return render(request, 'business_signup.html', {'service':service}) 
            else:
                business_profile_service_list = business_profile_service_list + [current_service]
        
        service.business_profile.add(business_profile)
        business_profile.service.add(Service.objects.filter(name=service_name).first())
        
        service_list = Service.objects.all()
        messages.success(request, "You details are added successfully added!")
        return render(request, 'business_home.html',{'services':services ,'service_list': service_list })

    service = Service.objects.all()
    return render(request, 'business_signup.html', {'service':service})


def loginUser(request):

    if request.method == "POST":
        username = request.POST.get('username')  

        user = authenticate(username = username, password= request.POST.get('password'))        
        print(user)
        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful! You are welcome!")
            if request.user.profile_type=="Individual":
                return render(request, 'individual_home.html', {'user':request.user})
            else:
                services = Service.objects.prefetch_related('business_profile').filter(business_profile__user=request.user)     
                service_list = Service.objects.all()
                return render(request, 'business_home.html',{'services':services ,'service_list': service_list })
        else:
            messages.error(request, "Invalid credentials! Please try again!")
            return redirect('home')   

    return render(request, 'login.html')
    

def logoutUser(request):
    django_logout(request)
    return render(request, 'home.html')


def business_home(request):
    services = Service.objects.prefetch_related('business_profile').filter(business_profile__user=request.user)     
    service_list = Service.objects.all()
    return render(request, 'business_home.html',{'services':services ,'service_list': service_list })

def business_service_add(request):
    if request.method=="POST":
        service_name = request.POST.get("service")
        business_profile=BusinessProfile.objects.filter(user=request.user).first()
        business_profile.service.add(Service.objects.filter(name=service_name).first())
        service =  Service.objects.filter(name=service_name).first()
        service.save()
        service.business_profile.add(business_profile)
        service_list = Service.objects.all()
        services = Service.objects.prefetch_related('business_profile').filter(business_profile__user=request.user)
        messages.success(request, "Your details are added successfully added!")
        return render(request, 'business_home.html',{'services':services, 'service_list':service_list})


#@login_required
def business_transaction(request):
    transactions = Transaction.objects.filter(by=request.user).order_by('-date','-time')
    messages.success(request, 'Welcome to the transactions page!')
    return render(request, 'business_transaction.html', locals())


#@login_required
def export_transaction(request):
     
    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['From', 'To', 'Amount', 'Service', 'Date', 'Time'])
    
    for transaction in Transaction.objects.select_related('by', 'to', 'service').filter(by=request.user).values_list('by__username', 'to__business_name', 'amount', 'service__name', 'date', 'time'):
        writer.writerow(transaction)
    
    response['Content-Disposition']='attachment;filename="transactions.csv"'    
    messages.success(request, "Your transactions file was downloaded successfully!")
    return response

#@login_required
def business_analysis(request):
    #daywise
    x1_data=[]
    y1_data=[]

    transactions = Transaction.objects.filter(by=request.user).order_by('date')

    for transaction in transactions:
        x1_data.append(transaction.date)
        y1_data.append(transaction.amount)
    
    fig = px.bar(x=x1_data, y=y1_data,labels={'x':"Day",'y':'Amount'})
    daywise = fig.to_html(full_html=False)

    #no_of_services_per_month
    x1_data=[]
    y1_data=[]

    transactions_per_month = Transaction.objects.filter(by=request.user).values_list("date").order_by("-date")
    no_of_services_per_month_dict = {}

    for i in transactions_per_month:
        if i[0] in no_of_services_per_month_dict:
            no_of_services_per_month_dict[i[0]] += 1
        else:
            no_of_services_per_month_dict[i[0]] = 1

    x1_data = list(no_of_services_per_month_dict.keys())
    y1_data = list(no_of_services_per_month_dict.values())

    fig = px.bar(x=x1_data, y=y1_data,labels={'x':"Day",'y':'Times'})
    service_per_month = fig.to_html(full_html=False)

    
    #no_of_times_each_service_used
    x1_data=[]
    y1_data=[]

    no_of_service_used = Transaction.objects.filter(by=request.user).values_list("service_id")

    service_type = Service.objects.values_list("id", "name")
    no_of_times_each_service_used_dict = {}

    for ser in no_of_service_used:
        temp = service_type[ser[0]-1][1]
        if temp in no_of_times_each_service_used_dict:
            no_of_times_each_service_used_dict[temp] += 1
        else:
            no_of_times_each_service_used_dict[temp] = 1

    x1_data = list(no_of_times_each_service_used_dict.keys())
    y1_data = list(no_of_times_each_service_used_dict.values())

    fig = px.bar(x=x1_data, y=y1_data,labels={'x':"Day",'y':'Amount'})
    number_times_service = fig.to_html(full_html=False)
    
    messages.success(request, "Welcome to the analysis page!")
    return render(request, 'business_analysis.html', {'daywise':daywise, 
                                                    'service_per_month':service_per_month,
                                                    'number_times_service':number_times_service})
                  


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
