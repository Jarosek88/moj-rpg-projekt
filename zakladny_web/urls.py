from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from game import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registracia/', views.registracia, name='registracia'),
    
    # HLAVNÉ STRÁNKY
    path('', views.zoznam_postav, name='zoznam_postav'),
    path('postavy/', views.zoznam_postav, name='zoznam_postav'),
    path('postavy/nova/', views.nova_postava, name='nova_postava'),
    path('postava/<int:postava_id>/batoh/', views.batoh, name='batoh'),
    
    # ZÁKLADNÉ FUNKCIE (Krčma a Odpočinok)
    path('postava/krcma/<int:postava_id>/', views.krcma, name='krcma'),
    
    # BOJ A KOVÁČ (To nové, čo sme pridali)
    path('postava/<int:postava_id>/boj/', views.dobrodruzstvo, name='dobrodruzstvo'),
    path('postava/<int:postava_id>/utok/<int:nepriatel_id>/', views.bojovat, name='bojovat'),
    path('postava/<int:postava_id>/kovac/', views.kovac, name='kovac'),
    path('postava/<int:postava_id>/vylepsit/<str:typ>/', views.nakup_vylepsenia, name='nakup_vylepsenia'),
    path('postava/<int:postava_id>/oddychnut/<str:typ_odpocinok>/', views.oddychnut, name='oddychnut'),
    path('postava/<int:postava_id>/kocky/', views.hrat_kocky, name='hrat_kocky'),
    path('postava/krcma/<int:postava_id>/karty/', views.hra_karty, name='hra_karty'),
    path('obliect/<int:predmet_id>/', views.obliect_predmet, name='obliect_predmet'),
    path('postava/<int:postava_id>/kovac/rozsirit/', views.rozsirit_batoh, name='rozsirit_batoh'),
    path('postava/<int:postava_id>/predat-vsetko/', views.predat_vsetko, name='predat_vsetko'),
]