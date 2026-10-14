import socket, sys, threading

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
		sock_serveur = socket.create_connection((ip_serveur, port_serveur))
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
	threading.Thread(target=copier, args=(sock_client, sock_serveur, fini)).start()
	threading.Thread(target=copier, args=(sock_serveur, sock_client, fini)).start()

if len(sys.argv) != 4:
	print("usage: python relay.py IP_SERVEUR PORT_SERVEUR PORT_LOCAL")
	sys.exit(1)
ip_serveur, port_serveur, port_local = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ecoute = socket.socket()
ecoute.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ecoute.bind(("", port_local))
ecoute.listen()
while True:
	sock_client, _ = ecoute.accept()
	gerer_client(sock_client, ip_serveur, port_serveur)
