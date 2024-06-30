#!/bin/sh

name=$1

echo $name

#ansible-playbook rm_host_zabbix.yml -e "name=$name"
python3 remove_host.py -n $name
