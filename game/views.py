from django.shortcuts import get_object_or_404, redirect , render
from .models import Postava
from .forms import PostavaForm
import random

def zoznam_postav(request):
    postavy = Postava.objects.all() # Vytiahne úplne všetko z databázy
    return render(request, 'game/zoznam.html', {'vsetky_postavy': postavy})

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
    postava.save()

    return redirect('/postavy/')