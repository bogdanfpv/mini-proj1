import socket, sys, threading
 
verrou_log = threading.Lock()
 
def charger_interdits(fichier="interdits.txt"):
    try:
        with open(fichier) as f:
            return [l.strip().lower() for l in f if l.strip()]
    except OSError:
        return []
 
def log_interdit(client_ip,uri):
    with verrou_log:
        with open("interdit.log","a") as f:
            f.write(f"{client_ip} {uri}\n")
 
 
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
        client_ip = sock_client.getpeername()[0]
        requete = sock_client.recv(4096)
        if not requete:
            sock_client.close()
            return
    except OSError:
        sock_client.close()
        return
 
    texte = requete.decode(errors='ignore')
    elements = texte.split('\r\n')[0].split(' ')
    if len(elements) > 1 and elements[0]=="GET":
        uri = elements[1]
        if any(site in texte.lower() for site in interdits):
            try:
                log_interdit(client_ip,uri)
            except OSError:
                pass
            corps = b"Interdit\n"
            entete = (b"HTTP/1.1 403 Forbidden\r\nContent-Type: text/plain\r\n"
                      b"Content-Length: " + str(len(corps)).encode() + b"\r\n\r\n")
            try:
                sock_client.sendall(entete + corps)
            except OSError:
                pass
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
 
    def fini():
        nonlocal restants
        with verrou:
            restants -= 1
            dernier = restants==0
        if dernier:
            sock_client.close()
            sock_serveur.close()
 
    threading.Thread(target=copier, args=(sock_client, sock_serveur, fini)).start()
    threading.Thread(target=copier,args=(sock_serveur, sock_client, fini)).start()
 
if len(sys.argv) != 4:
    print("usage :python relay_censeur.py IP_SERVEUR PORT_SERVEUR PORT_LOCAL")
    sys.exit(1)
 
ip_serveur, port_serveur, port_local = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
interdits = charger_interdits()
 
ecoute = socket.socket()
ecoute.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ecoute.bind(("", port_local))
ecoute.listen()
 
while True:
    sock_client, _ =ecoute.accept()
    threading.Thread(target=gerer_client, args=(sock_client, ip_serveur, port_serveur)).start()
