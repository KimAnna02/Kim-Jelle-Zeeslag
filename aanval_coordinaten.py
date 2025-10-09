# de basis functie die de vragen stelt
def poging(input_let,input_num):
    return f"dus de plek waar je op wil schieten is: {input_let}{input_num}? (ja/nee)"

# een bevestiging er in gezet die checkt je een bevesteging geeft of je inderdaad op die coordinaten wil schieten
while True:
    input_num = int(input("in welke colomn denk je dat een boot ligt (1 t/m 10): "))
    input_let = str(input("in welke rij denk je dat een boot ligt (A t/m J): "))

    bevestiging = str(input(poging(input_let, input_num)))
    print(bevestiging)

    if bevestiging == "ja":
        print(f"Aanval bevestigd op {input_let}{input_num}")
        break
    elif bevestiging == "nee":
        print("Oke, waar wil je dan op schieten?.\n")
    else:
        print("Gebruik 'ja' of 'nee' .\n")