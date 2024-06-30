#!/bin/sh

interface_a=$1
interface_b=$2
device_a=$1
device_b=$2

device_a=${device_a#*name\"\:\"}
device_a=${device_a%url*}
device_a=${device_a%\"\,\"url*}

device_b=${device_b#*name\"\:\"}
device_b=${device_b%url*}
device_b=${device_b%\"\,\"url*}

interface_a=${interface_a#*name}
interface_a=${interface_a#*name\"\:\"}
interface_a=${interface_a%\"\,\"url*}

interface_b=${interface_b#*name}
interface_b=${interface_b#*name\"\:\"}
interface_b=${interface_b%\"\,\"url*}

status="disable"

python3 update_interface.py -ia $interface_a -da $device_a -ib $interface_b -db $device_b -s $status
