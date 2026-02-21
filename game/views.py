from django.shortcuts import get_object_or_404, redirect , render
from .models import Postava, Predmet
from .forms import PostavaForm
import random

def zoznam_postav(request):
    postavy = Postava.objects.all() # Vytiahne úplne všetko z databázy
    return render(request, 'game/zoznam.html', {'postavy': postavy})

def nova_postava(request):
    if request.method == 'POST':
        form = PostavaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/postavy/') # Po úspechu vráti na zoznam
    else:
        form = PostavaForm()

    return render(request, 'game/formular.html', {'form': form})

def trenovat_postavu(request, postava_id):
    from django.shortcuts import get_object_or_404
    postava = get_object_or_404(Postava, id=postava_id)

    # Logika náhodnu silu
    postava.sila += random.randint(3, 8)

    # Level up systém, ak má silu viac ako 50 pôjde o level hore
    if postava.sila >= 50 and postava.level == 1:
        postava.level = 2
        postava.max_hp += 20 # Bonusové HP za level
        postava.hp = postava.max_hp
    
    postava.hp += 15 # Prida za každý trening život

    # poistka na presiahnutie maxima
    if postava.hp > postava.max_hp:
        postava.hp = postava.max_hp

    # Výpočet levelu za každých 100 jeden level
    novy_level = (postava.sila // 100) + 1

    if novy_level > postava.level:
        postava.level = novy_level
        # Bonus pri každom level pridame Hp o 20
        postava.max_hp += 20
        postava.hp = postava.max_hp # Vliečime ho trochu

    postava.save() # Zapíše sa zmena v databáze
    return redirect('/postavy/') #vráti sa naspat na zoznam

def dobrodruzstvo(request, postava_id):
    postava = get_object_or_404(Postava, id=postava_id)

    # Riziko: Postava stratí HP
    ubrate_hp = random.randint(15, 40)
    postava.hp -= ubrate_hp

    if postava.hp <= 0:
        #Hardcore postava zomrela, vymažeme ju
        postava.delete()
        return redirect('/postavy/') # Navrát na zoznam, postava už tam nebude
    
    # Odmena ak postava prežije získa silu
    postava.sila += random.randint(10, 20)

    # šanca na anjdenie predmetu
    sanca = random.randint(1, 10)
    if sanca <= 3:
        typ_lootu = random.choice(['lektvar', 'zbran', 'brnenie'])

        if typ_lootu == 'lektvar':
            Predmet.objects.create(nazov='Magický lektvár', typ='lektvar', bonus_hp=30, majitel=postava)
        elif typ_lootu == 'zbran':
            Predmet.objects.create(nazov='Ostrý meč', typ='zbran', bonus_sila=random.randint(5, 20), majitel=postava)
        elif typ_lootu == 'brnenie':
            Predmet.objects.create(nazov='Kožená vesta', typ='brnenie', bonus_obrana=random.randint(3, 12), majitel=postava)

     # Výpočet levelu za každých 100 jeden level
    novy_level = (postava.sila // 100) + 1

    if novy_level > postava.level:
        postava.level = novy_level
        # Bonus pri každom level pridame Hp o 20
        postava.max_hp += 20
        postava.hp = postava.max_hp # Vliečime ho trochu    

    postava.save()
    return redirect('/postavy/')

def pouzit_predmet(request, predmet_id):
    predmet = get_object_or_404(Predmet, id=predmet_id)
    postava = predmet.majitel

    if predmet.typ == 'lektvar':
        postava.hp += predmet.bonus_hp
        if postava.hp > postava.max_hp:
            postava.hp = postava.max_hp
        predmet.delete() # Lektvár sa vymaže s batohu

    elif predmet.typ == 'zbran':
        postava.sila += predmet.bonus_sila #pridame silu natrvalo
        predmet.delete() # meč sme nasadili a staa sa súčasťou sily

    elif predmet.typ == 'brnenie':
        postava.obrana += predmet.bonus_obrana # pridáme obranu natrvalo
        predmet.delete()

    postava.save() # Uložíme hrdinovi
    return redirect('/postavy/')