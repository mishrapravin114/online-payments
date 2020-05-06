from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('business.urls')),
]

handler400 = 'business.views.error_400'
handler403 = 'business.views.error_403'
handler400 = 'business.views.error_404'
handler500 = 'business.views.error_500'
