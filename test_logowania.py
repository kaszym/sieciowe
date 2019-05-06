#klient
import socket 
import select
import sys
import time

sc_gniazda = sys.argv[1]
ile = int(sys.argv[2])
interwal = float(sys.argv[3])
nazwa_programu = sys.argv[4]
nazwa_pliku = sys.argv[5]
komunikat = ""
for i in sys.argv[6:]:
	komunikat = komunikat + i + " "
	
g = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
g.connect((sc_gniazda))
print(sys.argv)

while True:
	for i in range(ile):
		i = str(i)
		dane = ""
		dane = nazwa_programu + i + " " + nazwa_pliku + i + " " + komunikat
		print(dane)
		dane = dane.encode('utf-8')
		g.sendall(dane)
		print("OK")
		time.sleep(interwal)
	g.close()
	sys.exit(0)