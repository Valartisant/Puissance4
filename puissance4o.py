import os
from random import randrange
import p4online as online
import subprocess

online.setStatus()
online.newlobby()


# Définition des constantes
NOMBRE_COLONNES = 7
NOMBRE_LIGNES = 6
NOMBRE_DE_CASES_POUR_GAGNER = 4
CASE_VIDE = "."

PION_JOUEUR_1 = "X"
PION_JOUEUR_2 = "O"

UTILISATION_APLHA_BETA = True


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

    def choix(self, joueurCourant, joueur1, joueur2):
        """
        Demande un numéro de colonne à l'utilisateur et renvoie ce numéro si la colonne est jouable, -1 pour arrêter
        :return: numéro de colonne (int) ou -1 pour quitter la partie
        """

        if joueurCourant == joueur2:
            reponse = online.hisTurn()
            try:
                reponse=int(reponse)
            except ValueError:
                if reponse.upper() =="EXIT":
                    return -1
            return reponse
        else:
            while True:
                reponse = input("Où voulez-vous jouer ? \n (exit pour quitter) ")
                try:
                    reponse = int(reponse)
                except ValueError:
                    if reponse.upper() == 'EXIT':
                        online.myturn(reponse)
                        #online.fullReset()
                        return -1
                else:
                    if reponse in self._jeu.colonnes_jouables:
                        online.myturn(reponse)
                        return reponse
                    else:
                        print('Veuillez saisir une valeur correcte')


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

        self._joueur1 = JoueurHumain(self._jeu, online.sName, PION_JOUEUR_1)
        self._joueur2 = JoueurHumain(self._jeu, online.oppName(), PION_JOUEUR_2)


        if (online.status=="h"):
            self._joueur_courant = self._joueur1
        else :
            self._joueur_courant = self._joueur2
        self._jeu.reinitialiser()
        self._effacer_ecran()
        self._affiche_plateau()

    def jouer(self):
        """
        Lance une partie entre les deux joueurs
        """
        self._nouvelle_partie()

        while True:
            # affiche le joueur courant
            print("C'est", self._joueur_courant.nom, "qui joue avec les ", self._joueur_courant.pion, " !")

            # choix d'un emplacement de jeu par le joueur
            choix = self._joueur_courant.choix(self._joueur_courant, self._joueur1, self._joueur2)
            if choix == -1:
                self.finduGame()
                break

            # on joue le coup
            self._jeu.jouer(choix, self._joueur_courant.pion)
            self._effacer_ecran()
            self._affiche_plateau()

            # Préparation du tour de jeu suivant
            if self._jeu.gagne:
                print('Bravo', self._joueur_courant.nom, '! Tu as gagné !')
                if online.recommencer():
                    if (online.checkRetry()):
                        self._nouvelle_partie()
                    else:
                        print('L\'adversaire ne souhaite pas rejouer.')
                        break
                else:
                    break

            elif self._jeu.nul:
                print("Fin de la partie, personne n'a gagné !")
                if online.recommencer(): #On demande au joueur s'il veut rejouer
                    if (online.checkRetry()): #On regarde si l'adversaire veut rejouer
                        online.resetlobby() #On  remet le salon à zéro
                        self._nouvelle_partie() #On recommence la partie
                    else:
                        print('L\'adversaire ne souhaite pas rejouer.')
                        break
                else:
                    break
            else:
                # inversion des joueurs
                if self._joueur_courant == self._joueur1:
                    self._joueur_courant = self._joueur2
                else:
                    self._joueur_courant = self._joueur1

    def finduGame(self):
        if self._joueur_courant == self._joueur2:
            print("Votre partenaire de jeu a quitté.")
        else:
            print("Vous avez abandonné la partie.")
        online.fullReset()
        input("-- Press any key --")
        subprocess.call("launch.bat", shell=True)
        exit()

puissance4 = Jeu()
partie = PartieConsole(puissance4)
partie.jouer()
