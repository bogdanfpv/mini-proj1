import socket, sys, threading

def copier(source, destination):
	try:
		while True:
			donnees = source.recv(4096)
			if not donnees:
				break
			destination.sendall(donnees)
	except OSError:
		pass
	finally:
		for s in (source, destination):
			try:
				s.shutdown(socket.SHUT_RDWR)
			except OSError:
				pass
			s.close()
	
def gerer_client(sock_client, ip_serveur, port_serveur):
	try:
		sock_serveur = socket.create_connection((ip_serveur, port_serveur))
	except OSError as e:
		print(f"connexion au server impossible :  {e}")
		sock_client.close()
		return
	threading.Thread(None, copier, None, (sock_client, sock_serveur)).start()
	threading.Thread(None, copier, None, (sock_serveur, sock_client)).start()

if len(sys.argv) != 4:
	print("usage: python relay.py IP_SERVEUR PORT_SERVEUR PORT_LOCAL")
	sys.exit(1)
ip_serveur, port_serveur, port_local = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ecoute = socket.socket()
ecoute.bind(("", port_local))
ecoute.listen()
while True:
	sock_client, _ = ecoute.accept()
	gerer_client(sock_client, ip_serveur, port_serveur)
