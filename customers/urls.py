from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('individual/transaction/',views.individual_transaction,name="individual_transaction"),
    path('individual/analysis/',views.individual_analysis,name="individual_analysis"),

    path('/index_individual/', views.index_individual, name="index_individual"),
    path('',views.loginUser_individual,name="loginUser_individual"),
    path('/signupUser_individual/',views.signupUser_individual,name="signupUser_individual"),
    path('/otp_verification_individual/',views.otp_verification_individual,name="otp_verification_individual"),
    path('/logout_individual/',views.logout_individual,name="logout_individual"),
    path('/home_individual/', views.home_individual, name='home_individual'),
] + static(settings.MEDIA_URL,document_root =  settings.MEDIA_ROOT)
