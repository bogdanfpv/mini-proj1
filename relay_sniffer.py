import socket, sys, threading

# === CHANGEMENT : Fonction pour écrire les logs dans un fichier ===
def log_sniffer(client_ip, requete):
    with open("sniffer.log", "a") as f:
        f.write(f"IP:{client_ip} | REQ:\n{requete.decode(errors='ignore')}\n---\n")

def copier(source, destination, fini):
    try:
        while True:
            donnees = source.recv(4096)
            if not donnees:
                break
            destination.sendall(donnees)
    except OSError:
        pass
    finally:
        try:
            destination.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        fini()
        
def gerer_client(sock_client, ip_serveur, port_serveur):
    try:
        # === CHANGEMENT : On récupère l'IP et on lit la requête avant de se connecter au serveur ===
        client_ip = sock_client.getpeername()[0]
        requete = sock_client.recv(4096)
        if not requete:
            sock_client.close()
            return
    except OSError:
        sock_client.close()
        return

    # === CHANGEMENT : On consigne la requête lue ===
    log_sniffer(client_ip, requete)

    try:
        sock_serveur = socket.create_connection((ip_serveur, port_serveur))
        # === CHANGEMENT : On transmet la requête qu'on vient de lire au serveur ===
        sock_serveur.sendall(requete)
    except OSError as e:
        print(f"connexion au server impossible :  {e}")
        sock_client.close()
        return

    restants = 2
    verrou = threading.Lock()

    def fini():
        nonlocal restants
        with verrou:
            restants -= 1
            dernier = restants == 0
        if dernier:
            sock_client.close()
            sock_serveur.close()

    # Ton code d'origine : les deux threads de copie
    threading.Thread(target=copier, args=(sock_client, sock_serveur, fini)).start()
    threading.Thread(target=copier, args=(sock_serveur, sock_client, fini)).start()

if len(sys.argv) != 4:
    print("usage: python relay_sniffer.py IP_SERVEUR PORT_SERVEUR PORT_LOCAL")
    sys.exit(1)

ip_serveur, port_serveur, port_local = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ecoute = socket.socket()
ecoute.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ecoute.bind(("", port_local))
ecoute.listen()

while True:
    sock_client, _ = ecoute.accept()
    gerer_client(sock_client, ip_serveur, port_serveur)
