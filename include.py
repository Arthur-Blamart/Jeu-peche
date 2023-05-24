from random import randint
from time import time
import pygame
import pickle


pygame.init()

class Poisson:
    def __init__(self):
        self.en_vie = True
        self.spawn = False
        self.tps_creation = time() #on regarde quand le poisson a été crée pour plus tard savoir quand il peut spawn
        self.tps_avant_spawn = randint(2,6)
        self.tps_spawn = time() 
        self.tps_avant_fuite = randint(1,4)
        self.taille = 100
        self.x = randint(0,600)
        self.y = randint(0,600)
        self.chance = randint(1,100)
        if self.chance<=40:
            self.rarete = (1,'poisson commun',0.5) #on a dans l'ordre : le numéro de la rarete, le nom de la rarete et le multiplcateur de score
        elif 40<self.chance<=65:
            self.rarete = (2,'poisson rare',0.75)
        elif 65<self.chance<=72:
            self.rarete = (3,'poisson épic',2)
        elif 72<self.chance<=75:
            self.rarete = (4,'poisson légendaire',5)
        elif 75<self.chance<=100:
            self.rarete = (5,'déchet',-0.5)
        if self.rarete[0] == 5:
            self.sprite = pygame.image.load("assets/goutte_dechet.png")
        else:
            self.sprite = pygame.image.load("assets/goutte.png")
    def test_spawn(self):
        if ecart_tps(self.tps_creation)>=self.tps_avant_spawn:
            self.spawn = True
            self.tps_spawn = time()
    def attraper(self):
        self.en_vie = False
    def test_fuite(self):
        if ecart_tps(self.tps_spawn)>=self.tps_avant_fuite:
            self.fuite()
            return True
        else:
            return False
    def fuite(self):
        if self.rarete[0] !=5:
            print('Oh non le poisson a fuit')
        else:
            print("Bravo tu ne t'est pas fait avoir !")
        self.en_vie = False

def test_position(x,y,debutx,debuty,taillex,tailley):
    abscisse = (debutx<=x<=(debutx+taillex))
    ordonne = (debuty<=y<=(debuty+tailley))
    return abscisse and ordonne

class Score:
    def __init__(self):
        self.montant = 0
    def variation(self,c_multi_rarete,c_multi_tps,multi_chain):
        self.montant += round(100*c_multi_rarete*c_multi_tps*(1+(multi_chain/5)))
        print(round(100*c_multi_rarete*c_multi_tps*(1+(multi_chain/5))))
    def reset(self):
        self.montant = 0

class Music:
    def __init__(self):
        self.etat = False #si une musique est en cours
        self.playlist = ["music1.wav","music2.wav"]
        self.pos_playlist = 0
        self.current_music = pygame.mixer.Sound("assets/music/music1.wav") #on commence a la premiere musique
        self.volume = 0.3
    def jouer(self):
        self.etat = True
        self.current_music.play(-1,0,5000)
    def arreter(self):
        self.etat = False
        self.current_music.stop()
    def suivante(self):
        self.etat = True
        self.current_music.stop() #on arrete la musqiue avant de changer sinon elles vont s'empiler
        if self.pos_playlist < len(self.playlist)-1 : #le -1 car si par exemple on a deux musique len(playlist) = 2 alors que la position de la deuxieme sera 1
            self.pos_playlist+=1
        else:
            self.pos_playlist = 0
        self.current_music = pygame.mixer.Sound("assets/music/{}".format(self.playlist[self.pos_playlist]))
        self.current_music.play(-1,0,5000)
    def baisser_volume(self):
        if self.volume>0.0:
            self.volume-=0.1
            self.current_music.set_volume(self.volume)
    def monter_volume(self):
        if self.volume<1.0:
            self.volume+=0.1
            self.current_music.set_volume(self.volume)

class Argent:
    def __init__(self):
        self.montant = 0
    def augmentation(self,c_valeure):
        self.montant += c_valeure
    def reset(self):
        self.montant = 0


class Bag():
    def __init__(self):
        self.contenu = []
        self.multi_vente = 1
        self.benefice = 0
    def ajouter(self,c_quoi):
        self.contenu.append(c_quoi)
    def vider(self):
        self.contenu = []
    def vente(self,c_lvl,bonus_stonks): #bonus_stonks si on a ce bonus on gagne plus d'argent
        self.benefice = 0
        if not(len(self.contenu) <= 0):
            if 0>len(self.contenu)>=10:
                self.multi_vente = 1
            elif 10>len(self.contenu)>=20:
                self.multi_vente = 1.5
            elif 20>len(self.contenu)>=30:
                self.multi_vente = 2
            elif 30>len(self.contenu)>=35:
                self.multi_vente = 2.5
            elif 35>len(self.contenu)>=40:
                self.multi_vente = 3
            elif 40>len(self.contenu)>=45:
                self.multi_vente = 3.5
            elif 45>len(self.contenu)>=47:
                self.multi_vente = 4
            elif 47>len(self.contenu)>=49:
                self.multi_vente = 4.5
            elif len(self.contenu) >= 50:
                self.multi_vente = 5
            for k in self.contenu:
                if k == 1:
                    self.benefice += 1 * self.multi_vente *(1+c_lvl/10)
                elif k == 2:
                    self.benefice += 1.5 * self.multi_vente
                elif k == 3:
                    self.benefice += 2 * self.multi_vente
                elif k == 4:
                    self.benefice += 3 * self.multi_vente
        if bonus_stonks:
            self.benefice*=1.5
        return round(self.benefice)

class Player:
    def __init__(self):
        self.niveau = 1
        self.avant_monter = (self.niveau+1) **8
        self.xp_debordant = 0 #sert a calculer l'xp qui deborde d'un lvl up
        self.lvl_up = False
    def verif_niveau(self,xp_gagne):
        self.lvl_up = False
        print("verif lvl")
        if self.avant_monter > xp_gagne:
            self.avant_monter -= xp_gagne
        else:
            self.lvl_up = True
            print("lvl up")
            if xp_gagne == self.avant_monter:
                self.avant_monter == (self.niveau+1) **8
                self.niveau += 1
            else:
                self.xp_debordant = xp_gagne - self.avant_monter
                self.niveau += 1
                self.avant_monter == ( (self.niveau+1) **8 ) - self.xp_debordant
                if self.avant_monter <=0:
                    self.avant_monter == (self.niveau+1) **8
                    self.niveau += 1
        self.xp_debordant = 0
        print('xp avant monter :',self.avant_monter)
        return self.lvl_up
    def reset(self):
        self.niveau = 1
        self.avant_monter = (self.niveau+1) **8

class Bonus():
    def __init__(self):
        self.liste_bonus_obtenu = []
        self.liste_bonus_manquant = ["Canne de rechange","Canne de rechange","Stonks"]
        self.hasard = 0 #va servir a choisir un element de la liste au hasard
        self.vie_en_plus = 0
    def reset(self):
        for k in range(len(self.liste_bonus_obtenu)):
            self.liste_bonus_manquant.append(self.liste_bonus_obtenu[0]) #les [0] marche car a chaque fois on supprime l'ancien on fait donc comme ca toute la liste
            del self.liste_bonus_obtenu[0]
    def gagner_alea(self):
        if len(self.liste_bonus_manquant)>0:
            self.hasard = randint(0,len(self.liste_bonus_manquant)-1)
            self.liste_bonus_obtenu.append(self.liste_bonus_manquant[self.hasard])
            del self.liste_bonus_manquant[self.hasard]
            return self.liste_bonus_obtenu[len(self.liste_bonus_obtenu)-1] #on retourne le dernier elements de la liste donc celui que l'on vient d'obtenir      
        

class Color:
    def __init__(self):
        self.bleu = (15,20,197)
        self.rouge = (255,51,51)
        self.noir = (0,0,0)
        self.blanc = (255,255,255)
        self.vert = (46, 251, 44)
        self.cyan =	(0,255,255)
def ecart_tps(tps_debut):
    return (time()-tps_debut)



def reset_score_best():
    with open("score.data","wb") as fic:
        rec = pickle.Pickler(fic)
        rec.dump(0)
    print('reset des scores effectué')