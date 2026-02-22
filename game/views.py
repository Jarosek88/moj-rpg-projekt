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
    lokalita = request.GET.get('lokalita', 'les') # Zistíme kam hráč klikol

    if lokalita == 'odmena':
        #Skontrolujeme či ma nárok na odmenu
        if postava.sila >= 30 and not postava.quest_sila_splneny:
            postava.zlato += 100
            postava.quest_sila_splneny = True
            postava.save()
            messages.success(request, f"🎁 Výborne! Za tvoju silu získavaš odmenu 100 zlata.")
        elif postava.quest_sila_splneny:
            messages.info(request, f"Túto odmenu si si už vybral")
        else:    
            messages.error(request, f"Ešte nie si dosť silný na túto odmenu!")
        return redirect('/postavy/')
    
    if lokalita == 'odmena_level':
        if postava.level >= 5 and not postava.quest_level_splneny:
            postava.zlato += 200
            postava.quest_level_splneny = True
            postava.save()
            messages.success(request, "Paráda! Za 5. level získavaš 200 zlata!")
        return redirect('/postavy/') # Vždy sa vráť späť, aby ťa nezožral troll!
    
    is_dungeon = (lokalita == 'dungeon')

    if lokalita == 'les':
        # Vyberieme len slabších sila pod 50
        vsetci_nepriatelia = Nepriatel.objects.filter(sila__lt=50)
    elif is_dungeon:
        vsetci_nepriatelia = Nepriatel.objects.filter(sila__gte=50)
    else:
        vsetci_nepriatelia = Nepriatel.objects.all()

    # Vyberieme nepriateľa z vyfiltrovaneho zoznamu
    if  vsetci_nepriatelia.exists():
        nepriatel = random.choice(vsetci_nepriatelia)
    else:
        #Ak by bol les prazdny
        nepriatel = random.choice(Nepriatel.objects.all())

    # Logika súboja
    # Nepriateľ udrie svojou silou, ale obrana stlmí úder
    poskodenie = nepriatel.sila - postava.obrana
    if poskodenie < 0: poskodenie = 0 #Obrana je silnejšia ako útok

    postava.hp -= poskodenie
    # Pridáme správu o súboji
    messages.warning(request, f"Stretol si, {nepriatel.ikona} {nepriatel.nazov}! Utrpel si {poskodenie} poškodenia.")

    # Ak hrdina prežil dostane XP
    if postava.hp > 0:
        vyhra = True
    else:
        vyhra = False

    if postava.hp <= 0:
        messages.error(request, f"Bohužiaľ, {nepriatel.nazov} ťa porazil. Letoslav padol v boji...")
        #Hardcore postava zomrela, vymažeme ju
        postava.delete()
        return redirect('/postavy/') # Navrát na zoznam, postava už tam nebude

    # šanca na najdenie predmetu
    sanca = random.randint(1, 10)
    if sanca <= 3:
        # 1. Kontrola limitu batohu (kapacita 5 slotov)
        if postava.batoh.count() >= 5:
            messages.warning(request, "Tvoj batoh je plný! Nič nové si neuniesol.")
        else:
            typ_lootu = random.choice(['lektvar', 'zbran', 'brnenie'])
            
            # 2. Určenie vzácnosti (rarity)
        
        vzacnost_sanca = random.randint(1, 100)
        if lokalita == 'dungeon':
            # Špeciálne šance pre Dungeon (30% na Legendárny)
            if vzacnost_sanca <= 30:
                vzacnost = 'legendary'
                nasobitel = 4
                prefix = "Dungeonový Artefakt "
            else:
                vzacnost = 'rare'
                nasobitel = 2
                prefix = "Vzácny "
        else:
            # Pôvodná logika pre Les (10% na Legendárny)
            if vzacnost_sanca <= 10:
                vzacnost = 'legendary'
                nasobitel = 3
                prefix = "Legendárny "
            elif vzacnost_sanca <= 30:
                vzacnost = 'rare'
                nasobitel = 2
                prefix = "Vzácny "
            else:
                vzacnost = 'common'
                nasobitel = 1
                prefix = ""

            # 3. Vytvorenie predmetu s priradením vzácnosti a majiteľa
            if typ_lootu == 'lektvar':
                novy_predmet = Predmet.objects.create(
                    majitel=postava, 
                    nazov=f"{prefix}Magický lektvar", 
                    typ='lektvar', 
                    bonus_hp=30 * nasobitel,
                    rarity=vzacnost
                )
            elif typ_lootu == 'zbran':
                novy_predmet = Predmet.objects.create(
                    majitel=postava, 
                    nazov=f"{prefix}Ostrý meč", 
                    typ='zbran', 
                    bonus_sila=random.randint(5, 20) * nasobitel,
                    rarity=vzacnost
                )
            elif typ_lootu == 'brnenie':
                novy_predmet = Predmet.objects.create(
                    majitel=postava, 
                    nazov=f"{prefix}Kožená vesta", 
                    typ='brnenie', 
                    bonus_obrana=random.randint(3, 12) * nasobitel,
                    rarity=vzacnost
                )
            
            messages.info(request, f"V tráve si našiel: {novy_predmet.nazov}")


    if vyhra:
        postava.xp += nepriatel.xp_odmena

        # Logika pre level up
        if postava.xp >= postava.xp_na_level:
            postava.level += 1
            postava.xp -= postava.xp_na_level # Zvyšok XP ostáva do dalšieho levelu
            postava.xp_na_level = int(postava.xp_na_level * 1.5) # Každý daľší level je tažší
            postava.max_hp += 20
            postava.hp = postava.max_hp # Pri level up sa uplne vylieči
            messages.success(request, f"💥LEVEL UP! Teraz si level {postava.level}!")    

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