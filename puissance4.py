import os
from random import randrange
import subprocess


# Définition des constantes
NOMBRE_COLONNES = 7
NOMBRE_LIGNES = 6
NOMBRE_DE_CASES_POUR_GAGNER = 4
CASE_VIDE = "."

PION_JOUEUR_1 = "X"
PION_JOUEUR_2 = "O"

UTILISATION_APLHA_BETA = True
AFFICHAGE_NBRE_COUPS_SIMULES = False


class Grille(object):
    """
    Conteneur rectangulaire
    """
    def __init__(self, nbre_lignes=1, nbre_colonnes=1, valeur_par_defaut=None):
        self._lignes = []
        self._valeur_par_defaut = valeur_par_defaut

        # le nombre de cases vides est mémorisé pour éviter de le calculer à chaque fois (gain de vitesse)
        self._cases_vides = nbre_colonnes * nbre_lignes

        for i in range(nbre_lignes):
            self._lignes.append([valeur_par_defaut] * nbre_colonnes)

    def afficher(self):
        """
        Affiche la grille dans la console
        """
        for i in range(self.nbre_lignes):
            for j in range(self.nbre_colonnes):
                print(self._lignes[i][j], end=' ')
            print()

    @property
    def nbre_lignes(self):
        """
        Renvoie le nombre de lignes de la grille
        :return: entier positif
        """
        return len(self._lignes)

    @property
    def nbre_colonnes(self):
        """
        Renvoie le nombre de colonnes de la grille
        :return: entier positif
        """
        # c'est le nombre de colonnes de la première ligne (toutes les lignes ont le même nombre de colonnes)
        return len(self._lignes[0])

    @property
    def nbre_cases_vides(self):
        """
        Renvoie le nombre de cases vides de la grille (remplies avec la valeur par défaut)
        :return: entier positif
        """
        return self._cases_vides

    def vider(self):
        """
        Place la valeur par défaut dans toute la grille
        """
        for i in range(self.nbre_lignes):
            for j in range(self.nbre_colonnes):
                self._lignes[i][j] = self._valeur_par_defaut

        # ne pas oublier de mettre à jour le nombre de cases vides
        self._cases_vides = self.nbre_colonnes * self.nbre_lignes

    @property
    def est_vide(self):
        """
        Teste si la grille est vide (seulement des cases par défaut)
        :return: True/False
        """
        return self._cases_vides == self.nbre_lignes * self.nbre_colonnes

    @property
    def est_pleine(self):
        """
        Teste si la grille est pleine (autre que des cases par défaut)
        :return: True/False
        """
        return self._cases_vides == 0

    def valeur(self, ligne, colonne):
        """
        Récupère la valeur située en un emplacement
        :param ligne:
        :param colonne:
        :return: Valeur contenue dans l'emplacement
        """
        return self._lignes[ligne][colonne]

    def remplir_case(self, ligne, colonne, valeur):
        """
        Place la valeur en [ligne][colonne] dans la grille
        :param ligne:
        :param colonne:
        :param valeur:
        """
        if valeur == self._valeur_par_defaut and self._lignes[ligne][colonne] != self._valeur_par_defaut:
            self._cases_vides += 1

        elif valeur != self._valeur_par_defaut and self._lignes[ligne][colonne] == self._valeur_par_defaut:
            self._cases_vides -= 1

        self._lignes[ligne][colonne] = valeur

    def vider_case(self, ligne, colonne):
        """
        Place la valeur par défaut en [ligne][colonne] dans la grille
        :param ligne:
        :param colonne:
        """
        self.remplir_case(ligne, colonne, self._valeur_par_defaut)

    def case_est_vide(self, ligne, colonne):
        """
        Teste si la case est vide (contient la valeur par défaut)
        :param ligne:
        :param colonne:
        :return: True/False
        """
        return self._lignes[ligne][colonne] == self._valeur_par_defaut


class Coup(object):
    """
    Mémorisation d'un coup du jeu
    """
    def __init__(self, ligne, colonne, pion):
        self.ligne = ligne
        self.colonne = colonne
        self.pion = pion


class Jeu(object):
    """
    Jeu de type puissance 4
    avec taille du plateau et condition de victoire paramètrables
    """
    def __init__(self, nbre_lignes=NOMBRE_LIGNES, nbre_colonnes=NOMBRE_COLONNES, nbre_cases_gain=NOMBRE_DE_CASES_POUR_GAGNER):
        self._grille = Grille(nbre_lignes, nbre_colonnes, CASE_VIDE)
        self.nbre_cases_gain = nbre_cases_gain

        self.gagne = False

    @property
    def nbre_lignes(self):
        """
        Renvoie le nombre de lignes du jeu
        :return: entier positif
        """
        return self._grille.nbre_lignes

    @property
    def nbre_colonnes(self):
        """
        Renvoie le nombre de colonnes du jeu
        :return: entier positif
        """
        return self._grille.nbre_colonnes

    @property
    def nul(self):
        """
        Perment de savoir si il y a égalité: plus de cases vides et pas de gagnant
        :return: True/False
        """
        return self._grille.est_pleine and not self.gagne

    @property
    def fini(self):
        """
        Permet de savoir si le jeu est terminé
        :return: True/False
        """
        return self.gagne or self._grille.est_pleine

    def afficher(self):
        """
        Affiche le jeu dans la console
        """
        self._grille.afficher()

    def reinitialiser(self):
        """
        Lancement d'un nouveau jeu
        """
        self._grille.vider()
        self.gagne = False

    def jouer(self, colonne, pion):
        """
        Joue avec le pion (on suppose que la colonne est jouable)
        :param colonne:
        :param pion
        :return: Coup joué
        """
        for ligne in range(self._grille.nbre_lignes - 1, -1, -1):
            # la colonne est jouable donc la condition suivante sera toujours vérifiée au cours de la boucle
            if self._grille.case_est_vide(ligne, colonne):
                # mémorisation du coup
                coup = Coup(ligne, colonne, pion)

                # remplissage grille
                self._grille.remplir_case(ligne, colonne, pion)

                # vérification si partie gagnée
                self.gagne = self._test_gain(coup)

                return coup

    def annuler(self, dernier_coup):
        """
        Annule le dernier coup joué
        :param dernier_coup:
        """
        self._grille.vider_case(dernier_coup.ligne, dernier_coup.colonne)

        # puisque le dernier coup vient d'être annulé, le jeu ne peut pas être gagné
        self.gagne = False

    def _test_gain(self, dernier_coup):
        """
        Recherche si le dernier coup est gagnant
        :param dernier_coup:
        :return: True/False
        """
        # ----------------------------------------------------------------------------------------------------------------------------
        # Pas besoin de tester au dessus du dernier coup (cases vides forcément)

        # ----------------------------------------------------------------------------------------------------------------------------
        # Cases du dessous
        if dernier_coup.ligne + self.nbre_cases_gain <= self._grille.nbre_lignes:
            for ligne in range(dernier_coup.ligne, dernier_coup.ligne + self.nbre_cases_gain):
                if self._grille.valeur(ligne, dernier_coup.colonne) != dernier_coup.pion:
                    break
            else:
                # Ce 'else' ne s'execute que si la boucle se termine sans 'break' : le jeu est alors gagné
                return True

        # ----------------------------------------------------------------------------------------------------------------------------
        # Cases horizontales
        recherche_droite = True
        recherche_gauche = True
        colonne_droite = dernier_coup.colonne + 1
        colonne_gauche = dernier_coup.colonne - 1
        nbre_de_cases_alignees = 1

        while True:
            if recherche_droite:
                if colonne_droite < self._grille.nbre_colonnes and self._grille.valeur(dernier_coup.ligne, colonne_droite) == dernier_coup.pion:
                    nbre_de_cases_alignees += 1
                    if nbre_de_cases_alignees == self.nbre_cases_gain:
                        return True

                    colonne_droite += 1
                else:
                    recherche_droite = False

            if recherche_gauche:
                if colonne_gauche >= 0 and self._grille.valeur(dernier_coup.ligne, colonne_gauche) == dernier_coup.pion:
                    nbre_de_cases_alignees += 1
                    if nbre_de_cases_alignees == self.nbre_cases_gain:
                        return True

                    colonne_gauche -= 1
                else:
                    recherche_gauche = False

            if not recherche_droite and not recherche_gauche:
                break

        # ----------------------------------------------------------------------------------------------------------------------------
        # Diagonales droites (/)
        recherche_haut = True
        recherche_bas = True
        colonne_droite = dernier_coup.colonne + 1
        colonne_gauche = dernier_coup.colonne - 1
        ligne_haut = dernier_coup.ligne - 1
        ligne_bas = dernier_coup.ligne + 1
        nbre_de_cases_alignees = 1

        while True:
            if recherche_haut:
                if colonne_droite < self._grille.nbre_colonnes and ligne_haut >= 0 and self._grille.valeur(ligne_haut, colonne_droite) == dernier_coup.pion:
                    nbre_de_cases_alignees += 1
                    if nbre_de_cases_alignees == self.nbre_cases_gain:
                        return True

                    colonne_droite += 1
                    ligne_haut -= 1
                else:
                    recherche_haut = False

            if recherche_bas:
                if colonne_gauche >= 0 and ligne_bas < self._grille.nbre_lignes and self._grille.valeur(ligne_bas, colonne_gauche) == dernier_coup.pion:
                    nbre_de_cases_alignees += 1
                    if nbre_de_cases_alignees == self.nbre_cases_gain:
                        return True

                    colonne_gauche -= 1
                    ligne_bas += 1
                else:
                    recherche_bas = False

            if not recherche_haut and not recherche_bas:
                break

        # ----------------------------------------------------------------------------------------------------------------------------
        # Diagonales gauches (\)
        recherche_haut = True
        recherche_bas = True
        colonne_droite = dernier_coup.colonne + 1
        colonne_gauche = dernier_coup.colonne - 1
        ligne_haut = dernier_coup.ligne - 1
        ligne_bas = dernier_coup.ligne + 1
        nbre_de_cases_alignees = 1

        while True:
            if recherche_haut:
                if colonne_gauche >= 0 and ligne_haut >= 0 and self._grille.valeur(ligne_haut, colonne_gauche) == dernier_coup.pion:
                    nbre_de_cases_alignees += 1
                    if nbre_de_cases_alignees == self.nbre_cases_gain:
                        return True

                    colonne_gauche -= 1
                    ligne_haut -= 1
                else:
                    recherche_haut = False

            if recherche_bas:
                if colonne_droite < self._grille.nbre_colonnes and ligne_bas < self._grille.nbre_lignes and self._grille.valeur(ligne_bas, colonne_droite) == dernier_coup.pion:
                    nbre_de_cases_alignees += 1
                    if nbre_de_cases_alignees == self.nbre_cases_gain:
                        return True

                    colonne_droite += 1
                    ligne_bas += 1
                else:
                    recherche_bas = False

            if not recherche_haut and not recherche_bas:
                break
        return False

    @property
    def colonnes_jouables(self):
        """
        Renvoie la liste des colonnes jouables
        :return: liste
        """
        colonnes_jouables = []
        for colonne in range(self._grille.nbre_colonnes):
            if self._grille.case_est_vide(0, colonne):
                colonnes_jouables.append(colonne)
        return colonnes_jouables

    def nbre_cases_alignees_pion(self, pion):
        """
        Détermination du nombre maximal de pions alignés
        :param pion: pion pour lequel il faut chercher les alignements
        :return: entier
        """
        nbre_max = 0

        # ----------------------------------------------------------------------------------------------------------------------------
        # lignes horizontales
        nb_cases_alignement = 0
        case_vide_debut_alignement = False

        for ligne in range(self._grille.nbre_lignes):
            for colonne in range(self._grille.nbre_colonnes):
                valeur_case = self._grille.valeur(ligne, colonne)

                if valeur_case != pion:
                    case_vide_fin_alignement = valeur_case == CASE_VIDE

                    if nb_cases_alignement > nbre_max and case_vide_fin_alignement:
                        nbre_max = nb_cases_alignement

                    nb_cases_alignement = 0
                    case_vide_debut_alignement = case_vide_fin_alignement
                else:
                    nb_cases_alignement += 1
                    if nb_cases_alignement > nbre_max and case_vide_debut_alignement:
                        nbre_max = nb_cases_alignement

        # ----------------------------------------------------------------------------------------------------------------------------
        # lignes verticales
        nb_cases_alignement = 0
        case_vide_debut_alignement = False

        for colonne in range(self._grille.nbre_colonnes):
            for ligne in range(self._grille.nbre_lignes):
                valeur_case = self._grille.valeur(ligne, colonne)

                if valeur_case != pion:
                    case_vide_fin_alignement = valeur_case == CASE_VIDE

                    if nb_cases_alignement > nbre_max and case_vide_fin_alignement:
                        nbre_max = nb_cases_alignement

                    nb_cases_alignement = 0
                    case_vide_debut_alignement = case_vide_fin_alignement
                else:
                    nb_cases_alignement += 1
                    if nb_cases_alignement > nbre_max and case_vide_debut_alignement:
                        nbre_max = nb_cases_alignement

        # ----------------------------------------------------------------------------------------------------------------------------
        # diagonales /
        nb_cases_alignement = 0
        case_vide_debut_alignement = False

        ligne_depart = 0
        colonne_depart = 0

        ligne = ligne_depart
        colonne = colonne_depart
        while True:
            valeur_case = self._grille.valeur(ligne, colonne)

            if valeur_case != pion:
                case_vide_fin_alignement = valeur_case == CASE_VIDE

                if nb_cases_alignement > nbre_max and case_vide_fin_alignement:
                    nbre_max = nb_cases_alignement

                nb_cases_alignement = 0
                case_vide_debut_alignement = case_vide_fin_alignement
            else:
                nb_cases_alignement += 1
                if nb_cases_alignement > nbre_max and case_vide_debut_alignement:
                    nbre_max = nb_cases_alignement

            if ligne > 0 and colonne < self._grille.nbre_colonnes - 1:
                ligne -= 1
                colonne += 1
            else:
                ligne_depart += 1
                if ligne_depart == self._grille.nbre_lignes:
                    break
                ligne = ligne_depart
                colonne = colonne_depart

        ligne_depart = self._grille.nbre_lignes - 1
        colonne_depart = 1

        ligne = ligne_depart
        colonne = colonne_depart
        while True:
            valeur_case = self._grille.valeur(ligne, colonne)

            if valeur_case != pion:
                case_vide_fin_alignement = valeur_case == CASE_VIDE

                if nb_cases_alignement > nbre_max and case_vide_fin_alignement:
                    nbre_max = nb_cases_alignement

                nb_cases_alignement = 0
                case_vide_debut_alignement = case_vide_fin_alignement
            else:
                nb_cases_alignement += 1
                if nb_cases_alignement > nbre_max and case_vide_debut_alignement:
                    nbre_max = nb_cases_alignement

            if ligne > 0 and colonne < self._grille.nbre_colonnes - 1:
                ligne -= 1
                colonne += 1
            else:
                colonne_depart += 1
                if colonne_depart == self._grille.nbre_colonnes:
                    break
                ligne = ligne_depart
                colonne = colonne_depart

        # ----------------------------------------------------------------------------------------------------------------------------
        # diagonales \
        nb_cases_alignement = 0
        case_vide_debut_alignement = False

        ligne_depart = 0
        colonne_depart = self._grille.nbre_colonnes - 1

        ligne = ligne_depart
        colonne = colonne_depart
        while True:
            valeur_case = self._grille.valeur(ligne, colonne)

            if valeur_case != pion:
                case_vide_fin_alignement = valeur_case == CASE_VIDE

                if nb_cases_alignement > nbre_max and case_vide_fin_alignement:
                    nbre_max = nb_cases_alignement

                nb_cases_alignement = 0
                case_vide_debut_alignement = case_vide_fin_alignement
            else:
                nb_cases_alignement += 1
                if nb_cases_alignement > nbre_max and case_vide_debut_alignement:
                    nbre_max = nb_cases_alignement

            if ligne > 0 and colonne > 0:
                ligne -= 1
                colonne -= 1
            else:
                ligne_depart += 1
                if ligne_depart == self._grille.nbre_lignes:
                    break
                ligne = ligne_depart
                colonne = colonne_depart

        ligne_depart = self._grille.nbre_lignes - 1
        colonne_depart = self._grille.nbre_colonnes - 2

        ligne = ligne_depart
        colonne = colonne_depart
        while True:
            valeur_case = self._grille.valeur(ligne, colonne)

            if valeur_case != pion:
                case_vide_fin_alignement = valeur_case == CASE_VIDE

                if nb_cases_alignement > nbre_max and case_vide_fin_alignement:
                    nbre_max = nb_cases_alignement

                nb_cases_alignement = 0
                case_vide_debut_alignement = case_vide_fin_alignement
            else:
                nb_cases_alignement += 1
                if nb_cases_alignement > nbre_max and case_vide_debut_alignement:
                    nbre_max = nb_cases_alignement

            if ligne > 0 and colonne > 0:
                ligne -= 1
                colonne -= 1
            else:
                colonne_depart -= 1
                if colonne_depart == -1:
                    break
                ligne = ligne_depart
                colonne = colonne_depart

        return nbre_max


class JoueurHumain(object):
    def __init__(self, jeu, nom, pion):
        self.nom = nom
        self.pion = pion

        self._jeu = jeu

    def choix(self):
        """
        Demande un numéro de colonne à l'utilisateur et renvoie ce numéro si la colonne est jouable, -1 pour arrêter
        :return: numéro de colonne (int) ou -1 pour quitter la partie
        """
        while True:
            reponse = input("Où voulez-vous jouer ? \n (exit pour quitter) ")
            try:
                reponse = int(reponse)
            except ValueError:
                if reponse == 'exit':
                    return -1
            else:
                if reponse in self._jeu.colonnes_jouables:
                    return reponse
                else:
                    print('Veuillez saisir une valeur correcte')


class IaAleatoire(object):
    def __init__(self, jeu, nom, pion):
        self.nom = nom
        self.pion = pion

        self._jeu = jeu

    def choix(self):
        """
        Renvoi une colonne au hasard parmi les colonnes jouables
        :return:
        """
        return randrange(len(self._jeu.colonnes_jouables))


class PartieConsole(object):
    def __init__(self, jeu):
        self._jeu = jeu
        self._joueur1 = None
        self._joueur2 = None
        self._joueur_courant = None

        # entêtes de colonne: c'est le numéro à saisir par le joueur pour placer son pion dans la colonne
        self._en_tete_colonne = [str(numero_colonne) for numero_colonne in range(self._jeu.nbre_colonnes)]

    def _effacer_ecran(self):
        """
        Efface la console (1ère commande pour windows, 2ème pour linux)
        """
        os.system('cls' if os.name == 'nt' else 'clear')

    def _affiche_plateau(self):
        """
        Affiche le plateau de jeu : en tête + grille
        """
        # affiche l'en-tête
        ncolonne = len(self._en_tete_colonne)
        for i in range(ncolonne):
            print(self._en_tete_colonne[i], end=' ')
        print()

        # affiche le jeu
        self._jeu.afficher()

        # affiche la séparation
        print()
        print("= " * ncolonne)

    def _recommencer(self):
        """
        Demande au joueur si il souhaite rejouer
        :return: True/False
        """
        while True:
            i = input('Voulez-vous rejouer ? o/n ')
            if i in ('o', 'n'):
                return i == 'o'
            else:
                print("Je n'ai pas bien compris...")

    def _nouvelle_partie(self):
        """
        Initialise une nouvelle partie
        """
        self._effacer_ecran()
        print('Bienvenue dans le jeu du puissance 4 !')

        nbre_joueurs_humains = self._demander_nbre_joueurs()

        if nbre_joueurs_humains == 0:
            profondeur = self._demander_profondeur_ia()
            if profondeur != -1:
                self._joueur1 = IAMinMax(self._jeu, 'MinMax1', PION_JOUEUR_1, PION_JOUEUR_2, profondeur, UTILISATION_APLHA_BETA)
                self._joueur2 = IAMinMax(self._jeu, 'MinMax2', PION_JOUEUR_2, PION_JOUEUR_1, profondeur, UTILISATION_APLHA_BETA)
            else:
                self._joueur1 = IaAleatoire(self._jeu, 'Random1', PION_JOUEUR_1)
                self._joueur2 = IaAleatoire(self._jeu, 'Random2', PION_JOUEUR_2)

        elif nbre_joueurs_humains == 1:
            nom = input('Pseudo du joueur ?')
            while nom == 'Minmax' or nom == 'Random':
                print('Le nom du joueur doit être différent de "Minmax" ou "Random" !')
                nom = input('Pseudo du joueur ?')
            profondeur = self._demander_profondeur_ia()
            self._joueur1 = JoueurHumain(self._jeu, nom, PION_JOUEUR_1)
            if profondeur != -1:
                self._joueur2 = IAMinMax(self._jeu, 'MinMax', PION_JOUEUR_2, PION_JOUEUR_1, profondeur, UTILISATION_APLHA_BETA)
            else:
                self._joueur2 = IaAleatoire(self._jeu, 'Random', PION_JOUEUR_2)

        elif nbre_joueurs_humains == 2:
            nom1 = input('Pseudo du joueur 1 ?')
            nom2 = input('Pseudo du joueur 2 ?')
            while nom1 == nom2:
                print('Le nom du joueur 2 doit être différent de celui du joueur 1 !')
                nom2 = input('Pseudo du joueur 2 ?')
            self._joueur1 = JoueurHumain(self._jeu, nom1, PION_JOUEUR_1)
            self._joueur2 = JoueurHumain(self._jeu, nom2, PION_JOUEUR_2)

        self._joueur_courant = self._joueur1
        self._jeu.reinitialiser()
        self._effacer_ecran()
        self._affiche_plateau()

    def _demander_nbre_joueurs(self):
        """
        Demande le nombre de joueurs humains à l'utilisateur
        :return: entier compris entre 0 et 2
        """
        while True:
            try:
                nbre_joueurs_humains = int(input('Nombre de joueurs humains (0/1/2) ?'))
            except ValueError:
                pass
            else:
                if nbre_joueurs_humains in [0, 1, 2]:
                    return nbre_joueurs_humains

    def _demander_profondeur_ia(self):
        """
        Demande la difficulté de l'IA à l'utilisateur (correspond à la profondeur de recherche des coups)
        :return: entier (-1 pour l'IA aléatoire, positif ou nulle pour MinMAx)
        """
        while True:
            try:
                profondeur = int(input("Difficulté de l'IA (0-5), (-1) pour une IA aléatoire ?"))
            except ValueError:
                print('Veuillez saisir un nombre entier !')
            else:
                if profondeur < -1:
                    print('Veuillez saisir une valeur correcte !')
                    return self._demander_profondeur_ia()
                else:
                    return profondeur

    def jouer(self):
        """
        Lance une partie entre les deux joueurs
        """
        self._nouvelle_partie()

        while True:
            # affiche le joueur courant
            print("C'est", self._joueur_courant.nom, "qui joue avec les ", self._joueur_courant.pion, " !")

            # choix d'un emplacement de jeu par le joueur
            choix = self._joueur_courant.choix()
            if choix == -1:
                break

            # on joue le coup
            self._jeu.jouer(choix, self._joueur_courant.pion)
            self._effacer_ecran()
            self._affiche_plateau()

            # Préparation du tour de jeu suivant
            if self._jeu.gagne:
                print('Bravo', self._joueur_courant.nom, '! Tu as gagné !')
                if self._recommencer():
                    self._nouvelle_partie()
                else:
                    break

            elif self._jeu.nul:
                print("Fin de la partie, personne n'a gagné !")
                if self._recommencer():
                    self._nouvelle_partie()
                else:
                    break
            else:
                # inversion des joueurs
                if self._joueur_courant == self._joueur1:
                    self._joueur_courant = self._joueur2
                else:
                    self._joueur_courant = self._joueur1


class IAMinMax(object):
    def __init__(self, jeu, nom, pion, pion_adversaire, profondeur=1, utilisation_alpha_beta=True):
        """
        :param jeu:
        :param nom:
        :param pion:
        :param pion_adversaire:
        :param profondeur: entier supérieur à 0
        """
        self.nom = nom
        self.pion = pion

        self._jeu = jeu
        self._pion_adversaire = pion_adversaire
        self._profondeur = profondeur
        self._utilisation_alpha_beta = utilisation_alpha_beta

        self._score_max = 1000
        self.nbre_coups_simules = 0

    def choix(self):
        """
        Lance la recherche du meilleur coup avec ou sans l'élagage alpha beta
        :return: colonne jouée
        """
        if self._utilisation_alpha_beta:
            return self._choix_alpha_beta()
        else:
            return self._choix_minmax()

    def _choix_minmax(self):
        """"
        Détermine le meilleur coup possible pour l'IA
        Cette méthode n'est appelée qui s'il y a au moins un coup jouable pour l'IA
        :return: colonne jouée
        """
        # Il faut retenir le coup qui donnera le score maximal pour l'IA.
        # On initialise donc "score_max" à la valeur la moins élevée...
        score_max = -self._score_max - 1  # -1 pour être certain que "score > score_max" sera vérifié au moins une fois

        # ...puis pour chaque premier coup possible pour l'IA...
        for colonne in self._jeu.colonnes_jouables:
            # ...on simule le coup...
            coup = self._jeu.jouer(colonne, self.pion)

            # ...puis on simule le meilleur coup possible de l'adversaire
            # et on récupère le score obtenu en évaluant la situation du point de vue de l'IA
            score = self.simuler_coup_adversaire(self._profondeur - 1)
            self.nbre_coups_simules += 1
            self._jeu.annuler(coup)  # annulation du coup simulé

            # Il faut donc retenir le score le plus avantageux pour l'IA...
            if score > score_max:
                score_max = score
                coup_retenu = coup

            # Puis on recommence pour rechercher un éventuel meilleur premier coup
            # (si tous les coups possibles ont été testés la boucle s'arrête)

        # Parmi tous les coups possibles de l'IA on retourne le meilleur
        if AFFICHAGE_NBRE_COUPS_SIMULES:
            print(self.nbre_coups_simules)
        self.nbre_coups_simules = 0
        return coup_retenu.colonne

    def _choix_alpha_beta(self):
        """"
        Détermine le meilleur coup possible pour l'IA
        Cette méthode n'est appelée qui s'il y a au moins un coup jouable pour l'IA
        :return: colonne jouée
        """
        alpha = -self._score_max
        beta = self._score_max

        # Il faut retenir le coup qui donnera le score maximal pour l'IA.
        # On initialise donc "score_max" à la valeur la moins élevée...
        score_max = -self._score_max-1  # -1 pour être certain que "score > score_max" sera vérifié au moins une fois

        # ...puis pour chaque premier coup possible pour l'IA...
        for colonne in self._jeu.colonnes_jouables:
            # ...on simule le coup...
            coup = self._jeu.jouer(colonne, self.pion)

            # ...puis on simule le meilleur coup possible de l'adversaire
            # et on récupère le score obtenu en évaluant la situation du point de vue de l'IA
            score = self.simuler_coup_adversaire_alpha_beta(self._profondeur - 1, alpha, beta)
            self.nbre_coups_simules += 1
            self._jeu.annuler(coup)  # annulation du coup simulé

            # Il faut donc retenir le score le plus avantageux pour l'IA...
            if score > score_max:
                score_max = score
                coup_retenu = coup

            if score_max >= beta:
                break

            alpha = max(alpha, score_max)

            # Puis on recommence pour rechercher un éventuel meilleur premier coup
            # (si tous les coups possibles ont été testés la boucle s'arrête)

        # Parmi tous les coups possibles de l'IA on retourne le meilleur
        if AFFICHAGE_NBRE_COUPS_SIMULES:
            print(self.nbre_coups_simules)
        self.nbre_coups_simules = 0
        return coup_retenu.colonne

    def simuler_coup_adversaire(self, profondeur):
        """
        Simulation des coups possibles pour l'adversaire
        If faut retenir le score minimal du point de vue de l'IA
        C'est la fonction "min" de l'algorithme minmax
        :param profondeur: profondeur maximale de recherche des coups
        :return: score obtenu le plus défavorable du point de vue de l'IA
        """
        # Si la profondeur maximale est atteinte (-1 si départ avec profondeur=0, 0 autrement) ou si le jeu est fini,
        # il faut évaluer la situation suite au dernier coup joué. Ce coup a été joué par l'IA
        if profondeur <= 0 or self._jeu.fini:
            return self._evaluer_score(self.pion)

        # On va simuler les coups possibles de l'adversaire en réponse au dernier coup joué par l'IA
        # On va retenir le score minimal obtenu en évaluant la situation du point de vue de l'IA
        # On va donc récupérer la pire situation dans laquelle va se trouver l'IA suite au coup de l'adversaire
        score_min = self._score_max

        for colonne in self._jeu.colonnes_jouables:
            coup = self._jeu.jouer(colonne, self._pion_adversaire)
            score = self.simuler_coup_ia(profondeur - 1)
            self.nbre_coups_simules += 1
            self._jeu.annuler(coup)

            score_min = min(score, score_min)

        return score_min

    def simuler_coup_ia(self, profondeur):
        """
        Simulation des coups possibles pour l'IA
        If faut retenir le score maximal du point de vue de l'IA
        C'est la fonction "max" de l'algorithme minmax
        :param profondeur: profondeur maximale de recherche des coups
        :return: score obtenu le plus favorable du point de vue de l'IA
        """
        # Si la profondeur maximale est atteinte (-1 si départ avec profondeur=0, 0 autrement) ou si le jeu est fini,
        # il faut évaluer la situation suite au dernier coup joué. Ce coup a été joué par l'adversaire
        if profondeur <= 0 or self._jeu.fini:
            return self._evaluer_score(self._pion_adversaire)

        # On va simuler les coups possible de l'IA en réponse au dernier coup joué par l'adversaire
        # On va retenir le score maximal obtenu en évaluant la situation du point de vue de l'IA
        # On va donc récupérer la meilleur situation dans laquelle va se trouver l'IA après qu'elle ait jouée
        score_max = -self._score_max

        for colonne in self._jeu.colonnes_jouables:
            coup = self._jeu.jouer(colonne, self.pion)
            score = self.simuler_coup_adversaire(profondeur - 1)
            self.nbre_coups_simules += 1
            self._jeu.annuler(coup)

            score_max = max(score, score_max)

        return score_max

    def simuler_coup_adversaire_alpha_beta(self, profondeur, alpha, beta):
        """
        Simulation des coups possibles pour l'adversaire
        If faut retenir le score minimal du point de vue de l'IA
        C'est la fonction "min" de l'algorithme minmax
        :param profondeur: profondeur maximale de recherche des coups
        :param alpha: valeur minimale que l'IA peut espérer obtenir en jouant le coup
        :param beta: valeur maximale que l'IA peut espérer obtenir en jouant le coup
        :return: score obtenu le plus défavorable du point de vue de l'IA
        """
        # Si la profondeur maximale est atteinte (-1 si départ avec profondeur=0, 0 autrement) ou si le jeu est fini,
        # il faut évaluer la situation suite au dernier coup joué. Ce coup a été joué par l'IA
        if profondeur <= 0 or self._jeu.fini:
            return self._evaluer_score(self.pion)

        # On va simuler les coups possible de l'adversaire en réponse au dernier coup joué par l'IA
        # On va retenir le score minimal obtenu en évaluant la situation du point de vue de l'IA
        # On va donc récupérer la pire situation dans laquelle va se trouver l'IA suite au coup de l'adversaire
        score_min = self._score_max

        for colonne in self._jeu.colonnes_jouables:
            coup = self._jeu.jouer(colonne, self._pion_adversaire)
            score = self.simuler_coup_ia_alpha_beta(profondeur - 1, alpha, beta)
            self.nbre_coups_simules += 1
            self._jeu.annuler(coup)

            score_min = min(score, score_min)

            # coupure alpha
            if score_min <= alpha:
                break
            beta = min(beta, score_min)

        return score_min

    def simuler_coup_ia_alpha_beta(self, profondeur, alpha, beta):
        """
        Simulation des coups possibles pour l'IA
        If faut retenir le score maximal du point de vue de l'IA
        C'est la fonction "max" de l'algorithme minmax
        :param profondeur: profondeur maximale de recherche des coups
        :param alpha: valeur minimale que l'IA peut espérer obtenir en jouant le coup
        :param beta: valeur maximale que l'IA peut espérer obtenir en jouant le coup
        :return: score obtenu le plus favorable du point de vue de l'IA
        """
        # Si la profondeur maximale est atteinte (-1 si départ avec profondeur=0, 0 autrement) ou si le jeu est fini,
        # il faut évaluer la situation suite au dernier coup joué. Ce coup a été joué par l'adversaire
        if profondeur <= 0 or self._jeu.fini:
            return self._evaluer_score(self._pion_adversaire)

        # On va simuler les coups possible de l'IA en réponse au dernier coup joué par l'adversaire
        # On va retenir le score maximal obtenu en évaluant la situation du point de vue de l'IA
        # On va donc récupérer la meilleur situation dans laquelle va se trouver l'IA après qu'elle ait jouée
        score_max = -self._score_max

        for colonne in self._jeu.colonnes_jouables:
            coup = self._jeu.jouer(colonne, self.pion)
            score = self.simuler_coup_adversaire_alpha_beta(profondeur - 1, alpha, beta)
            self.nbre_coups_simules += 1
            self._jeu.annuler(coup)

            score_max = max(score, score_max)

            # coupure beta
            if score_max >= beta:
                break
            alpha = max(alpha, score_max)

        return score_max

    def _evaluer_score(self, pion):
        """
        Calcul une évaluation de la situation du jeu du point de vue de l'IA
        :param pion: c'est le dernier pion qui a été joué
        :return: un entier compris entre -score_max et +score_max
        """
        if self._jeu.gagne:
            if pion == self.pion:
                # la partie est gagnée par l'IA
                return self._score_max
            else:
                # la partie est gagnée par l'adversaire
                return -self._score_max

        elif self._jeu.nul:
            # égalité
            return 0

        # évaluation de la situation du point de vue de l'IA

        # on calcule le nombre maximal de cases alignées pour l'Ia et l'adversaire
        nbre_pions_alignes_ia = self._jeu.nbre_cases_alignees_pion(self.pion)
        nbre_pions_alignes_adversaire = self._jeu.nbre_cases_alignees_pion(self._pion_adversaire)

        # on calcule le score pour chaque joueur (arrondi à l'entier inférieur) tel que la différence reste comprise
        # entre -score_max et score_max
        score_ia = nbre_pions_alignes_ia * self._score_max // (2 * self._jeu.nbre_cases_gain)
        score_adversaire = nbre_pions_alignes_adversaire * self._score_max // (2 * self._jeu.nbre_cases_gain)

        # le score relatif pour l'IA est la différence
        return score_ia - score_adversaire


puissance4 = Jeu()
partie = PartieConsole(puissance4)
partie.jouer()

subprocess.call("launch.bat" if os.name=='nt' else 'welcome.py', shell=True)
exit()
