import serial, time

# Input fra bruker for konfigurasjon
com_port = input("Oppgi COM-port (f.eks. COM3): ")
username = input("Angi nytt brukernavn: ")
password = input("Angi passord for brukeren: ")
ip_addr = input("Angi IP-adresse for ruteren (192.168.x.x): ")

# Forsøk å åpne seriellporten
try:
    ser = serial.Serial(com_port, baudrate=9600, timeout=20)
except Exception as e:
    print("Feil: kunne ikke åpne seriellporten.")
    exit(1)

# Send kommandoer til ruteren via konsoll
time.sleep(1)
ser.write(b"\r\n")  # send "Enter" for å få frem eventuelt konsollprompt
time.sleep(1)
ser.write(b"enable\r\n")            # gå til privilegert modus
time.sleep(0.5)
ser.write(b"configure terminal\r\n")# gå til konfigurasjonsmodus
time.sleep(0.5)

# Konfigurer grensesnitt med IP-adresse (antatt GigabitEthernet0/0)
ser.write(b"interface GigabitEthernet0/1\r\n")
time.sleep(0.5)
ser.write(f"ip address {ip_addr} 255.255.255.0\r\n".encode())  # sett IP + standard /24 nettmaske
time.sleep(0.5)
ser.write(b"no shutdown\r\n")      # aktiver grensesnittet
time.sleep(0.5)
ser.write(b"exit\r\n")             # tilbake fra grensesnitt-konfig

# Konfigurer lokal bruker og SSH
ser.write(b"ip domain-name example.com\r\n")  # sett et domenenavn (påkrevd for RSA-nøkler)
time.sleep(0.5)
ser.write(f"username {username} privilege 15 password {password}\r\n".encode())  # opprett lokal bruker
time.sleep(0.5)
ser.write(b"crypto key generate rsa modulus 1024\r\n")  # generer RSA-nøkkel (1024-bit)
time.sleep(3)  # vent litt for nøkkelgenerering
ser.write(b"ip ssh version 2\r\n")    # sikre at SSH v2 benyttes
time.sleep(0.5)
ser.write(b"line vty 0 4\r\n")       # konfigurer vty-linjene 0-4
time.sleep(0.5)
ser.write(b"login local\r\n")       # krev lokal innlogging på vty
time.sleep(0.5)
ser.write(b"transport input ssh\r\n")# tillat kun SSH (deaktiver telnet) på vty
time.sleep(0.5)
ser.write(b"end\r\n")               # avslutt konfigurasjonsmodus
time.sleep(0.5)

ser.close()
# Skriptet ferdig (ingen suksessmelding iht. krav om kun feilmelding ved feil)
