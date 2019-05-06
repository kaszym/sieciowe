import socket
import sys
import getopt
import select


try:
	opt, arg = getopt.getopt(sys.argv[1:], 'p:t:vq')
except getopt.GetoptError as err:
	print('ERROR: ', err)
	sys.exit(1)
	
numer_portu = 65432
powitanie = "Witaj!"
wyswietalnie_info = False
#print (opt, arg) 	
for opts, args in opt:
	if opts in ("-p"):
		numer_portu = int(args)
	elif opts in ("-t"):
		powitanie = args
	elif opts in ("-v"):
		wyswietalnie_info = True
	#elif opts in ("-q"):
	#	wyswietalnie_info = False
		
if ('-q', '') in opt:
	wyswietalnie_info = False
		
klienci = {} # (port, pseudonim)
gniazda = {} # (pseudonim, gniazdo)
wyswietlanie_wiadomosci = {} # {gniazdo, 1/0}

g_nas = socket.socket()
g_nas.bind(('', numer_portu))
g_nas.listen()
l_g = [g_nas]
powitanie = powitanie.encode('utf-8')

while True:
	#print(gniazda)
	r, w, x = select.select(l_g, [], [])
	do_usuniecia = []
	#print(l_g)
	for g in r:
		if g == g_nas:
			nowe_g, adres = g_nas.accept()
			if nowe_g in l_g:
				nowe_g.sendall(b'ERROR: Nie mozna polaczyc tego klienta \r\n')
			else:
				l_g.append(nowe_g)
			if wyswietalnie_info == True:
				print('-- nowe połączenie:', adres)
		else:
			dane = g.recv(1024)
			dane = dane.decode('utf-8')
			dane = dane.strip()
			if wyswietalnie_info == True:
				gniazdo = g.getpeername()
				gn = gniazdo[1]
				print('-- żadanie od użytkownika: ', klienci.get(gn))
				print('---- treść: ' + dane)
			if dane.find("LIST") != -1 :
				k = ""
				for i in klienci.keys():
					user = klienci[i]
					k = k + user + " "
				k = "USERS " + k
				#print(k, g)
				k = k.strip().encode('utf-8')
				g.sendall(k + b'\r\n')
				break
			elif dane.find("LOGIN") != -1:
				gniazdo = g.getpeername()
				gn = gniazdo[1]
				tab = dane.split(" ")
				login = tab[1]
				if login in gniazda:
					g.sendall(b'ERROR: Klient o takim pseudonimie juz jest zalogowany, zaloguj sie jeszcze raz \r\n')
					do_usuniecia.append(g)
					g.close()
					if wyswietalnie_info == True:
						print('-- zamykamy połączenie' , g)
				else: 
					klienci[gn] = login
					wyswietlanie_wiadomosci[g] = int(tab[2])
					gniazda[login] = g
					g.sendall(b'OK\r\n')
					g.sendall(powitanie + b'\r\n')
					if wyswietalnie_info == True:
						print('-- dodano nowego uzytkownika o loginie: ', login)
					break
			elif dane.find("RENAME") != -1:
				gniazdo = g.getpeername()
				gn = gniazdo[1]
				tab = dane.split(" ")
				if len(tab) == 2:			
					nowy = tab[1]
					if (gn in klienci and nowy not in gniazda and len(tab) == 2):
						k = klienci[gn]
						klienci[gn] = nowy
						gniazda.pop(k)
						gniazda[nowy] = g
						g.sendall(b'OK\r\n')
						if wyswietalnie_info == True:
							print('-- zmieniono pseudonim uzytkownika gniazda ' + str(gn) + ' na ' + nowy)
						break
					elif gn not in klienci:
						klienci[gn] = nowy
						gniazda[nowy] = g
						g.sendall(b'OK\r\n')
						if wyswietalnie_info == True:
							print('-- zmieniono pseudonim uzytkownika gniazda ' + str(gn) + ' na ' + nowy)
						break
					else: 
						g.sendall(b'ERROR: Nie powiodla sie zmiana pseudonimu \r\n')
						if wyswietalnie_info == True:
							print('-- nie powiodła się zmiana pseudonimu')
						break
				else:
					g.sendall(b'ERROR: Nie powiodla sie zmiana pseudonimu \r\n')
					break
			elif dane.find("PRIV") != -1:
				tab = dane.split(" ")
				if len(tab) >= 2:
					pseudo = tab[1]
					gniazdo = g.getpeername()
					gn = gniazdo[1]
					if pseudo in gniazda:
						if wyswietlanie_wiadomosci.get(gniazda.get(pseudo)) == 1: 
							wiadomosc = "PRIV_FROM " + klienci[gn] + " "
							for i in tab[2:]:
								wiadomosc = wiadomosc + i + " "
							if wyswietalnie_info == True:
								print('-- wyslano wiadomosc prywatną: ', wiadomosc)
							wiadomosc = wiadomosc.strip().encode('utf-8')
							gniazda[pseudo].sendall(wiadomosc + b'\r\n')
							g.sendall(b'OK\r\n')
							break
						else:
							g.sendall(b'ERROR: Ten uzytkownik nie odbiera wiadomosci publicznych ani prywatnych \r\n')
							if wyswietalnie_info == True:
								print('-- nie powiodlo sie wyslanie wiadomosci prywatnej')
					    
					else:
						g.sendall(b'ERROR: Nie udalo sie wyslac wiadomosci prywatnej \r\n')
						if wyswietalnie_info == True:
							print('-- nie powiodlo sie wysłanie wiadomosci prywatnej')
						break
				else:
					g.sendall(b'ERROR: Nie udalo sie wyslac wiadomosci prywatnej \r\n')
					if wyswietalnie_info == True:
						print('-- nie powiodlo sie wysłanie wiadomosci prywatnej')
					break
			elif dane.find("PUB") != -1:
				tab = dane.split(" ")
				wiadomosc = "PUB_MSG "
				for i in tab[1:]:
					wiadomosc = wiadomosc + i + " "
				if wyswietalnie_info == True:
					print('-- wyslano wiadomosc publiczna: ', wiadomosc)
				wiadomosc = wiadomosc.strip().encode('utf-8')
				for k in gniazda.keys():
					if gniazda.get(k) != g:
						gniazda.get(k).sendall(wiadomosc + b'\r\n')
			if len(dane) == 0:
				gniazdo = g.getpeername()
				gn = gniazdo[1]
				ps = klienci.get(gn)
				klienci.pop(gn)
				gniazda.pop(ps)
				wyswietlanie_wiadomosci.pop(g)
				g.close()
				do_usuniecia.append(g)
				if wyswietalnie_info == True:
					print('-- zamykamy połączenie od użytkownika' , ps)
	for g in do_usuniecia:
		l_g.remove(g)
				