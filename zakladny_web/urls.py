"""
URL configuration for zakladny_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from game.views import zoznam_postav, nova_postava, trenovat_postavu, dobrodruzstvo # Importujeme funkciu
from game import views

urlpatterns = [

    path('admin/', admin.site.urls),
    path('postavy/', zoznam_postav), # Ak poúživateľ pôjde na /postavy uvidí zoznam
    path('postavy/nova/', nova_postava), # Nová cesta pre formulár
    path('postavy/trenovat/<int:postava_id>/', trenovat_postavu , name = 'trenovat'),
    path('postavy/dobrodruzstvo/<int:postava_id>/', dobrodruzstvo, name='dobrodruzstvo'),
    path('pouzit-predmet/<int:predmet_id>/', views.pouzit_predmet, name='pouzit_predmet'),
    path('predat/<int:predmet_id>/', views.predat_predmet, name='predat_predmet'),
    path('kupit-lektvar/<int:postava_id>', views.kupit_lektvar, name='kupit_lektvar'),
]
