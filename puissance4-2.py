#Alternate version of the base game, for 1v1-online testing purpose

import os
import p4online as online

online.newlobby()

# Définition des constantes
LARGEURGRILLE = 7
HAUTEURGRILLE = 6
NOMBREDECASESPOURGAGNER = 4
CASEVIDE = "."
CASEJOUEUR1 = "X"
CASEJOUEUR2 = "O"
SEPARATION = "="


# Efface la console (1ère commande pour windows, 2ème pour linux)
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# Crée de la grille de jeu
def creer_grille():
    liste = []
    for i in range(HAUTEURGRILLE):
        liste.append([CASEVIDE] * LARGEURGRILLE)
    liste.append([''] * LARGEURGRILLE)
    liste.append([SEPARATION] * LARGEURGRILLE)
    return liste


# Génère l' en-tête : liste de chaînes
def en_tete_colonnes():
    return [str(numero_colonne) for numero_colonne in range(LARGEURGRILLE)]


# Affiche le plateau de jeu : en tête + grille
def affiche_plateau(en_tete, matrice):
    #affiche l'en-tête
    ncolonne = len(en_tete)
    for i in range(ncolonne):
        print(en_tete[i], end=' ')
    print()
    #affiche la grille
    nligne = len(matrice)
    ncolonne = len(matrice[0])
    for i in range(nligne):
        for j in range(ncolonne):
            print(matrice[i][j], end=' ')
        print()


# Teste si la saisie du joueur est valide (une des valeurs de l'en-tête) : retourne l'indice de la colonne choisie
def saisie(en_tete, case):
    if (case == 'X'):
        print("Ce sont les", case, "qui jouent !")
        reponse = input("Où voulez-vous jouer ? ")
        if reponse in en_tete:
            return en_tete.index(reponse)
        else:
            print('Veuillez saisir une valeur correcte')
    else :
        print("Ce sont les", case, "qui jouent !")
        reponse = online.hisTurn()
        return en_tete.index(reponse)
    return saisie(en_tete, case)


# Gère la saisie du joueur : modifie la grille en fonction de la saisie du joueur, renvoie True si la grille à été
# modifiée, False sinon
# On remonte la colonne choisie par le joueur et on remplit la première case vide par son pion
def gestion_saisie(grille, saisie_joueur, casejoueur):
    if grille[0][saisie_joueur] == CASEVIDE:
        for k in range(HAUTEURGRILLE-1, -1, -1):
            if grille[k][saisie_joueur] == CASEVIDE:
                grille[k][saisie_joueur] = casejoueur
                return True
    return False


# Fonction intermédiaire pour tester si NOMBREDECASESPOURGAGNER cases successives sont de la même couleur
def case_test(grille, ligne_depart, colonne_depart, decalage_ligne, decalage_colonne, pion_du_joueur):
    dl = 0
    dc = 0

    for case in range(NOMBREDECASESPOURGAGNER):
        if grille[ligne_depart + dl][colonne_depart + dc] != pion_du_joueur:
            return False
        dl += decalage_ligne
        dc += decalage_colonne
    return True


# Teste si le jeu est gagné : renvoie True si le joueur à gagné, False sinon
def gain_du_jeu(grille, pion_du_joueur):
    # Variable intermédiaire empêchant de tester en dehors de la grille
    limite = NOMBREDECASESPOURGAGNER-1
    # Teste les colonnes
    for colonne in range(LARGEURGRILLE):
        for ligne in range(HAUTEURGRILLE - limite):
            if case_test(grille, ligne, colonne, 1, 0, pion_du_joueur):
                return True
    # Teste les lignes
    for ligne in range(HAUTEURGRILLE):
        for colonne in range(LARGEURGRILLE - limite):
            if case_test(grille, ligne, colonne, 0, 1, pion_du_joueur):
                return True
    # Teste les diagonales gauches (\)
    for colonne in range(LARGEURGRILLE - limite):
        for ligne in range(HAUTEURGRILLE - limite):
            if case_test(grille, ligne, colonne, 1, 1, pion_du_joueur):
                return True
    # Teste les diagonales droites (/)
    for colonne in range(limite, LARGEURGRILLE):
        for ligne in range(HAUTEURGRILLE - limite):
            if case_test(grille, ligne, colonne, 1, -1, pion_du_joueur):
                return True
    return False


# Teste si il reste des cases à remplir
def complet(grille):
    for colonne in range(LARGEURGRILLE):
        if grille[0][colonne] == CASEVIDE:
            return False
    return True


# Demande au joueur si il souhaite rejouer
def recommencer():
    i = input('Voulez-vous rejouer ? o/n ')
    if i in ('o','n'):
        if i == 'o':
            return True
        else:
            return False
    else:
        print("je n'ai pas bien compris...")
        return recommencer()


# Initialise une nouvelle partie : renvoie le joueur courant et la grille vierge
def nouvelle_partie():
    # Grille représentant l'état du jeu
    grille = creer_grille()
    joueur_courant = CASEJOUEUR1
    clear()
    affiche_plateau(en_tete, grille)
    return joueur_courant, grille


# En tête qui sera affichée au dessus de la grille
en_tete = en_tete_colonnes()

# Initialise le joueur courant et la grille
joueur_courant, grille = nouvelle_partie()


# Déroulement du jeu
while True:
    print()
    n = saisie(en_tete, joueur_courant)
    if gestion_saisie(grille, n, joueur_courant):
        clear()
        affiche_plateau(en_tete, grille)
        if gain_du_jeu(grille, joueur_courant):
            print('Bravo ! Gain des', joueur_courant, '!')
            if recommencer():
                joueur_courant, grille = nouvelle_partie()
            else:
                break
        elif complet(grille):
            print("Fin de la partie, personne n'a gagné !")
            if recommencer():
                joueur_courant, grille = nouvelle_partie()
            else:
                break
        elif joueur_courant == CASEJOUEUR1:
            joueur_courant = CASEJOUEUR2
        else:
            joueur_courant = CASEJOUEUR1
    else :
        print()
        print("Cette colonne n'est pas valide !")

print("\n\nAdieu...")
