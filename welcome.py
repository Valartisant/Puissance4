import subprocess
import os
import firebase_admin

#Écran d'accueil du jeu, redirige vers les différentes versions du jeu

os.system('cls' if os.name == 'nt' else 'clear')

print('-------------------------------------------------')
print('-      Bienvenue sur le jeu du Puissance 4      -')
print("-------------------------------------------------\n")

print('Que voulez-vous faire ?\n')
i = 0
while(i not in ('1','2','3','exit')):
    if (i !=0 and i not in ('1','2','3')):
        print('Je n\'ai pas bien compris...')
    i = input(' [1] 1v1 local\n [2] 1v1 en ligne\n [exit] Quitter le jeu\n\n >>')


if (i == '1'):
    import puissance4
    exit()
elif (i=='2'):
    import puissance4o2

elif (i=='exit'):
    print("On espère vous revoir bientôt...\n\n")
    input("-- Press any key --")
    exit()

else :
    import puissance4
