import sys
import os
import subprocess
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

#status = 'h'

nameList = ["VAL", "THMS", "CHRISTOPHE", "LUDOVIC"] #Easter-Egg - si le nom entré par le joueur figure dans cette liste, il est remplacé par un nom de altName
altName = ["Valartisant", "Lalicorne", "Mr. Durant", "Mr. Rion"]

sName = "sName"


def init():
    oppName = "none"
    selfName = "none"
    # Fetch the service account key JSON file contents
    path = os.path.join(sys.path[0], 'service-account-credentials.json')

    cred = credentials.Certificate('serviceAccountCredentials.json')
    # Initialize the app with a None auth variable, limiting the server's access
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://puissance-4-cyka.firebaseio.com/',
        'databaseAuthVariableOverride': None
    })

    global ref
    ref = db.reference("/1v1-online")

    # The app only has access to public data as defined in the Security Rules

'''
ref = db.reference('/test')
str = ref.get()
print(str)
'''
#ANY - asks if player wants to create or join, and sets status
def setStatus():
    print('Que Voulez-vous faire ?\n')
    global status
    i = input(" [1] créer une partie\n [2] rejoindre une partie\n\n >>")
    if (i not in ("1","2")):
        print("Je n'ai pas bien compris...")
        setStatus()
    else:
        if (i=='1'):
            status = 'h'
        else :
            status ='g'
        varSet(status)
        return True

#ANY - Set vars based on status
def varSet(status):
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

#HOST - create lobby
def newlobby():
    if (status=='h'):
        lobbylist = ref.get()
        print(lobbylist)
        for lobby in lobbylist:
            current = ref.child(lobby)
            global myref
            myref = ref.child(lobby)
            if(current.child('gameOn').get()=="False"):
                current.update({"gameOn" : "True"})
                print("done")
                myref.update({"playercount" : 1})
                resetlobby()
                getName(True)
                wait()

                return True
        print('No available lobby. Try to join one, or try again later.')
        input('press any key to continue...')
        subprocess.call("welcome.py", shell=True)
        return False
    else:
        joinlobby()

def wait():
    i = 0
    while (myref.child('playercount').get()!=2):
        if(i!=40):
            time.sleep(0.5)
            sys.stdout.write("\r" +'waiting for opponent to join...'+ i*'.')
            sys.stdout.flush()
            i+=1
        else :
            print('no opponent seems to come...')
            n = ""
            while(n not in ('o','n')):
                n = input('Voulez-vous continuer d\'attendre ? o/n ')
            if n == 'o':
                wait()
            else :
                subprocess.call("welcome.py", shell=True)


#GUEST - show available lobbies to join
def showlobbies():
    currentGames = []
    lobbylist = ref.get()
    for lobby in lobbylist:
        if (ref.child(lobby).child('gameOn').get()=='True' and ref.child(lobby).child('playercount').get()!=2):
            currentGames.append(lobby+'\n')
    if (len(currentGames) == 0):
        print('no games. You can create a game, instead.')
        input('press any key to go back...')
        subprocess.call('puissance4o.py', shell=True)
    print(currentGames)

#GUEST - join a lobby
def joinlobby():
    print("Open lobbies :")
    showlobbies()
    i = input("which one you join ? Enter number : ")
    if (i not in ('1','2','3')):
        print("invalid lobby")
        joinlobby()
    else :
        lobby = 'lobby'+i
        global myref
        myref = ref.child(lobby)
        getName(True)
        myref.update ({'playercount' : 2})
        global savedLp
        savedLp = myref.child('h_last').get()
        return True
    return False

#HOST - set default values
def resetlobby():
    if (status=='h'):
        #if (input('Do you want to play first ? Y/N')=='Y'):
        if True:
            whoplays = 1
        else:
            whoplays = 2
        myref.update({
        "g_last" : "none",
        "g_play" : "0",
        "g_replay" : "0",
        "h_last" : "none",
        "h_play" : "0",
        "h_replay" : "0",
        "replayOn" : "False",
        "whoplays" : whoplays,
        })
        global savedLp
        savedLp = myref.child('g_last').get()
        return True
    print('done')
    return False

def fullReset():
    if (status=='h'):
        myref.update({
        "g_last" : "none",
        "g_play" : "0",
        "g_replay" : "0",
        "g_name" : "gname",
        "h_last" : "none",
        "h_name" : "hname",
        "gameOn" : "False",
        "h_play" : "0",
        "h_replay" : "0",
        "replayOn" : "False",
        "whoplays" : "none",
        "playercount" : 0
        })
    print('done')

#ANY - asks for player's name
def getName(pushAfter):
    name = input("Quel est votre nom ? \n\n >>")
    if name.upper() in nameList:
        name = altName[nameList.index(name.upper())]
    i = input("Vous vous appelez " + name + " c'est bien ça ? [o/n] \n\n>>")
    while (i not in ("o","n")):
        i = input("Je n'ai pas bien compris... \n\n>>")
    if i == "o":
        print("Bien reçu !")
        global sName
        sName = name
        if pushAfter:
            pushName()
    else:
        getName(pushAfter)

#ANY - pushes player's name to server
def pushName():

    i = input("Vous vous appelez "+sName+" c'est bien ça ? [o/n] \n\n>>")
    while (i not in ("o","n")):
        i = input("Je n'ai pas bien compris... \n\n>>")
    if (i=="o"):
        myref.update({s_name: sName})
    else :
        getName(True)

#ANY - Fetch Opponent's name
def oppName():
    return myref.child(o_name).get()

#ANY - fetches opponent's last action from db
def hisTurn():
    global savedLp
    i = 0
    while(myref.child(o_last).get() == savedLp):
         time.sleep(0.5)
         sys.stdout.write("\r" +'waiting for opponent to play...'+ i*'.')
         sys.stdout.flush()
         i+=1
    n = myref.child(o_play).get()
    savedLp = myref.child(o_last).get()
    print(n)
    return n

#ANY - Handles action of player and sends it to server
def myturn(n):
    myref.update({s_play : n})
    myref.update({s_last : time.time()})
    return True

#ANY - Says if player wants to replay
def recommencer():
    i = input('Voulez-vous rejouer ? o/n ')
    if i in ('o','n'):
        if i == 'o':
            myref.update({s_replay : '1'})
            return True
        else:
            myref.update({s_replay : '2'})
            return False
    else:
        print("je n'ai pas bien compris...")
        return recommencer()
#ANY - Checks if opponent wants to replay
def checkRetry():
    i = 0
    while(myref.child(o_replay).get()=='0'):
        time.sleep(0.5)
        sys.stdout.write("\r" +'waiting for opponent...'+ i*'.')
        sys.stdout.flush()
        i+=1
    if (myref.child(o_replay).get()=='1'):
        return True
    else :
        return False

init()
