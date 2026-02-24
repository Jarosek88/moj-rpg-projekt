from django.contrib import admin
from .models import Postava, Predmet, Nepriatel

@admin.register(Postava)
class PostavaAdmin(admin.ModelAdmin):
    list_display = ('meno', 'pouzivatel', 'level', 'zlato') 
    list_filter = ('pouzivatel',)

admin.site.register(Predmet)
admin.site.register(Nepriatel)

# Register your models here.
