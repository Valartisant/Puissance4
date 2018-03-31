# Définition des constantes
LARGEURGRILLE = 7
HAUTEURGRILLE = 6
CASEVIDE = "."
CASEJOUEUR1 = "X"
CASEJOUEUR2 = "O"


# Création de la grille de jeu
def creer_grille():
    liste = []
    for i in range(HAUTEURGRILLE):
        liste.append([CASEVIDE] * LARGEURGRILLE)
    return liste


# Génère les en-têtes : liste de chaînes
def en_tete_colonnes():
    return [str(numero_colonne) for numero_colonne in range(LARGEURGRILLE)]


# Affiche une matrice d'une manière 'propre' : sert à afficher la grille de jeu
def affiche_grille(matrice):
    nligne = len(matrice)
    ncolonne = len(matrice[0])
    for i in range(nligne):
        for j in range(ncolonne):
            print(matrice[i][j], end=' ')
        print()


# Affiche une liste d'une manière 'propre' : sert à afficher l'en-tête
def affiche_en_tete(en_tete):
    ncolonne = len(en_tete)
    for i in range(ncolonne):
        print(en_tete[i], end=' ')
    print()


# Affiche le plateau de jeu : en tête + grille
def affiche_plateau(en_tete, grille):
    affiche_en_tete(en_tete)
    affiche_grille(grille)


# Teste si la saisie du joueur est valide (une des valeurs de l'en-tête) : retourne l'indice de la colonne choisie
def saisie(en_tete):
    reponse = input("Où voulez-vous jouer ? ")
    if reponse in en_tete:
        return en_tete.index(reponse)
    else:
        print('Veuillez saisir une valeur correcte')
        return saisie(en_tete)


# Gère la saisie du joueur : modifie la grille en fonction de la saisie du joueur, renvoie True si la grille à été
# modifiée, False sinon
def gestion_saisie(grille, saisie_joueur, casejoueur):
    n = 0
    for k in range(HAUTEURGRILLE-1):
        if grille[k][saisie_joueur] == CASEVIDE:
            n += 1
        else:
            grille[n][saisie_joueur] = casejoueur
            return True


    return False


# Grille représentant l'état du jeu
grille = creer_grille()
# En tête qui sera affichée au dessus de la grille
en_tete = en_tete_colonnes()

affiche_plateau(en_tete, grille)
n = saisie(en_tete)
gestion_saisie(grille, n, CASEJOUEUR1)
affiche_plateau(en_tete, grille)


# Pour l'animation : il faudrait modifier 'en direct' le plateau qui serait tout le temps affiché


