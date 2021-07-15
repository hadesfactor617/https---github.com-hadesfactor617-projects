import napalm
from getpass import getpass
import json

driver = napalm.get_network_driver('ios')
# password = getpass()
device = driver(hostname='192.168.1.2', username='eric', password='showbiz666!')

device.open()
# print(device.get_interfaces())
cmds = ['show interface status | include notconnect']
input = device.cli(cmds)
print(len(input))
for i in input.keys():
    print(i)
    input[i] = input[i].split('\n')

print(json.dumps(input, sort_keys=True, indent=4))
device.close()