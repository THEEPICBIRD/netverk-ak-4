# netverk-ak-4
Dette oppsette er for 2 rutere med hsrp og dhcp, 2 switcher hvor en har etherchannel.

prereqs

cisco nettverks enehter

ansible controller i linux

må kjøre følgenmde kommando i linux ansible-galaxy collection install cisco.ios

Hvordan kjøre oppsettet

steg 1 clone github repo

steg 2 kjør python script for å sette mgmgt ip på enhetene og opprette mulighet for ssh påloggning.

steg 3 sørg for at du lagrer scriptene på filområdet som matcher ansible.cfg filen hvis ikke må du oppdatere filstien.
