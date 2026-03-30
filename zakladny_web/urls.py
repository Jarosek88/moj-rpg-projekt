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
    
    # ZÁKLADNÉ FUNKCIE (Krčma a Odpočinok)
    path('postava/krcma/<int:postava_id>/', views.krcma, name='krcma'),
    path('postava/<int:postava_id>/odpocinok/', views.odpocinok, name='odpocinok'),
    
    # BOJ A KOVÁČ (To nové, čo sme pridali)
    path('postava/<int:postava_id>/boj/', views.dobrodruzstvo, name='dobrodruzstvo'),
    path('postava/<int:postava_id>/utok/<int:nepriatel_id>/', views.bojovat, name='bojovat'),
    path('postava/<int:postava_id>/kovac/', views.kovac, name='kovac'),
    path('postava/<int:postava_id>/vylepsit/<str:typ>/', views.nakup_vylepsenia, name='nakup_vylepsenia'),
    path('postava/<int:postava_id>/oddychnut/<str:typ_odpocinok>/', views.oddychnut, name='oddychnut'),
    path('postava/<int:postava_id>/kocky/', views.hrat_kocky, name='hrat_kocky'),
]