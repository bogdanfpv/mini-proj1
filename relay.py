import socket, sys, threading

def copier(source, destination):
	while True:
		donnees = source.recv(4096)
		if not donnees:
			break
		destination.sendall(donnees)
	destination.close()
	
def gerer_client(sock_client, ip_serveur, port_serveur):
	sock_serveur = socket.create_connection((ip_serveur, port_serveur))
	threading.Thread(None, copier, None, (sock_client, sock_serveur))
	
ip_serveur, port_serveur, port_local = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ecoute = socket.socket()
ecoute.bind(("", port_local))
ecoute.listen()
while True:
	sock_client, _ = ecoute.accept()
	gerer_client(sock_client, ip_serveur, port_serveur)
