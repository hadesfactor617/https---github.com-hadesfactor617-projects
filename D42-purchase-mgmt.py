#!/usr/bin/env python3

import json
from device42api import Device42API, IPAM_vlan
import os 
from os import environ
import requests
import httplib2
import pandas as pd
import sys
from getpass import getpass


def fetchMachinesD42(savedQueryName, endpoint, username, password):
    """Returns lists of Machines"""
    URL = "https://" + endpoint + "/services/data/v1.0/query/?saved_query_name=" + savedQueryName + "&output_type=json"
    httplib2.Http(disable_ssl_certificate_validation=True)
    try:
        resp = requests.get(URL, auth=(username, password), verify=False)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    # Converts JSON response to Dictionary
    data = resp.json()
    # TODO: Add error handling here
    print(resp.status_code)
    return data

#Imports Excell Spread with Purchase info
def load_excel(filePath):
    # Create a dictionary, keyed by serial number for each XLS row for
    # fast index-based comparison later
    serials = dict()
    df = pd.read_excel(filePath, skiprows=2)
    for index, row in df.iterrows():
        s = str(row['serial_no']).upper()
        if s in serials.keys():
            print("Found duplicate serial: {}".format(s))
        serials[s] = row
    return serials

# Asks user to input selection of DOQL import or API scrape
def yes_no(question):
    while "Invalid Selection, Please choose Y for API Scrape or n for DOQL Import":
        reply = (raw_input(question+' (Y/n): '))
        if reply == 'Y':
            return True
        elif reply == 'n':
            return False
        else:
            print("Invalid Selection, Please choose Y for API Scrape or n for DOQL Import")
    return yes_no
  


def main():
    
    endpoint = ('inventory.tmaws.io')
    reply = yes_no('Please choose Y for API Scrape or n for DOQL Import')
    
    if reply == False:
        machines = loadMachinesD42(raw_input("Enter File location and Name of DOQL: "))
        print("Total Machines Loaded from D42: {}".format(len(machines)))
    
    if reply == True:
        print("Fetching Devices from Device42")
        username = getpass(prompt = 'Tecops UserName ')
        password = getpass(prompt = 'Techops PWD ')
        machines = fetchMachinesD42(savedQueryName="dcops_automation",
                                    endpoint=endpoint,
                                    username=username,
                                    password=password)
        print("Total Machines Loaded from D42: {}".format(len(machines)))  
            
    serials = load_excel(raw_input("Enter File location and Name of XLS: "))
    print("Total Machines Loaded from Recycle List: {}".format(len(serials)))

    print("Iterating over Lists...")
    dup_serials, notInD42 = iter_data(machines, serials)
    
    print("Duplicate Machines: {}".format(len(dup_serials)))
    print("Machines NOT IN D42: {}".format(len(notInD42)))

    df1 = pd.DataFrame(dup_serials, columns=['serial_no', 'device_name', 'hardware_name', 'room_name', 'Rack Name', 'service_level'])
    print("Exporting dup_serial.xlsx to current DIR")
    df1.to_excel('./dup_serial.xlsx', header=True, index=False)
    
    df2 = pd.DataFrame(notInD42, columns=['name', 'serial_no', 'manufacturer', 'hardware', 'is_it_switch', 'in_service', 'service_level','storage_room', 'storage_room_id'])
    print("Exporting serials_missing_in_d42.xlsx to current DIR")
    df2.to_excel('./serials_missing_in_d42.xlsx', header=True, index=False)

if __name__ == "__main__":
    main()