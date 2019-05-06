import socket
import os
import sys
import select

g = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)

adres = sys.argv[1]
katalog = sys.argv[2]
g.bind(adres)
os.chmod(adres, 0o622)

if not os.path.exists(katalog):
	os.makedirs(katalog)
	
os.chdir(katalog)
g.listen()
l_g = [g]

while True:
	r, w, x = select.select(l_g, [], [])
	do_usuniecia = []
	for gn in r:
		if gn == g:
			gp, adzd = gn.accept()
			print('======', gp, adzd)
			l_g.append(gp)
		else:		
			
			dane = gp.recv(1024)
			dane = dane.decode('utf-8')
			tab = dane.split(" ")
			if len(dane)>0:
				print(tab)
				nazwa_pliku = tab[1]
				if nazwa_pliku.find("/") == -1:
					plik = open(nazwa_pliku, 'a')
					log = tab[0] + ": "
					for i in tab[2:]:
						log = log + i + " "
					plik.write(log)
					plik.close()
			else:
				gn.close()
				do_usuniecia.append(gn)
	for gn in do_usuniecia:
		l_g.remove(gn)