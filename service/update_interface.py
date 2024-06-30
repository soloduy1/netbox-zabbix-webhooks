import argparse
import re
import os
from methods import *
from dotenv import load_dotenv

parser = argparse.ArgumentParser()
parser.add_argument("-ia", help="interface a")
parser.add_argument("-ib", help="interface b")
parser.add_argument("-da", help="device b")
parser.add_argument("-db", help="deice b")
parser.add_argument("-s", help="status")


args = parser.parse_args()
print(args)

dev_a = {args.ia: args.da}
dev_b = {args.ib: args.db}
devs = [dev_a, dev_b]
status = args.s

load_dotenv()
NETBOX_URL = os.getenv('NETBOX_URL')
ZABBIX_URL = os.getenv('ZABBIX_URL')
NETBOX_TOKEN = os.getenv('NETBOX_TOKEN')
ZABBIX_TOKEN = os.getenv('ZABBIX_TOKEN')
ROLES = os.getenv('ROLES')
INTERFACE_REGEX = os.getenv('INTERFACE_REGEX')

nb = get_api_netbox(NETBOX_URL, NETBOX_TOKEN)
z = get_api_zabbix(ZABBIX_URL, ZABBIX_TOKEN)

for devices in devs:
    for key in devices:
        interface = str(key)
        if re.search(INTERFACE_REGEX, interface):
            name = devices[key]
            device = get_device(nb, name, ROLES)
            if device:
                for dev in device:
                    model = str(dev.device_type.slug)
                    type, port = normalize_int(key)

                    out = normalize_port(model, port, type)

                    if status == "conn":
                        add_items(z, name, out)
                    else:
                        rm_items(z, name, out)
                    print(out)
            else:
                break

