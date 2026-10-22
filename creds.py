from getpass import getpass
import json
import bcrypt

def get_creds():
    creds = json.load(open("jolib/creds.json"))

    if not creds["password"]:
        mot_de_passe = getpass("Initialisez un secret: ")
        creds["password"] = bcrypt.hashpw(mot_de_passe.encode(), bcrypt.gensalt()).decode()

        with open("jolib/creds.json", "w") as output:
            json.dump(creds, output)

    return creds["password"]    