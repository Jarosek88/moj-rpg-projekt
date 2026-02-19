from django.db import models

class Postava(models.Model):
    meno = models.CharField(max_length=100)
    hp = models.IntegerField(default=100)
    max_hp = models.IntegerField(default=100)
    sila = models.IntegerField(default=20)
    level = models.IntegerField(default=1)
    xp = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.meno} (Level {self.level})"
    
class Predmet(models.Model):
    meno = models.CharField(max_length=100)
    hp = models.IntegerField(default=0)
    sila_bonus = models.IntegerField(default=0)

    def __str__(self):
        return self.meno