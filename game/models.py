from django.db import models

class Postava(models.Model):
    meno = models.CharField(max_length=100)
    hp = models.IntegerField(default=100)
    max_hp = models.IntegerField(default=100)
    sila = models.IntegerField(default=20)
    level = models.IntegerField(default=1)
    xp = models.IntegerField(default=0)
    obrana = models.IntegerField(default=0)

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

    def __str__(self):
        return f"{self.nazov} ({self.get_typ_display()})"

