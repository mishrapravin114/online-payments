from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.login, name='login'),
    path('registration/', views.registration, name='register'),
    path('about/', views.about, name='about'),
    path('business/detail/', views.detail, name='detail'),
    path('business/home/', views.business_home, name='business_home'),
    path('business/transactions/', views.business_transaction, name='transactions'),
    path('business/profile/', views.business_profile, name='business_profile'),
    path('business/404/', views.e_404, name='404'),
    path('business/403/', views.e_403, name='403'),
    path('business/400/', views.e_400, name='400'),
    path('business/500/', views.e_500, name='500'),
]
