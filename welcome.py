import subprocess
import os

#Écran d'accueil du jeu, redirige vers les différentes versions du jeu

os.system('cls' if os.name == 'nt' else 'clear')

print('-------------------------------------------------')
print('-      Bienvenue sur le jeu du Puissance 4      -')
print("-------------------------------------------------\n")

print('Que voulez-vous faire ?\n')
i = 0
while(i not in ('1','2','3')):
    if (i !=0 and i not in ('1','2','3')):
        print('Je n\'ai pas bien compris...')
    i = input(' [1] 1v1 local\n [2] 1v1 en ligne\n [3] Contre l\'IA\n\n >>')


if (i == '1'):
    subprocess.call('puissance4.py', shell=True)
elif (i=='2'):
    subprocess.call("puissance4-o.py", shell=True)
else :
    print('ça va venir...')
    input('Press any key to continue...')
    subprocess.call("welcome.py", shell=True)
