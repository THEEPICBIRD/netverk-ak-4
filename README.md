# netverk-ak-4
Dette oppsettet konfigurerer to rutere med HSRP og DHCP, samt to switcher hvor én av dem bruker EtherChannel.

Forutsetninger

Cisco-nettverksenheter

Ansible controller med Linux

Installer nødvendige Ansible-samlinger med følgende kommando:

ansible-galaxy collection install cisco.ios

Hvordan kjøre oppsettet

Steg 1

Klone GitHub-repositoriet:

git clone <repo-url>

Steg 2

Kjør Python-scriptet for å konfigurere administrasjons-IP (mgmt IP) på enhetene og aktivere SSH-tilgang. dette må gjøres via consoll kabel. følg ip plan sim ligger ved, hvis du ønsker å bruke andre iper så må inventory.yaml filen oppdateres med nmye iper. OBS fra dette steget er det viktig å se om enehten bruker FastEthernet eller GigabitEthernet. all code er satt opp med Gigabit med mindre den spør om input fra deg.

Steg 3

Sørg for at Ansible-scriptene lagres på det filområdet som er angitt i ansible.cfg. Dersom du bruker en annen filbane, må du oppdatere denne filbanen i ansible.cfg.

Steg 4

Kjør Ansible-scriptene i følgende rekkefølge:

R1 -> R2 -> SW2 -> SW3

Det anbefales å vente cirka 5 minutter mellom hvert script for å verifisere at konfigurasjonen blir korrekt utført.


