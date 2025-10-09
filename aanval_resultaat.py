import aanval_coordinaten
# variablen om aan te geven of schot raakte of niet
raak = "Die was goed raak!"
mis = "Helaas heb je die gemist!"
schot_locatie = aanval_coordinaten.poging

# functie om het resultaat van het schot te printen
def poging_resultaat(boot_locatie,raak,mis):
    boot_locatie = boot_locatie
    raak = raak
    mis = mis
    if schot_locatie == boot_locatie:
        print(raak)
    else:
        print(mis)