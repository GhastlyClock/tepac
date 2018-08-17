import random
from math import sqrt
import time
import tkinter as tk
from winsound import Beep

VISINA = 500
SIRINA = 900
VELIKOST = 30
HITROST_OVIRE = 0.45
RDECA, RUMENA, ZELENA, CRNA, MODRA, CIAN, MAGENTA = 'rdeca', 'rumena', 'zelena', 'crna', 'modra', 'cian', 'magenta'
LEVO, DESNO, GOR, DOL = 'levo', 'desno', 'gor', 'dol'
barve = [CIAN, MAGENTA, RDECA, RUMENA, ZELENA, CRNA, MODRA]
prevajalnik = {
    RDECA: 'red',
    RUMENA: 'yellow',
    ZELENA: 'green',
    CRNA: 'black',
    MODRA: 'blue',
    CIAN: 'cyan',
    MAGENTA: 'magenta'
}
inverzni_prevajalnik = {v: k for k, v in prevajalnik.items()}

class Tekac: 
    def __init__(self, polozaj):
        self.polozaj = polozaj
    
    def repr(self):
        return 'Tekac({})'.format(self.polozaj)
    
    def premik(self, smer):
        x, y = self.polozaj
        if smer == LEVO:
            if x > VELIKOST:
                self.polozaj = (x - 15, y)
        elif smer == DESNO:
            if x < SIRINA - VELIKOST:
                self.polozaj = (x + 15, y)
        elif smer == GOR:
            if y > VELIKOST:
                self.polozaj = (x, y - 15)
        elif smer == DOL:
            if y < (VISINA - VELIKOST):
                self.polozaj = (x, y + 15)

class Datoteka:
    def __init__(self, ime):
        self.ime = str(ime)

    def zapisi(self, *args):
        with open(self.ime, 'a') as d:
            for stvar in args:
                print(stvar, file=d)
    
    def uredi(self):
        # Podatki v datoteki bodo zapisani v obliki "ime,rezultat"
        try:
            podatki = []
            with open(self.ime) as d:
                for vrstica in d:
                    ime, rezultat = vrstica.split(',')
                    podatki.append((ime, rezultat))
                podatki.sort(key=lambda x: int(x[1]), reverse=True) # Moram pazit ker so podatki zapisani v 'stringih'
                podatki = podatki[:5]

            with open(self.ime, 'w') as z:
                for podatek in podatki:
                    ime, rezultat = podatek
                    print(ime + ',' + rezultat, file=z, end='')
        except FileNotFoundError:
            pass
    
    def vrni_podatke(self):
        try:
            podatki = []
            with open(self.ime) as d:
                for vrstica in d:
                    ime, rezultat = vrstica.strip('\n').split(',')
                    podatki.append((ime, rezultat))
            return podatki
        except FileNotFoundError:
            return []
                
class Ovira:
    def __init__(self, polozaj, velikost=VELIKOST):
        # Omejim velikost,da slucajno nebi bila premajhna
        if velikost > 15:
            self.velikost = velikost
        else:
            self.velikost = 15
        # barva = prevajalnik[random.choice(barve)]
        self.polozaj = polozaj
        self.barva = prevajalnik[random.choice(barve)]
    
    def repr(self):
        return 'Tekac({}, barva={}, velikost={})'.format(
            self.polozaj, inverzni_prevajalnik[self.barva], self.velikost
        )

    def premik(self, hitrost):
        x, y = self.polozaj
        self.polozaj = (x - hitrost, y)

class Jabolko:
    def __init__(self, polozaj):
        self.polozaj = polozaj
    
    def __repr__(self):
        return 'Jabolko({})'.format(self.polozaj)

class Tocke:
    def __init__(self, tocke):
        self.tocke = tocke

    def __repr__(self):
        return 'Tocke({})'.format(self.tocke)

    def pristevek(self, prist=1):
        self.tocke += prist
    
    def odstevek(self, ods=1):
        self.tocke -= ods

    def resetiraj(self):
        self.tocke = 0

class Igra:
    def __init__(self, okno):
        # Ustvarim oz. odprem datoteko za rezultate
        self.rezultati = Datoteka('rezultati.txt')
        
        # V program vpeljem slike
        self.slika_odzadja = tk.PhotoImage(file='odzadje.gif')
        self.slika_jabolka = tk.PhotoImage(file='jabolko.gif')
        self.slika_tekaca = tk.PhotoImage(file='raketa.gif')
        self.slika_pavze = tk.PhotoImage(file='pause.gif')

        # Priprava okna
        self.okno = okno
        self.igralna_plosca = tk.Canvas(
            width=SIRINA, height=VISINA, bg='white'
        )
        self.ime_igralca = tk.Entry(self.igralna_plosca)
        self.okno_za_gumbe = tk.Frame(self.okno)
        self.nova_igra_gumb = tk.Button(self.okno_za_gumbe, text='NOVA IGRA', command=self.nova_igra)
        self.prikazovalnik_tock = tk.Label(self.okno_za_gumbe, text='0')
        self.prikazovalnik_tock.grid()
        self.nova_igra_gumb.grid()
        self.igralna_plosca.pack()
        self.okno_za_gumbe.pack()

        # Definiramo še točke, ki se boo uporabljale skozi program
        self.tocke_jabolka = Tocke(0)
        self.tocke = Tocke(0)
        self.cakanje_na_odziv()

    def postavi_jabolko(self):
        tekac_x, tekac_y = self.tekac.polozaj
        y = random.randint(0, VISINA)
        x = random.randint(30, SIRINA/2)
        razdalja = sqrt((tekac_x - x) ** 2 + (tekac_y - y) ** 2)
        while razdalja < 100:
            y = random.randint(0, VISINA)
            x = random.randint(30, SIRINA/2)
            razdalja = sqrt((tekac_x - x) ** 2 + (tekac_y - y) ** 2)
        self.jabolko = Jabolko((x, y))

    def pavza(self, event):
        if self.pavza_gumb is False:
            self.okno.after_cancel(self.id)
            self.okno.unbind('<Key>')
            #self.nova_igra_gumb.config(state=tk.NORMAL)
            self.igralna_plosca.create_image(SIRINA/2, VISINA/2, image=self.slika_pavze)
        else:
            self.okno.bind('<Key>', self.obdelaj_tipko)
            #self.nova_igra_gumb.config(state=tk.DISABLED)
            self.osvezi_prikaz()
        self.pavza_gumb = not self.pavza_gumb

    def koncaj_igro(self):
        self.okno.after_cancel(self.id)
        Beep(250, 500) # Naredi globok zvok za konec igre
        self.rezultati.zapisi(self.ime + ',' + str(self.tocke.tocke + self.tocke_jabolka.tocke))
        self.rezultati.uredi()
        self.pokazi_rezultate()

    def nova_igra(self):
        self.okno.unbind('<Return>')  # Odstranim tipko ki sprozi novo igro
        self.ime = self.ime_igralca.get().strip()
        self.ime_igralca.config(state=tk.DISABLED)
        self.nova_igra_gumb.config(text='KONEC', command=self.koncaj_igro)
        if self.ime == 'Vpiši ime' or self.ime.find(',') > 0 or len(self.ime) > 20:
            self.ime = 'Janezsvetokriški'
        self.okno.bind('<Key>', self.obdelaj_tipko)
        self.okno.bind('<p>', self.pavza)
        self.pavza_gumb = False
        self.hitrost_ovir = HITROST_OVIRE  # Nastavim hitrost na začetno
        self.tekac = Tekac((100, VISINA - 75))
        self.postavi_jabolko()
        self.postavi_oviro(VELIKOST * 2)
        self.osvezi_prikaz()

    def osvezi_tocke(self):
        self.prikazovalnik_tock.configure(text=str(self.tocke.tocke + self.tocke_jabolka.tocke))

    def cakanje_na_odziv(self):
        ''' Pojavno okno, pred začetkom igre oziroma med igrama '''
        self.okno.unbind('<Return>')  # Odstranim tipko za prehod iz tabelena začetno stran
        self.igralna_plosca.delete('all')
        def startaj(event):
            self.nova_igra()
        self.igralna_plosca.create_image(SIRINA/2, VISINA/2, image=self.slika_odzadja)
        self.igralna_plosca.create_text(SIRINA/2, VISINA/2, font=("Purisa"), text="\tPozdravljeni v igri Tepač!"\
        + "\nPritisnite gumb \"NOVA IGRA\" za začetek igre")
        self.igralna_plosca.create_text(10, VISINA, text='* V okence vpišite ime, ki je krajše od 20 znakov in ne vsebuje vejice!', anchor=tk.SW) # V spodnji d+levi rob napišem obvestila
        self.ime_igralca.config(state=tk.NORMAL)
        self.ime_igralca.delete(0, last=tk.END)
        self.ime_igralca.insert(0, 'Vpiši ime')
        self.igralna_plosca.create_window(SIRINA/2, VISINA/1.6, window=self.ime_igralca)
        self.okno.bind('<Return>', startaj)

    def pokazi_rezultate(self):
        self.nova_igra_gumb.config(state=tk.DISABLED)
        self.igralna_plosca.delete('all')
        # Odstranim vse "binde" da se v meniju ne dogajajo čudne stvari
        self.okno.unbind('<Key>')
        self.okno.unbind('<p>')
        self.igralna_plosca.create_image(SIRINA/2, VISINA/2, image=self.slika_odzadja)
        def vrni_prikaz(event):
            self.tocke_jabolka.resetiraj()
            self.tocke.resetiraj()
            self.osvezi_tocke() # Da se v začetnem meniju ne pojavlja rezultat prejšne igre
            self.nova_igra_gumb.config(state=tk.NORMAL, text='NOVA IGRA', command=self.nova_igra)
            self.cakanje_na_odziv()
        self.okno.bind('<Return>', vrni_prikaz)
        podatki = self.rezultati.vrni_podatke()
        for stevilo, podatek in enumerate(podatki, 1):
            self.igralna_plosca.create_text(SIRINA/3, VISINA/3 + (stevilo * 30), text=str(stevilo) + '.' + '\t' + str(podatek[0]) + '  ' + str(podatek[1]), font=('Purisa'), anchor=tk.SW)
        self.igralna_plosca.create_text(10, VISINA, text='Za nadaljevanje pritisnite ENTER', anchor=tk.SW)

    def postavi_oviro(self, velikost):
        polozaj = random.randint(50, VISINA - 50)
        self.ovira = Ovira((SIRINA, polozaj), velikost)

    def obdelaj_tipko(self, event):
        if event.keysym == 'Right':
            self.tekac.premik(DESNO)
        elif event.keysym == 'Left':
            self.tekac.premik(LEVO)
        elif event.keysym == 'Up':
            self.tekac.premik(GOR)
        elif event.keysym == 'Down':
            self.tekac.premik(DOL)
        elif event.keysym == 'space':
            self.streljanje()

    def streljanje(self):
        Beep(800, 10)
        t_x, t_y = self.tekac.polozaj
        o_x, o_y = self.ovira.polozaj
        if abs(t_y - o_y) < self.ovira.velikost:
            self.tocke.pristevek()
            self.povecanje_hitrosti_ovir()
            self.igralna_plosca.create_line(t_x + VELIKOST, t_y, o_x - self.ovira.velikost, t_y)
            time.sleep(0.025)
            self.postavi_oviro((VELIKOST * 2) - self.tocke.tocke)
        else:
            self.igralna_plosca.create_line(t_x + VELIKOST, t_y, SIRINA, t_y)

    def pobiranje_jabolk(self):
        t_x, t_y = self.tekac.polozaj
        j_x, j_y = self.jabolko.polozaj
        razdalja = sqrt((j_x - t_x) ** 2 + (j_y - t_y) ** 2)
        return razdalja < (int(self.slika_jabolka.width() - 16)) + (int(self.slika_jabolka.width()) - 16)

    def ali_se_sekata(self):
        ''' Preverimo ali se je ovira dotaknila tekača '''
        o_x, o_y = self.ovira.polozaj  # koordinate ovire
        t_x, t_y = self.tekac.polozaj  # koordinate tekaca
        razdalja = sqrt((o_x - t_x) ** 2 + (o_y - t_y) ** 2)
        if razdalja < (self.slika_tekaca.width() + self.ovira.velikost) - 25:
            self.okno.after_cancel(self.id)
        return razdalja < (self.slika_tekaca.width() + self.ovira.velikost) - 25

    def ali_je_ovira_iz_platna(self):
        x, y = self.ovira.polozaj
        if x < -self.ovira.velikost and self.ovira.velikost < VELIKOST * 2:
            self.povecanje_hitrosti_ovir(povecava=-0.1)
        return x < -self.ovira.velikost
    
    def povecanje_hitrosti_ovir(self, povecava=0.01):
        self.hitrost_ovir += povecava

    def osvezi_prikaz(self):
        self.ovira.premik(self.hitrost_ovir)
        self.igralna_plosca.delete('all')
        self.igralna_plosca.create_image(SIRINA/2, VISINA/2, image=self.slika_odzadja)
        self.igralna_plosca.create_image(self.jabolko.polozaj[0], self.jabolko.polozaj[1], image=self.slika_jabolka)
        if not self.ali_se_sekata():
            self.id = self.okno.after(2, self.osvezi_prikaz)
            t_x, t_y = self.tekac.polozaj
            self.igralna_plosca.create_image(t_x, t_y, image=self.slika_tekaca)
            #self.igralna_plosca.create_rectangle(
            #    t_x - VELIKOST, t_y - VELIKOST, t_x + VELIKOST, t_y + VELIKOST, fill=self.tekac.barva
            #)
            if self.pobiranje_jabolk():
                self.tocke_jabolka.pristevek(3)
                self.postavi_jabolko()
            if not self.ali_je_ovira_iz_platna():
                o_x, o_y = self.ovira.polozaj
                self.igralna_plosca.create_oval(
                o_x - self.ovira.velikost, o_y - self.ovira.velikost, o_x + self.ovira.velikost,
                 o_y + self.ovira.velikost, outline=self.ovira.barva, fill=self.ovira.barva
            )
            else:
                # Če se je ovira dotaknila stene odštejemo vse pridobljene točke od jabolk in odstejemo še 10 tock
                self.tocke.odstevek(10)
                self.tocke_jabolka.resetiraj()
                self.postavi_oviro((VELIKOST * 2) - self.tocke.tocke)
        else:
            self.koncaj_igro()
        self.osvezi_tocke()


okno = tk.Tk()
okno.title('Tepač')
okno.iconbitmap('raketa.ico')
moj_program = Igra(okno)
okno.mainloop()