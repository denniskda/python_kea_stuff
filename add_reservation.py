#!/usr/bin/python3
#Script made for specific kea setup when mysql backend is used as reservations database only
#Also default procedures for audit entry creation are deleted, and custom columns added
#Classes used in script must be defined in config file
#Also dont forget to change keahost and db variables

#required mysql-connector-python
import mysql.connector
import ipaddress
import argparse
import getpass
import re

# Colors of course
from colorama import Fore
green = Fore.GREEN
yellow = Fore.YELLOW
red = Fore.RED
color_reset = Fore.RESET

#Validation functions
def valid_ip(ipaddr):
    try:
        ipaddress.ip_address(ipaddr)
    except ValueError:
        if ipaddr == None:
            print(red + "No ip addres or device list given." + color_reset)
        print(red + f"Ip validation failed for {ipaddr}" + color_reset)
        exit(code=1)
    return ipaddr

def valid_mac(macaddr):    
    str(macaddr)
    regexp = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'

    pregexp = re.compile(regexp)
    
    if re.search(pregexp,macaddr):
        macaddr = macaddr.replace('-', '')
        macaddr = macaddr.replace(':', '')
        macaddr = macaddr.lower()
        return macaddr
    else:
        print(red + "Mac address verification failed." + color_reset)
        exit(code=1)

#Arguments handling
parser = argparse.ArgumentParser(usage="add_reservation.py HWADDRES ADDRESS SUBNET_ID DEVCLASS")
parser.add_argument("hwaddress", help="MAC addres of device")
parser.add_argument("address", help="IP address to reserve")
parser.add_argument("subnet_id", help="ID of subnet of reservation",type=int)
parser.add_argument("devclass", help="Class of device: laptop, desktop or server", choices=["laptop","desktop","server"])

arg = parser.parse_args()

#User inputs
user = input("Username: ")
password = getpass.getpass()

#Hardcoded vars
keahost = '*database_host*'
db = '*database_name*'

#Check user input
hwaddr = valid_mac(arg.hwaddress)
ipaddr = valid_ip(arg.address)

#DBconnection
keadb = mysql.connector.connect(host=keahost,user=user,password=password,database=db)

sqlcursor = keadb.cursor()

#timestamp and added_by columns are added manually instead of kea default audit options
sqlcursor.execute(f"INSERT INTO `hosts` (`dhcp_identifier`, `dhcp_identifier_type`, `ipv4_address`, `dhcp4_subnet_id`, `dhcp4_client_classes`, `timestamp`, `added_by`) \
                  VALUES ('0x{hwaddr}', '0', INET_ATON('{ipaddr}'), '{arg.subnet_id}', '{arg.devclass}', current_timestamp(), 'CURRENT_USER()')")
keadb.commit()
