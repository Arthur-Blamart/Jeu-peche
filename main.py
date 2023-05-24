import pygame
import pickle
from include import *
from time import time
from random import randint

pygame.init()

taille_fenetre_x,taille_fenetre_y = 700,700

canne_icon = pygame.image.load("assets/canne_icon.png")
background_intro=pygame.image.load("assets/background_intro.png")
background = pygame.image.load("assets/background.png")
background_vendre = pygame.image.load("assets/background_vendre.png")
background_roue = pygame.image.load("assets/background_roue.png")
bouton_reset = pygame.image.load('assets/reset.png')
bouton_musique = pygame.image.load('assets/musique.png')
bouton_nomusique = pygame.image.load('assets/nomusique.png')
bouton_musique_suivante = pygame.image.load('assets/musique_suivante.png')
cursor = pygame.image.load('assets/cursor.png')
bouton_retour_menu = pygame.image.load("assets/retour_menu.png")
bouton_abandon = pygame.image.load("assets/abandon.png")
bouton_vendre = pygame.image.load("assets/vendre.png")
ecran = pygame.display.set_mode((taille_fenetre_x,taille_fenetre_y))
pygame.display.set_icon(canne_icon)
pygame.display.set_caption("Un super jeu")
son_ploup = pygame.mixer.Sound("assets/ploup.wav")
son_ploup.set_volume(0.3)
bouton_oui = pygame.image.load("assets/oui.png")
bouton_non = pygame.image.load("assets/non.png")
bouton_musique_moins = pygame.image.load("assets/musique_moins.png")
bouton_musique_plus = pygame.image.load("assets/musique_plus.png")
bouton_roue = pygame.image.load("assets/roue.png")
bouton_magasin = pygame.image.load("assets/bouton_magasin.png")
bouton_peche = pygame.image.load("assets/bouton_peche.png")
bouton_stats = pygame.image.load("assets/bouton_stats.png")
fleche_gauche = pygame.image.load("assets/fleche_gauche.png")

taille_goutte = 100
running = True
poisson_arrive=False
x,y=0,0

vie_base = 1

multi_tps_act = 1 #sert a multiplier le score plus le temps avance
nb_multi_change = 1 #sert a savoir combien de fois le multiplicateur a changé
tps_entre_chang_multi = 5 #5 secondes entre chaque changement de multiplicateur de temps
variation_multi_tps = 0.01 #de combien monte le multi tps par <tps_entre_chang_multi>
tps_en_pause = 0 #il faut bien savoir combien de temps on est rester en pause pour ne pas que ce temps soit compter dans le mutliplicateur de temps de jeu
poisson_catch_chain = 0 #combien de poisson on enchaine ce qui donne de plus en plus de points
duree_message_poisson = 2 #combien de temps le message qui affiche quel type de poisson on a eu doit rester
tps_spawn_message_poisson = 0 #quand le message est apparu
message_poisson_etat = False #true si un message sur le poisson attraper est à l'écran
message_poisson_rarete_dernier = ("") #a la rarete du poisson attraper, il faut le mettre dans une variable car le message doit s'afficher meme quand le nouveau poisson sera créé

score = Score()

musique = Music()

sac = Bag()

money = Argent()

couleur = Color()

font = pygame.font.Font('freesansbold.ttf',34)
def show_txt(quoi,x,y,color):
    score_surf = font.render(quoi,True,color)
    ecran.blit(score_surf, (x,y))

try:
    with open("score.data","rb") as fic:
        rec = pickle.Unpickler(fic)
        score_best_old = rec.load()
    print("Fichier 1 localisé.") 
except:
    print('pas de fichier, creation du fichier...')
    with open("score.data","wb") as fic:
        rec = pickle.Pickler(fic)
        rec.dump(0)

    score_best_old = 0


try:
    with open("argent.data","rb") as fic:
        rec = pickle.Unpickler(fic)
        money.montant = rec.load()
    print("Fichier 2 localisé.")
except:
    with open("argent.data","wb") as fic:
        rec = pickle.Pickler(fic)
        rec.dump(0)#pas besoin de mettre agrent.montant = 0 car quand la classe a été init ca été deja mis a 0

try:
    with open("player.data","rb") as fic:
        rec = pickle.Unpickler(fic)
        joueur = rec.load()
    print("Fichier 3 localisé.")
except:
    joueur = Player()
    with open("player.data","wb") as fic:
        rec = pickle.Pickler(fic)
        rec.dump(joueur)

try:
    with open("bonus.data","rb") as fic:
        rec = pickle.Unpickler(fic)
        bonus = rec.load()
    print("fichier 4 localisé.")
except:
    bonus = Bonus()
    with open("bonus.data","wb") as fic:
        rec = pickle.Pickler(fic)
        rec.dump(bonus)


print("PB : {}".format(score_best_old))

def intro(c_running):
    global running
    global score_best_old
    global x,y
    global intro_running
    intro_running=c_running
    while intro_running:
        ecran.blit(background_intro,(0,0))
        ecran.blit(bouton_magasin,(100,200))
        ecran.blit(bouton_peche,(450,240))
        ecran.blit(bouton_stats,(280,450))
        ecran.blit(bouton_reset,(taille_fenetre_x-100,taille_fenetre_y-35))
        if musique.etat:
            ecran.blit(bouton_nomusique,(0,taille_fenetre_y-50))
        else:
            ecran.blit(bouton_musique,(0,taille_fenetre_y-50))
        ecran.blit(bouton_musique_suivante,(50,taille_fenetre_y-50))
        ecran.blit(bouton_musique_moins,(100,taille_fenetre_y-50))
        ecran.blit(bouton_musique_plus,(150,taille_fenetre_y-50))
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_SPACE:
                    intro_running=False
                elif event.key == pygame.K_ESCAPE:
                    intro_running = False
                    running = False
                elif event.key == pygame.K_f:
                    print("touche de teste")
                    musique.baisser_volume()
                elif event.key == pygame.K_g:
                    musique.monter_volume()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                if test_position(x,y,taille_fenetre_x-100,taille_fenetre_y-35,100,35): #teste si on clique sur le bouton reset
                    if reset_protection(): #return True si on veut reset
                        reset_score_best()
                        score_best_old = 0 #la c'est pour que le bon nombre soit afficher a l'écran
                        money.reset()
                        joueur.reset()
                        bonus.reset()
                elif test_position(x,y,0,taille_fenetre_y-50,50,50):
                    if musique.etat:
                        musique.arreter()
                    else:
                        musique.jouer()
                elif test_position(x,y,50,taille_fenetre_y-50,50,50): #musique suivante
                    musique.suivante()
                elif test_position(x,y,100,taille_fenetre_y-50,50,50):#volume moins
                    musique.baisser_volume()
                elif test_position(x,y,150,taille_fenetre_y-50,50,50):#volume plus
                    musique.monter_volume()
                elif test_position(x,y,100,200,150,110):#bouton magasin    110 en tailley et pas 150 parce que la queu de la bulle depasse de 40px et on ne veut pas que cliquer a coter de la qeu marche
                    shop()
                elif test_position(x,y,450,240,150,110):#bouton peche
                    intro_running = False
                elif test_position(x,y,280,490,150,110):#bouton stats
                    print("stats")
            elif event.type==pygame.QUIT:
                running=False
                intro_running = False
        show_txt("argent : {}".format(str(money.montant)),taille_fenetre_x-230,0,couleur.bleu)
        show_txt("lvl : {}".format(str(joueur.niveau)),0,0,couleur.bleu)
        pygame.display.flip()

def jeu(c_running):
    global running,jeu_running
    global tps_debut_jeu
    global multi_tps_act
    global nb_multi_change
    global x,y
    global poisson_catch_chain
    global message_poisson_etat,message_poisson_rarete_dernier_attraper,tps_spawn_message_poisson
    global tps_en_pause

    tps_debut_jeu = time()
    poisson_catch_chain = 0
    multi_tps_act = 1
    tps_en_pause = 0
    vie = vie_base + bonus.liste_bonus_obtenu.count("Canne de rechange")

    sac.vider()

    jeu_running=c_running
    poisson_actuel = Poisson()

    while jeu_running:
        ecran.blit(background,(0,0))
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running,jeu_running=False,False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    pause()
                elif event.key == pygame.K_g:
                    print("Touche de teste")
                    perdu()
            elif event.type==pygame.MOUSEMOTION:
                x,y=event.pos
            elif event.type==pygame.MOUSEBUTTONDOWN:
                son_ploup.play()
                if test_position(x,y,poisson_actuel.x,poisson_actuel.y,poisson_actuel.taille,poisson_actuel.taille):
                    print('Tu as péché un',poisson_actuel.rarete[1])
                    poisson_actuel.attraper()
                    score.variation(poisson_actuel.rarete[2],multi_tps_act,poisson_catch_chain)
                    if  poisson_actuel.rarete[0] == 5: #si on attrape un dechet ca casse la chaine
                        poisson_catch_chain = 0
                        vie -= 1
                    else:
                        poisson_catch_chain += 1
                        sac.contenu.append(poisson_actuel.rarete[0])
                    tps_spawn_message_poisson = time()
                    message_poisson_etat = True
                    message_poisson_rarete_dernier_attraper = poisson_actuel.rarete[1]

        if vie <= 0:
            perdu()

        if poisson_actuel.en_vie==False:
            poisson_actuel = Poisson()

        if not(poisson_actuel.spawn):
            poisson_actuel.test_spawn()
        else:
            ecran.blit(poisson_actuel.sprite,(poisson_actuel.x,poisson_actuel.y))
            if poisson_actuel.test_fuite():
                if poisson_actuel.rarete[0]!=5:
                    poisson_catch_chain = 0
                    vie -=1

        if ecart_tps(tps_debut_jeu)-tps_en_pause>=(tps_entre_chang_multi*nb_multi_change):
            multi_tps_act += variation_multi_tps
            nb_multi_change += 1
        ecran.blit(cursor,(x-15,y))
        show_txt("Score : {}".format(str(score.montant)),0,0,couleur.bleu)

        if message_poisson_etat:
            show_txt(message_poisson_rarete_dernier_attraper,250,50,couleur.bleu)
            if ecart_tps(tps_spawn_message_poisson) >= duree_message_poisson:
                message_poisson_etat = False

        pygame.display.flip()

def pause():
    global running,jeu_running
    global x,y
    global tps_en_pause
    pause_running = True
    debut_pause = time()
    show_txt("Jeu en Pause",240,50,couleur.noir)
    print(sac.contenu)
    while pause_running:
        ecran.blit(bouton_vendre,((taille_fenetre_x-350)//2,150))
        ecran.blit(bouton_abandon,((taille_fenetre_x-350)//2,250))
        ecran.blit(bouton_musique_moins,(100,taille_fenetre_y-50))
        ecran.blit(bouton_musique_plus,(150,taille_fenetre_y-50))
        if musique.etat:
            ecran.blit(bouton_nomusique,(0,taille_fenetre_y-50))
        else:
            ecran.blit(bouton_musique,(0,taille_fenetre_y-50))
        ecran.blit(bouton_musique_suivante,(50,taille_fenetre_y-50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pause_running,jeu_running,running = False,False,False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_running = False
            elif event.type ==pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                if test_position(x,y,(taille_fenetre_x-350)//2,150,350,70): #bouton retour menu
                    ecran_score()
                    pause_running,jeu_running = False,False
                elif test_position(x,y,(taille_fenetre_x-350)//2,250,350,70): #bouton abandon
                    pause_running,jeu_running = False,False
                elif test_position(x,y,0,taille_fenetre_y-50,50,50):
                    if musique.etat:
                        musique.arreter()
                    else:
                        musique.jouer()
                elif test_position(x,y,50,taille_fenetre_y-50,50,50): #musique suivante
                    musique.suivante()
                elif test_position(x,y,100,taille_fenetre_y-50,50,50):#volume moins
                    musique.baisser_volume()
                elif test_position(x,y,150,taille_fenetre_y-50,50,50):#volume plus
                    musique.monter_volume()
        pygame.display.flip()
    tps_en_pause += ecart_tps(debut_pause)

def perdu():
    global jeu_running,running
    global x,y
    perdu_running = True
    etat_mot = True# on doit ecrire le mot (ensuite ce sera false quand il sera deja apparu pour qu'on ai qu'a creer le texte qu'une fois)
    while perdu_running:
        ecran.blit(bouton_retour_menu,((taille_fenetre_x-350)//2,250))
        ecran.blit(bouton_musique_moins,(100,taille_fenetre_y-50))
        ecran.blit(bouton_musique_plus,(150,taille_fenetre_y-50))
        if musique.etat:
            ecran.blit(bouton_nomusique,(0,taille_fenetre_y-50))
        else:
            ecran.blit(bouton_musique,(0,taille_fenetre_y-50))
        ecran.blit(bouton_musique_suivante,(50,taille_fenetre_y-50))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                perdu_running,jeu_running,running = False,False,False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    perdu_running,jeu_running = False,False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                if test_position(x,y,0,taille_fenetre_y-50,50,50):
                    if musique.etat:
                        musique.arreter()
                    else:
                        musique.jouer()
                elif test_position(x,y,50,taille_fenetre_y-50,50,50): #musique suivante
                    musique.suivante()
                elif test_position(x,y,100,taille_fenetre_y-50,50,50):#volume moins
                    musique.baisser_volume()
                elif test_position(x,y,150,taille_fenetre_y-50,50,50):#volume plus
                    musique.monter_volume()
                if test_position(x,y,(taille_fenetre_x-350)//2,150,(taille_fenetre_x-350)//2+340,150+65): #bouton retour menu
                    perdu_running,jeu_running = False,False

        if etat_mot:
            show_txt("Fin de la partie",250,20,couleur.rouge)
            show_txt("Vous avez casser toutes vos cannes",40,70,couleur.rouge)
            show_txt("Votre score : {}".format(score.montant),240,140,couleur.vert)
            etat_mot = False
        
        pygame.display.flip()
    print("fin perdu")

def ecran_score():
    global running
    global background_vendre
    ecran_score_running = True
    etat_mot = True
    lvl_up = joueur.verif_niveau(score.montant) #return True si on a gagné un niveau masi fait les calculs dans tous les cas
    argent_obtenu = sac.vente(joueur.niveau,"Stonks" in bonus.liste_bonus_obtenu) #le dernier parametre est pour savoir si on a le bonus "stonks" qui donne plus d'argent
    print("Stonks" in bonus.liste_bonus_obtenu)
    money.augmentation(argent_obtenu)
    print("Tu as gagné {} de money.".format(argent_obtenu))
    pygame.draw.rect(ecran,couleur.noir,(0,0,700,700))
    if argent_obtenu > 0:
        background_vendre = pygame.image.load("assets/background_vendre.png")
    else:
        background_vendre = pygame.image.load("assets/background_vendre_0.png")

    while ecran_score_running:
        ecran.blit(background_vendre,(0,0))
        for event in pygame.event.get():
            if event.type ==pygame.QUIT:
                ecran_score_running,running = False,False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ecran_score_running = False
        if lvl_up:
            show_txt("LVL UP",300,40,couleur.vert)
        show_txt("Vous avez gagné {} piece.".format(argent_obtenu),150,0,couleur.noir)
        show_txt("Appuyez sur espace pour continuer",60,480,couleur.noir)
        pygame.display.flip()
    print(joueur.avant_monter)

def reset_protection():
    global running,intro_running,running
    global x,y
    reset_running = True
    etat_affiche = True #si on doit faire apparaitre les trucs qui ne doivent etre appeler qu'une fois (ensuite ce sera false quand il sera deja apparu pour qu'on ai qu'a creer les trucs qu'une fois)
    etat_reset = False #sait si on a reset ou pas le score
    while reset_running:
        ecran.blit(bouton_oui,(225,230))
        ecran.blit(bouton_non,(375,230))
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    print('')
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                if test_position(x,y,225,230,100,35):#bouton oui
                    etat_reset = True
                    reset_running = False
                elif test_position(x,y,375,230,100,35):#bouton non
                    reset_running = False
            elif event.type == pygame.QUIT:
                reset_running,intro_running,running = False,False,False
        if etat_affiche:
            etat_affiche = False
            pygame.draw.rect(ecran,couleur.noir,(150,130,400,200))
            show_txt("Etes vous sûr ?",222,150,couleur.rouge)
        pygame.display.flip()
    return etat_reset

def shop():
    global intro_running,running,shop_running
    shop_running = True
    while shop_running:
        ecran.blit(background_roue,(0,0))
        ecran.blit(fleche_gauche,(0,600))
        ecran.blit(bouton_roue,(30,235)) #roue de gauche pour skin
        ecran.blit(bouton_roue,(500,235)) #roue de droite pour skin
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                shop_running,intro_running,running = False,False,False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    shop_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                if test_position(x,y,30,235,150,150):#si on touche la roue a skin
                    print("roue skin")
                elif test_position(x,y,500,235,150,150):#si on touche la roue a bonus
                    roue_bonus()
                elif test_position(x,y,0,600,100,100):
                    shop_running =False

        pygame.display.flip()


def roue_bonus():
    global running,intro_running,shop_running
    roue_bonus_running = True
    prix_bonus = 100 * (len(bonus.liste_bonus_obtenu)+1)
    pygame.draw.rect(ecran,couleur.cyan,(75,130,550,250))
    nouveau_bonus = ""
    show_txt("Voulez vous payer {} ?".format(prix_bonus),150,150,couleur.noir)
    while roue_bonus_running:
        ecran.blit(bouton_oui,(225,230))
        ecran.blit(bouton_non,(375,230))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                roue_bonus_running,running,intro_running,shop_running = False,False,False,False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    roue_bonus_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                if test_position(x,y,225,230,100,35):#bouton oui
                    pygame.draw.rect(ecran,couleur.cyan,(75,230,550,150)) #on fait apparaitre un rectangle sur le texte qui dis ce qu'on a deja gagner pour le cacher pour ne pas que le text se superpose
                    if money.montant >= prix_bonus: 
                        if len(bonus.liste_bonus_manquant) > 0:
                            money.montant -= prix_bonus
                            nouveau_bonus = bonus.gagner_alea()
                            show_txt("Vous avez gagner :",175,280,couleur.noir)
                            show_txt("{}".format(nouveau_bonus),150,320,couleur.noir)
                            pygame.draw.rect(ecran,couleur.cyan,(75,130,550,100)) #pour actualiser le nouveau prix du bonus sans quel es mots s'empile
                            prix_bonus = 100 * (len(bonus.liste_bonus_obtenu)+1)
                            show_txt("Voulez vous payer {} ?".format(prix_bonus),150,150,couleur.noir)
                        else:
                            show_txt("Vous avez deja tout les bonus",100,270,couleur.noir)
                    else:
                        show_txt("Vous n'avez pas assez d'argent.",100,270,couleur.noir)
                elif test_position(x,y,375,230,100,35):#bouton non
                    roue_bonus_running = False

        
        pygame.display.flip()


while running:
    intro(running)
    pygame.draw.rect(ecran,couleur.noir,(0,0,700,700))
    pygame.display.flip()
    jeu(running)

    score_fin = score.montant
    score.reset()
    if score_best_old<score_fin:
        with open("score.data","wb") as fic:
            rec = pickle.Pickler(fic)
            rec.dump(score_fin)
        print('Bravo tu as battu ton record :D  !')
        score_best_old = score_fin
    else:
        print('Tu as fait moins bien :(  !')

    print("Tu as fait",score_fin,"points.")

with open("argent.data","wb") as fic:
    rec = pickle.Pickler(fic)
    rec.dump(money.montant)

with open("player.data","wb") as fic:
    rec = pickle.Pickler(fic)
    rec.dump(joueur)

with open("bonus.data","wb") as fic:
    rec = pickle.Pickler(fic)
    rec.dump(bonus)