import socket, sys, threading

cache = {}
cache_lock = threading.Lock()

def copier(source, destination, fini, stockage=None):
    try:
        while True:
            donnees = source.recv(4096)
            if not donnees:
                break
            if stockage is not None:
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
    try:
        requete = sock_client.recv(4096)
        if not requete:
            sock_client.close()
            return
    except OSError:
        sock_client.close()
        return

    premiere_ligne = requete.decode(errors='ignore').split('\r\n')[0]
    elements = premiere_ligne.split(' ')
    is_get = (len(elements) > 1 and elements[0] == "GET")
    uri = elements[1] if is_get else None

    if is_get and uri:
        with cache_lock:
            if uri in cache:
                sock_client.sendall(cache[uri])
                sock_client.close()
                return

    try:
        sock_serveur = socket.create_connection((ip_serveur, port_serveur))
    except OSError as e:
        print(f"connexion au server impossible :  {e}")
        sock_client.close()
        return
    try:
        sock_serveur.sendall(requete)
    except OSError:
        sock_client.close()
        sock_serveur.close()
        return

    restants = 2
    verrou = threading.Lock()
    reponse_serveur = bytearray() if (is_get and uri) else None

    def fini():
        nonlocal restants
        with verrou:
            restants -= 1
            dernier = restants == 0
        if dernier:
            sock_client.close()
            sock_serveur.close()
            if is_get and uri and len(reponse_serveur) > 0:
                with cache_lock:
                    cache[uri] = bytes(reponse_serveur)
    threading.Thread(target=copier, args=(sock_client, sock_serveur, fini)).start()
    threading.Thread(target=copier, args=(sock_serveur, sock_client, fini, reponse_serveur)).start()

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
