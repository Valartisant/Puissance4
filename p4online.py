import sys
import os
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

status = 'h'
if status == 'h':
    o_last = 'g_last'
    o_play = 'g_play'
    o_replay = 'g_replay'
    s_last='h_last'
    s_play='h_play'
    s_replay='h_replay'
else:
    o_last = "h_last"
    o_play = "h_play"
    o_replay='h_replay'
    s_last='g_last'
    s_play='g_play'
    s_replay='g_replay'


def init():
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

#HOST - create lobby
def newlobby():
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
            return True
    return False

#GUEST - show available lobbies to join
def showlobbies():
    currentGames = []
    lobbylist = ref.get()
    for lobby in lobbylist:
        if (ref.child(lobby).child('gameOn').get()=='True' and ref.child(lobby).child('playercount').get()!=2):
            currentGames.append(lobby)
    print(currentGames)

#HOST - set default values
def resetlobby():
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
    "winner" : "nobody"
    })
    global savedLp
    savedLp = myref.child('g_last').get()
    print('done')

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
