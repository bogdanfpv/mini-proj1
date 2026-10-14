import sys

if len(sys.argv) != 2:
    print("usage: python search_log.py URI_OU_PARTIE")
    sys.exit(1)

recherche = sys.argv[1]
try:
    with open("sniffer.log", "r") as f:
        derniere_ip = None
        for ligne in f:
            if "CLIENT_IP:" in ligne:
                derniere_ip = ligne.split("CLIENT_IP:")[1].split(" ")[0]
            if recherche in ligne and derniere_ip:
                print(f"Trouvé ! IP du client : {derniere_ip} -> Ligne : {ligne.strip()}")
except FileNotFoundError:
    print("Aucun fichier sniffer.log trouvé.")
