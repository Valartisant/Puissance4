import sys
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
def init():
    # Fetch the service account key JSON file contents
    path = os.path.join(sys.path[0], 'service-account-credentials.json')

    cred = credentials.Certificate('serviceAccountCredentials.json')
    # Initialize the app with a None auth variable, limiting the server's access
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://puissance-4-cyka.firebaseio.com/',
        'databaseAuthVariableOverride': None
    })

    # The app only has access to public data as defined in the Security Rules

'''
ref = db.reference('/test')
str = ref.get()
print(str)
'''

def newlobby():
    ref = db.reference("/1v1-online")
    lobbylist = ref.get()
    print(lobbylist)
    for lobby in lobbylist:
        current = ref.child(lobby)
        if(current.get('gameOn')==False):
            current.child('gameOn').setValue('True')
            print("done")
            return True
    return False

init()
newlobby()
