from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.decorators import login_required
from .models import Service, BusinessProfile, Transaction, Profile
from django.contrib.auth import get_user_model
User = get_user_model()
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

otp = 0

def signupUser_individual(request):   
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name'] 
        email =  request.POST['email']     
        if len(username)<5:
            messages.error(request, "Length of username  must be of atleast 5 Digit")
            return render(request, 'individual_signup.html')       
        if User.objects.filter(username=username).exists():
            messages.success(request, "Account already exist")
            return render(request, 'individual_login.html')
        user = User.objects.create_user(username=username, password=password ,email = email,first_name=first_name,last_name=last_name,wallet = 1000)
        user.first_name = first_name
        user.last_name = last_name
        user.save()  
        global otp
        otp = randint(100000, 999999)          
        send_mail(
            'django_test',str(otp),'mishrapravin214@gmail.com',['mishrapravin441@gmail.com'],fail_silently=False)
        login(request, user)
        return render(request, 'individual_otp.html', {'user':request.user})        
    return render(request, 'individual_signup.html')

def home_individual(request):
    return render(request, 'individual_home.html')




def loginUser_individual(request):    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']      
        user = authenticate(username = username, password = password)        
        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful! You are welcome!")
            return redirect('index_individual')
        else:
            messages.error(request, "Invalid credentials! Please try again!")
            return redirect('loginUser_individual')   
    return render(request, 'individual_login.html')


def logout_individual(request):
  django_logout(request)
  return render(request, 'individual_login.html')

def otp_verification_individual(request):

    if request.method == "POST":
        userotp = request.POST['otp']
        return redirect('index_individual')
    else:
            messages.error(request, "Invalid Otp! Please try again")
            return render(request, "individual_signup.html")
            
    return render(request, "individual_otp.html")

def index_individual(request):
    data = []
    service = Service.objects.all()
    services = Service.objects.all()
    count = 1
    for service in services:     
        for profile in service.services_of_business.all():
            count = count + 1
            amount = 10
            data = data + [[service.name,str(profile.user),service.image,count,amount]]
            print(data)
    service = Service.objects.all()
    amount_left=request.user.wallet
    return render(request, 'individual_index.html',{'service': data,'amount':amount_left})


def pay_individual(request , service_name ,service_owner ,service_price ):
    print(service_name,type(service_owner),service_owner, service_price)
    #deduct balance
    logged_in_user = User.objects.filter(username=request.user.username).first()
    print(logged_in_user)
    logged_in_user.wallet = logged_in_user.wallet - service_price
    logged_in_user.save()   
    business_user=User.objects.filter(username=service_owner).first()
    print(business_user)
    business_user.wallet += service_price
    business_user.save()    
    transaction = Transaction.objects.create(by=request.user,
                    to = BusinessProfile.objects.filter(user=User.objects.filter(username=service_owner).first()).first(),
                    amount= service_price, service=Service.objects.filter(name=service_name).first())
    transaction.save()    
    return render(request, 'about.html')

#@login_required
def individual_transaction(request):
    transactions = Transaction.objects.filter(by=request.user).order_by('-date','-time')
    messages.success(request, 'Welcome to the transactions page!')
    return render(request, 'individual_transaction.html', locals())


#@login_required
def individual_analysis(request):
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
    return render(request, 'individual_analysis.html', {'daywise':daywise, 
                                                    'service_per_month':service_per_month,
                                                    'number_times_service':number_times_service})

def error_400(request, exception):
    return render(request, '400.html')


def error_403(request, exception):
    return render(request, '403.html')

def about_individual(request):
    return render(request, 'about.html')

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
