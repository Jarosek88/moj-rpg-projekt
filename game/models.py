from django.db import models
from django.contrib.auth.models import User

class Postava(models.Model):
    pouzivatel = models.ForeignKey(User, on_delete=models.CASCADE, related_name="postavy", null=True, blank=True)
    meno = models.CharField(max_length=100)
    hp = models.IntegerField(default=100)
    max_hp = models.IntegerField(default=100)
    sila = models.IntegerField(default=20)
    level = models.IntegerField(default=1)
    xp = models.IntegerField(default=0)
    xp_na_level = models.IntegerField(default=100)
    obrana = models.IntegerField(default=0)
    zlato = models.IntegerField(default=0)
    max_sloty_batohu = models.IntegerField(default=5) # Nový limit
    quest_sila_splneny = models.BooleanField(default=False)
    quest_level_splneny = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.meno} (Level {self.level})"
    
class Predmet(models.Model):
    nazov = models.CharField(max_length=100)
    # Pridame typ, aby sme vedeli o aký predmet ide
    TYPY_PREDMETOV = [
        ('zbran', 'Zbraň'),
        ('brnenie', 'Brnenie'),
        ('lektvar', 'Lektvár'),
    ]
    typ = models.CharField(max_length=20, choices=TYPY_PREDMETOV, default='lektvar')
    bonus_hp = models.IntegerField(default=0)
    bonus_sila = models.IntegerField(default=0)
    bonus_obrana = models.IntegerField(default=0)

    # Prepojenie na postavu
    majitel = models.ForeignKey(Postava, on_delete=models.CASCADE, related_name="batoh", null=True, blank=True)

    RARITY_CHOICES = [
        ('common', 'Obyčajný'),
        ('rare', 'Vzácny'),
        ('legendary', 'Legendárny'),
    ]
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')

    def __str__(self):
        return f"{self.nazov} ({self.get_typ_display()})"
    
class Nepriatel(models.Model):
    nazov = models.CharField(max_length=100)
    sila = models.IntegerField(default=10)
    hp = models.IntegerField(default=50)
    xp_odmena = models.IntegerField(default=20) # Koľko získa hrdina XP keď vyhrá
    ikona = models.CharField(max_length=50, default="⚔")

    def __str__(self):
        return f"{self.nazov} (Sila: {self.sila})"

