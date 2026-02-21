from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect , render
from .models import Postava, Predmet, Nepriatel
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

    # Vyberieme náhodneho nepriateľas databaázy
    vsetci_nepriatelia = Nepriatel.objects.all()

    if vsetci_nepriatelia.exists():
        nepriatel = random.choice(vsetci_nepriatelia)

        # Logika súboja
        # Nepriateľ udrie svojou silou, ale obrana stlmí úder
        poskodenie = nepriatel.sila - postava.obrana
        if poskodenie < 0: poskodenie = 0 #Obrana je silnejšia ako útok

        postava.hp -= poskodenie
        # Pridáme správu o súboji
        messages.warning(request, f"Stretol si, {nepriatel.ikona} {nepriatel.nazov}! Utrpel si {poskodenie} poškodenia.")

    # Ak hrdina prežil dostane XP
    if postava.hp > 0:
        postava.xp += nepriatel.xp_odmena
        messages.success(request, f"Vyhral si! Získal si , {nepriatel.xp_odmena} XP.")
        # Pridáme aj náhodnu silu 
        postava.sila += random.randint(1, 5) 

    if postava.hp <= 0:
        messages.error(request, f"Bohužiaľ, {nepriatel.nazov} ťa porazil. Letoslav padol v boji...")
        #Hardcore postava zomrela, vymažeme ju
        postava.delete()
        return redirect('/postavy/') # Navrát na zoznam, postava už tam nebude

    # šanca na najdenie predmetu
    sanca = random.randint(1, 10)
    if sanca <= 3:
        typ_lootu = random.choice(['lektvar', 'zbran', 'brnenie'])

        if typ_lootu == 'lektvar':
            novy_predmet = Predmet.objects.create(nazov='Magický lektvár', typ='lektvar', bonus_hp=30, majitel=postava)
        elif typ_lootu == 'zbran':
            novy_predmet = Predmet.objects.create(nazov='Ostrý meč', typ='zbran', bonus_sila=random.randint(5, 20), majitel=postava)
        elif typ_lootu == 'brnenie':
            novy_predmet = Predmet.objects.create(nazov='Kožená vesta', typ='brnenie', bonus_obrana=random.randint(3, 12), majitel=postava)

        messages.info(request, f"V tráve si našiel: {novy_predmet.nazov}")

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

def predat_predmet(request, predmet_id):
    predmet = get_object_or_404(Predmet, id= predmet_id)
    postava = predmet.majitel

    postava.zlato += 50 # Pevna cena za predaj
    postava.save()

    nazov_predmetu = predmet.nazov
    predmet.delete()

    messages.success(request, f"Predal si {nazov_predmetu} za 50 zlatých!")
    return redirect('/postavy/')

def kupit_lektvar(request, postava_id):
    postava = get_object_or_404(Postava, id = postava_id)
    cena = 50

    if postava.zlato >= cena:
        postava.zlato -= cena
        postava.hp += 30
        if postava.hp > postava.max_hp:
            postava.hp = postava.max_hp
        
        postava.save()
        messages.success(request, f"Kúpil si si lektvar! HP doplnené na {postava.hp}.")
    else:
        messages.success(request, f"Nemáš dosť zlata na lektvar!") 

    return redirect('/postavy/')