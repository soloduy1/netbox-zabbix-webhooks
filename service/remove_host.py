import os
import argparse
import logging
from dotenv import load_dotenv


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
parser = argparse.ArgumentParser()
parser.add_argument("-n", help="name")

args = parser.parse_args()
name = args.n
logging.info(f"REMOVE_HOST: Parse 'name' with arg '{name}'")

load_dotenv()
ZABBIX_URL = os.getenv('ZABBIX_URL')
ZABBIX_TOKEN = os.getenv('ZABBIX_TOKEN')

quot = '"'
os.system(f"ansible-playbook rm_host_zabbix.yml -e 'name={quot}{name}{quot} zabbix_key={quot}{ZABBIX_TOKEN}{quot} zabbix_host={quot}{ZABBIX_URL}{quot}'")
logging.info(f"REMOVE_HOST: Successfully removed device with name '{name}' from Zabbix")
