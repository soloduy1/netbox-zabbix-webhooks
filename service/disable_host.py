import argparse
import logging
import emoji
import tlglog
import os
from dotenv import load_dotenv
from methods import *

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("-n", help="name")

args = parser.parse_args()
name = args.n
logging.info(f"DISABLE_HOST: Parse 'name' with arg '{name}'")


load_dotenv()
ZABBIX_URL = os.getenv('ZABBIX_URL')
ZABBIX_TOKEN = os.getenv('ZABBIX_TOKEN')

nb = get_api_netbox(NETBOX_URL, NETBOX_TOKEN)
z = get_api_zabbix(ZABBIX_URL, ZABBIX_TOKEN)
device = get_host_id_by_name(z, name)

if device:
    if device[0]['status'] == "0":
        z.host.update(hostid=device[0]['hostid'], status=1)
        logging.info(f"DISABLE_HOST: Successfully deactivated device '{name}' in Zabbix")
else:
    e = f"DISABLE_HOST: Can't find device with name '{name}' in Zabbix!"
    tlg = emoji.emojize(f":no_entry::warning:ПРОВЕРЬ ЛОГИ!!!:no_entry:\n\nМодуль: disable_host.py\n\nОшибка: '{e}'")
    logging.warning(e)
    tlglog.send_tg(tlg)
