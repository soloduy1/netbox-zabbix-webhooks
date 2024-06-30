import argparse
import os
import sys
import logging
import tlglog
import emoji
from methods import *
from dotenv import load_dotenv

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
parser = argparse.ArgumentParser()
parser.add_argument("-n", help="name")

args = parser.parse_args()
logging.info(f'UPD_HOST: Parse args "{args}"')
name = args.n

load_dotenv()
NETBOX_URL = os.getenv('NETBOX_URL')
ZABBIX_URL = os.getenv('ZABBIX_URL')
NETBOX_TOKEN = os.getenv('NETBOX_TOKEN')
ZABBIX_TOKEN = os.getenv('ZABBIX_TOKEN')
ROLES = os.getenv('ROLES')
TEMPLATES = os.getenv('TEMPLATES')
TEMPLATE_DEFAULT = os.getenv('TEMPLATE_DEFAULT')

nb = get_api_netbox(NETBOX_URL, NETBOX_TOKEN)
z = get_api_zabbix(ZABBIX_URL, ZABBIX_TOKEN)

item = get_device(nb, name, ROLES)
if item:
    for device in item:
        ip = str(device.primary_ip.address)
        ip = ip_strip(ip)
        name = str(device.name)
        platform = str(device.platform)
        site = str(device.site.slug)
        status = str(device.status)
        serial = str(device.serial)
        url = str(device.url)
        url = no_api(url)
        vendor = str(device.platform.name)

        try:
            zabbix_id = get_zabbix_host(z, ip, name)
        except:
            zabbix_id = False
            logging.info("UPD_HOST: No changes in device name")

        if zabbix_id:
            logging.info("UPD_HOST: Device name had been changed")
            update_host_name(z, zabbix_id, name, ip)

        for key in TEMPLATES.keys():
            template = TEMPLATES.pop(key)
            break

        if 'template' not in locals():
            template = TEMPLATE_DEFAULT
            e = f"Can't find template in Zabbix to device '{name}'! Using {template}"
            tlg = emoji.emojize(f":no_entry::warning:CHECK LOGS!!!:no_entry:\n\Module: update_host.py\n\Error: '{e}'")
            logging.warning(e)
            tlglog.send_tg(tlg)

        if status == "Active":
            status = "enabled"
        else:
            status = 'disabled'
        # Pass args to ansible
        print(name, ip, template, serial, status, url)
        quot = '"'
        os.system(f"ansible-playbook add_host_zabbix.yml -e 'url={quot}{url}{quot} name={quot}{name}{quot} ip={quot}{ip}{quot} vendor={quot}{vendor}{quot} serial={quot}{serial}{quot} template={quot}{template}{quot} status={quot}{status}{quot} zabbix_key={quot}{ZABBIX_TOKEN}{quot} zabbix_host={quot}{ZABBIX_URL}{quot}'")
else:
    e = f"Can't find device '{name}' in Netbox!"
    tlg = emoji.emojize(f":no_entry::warning:CHECK LOGS!!!:no_entry:\n\Module: update_host.py\n\Error: '{e}'")
    logging.warning(e)
    tlglog.send_tg(tlg)
