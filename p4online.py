import sys
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

status = 'h'

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
            return True
    ref.child(gameLobby).update({"playercount" : 1})
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
    if (input('Do you want to play first ? Y/N')=='Y'):
        whoplays = 1
    else:
        whoplays = 2
    myref.update({
    "g_last" : "none",
    "g_play" : 0,
    "g_replay" : 0,
    "h_last" : "none",
    "h_play" : 0,
    "h_replay" : 0,
    "replayOn" : "False",
    "whoplays" : whoplays,
    "winner" : "nobody"
    })
    print('done')

def hisTurn():
    lastPlay = myref.child('g_last').get()
    n = myref.child('g_play').get()

init()
newlobby()
resetlobby()
