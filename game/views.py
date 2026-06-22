from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import Postava, Predmet, Nepriatel
from .forms import PostavaForm
import random


# --- REGISTRÁCIA A ZOZNAM ---
def registracia(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('zoznam_postav')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registracia.html', {'form': form})


@login_required
def zoznam_postav(request):
    postavy = Postava.objects.filter(pouzivatel=request.user)
    return render(request, 'game/zoznam.html', {'postavy': postavy})


@login_required
def nova_postava(request):
    if request.method == 'POST':
        form = PostavaForm(request.POST)
        if form.is_valid():
            postava = form.save(commit=False)
            postava.pouzivatel = request.user
            postava.save()
            return redirect('zoznam_postav')
    else:
        form = PostavaForm()
    return render(request, 'game/formular.html', {'form': form})


@login_required
def zoznam_postav(request):
    postavy = Postava.objects.filter(pouzivatel=request.user)

    # Pre každú postavu priradíme jej aktuálnu výbavu
    for postava in postavy:
        postava.vybava = {
            'zbran': postava.batoh.filter(nasadene=True, typ='zbran').first(),
            'stit': postava.batoh.filter(nasadene=True, typ='stit').first(),
            'brnenie': postava.batoh.filter(nasadene=True, typ='brnenie').first(),
            'prsten': postava.batoh.filter(nasadene=True, typ='prsten').first(),
        }

    return render(request, 'game/zoznam.html', {'postavy': postavy})


# --- KRČMA ---
@login_required
def krcma(request, postava_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    hlasky = ["Daj si pivo!", "V lese sú vlky.", "Tvoj meč je tupý."]
    if 'aktualna_karta' not in request.session:
        request.session['aktualna_karta'] = random.randint(1, 10)
    return render(request, 'game/krcma.html', {'postava': postava, 'hlaska': random.choice(hlasky)})


@login_required
def oddychnut(request, postava_id, typ_odpocinok):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    cena, liecenie = (10, 20) if typ_odpocinok == 'pivo' else (30, 50)
    if postava.zlato >= cena:
        postava.zlato -= cena
        postava.hp = min(postava.hp + liecenie, postava.max_hp)
        postava.save()
        messages.success(request, f"Vyliečený o {liecenie} HP!")
    else:
        messages.error(request, "Málo zlata!")
    return redirect('krcma', postava_id=postava.id)


# --- HAZARD ---
@login_required
def hrat_kocky(request, postava_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    if request.method == 'POST':
        try:
            stavka = int(request.POST.get('stavka', 0))
        except ValueError:
            stavka = 0
        if 0 < stavka <= postava.zlato:
            h, k = random.randint(1, 6), random.randint(1, 6)
            if h > k:
                postava.zlato += stavka
                messages.success(request, f"Vyhral si! Ty {h}, krčmár {k}. +{stavka} zlata")
            elif h < k:
                postava.zlato -= stavka
                messages.error(request, f"Prehral si! Ty {h}, krčmár {k}. -{stavka} zlata")
            else:
                messages.info(request, "Remíza!")
            postava.save()
    return redirect('krcma', postava_id=postava.id)


@login_required
def hra_karty(request, postava_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)

    if request.method == 'POST':
        tip = request.POST.get('tip')
        try:
            stavka = int(request.POST.get('stavka', 0))
        except ValueError:
            stavka = 0

        if stavka <= 0 or stavka > postava.zlato:
            messages.error(request, "Neplatná stávka alebo máš málo zlata!")
            return redirect('krcma', postava_id=postava.id)

        stara_karta = request.session.get('aktualna_karta', random.randint(1, 10))
        nova_karta = random.randint(1, 10)
        while nova_karta == stara_karta:
            nova_karta = random.randint(1, 10)

        vyhra = False
        if tip == 'vyssia' and nova_karta > stara_karta:
            vyhra = True
        elif tip == 'nizsia' and nova_karta < stara_karta:
            vyhra = True

        request.session['aktualna_karta'] = nova_karta

        if vyhra:
            postava.zlato += stavka
            messages.success(request, f"Vyhral si! Nová karta bola {nova_karta} (stará {stara_karta}). +{stavka} zlata")
        else:
            postava.zlato -= stavka
            messages.error(request, f"Prehral si! Nová karta bola {nova_karta} (stará {stara_karta}). -{stavka} zlata")
        postava.save()

    return redirect('krcma', postava_id=postava.id)


# --- DIVOČINA ---
@login_required
def dobrodruzstvo(request, postava_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    zona = request.GET.get('zona', 'razcestie')
    nepriatel = None

    if zona == 'dungeon':
        if postava.level < 5:
            messages.error(request, "Na Dungeon potrebuješ level 5!")
            return redirect(f"/postava/{postava.id}/boj/?zona=razcestie")
        vsetci = Nepriatel.objects.filter(sila__gte=50, sila__lt=150)
        if vsetci.exists(): nepriatel = random.choice(vsetci)

    elif zona == 'boss':
        if postava.level < 8:
            messages.error(request, "Na Bossa potrebuješ level 8!")
            return redirect(f"/postava/{postava.id}/boj/?zona=razcestie")
        vsetci = Nepriatel.objects.filter(sila__gte=150)
        if vsetci.exists(): nepriatel = random.choice(vsetci)

    elif zona == 'les':
        vsetci = Nepriatel.objects.filter(sila__lt=50)
        if vsetci.exists(): nepriatel = random.choice(vsetci)

    return render(request, 'game/les.html', {'postava': postava, 'nepriatel': nepriatel, 'zona_name': zona})


@login_required
def bojovat(request, postava_id, nepriatel_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    nepriatel = get_object_or_404(Nepriatel, id=nepriatel_id)
    zona = request.GET.get('zona', 'les')

    # Výpočet bonusov z iba NASADENÝCH predmetov
    bonus_sila = sum(item.bonus_sila for item in postava.batoh.all() if item.nasadene)
    bonus_obrana = sum(item.bonus_obrana for item in postava.batoh.all() if item.nasadene)

    # Logika boja (Započítané aj s bonusmi z vecí)
    dmg_hrac = postava.sila + bonus_sila
    dmg_nepriatel = max(0, nepriatel.sila - (postava.obrana + bonus_obrana))

    postava.hp -= dmg_nepriatel

    if postava.hp <= 0:
        messages.error(request, f"Bohužiaľ, {nepriatel.nazov} ťa porazil...")
        postava.hp = 0
        postava.save()
        return redirect('zoznam_postav')

    postava.xp += nepriatel.xp_odmena
    postava.zlato += 20
    messages.info(request, f"Zasiahol si {nepriatel.nazov} za {dmg_hrac} dmg! On tebe ubral {dmg_nepriatel} HP.")

    # --- LOGIKA PADANIA PREDMETOV ---
    sanca = random.randint(1, 100)
    if sanca <= 30:
        pocet_predmetov = Predmet.objects.filter(majitel=postava).count()

        # Dynamická kontrola voči limitu postavy
        if pocet_predmetov >= postava.kapacita_batohu:
            messages.warning(request,
                             f"🎒 Tvoj batoh je plný! Máš v ňom maximum ({postava.kapacita_batohu} vecí). Nový predmet sa už nezmestil.")
        else:
            vybrany_typ = random.choice(['zbran', 'stit', 'brnenie', 'prsten'])
            sanca_rarita = random.randint(1, 100)

            if sanca_rarita <= 5:
                vybrana_rarita = 'legendary'
                prefix = 'Legendárny'
                bonus_nasobic = 3
            elif sanca_rarita <= 25:
                vybrana_rarita = 'rare'
                prefix = 'Vzácny'
                bonus_nasobic = 2
            else:
                vybrana_rarita = 'common'
                prefix = 'Obyčajný'
                bonus_nasobic = 1

            novy_item = Predmet.objects.create(
                nazov=f"{prefix} {vybrany_typ}",
                typ=vybrany_typ,
                bonus_sila=random.randint(1, 5) * bonus_nasobic,
                bonus_obrana=random.randint(1, 5) * bonus_nasobic,
                majitel=postava,
                rarity=vybrana_rarita,
                nasadene=False
            )
            messages.success(request, f"🎒 Našiel si {novy_item.nazov} a schoval ho do batohu!")

    # Level Up logika
    if postava.xp >= postava.xp_na_level:
        postava.level += 1
        postava.xp -= postava.xp_na_level
        postava.xp_na_level = int(postava.xp_na_level * 1.5)
        postava.max_hp += 20
        postava.hp = postava.max_hp
        messages.success(request, f"💥 LEVEL UP! Dosiahol si level {postava.level}!")

    postava.save()
    return redirect(f"/postava/{postava.id}/boj/?zona={zona}")


# --- KOVÁČ ---
@login_required
def kovac(request, postava_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    inventar = Predmet.objects.filter(majitel=postava)
    return render(request, 'game/kovac.html', {'postava': postava, 'inventar': inventar})


@login_required
def nakup_vylepsenia(request, postava_id, typ):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    if postava.zlato >= 100:
        postava.zlato -= 100
        if typ == 'sila':
            postava.sila += 10
        else:
            postava.obrana += 10
        postava.save()
        messages.success(request, f"⚒️ Tvoja {typ} bola úspešne vylepšená!")
    else:
        messages.error(request, "Nemáš dosť zlata na vylepšenie!")
    return redirect('kovac', postava_id=postava.id)


@login_required
def predat_vsetko(request, postava_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    predmety_v_batohu = Predmet.objects.filter(majitel=postava, nasadene=False)

    zisk = 0
    for item in predmety_v_batohu:
        if item.rarity == 'legendary':
            zisk += 50
        elif item.rarity == 'rare':
            zisk += 20
        else:
            zisk += 5

    postava.zlato += zisk
    postava.save()
    predmety_v_batohu.delete()

    messages.success(request, f"⚒️ Predal si veci z batohu za {zisk} zlata!")
    return redirect('kovac', postava_id=postava.id)


@login_required
def rozsirit_batoh(request, postava_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    cena_rozsirenia = 500  # Cena za rozšírenie batohu

    if postava.zlato >= cena_rozsirenia:
        postava.zlato -= cena_rozsirenia
        postava.kapacita_batohu += 1
        postava.save()
        messages.success(request, f"🎒 Kováč ti rozšíril batoh! Nová kapacita je {postava.kapacita_batohu} slotov.")
    else:
        messages.error(request, f"Nemáš dosť zlata! Rozšírenie batohu stojí {cena_rozsirenia} zlata.")

    return redirect('kovac', postava_id=postava.id)


# --- INVENTÁR / AKCIE S PREDMETMI ---
@login_required
def batoh(request, postava_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    predmety = Predmet.objects.filter(majitel=postava)
    return render(request, 'game/batoh.html', {'postava': postava, 'predmety': predmety})


@login_required
def obliect_predmet(request, predmet_id):
    predmet = get_object_or_404(Predmet, id=predmet_id, majitel__pouzivatel=request.user)
    postava = predmet.majitel

    if predmet.nasadene:
        predmet.nasadene = False
        predmet.save()
        messages.info(request, f"🎒 Vyzliekol si predmet: {predmet.nazov}.")
    else:
        Predmet.objects.filter(majitel=postava, typ=predmet.typ, nasadene=True).update(nasadene=False)
        predmet.nasadene = True
        predmet.save()
        messages.success(request, f"⚔️ Nasadil si si: {predmet.nazov}!")

    return redirect('batoh', postava_id=postava.id)