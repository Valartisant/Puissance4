import os
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


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

def reset():
  ref.update({
      "lobby1" : {
        "g_last" : "none",
        "g_play" : "0",
        "g_name" : "gname",
        "h_name": "hname",
        "g_replay" : "0",
        "gameOn" : "False",
        "h_last" : "none",
        "h_play" : "0",
        "h_replay" : "0",
        "playercount" : 0,
        "replayOn" : "False"
      },
      "lobby2" : {
        "g_name": "gname",
        "h_name": "hname",
        "g_last" : "none",
        "g_play" : "0",
        "g_replay" : "0",
        "gameOn" : "False",
        "h_last" : "none",
        "h_play" : "0",
        "h_replay" : "0",
        "playercount" : 0,
        "replayOn" : "False"
      },
      "lobby3" : {
        "g_name": "gname",
        "h_name": "hname",
        "g_last" : "none",
        "g_play" : "0",
        "g_replay" : "0",
        "gameOn" : "False",
        "h_last" : "none",
        "h_play" : "0",
        "h_replay" : "0",
        "playercount" : 0,
        "replayOn" : "False"
      }
  })
  print("done")

reset()
