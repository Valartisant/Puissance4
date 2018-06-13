Les différents fichiers envoyés sont :
	- readme.txt
	- lauch.bat (Fichier de lancement : permet de relancer le jeu automatiquement)
	- welcome.py (Fichier d'accueil : comprend le menu principal du jeu)
	- puissance4.py (Fichier du jeu solo : comprend le jeu solo et l'IA)
	- p4online.py (Appelé en module dans puissance4o, permet de communiquer avec la base de données)
	- puissance4o.py (Fichier du jeu multi : gère le jeu en ligne)
	- serviceAccountCredentials.json (Permet de se connecter à la base de données)	

Les différents modules utilisés sont :
	- os
	- sys
	- time
	- random
	- subprocess
	- firebase-admin

Pour lancer le jeu, simplement double-cliquer sur le fichier "launch.bat" (sous windows) ou sur le fichier "welcome.py" (sous linux)