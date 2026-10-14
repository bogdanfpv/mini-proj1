import socket, sys, threading

# === AJOUTS GLOBAUX POUR LE CACHE ===
cache = {}                  # Le dictionnaire partagé pour retenir les pages
cache_lock = threading.Lock() # Le verrou pour protéger ce dictionnaire entre les clients
# ====================================

def copier(source, destination, fini, stockage=None): # <--- Ajout de 'stockage=None' pour capturer les données
    try:
        while True:
            donnees = source.recv(4096)
            if not donnees:
                break
            if stockage is not None:                 # <--- Si on veut enregistrer, on accumule ici
                stockage.extend(donnees)
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
    
    # === AJOUT 1 : LIRE LA REQUÊTE CLIENT AVANT DE SE CONNECTER ===
    try:
        requete = sock_client.recv(4096)
        if not requete:
            sock_client.close()
            return
    except OSError:
        sock_client.close()
        return

    # Extraire l'URI (ex: "GET /README.md HTTP/1.1" -> URI = "/README.md")
    premiere_ligne = requete.decode(errors='ignore').split('\r\n')[0]
    elements = premiere_ligne.split(' ')
    is_get = (len(elements) > 1 and elements[0] == "GET")
    uri = elements[1] if is_get else None

    # === AJOUT 2 : VÉRIFIER SI C'EST DÉJÀ DANS LE CACHE ===
    if is_get and uri:
        with cache_lock:
            if uri in cache:
                sock_client.sendall(cache[uri]) # On renvoie direct le cache au client
                sock_client.close()
                return                          # On s'arrête là, pas besoin de contacter le serveur !
    # ====================================================

    try:
        sock_serveur = socket.create_connection((ip_serveur, port_serveur))
    except OSError as e:
        print(f"connexion au server impossible :  {e}")
        sock_client.close()
        return

    # === AJOUT 3 : ENVOYER LA REQUÊTE AU SERVEUR (PUISQU'ON L'A LUE PLUS HAUT) ===
    try:
        sock_serveur.sendall(requete)
    except OSError:
        sock_client.close()
        sock_serveur.close()
        return
    # ===========================================================================

    restants = 2
    verrou = threading.Lock()

    # === AJOUT 4 : PRÉPARER UN BUFFER POUR ENREGISTRER LA RÉPONSE DU SERVEUR ===
    reponse_serveur = bytearray() if (is_get and uri) else None
    # =========================================================================

    def fini():
        nonlocal restants
        with verrou:
            restants -= 1
            dernier = restants == 0
        if dernier:
            sock_client.close()
            sock_serveur.close()
            
            # === AJOUT 5 : STOCKER DANS LE CACHE QUAND LA TRANSMISSION EST FINIE ===
            if is_get and uri and len(reponse_serveur) > 0:
                with cache_lock:
                    cache[uri] = bytes(reponse_serveur)
            # =====================================================================

    # Ton code d'origine : les deux threads de copie
    threading.Thread(target=copier, args=(sock_client, sock_serveur, fini)).start()
    
    # On passe 'reponse_serveur' au thread qui reçoit les données du serveur
    threading.Thread(target=copier, args=(sock_serveur, sock_client, fini, reponse_serveur)).start()

# Tout le reste (le main) est strictement identique à ton relay.py
if len(sys.argv) != 4:
    print("usage: python relay_cache.py IP_SERVEUR PORT_SERVEUR PORT_LOCAL")
    sys.exit(1)

ip_serveur, port_serveur, port_local = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ecoute = socket.socket()
ecoute.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ecoute.bind(("", port_local))
ecoute.listen()

while True:
    sock_client, _ = ecoute.accept()
    gerer_client(sock_client, ip_serveur, port_serveur)
