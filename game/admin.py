from django.contrib import admin
from .models import Postava, Predmet, Nepriatel

@admin.register(Postava)
class PostavaAdmin(admin.ModelAdmin):
    # Tu definuješ, ktoré stĺpce chceš vidieť v zozname
    list_display = ('meno', 'pouzivatel', 'level', 'zlato') 
    # Pridá filter na pravú stranu, aby si mohol filtrovať podľa hráčov
    list_filter = ('pouzivatel',)

admin.site.register(Postava)
admin.site.register(Predmet)
admin.site.register(Nepriatel)

# Register your models here.
