import sys

if len(sys.argv) != 2:
    print("usage: python search_log.py URI_OU_PARTIE")
    sys.exit(1)

recherche = sys.argv[1]
try:
    with open("sniffer.log", "r") as f:
        derniere_ip = None
        for ligne in f:
            if ligne.startswith("IP:"):
            	derniere_ip = ligne.split("IP:")[1].split(" ")[0]
            elif ligne.startswith("GET ") and recherche in ligne and derniere_ip:
            	print(f"IP du client: {derniere_ip} -> Ligne : {ligne.strip()}")
except FileNotFoundError:
    print("Aucun fichier sniffer.log trouvé.")
