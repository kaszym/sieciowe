#klient
import socket 
import getopt
import sys
import select
import getpass

try:
	opt, arg = getopt.getopt(sys.argv[1:], 'p:s:l:i')
except getopt.GetoptError as err:
	print('ERROR: ', err)
	sys.exit(1)
	
numer_portu = 65432
adres_serwera = "localhost"
pseudonim = getpass.getuser()
wyswietlanie_wiadomosci = 1

#print (opt, arg) 	
for opts, args in opt:
	if opts in ("-p"):
		numer_portu = int(args)
	elif opts in ("-s"):
		adres_serwera = args
	elif opts in ("-l"):
		print(args)
		pseudonim = args
	elif opts in ("-i"):
		wyswietlanie_wiadomosci = 0
			
g = socket.socket()

try:
	g.connect((adres_serwera, numer_portu))
except ConnectionRefusedError as w:
	print('error: ', w)
	#print(repr(w))
	sys.exit(1)
	
w = str(wyswietlanie_wiadomosci)	
p = pseudonim.encode('utf-8')
w = w.encode('utf-8')
g.sendall(b'LOGIN ' + p + b' ' + w)
	
while True:
	#print("petla")
	r, w, x = select.select([g, sys.stdin], [], [])
	if g in r:
		odp = g.recv(1024)
		odp = odp.decode('utf-8')
		if odp == "":
			g.close()
			sys.exit(0)
		if wyswietlanie_wiadomosci == 0 and (odp.strip().find("ERROR") != -1 or odp.strip().find("OK") != -1 or odp.strip().find("USERS") != -1):
			print('>>', odp)
		elif wyswietlanie_wiadomosci == 1:
			print('>>', odp)
	if sys.stdin in r:
		dane = input()
		dane = dane.strip()
		#print("przed ifem")
		if dane.find("/list") != -1:
			dane = "LIST"
			dane = dane.encode('utf-8')
		elif dane.find("/rename") != -1:
			tab = dane.split(" ")
			tab[0] = "RENAME"
			dane = ""
			for i in tab:
				dane = dane + i + " "
			dane = dane.strip()
			dane = dane.encode('utf-8')
		elif dane.find("/priv") != -1:
			tab = dane.split(" ")
			tab[0] = "PRIV"
			dane = ""
			for i in tab:
				dane = dane + i + " "
			dane = dane.strip()
			dane = dane.encode('utf-8')
		else: 
			dane = "PUB " + dane
			dane = dane.strip()
			dane = dane.encode('utf-8')
			#print("hello")
		#print(dane)
		g.sendall(dane)
