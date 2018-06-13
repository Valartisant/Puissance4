import sys
import os
import subprocess
import time
try :
    import firebase_admin
except ModuleNotFoundError:
    print("Erreur d'importation d'un module. Merci de quitter et relancer le jeu.")
    input("Presser une touche pour continuer...")
    exit()
from firebase_admin import credentials
from firebase_admin import db


nameList = ["VAL", "THMS", "CHRISTOPHE", "LUDOVIC"] #Easter-Egg - si le nom entré par le joueur figure dans cette liste, il est remplacé par un nom de altName
altName = ["Valartisant", "Lalicorne", "Mr. Durant", "Mr. Rion"]

sName = "sName"


def init():
    """
    Connexion à la racine de la BDD et authentification auprès du serveur
    """
    oppName = "none"
    selfName = "none"
    # On récupère les informations de connexion
    path = os.path.join(sys.path[0], 'service-account-credentials.json')

    cred = credentials.Certificate('serviceAccountCredentials.json')
    # On initialise la connexion au serveur
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://puissance-4-cyka.firebaseio.com/',
        'databaseAuthVariableOverride': None
    })

    global ref
    ref = db.reference("/1v1-online") #On prend la partie "online" de la BDD


def screenClear():
    """
    Efface la console (1ère commande pour windows, 2ème pour linux)
    """
    os.system('cls' if os.name == 'nt' else 'clear')

#TOUS - asks if player wants to create or join, and sets status
def setStatus():
    """
    Définit le statut du joueur en fonction de ce qu'il veut faire
    """
    print('Que Voulez-vous faire ?\n')
    global status
    i = input(" [1] Créer une partie\n [2] Rejoindre une partie\n [exit] Retourner au menu\n\n >>")
    if (i.upper() not in ("1","2","EXIT")):
        print("Je n'ai pas bien compris...")
        setStatus()
    else:
        if (i=='1'):
            status = 'h' #Si le joueur crée une partie, il devient hôte
        elif (i=='2') :
            status ='g' #Sinon il devient invité
        else :
            return subprocess.call("launch.bat", shell=True) #Retour au menu si le joueur veut quitter
        varSet(status)
        return True

def varSet(status):
    """
    Affecte le nom des références à la BDD en fonction du statut du joueur
    """
    global o_last, o_play, o_replay, o_name
    global s_last, s_play, s_replay, s_name
    if status == 'h':
        o_last = 'g_last'
        o_play = 'g_play'
        o_replay = 'g_replay'
        o_name='g_name'
        s_last='h_last'
        s_play='h_play'
        s_replay='h_replay'
        s_name='h_name'
    else:
        o_last = "h_last"
        o_play = "h_play"
        o_replay='h_replay'
        o_name='h_name'
        s_last='g_last'
        s_play='g_play'
        s_replay='g_replay'
        s_name='g_name'
    return True

def newlobby():
    """
    (Hôte seulement)
    Création d'un salon et remise à zéro
    """
    if (status=='h'):
        lobbylist = ref.get() #On récupère la liste des salons sur la BDD
        for lobby in lobbylist:
            current = ref.child(lobby)
            global myref
            myref = ref.child(lobby)
            if(current.child('gameOn').get()=="False"): #On vérifie si le salon n'est pas déjà occupé
                current.update({"gameOn" : "True"})
                myref.update({"playercount" : 1})
                resetlobby() #On remet le salon à zéro
                getName() #On demande au joueur son nom
                wait() #On attend un adversaire
                return True
        print('Malheureusement, il n\'y a pas de salon disponible... Merci de réessayer plus tard.')
        input('Presser une touche pour continuer...')
        subprocess.call("launch.bat", shell=True) #On relance le programme
        return False
    else:
        joinlobby() #Si le joueur a le statut d'invité, on le redirige vers la fonction correspondante

def wait():
    """
    (Hôte seulement)
    Écran d'attente
    """
    screenClear()
    print("Vous avez rejoint le lobby n°"+myref.child("nbr").get()) #On affiche le salon qui vient d'être créé
    i = 0
    while (myref.child('playercount').get()!=2): #Tant qu'un autre joueur n'a pas rejoint, on affiche un message d'attente
        if(i!=30): #On met en place un timer
            time.sleep(0.5)
            sys.stdout.write("\r" + 'En attente d\'un adversaire.' + (i % 3) * '.' + (16 - (i % 4)) * ' ')
            sys.stdout.flush()
            i+=1
        else :
            #Si le temps d'attente devient long, on demande au joueur s'il veut continuer d'attendre ou pas
            print('\n Aucun adversaire ne semble arriver...')
            n = ""
            while(n not in ('o','n')):
                n = input('Voulez-vous continuer d\'attendre ? o/n ')
            if n == 'o':
                wait()
            else :
                fullReset() #On remet le salon entièrement à zéro
                subprocess.call("launch.bat", shell=True) #On relance le jeu
                exit()

def showlobbies():
    """
    (Invité seulement)
    Affiche les salons ouverts et disponibles
    """
    global currentGames
    currentGames = []
    gameList=[]
    lobbylist = ref.get()
    for lobby in lobbylist: #Pour chaque salon, on regarde s'il est activé, et s'il n'y a qu'un joueur
        if (ref.child(lobby).child('gameOn').get()=='True' and ref.child(lobby).child('playercount').get()!=2):
            host = ref.child(lobby).child("h_name").get() #On récupère le nom de l'hôte
            currentGames.append(lobby)
            gameList.append(lobby + ' ('+host+')')
    if (len(currentGames) == 0): #S'il n'y a aucun salon disponible
        print('Aucun salon n\'est disponible. Vous pouvez essayer d\'en créer un, à la place.')
        input('Presser une touche pour continuer...')
        subprocess.call("launch.bat", shell=True)
        status=""
        exit()
        return False
    print('')
    for s in gameList: #On affiche les salons disponibles
        print("- "+s)
    print('')

def joinlobby():
    """
    (Invité seulement)
    Le joueur choisit un salon, et le programme y établit la connexion
    """
    screenClear() #On efface la console
    print("Salons disponibles :")
    showlobbies()
    i = input("Lequel voulez-vous rejoindre ? (Écrivez le numéro correspondant, ou \'exit\' pour quitter.) \n\n >>")
    if i.upper()=="EXIT": #Si le joueur veut quitter
        subprocess.call("launch.bat", shell=True) #on retourne au menu
        status="" #On réinitialise le statut du joueur
        exit()
        return False
    elif (i not in ('1','2','3')):
        print("invalid lobby")
        time.sleep(2)
        joinlobby()
    else :
        current = []
        for s in currentGames: #On crée une liste contenant les numéros des salons disponibles
            current.append(s[-1])
        if i not in current :
            print("Ce salon n'est pas disponible. Il est peut-être complet ou vide...")
            time.sleep(2)
            joinlobby()

        lobby = 'lobby'+i #On fabrique une référence à la BDD à partir de l'entrée utilisateur
        global myref
        myref = ref.child(lobby) #On établit la connexion au salon choisi
        getName() #On récupère le nom du joueur
        myref.update ({'playercount' : 2}) #On met à jour la BDD
        global savedLp
        savedLp = myref.child('h_last').get() #On initialise la variable contenant le timecode du dernier coup de l'hôte
        return True
    return False

def resetlobby():
    """
    (Hôte seulement)
    Remise de la BDD à zéro en début de partie
    """
    if (status=='h'):
        myref.update({
        "g_last" : "none",
        "g_play" : "0",
        "g_replay" : "0",
        "h_last" : "none",
        "h_play" : "0",
        "h_replay" : "0",
        "replayOn" : "False",
        })
        global savedLp
        savedLp = myref.child('g_last').get() #On initialise la variable contenant le timecode du dernier coup de l'invité
        return True
    return False

def fullReset():
    """
    (Hôte seulement)
    Remise à zéro de la BDD en fin de partie
    """
    if (status=='h'):
        myref.update({
        "g_replay" : "0",
        "g_name" : "gname",
        "h_name" : "hname",
        "gameOn" : "False",
        "h_replay" : "0",
        "replayOn" : "False",
        "playercount" : 0
        })

def getName():
    """
    L'utilisateur rentre son nom
    """
    name = input("Quel est votre nom ? \n\n >>")
    if name.upper() in nameList: #Si le nom rentré est dans la liste de l'Easter Egg, on le remplace en conséquence
        name = altName[nameList.index(name.upper())]
    i = input("Vous vous appelez " + name + " c'est bien ça ? [o/n] \n\n>>") #Le joueur valide son nom
    while (i not in ("o","n")):
        i = input("Je n'ai pas bien compris... \n\n>>")
    if i == "o":
        print("Bien reçu !")
        global sName
        sName = name #On affecte à la variable globale la valeur de la variable locale 'name'
        pushName()
    else:
        getName() #si l'utilisateur répond 'non', on lui redemande son nom

def pushName():
    """
    Envoi du nom du joueur à la BDD
    """
    myref.update({s_name: sName})

def oppName():
    """
    Lecture du nom de l'adversaire sur la BDD
    """
    return myref.child(o_name).get()

def hisTurn():
    """
    Récupère le coup de l'adversaire
    """
    global savedLp
    i = 0
    while(myref.child(o_last).get() == savedLp): #On affiche un message d'attente tant que l'adversaire n'a pas joué
         time.sleep(0.5)
         sys.stdout.write("\r" + 'L\'adversaire joue.' + (i % 3) * '.' + (16 - (i % 4)) * ' ')
         sys.stdout.flush()
         i+=1
    n = myref.child(o_play).get() #On récupère le coup de l'adversaire
    savedLp = myref.child(o_last).get() #On enregiste le timecode correspondant au coup actuel
    return n #On renvoie le coup de l'adversaire

def myturn(n):
    """
    Envoie le coup de l'utilisateur à la BDD
    """
    myref.update({s_play : n}) #On enregistre le coup
    myref.update({s_last : time.time()}) #On enregistre le timecode
    return True

def recommencer():
    """
    Demande à l'utilisateur s'il désire rejouer une partie
    """
    i = input('Voulez-vous rejouer ? o/n ')
    if i in ('o','n'):
        if i == 'o':
            myref.update({s_replay : '1'}) #Enregistre la réponse sur la BDD
            return True
        else:
            myref.update({s_replay : '2'}) #Enregistre la réponse sur la BDD
            return False
    else:
        print("je n'ai pas bien compris...")
        return recommencer()

def checkRetry():
    """
    Récupération de la réponse de l'adversaire
    """
    i = 0
    while(myref.child(o_replay).get()=='0'): #On affiche un message tant que l'adversaire n'a pas répondu
        time.sleep(0.5)
        sys.stdout.write("\r" + 'En attente de l\'adversaire.' + (i % 3) * '.' + (16 - (i % 4)) * ' ')
        sys.stdout.flush()
        i+=1
    if (myref.child(o_replay).get()=='1'): #Si l'adversaire désire rejouer, on renvoie True
        return True
    else :
        return False

init()
