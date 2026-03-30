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
    else: form = UserCreationForm()
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
    else: form = PostavaForm()
    return render(request, 'game/formular.html', {'form': form})

# --- KRČMA ---
@login_required
def krcma(request, postava_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    hlasky = ["Daj si pivo!", "V lese sú vlky.", "Tvoj meč je tupý."]
    return render(request, 'game/krcma.html', {'postava': postava, 'hlaska': random.choice(hlasky)})

# Pôvodný odpočinok (zadarmo / plné zdravie)
@login_required
def odpocinok(request, postava_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    postava.hp = postava.max_hp
    postava.save()
    messages.success(request, "Si plný síl!")
    return redirect('krcma', postava_id=postava.id)

# Nový odpočinok (pivo / jedlo)
@login_required
def oddychnut(request, postava_id, typ_odpocinok):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    cena, liecenie = (10, 20) if typ_odpocinok == 'pivo' else (30, 50)
    if postava.zlato >= cena:
        postava.zlato -= cena
        postava.hp = min(postava.hp + liecenie, postava.max_hp)
        postava.save()
        messages.success(request, f"Vyliečený o {liecenie} HP!")
    else: messages.error(request, "Málo zlata!")
    return redirect('krcma', postava_id=postava.id)

# --- HAZARD ---
@login_required
def hrat_kocky(request, postava_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    if request.method == 'POST':
        try: stavka = int(request.POST.get('stavka', 0))
        except: stavka = 0
        if 0 < stavka <= postava.zlato:
            h, k = random.randint(1, 6), random.randint(1, 6)
            if h > k:
                postava.zlato += stavka
                messages.success(request, f"Vyhral si! Ty {h}, krčmár {k}. +{stavka}z")
            elif h < k:
                postava.zlato -= stavka
                messages.error(request, f"Prehral si! Ty {h}, krčmár {k}. -{stavka}z")
            else: messages.info(request, "Remíza!")
            postava.save()
    return redirect('krcma', postava_id=postava.id)

# --- DIVOCINA ---
@login_required
def dobrodruzstvo(request, postava_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    zona = request.GET.get('zona', 'razcestie')
    vsetci = Nepriatel.objects.filter(sila__lt=50) if zona == 'les' else None
    nepriatel = random.choice(vsetci) if vsetci else None
    return render(request, 'game/les.html', {'postava': postava, 'nepriatel': nepriatel, 'zona_name': zona})

@login_required
def bojovat(request, postava_id, nepriatel_id):
    postava = get_object_or_404(Postava, id=postava_id, pouzivatel=request.user)
    nepriatel = get_object_or_404(Nepriatel, id=nepriatel_id)
    dmg = max(0, nepriatel.sila - postava.obrana)
    postava.hp -= dmg
    if postava.hp <= 0:
        postava.delete()
        return redirect('zoznam_postav')
    postava.xp += nepriatel.xp_odmena
    postava.zlato += 20
    postava.save()
    messages.warning(request, f"Boj s {nepriatel.nazov}! -{dmg} HP. Si stále v divočine!")
    return redirect(f"/postava/{postava.id}/boj/?zona=les")

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
        if typ == 'sila': postava.sila += 10
        else: postava.obrana += 10
        postava.save()
    return redirect('kovac', postava_id=postava.id)