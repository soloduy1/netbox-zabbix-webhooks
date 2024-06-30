import re
import time
import pynetbox
from pyzabbix import ZabbixAPI


def get_api_netbox(url, token):
    """
    Get Netbox API for access to NB instance

    url: [STRING] Address or IP w/ active Netbox
    token: [STRING] Netbox token for access to NB data (read-only rights enough)
    threading: [BOOLEAN] If True then uses multi-threading CPU when running

    :return [API] Netbox API instance
    """
    nb = pynetbox.api(
        url,
        token=token,
        threading=True
    )
#    nb.http_session.verify = False

    return nb


def get_api_zabbix(url, token):
    """
    Get Zabbix API for access to Zabbix instance

    url: [STRING] Address or IP w/ active Zabbix
    token: [STRING] API Token for acces to Zabbix API

    :return [API] Zabbix API instance
    """
    z = ZabbixAPI(url, detect_version=False)
#    z.session.verify = False
    z.login(api_token=token)

    return z


def get_device(nb, val, roles):
    """
    Get devices from NB according to them name and device_role

    nb: [API] Netbox API instance
    val: [STRING] Name of requiring device
    roles: [LIST] List of roles to search for

    :return [CONTAINER] Netbox devices container
    """
    devices = nb.dcim.devices.filter(name=val, has_primary_ip='true', role=roles)
    if devices:
        return devices


def get_host_id_by_name(z, name):
    """
    Get zabbix host ID according to its name

    z: [API] Zabbix API instance
    name: [STRING] Name of requiring host

    :return [INT] Zabbix host ID
    """
    f = {'host': name}
    hosts = z.host.get(filter=f)
    return hosts


def get_zabbix_host(z, address, name):

    host = get_interface_id_by_ip(z, address)
    if host:
        hostname = z.host.get(hostids=host, output=['hostid', 'name'])
        if hostname[0]['name'] != name:
            return host


def update_host_name(z, id, name, ip):
    try:
        z.host.update(hostid=id, host=name)
    except:
        iface = z.hostinterface.get(hostids=id)
        i = iface[0]['interfaceid']
        z.hostinterface.update(interfaceid=i, ip=ip)


def get_interface_id_by_ip(z, ip):
    f = {'ip': ip}
    interfaces = z.hostinterface.get(filter=f, output=['hostid'])
    if len(interfaces) > 1:
        return interfaces[-1]['hostid']
    else:
        return interfaces[0]['hostid']


def execute_now(z, id):
    ids = z.discoveryrule.get(hostids=id[0]['hostid'])
    time.sleep(240)
    for lld in ids:
        z.task.create(type=6, request={"itemid": lld['itemid']})
    time.sleep(60)


def get_items_id(z, name, out):
    id = get_host_id_by_name(z, name)
    out_mikro = out + "-"
    out = out + "("

    try:
        items = z.item.get(hostids=id[0]['hostid'], output=['itemid'], search={'name': out})
        items_mikro = z.item.get(hostids=id[0]['hostid'], output=['itemid'], search={'name': out_mikro})
    except:
        print('!!!!!!')

    if items == [] and items_mikro == []:
        execute_now(z, id)
        items = z.item.get(hostids=id[0]['hostid'], output=['itemid'], search={'name': out})
        items_mikro = z.item.get(hostids=id[0]['hostid'], output=['itemid'], search={'name': out_mikro})

    if items == []:
        return items_mikro
    else:
        return items


def add_items(z, name, out):
    """
    Activate zabbix host's items

    z: [API] Zabbix API instance
    name: [STRING] Name of requiring item

    """
    items = get_items_id(z, name, out)
    for item in items:
        print(item)
        z.item.update(itemid=item['itemid'], status=0)


def rm_items(z, name, out):
    items = get_items_id(z, name, out)
    for item in items:
        print(item)
        z.item.update(itemid=item['itemid'], status=1)


def normalize_int(var):
    gi = "gi"
    fa = "ether"
    sfp = "sfp"
    sfp_plus = "sfp+"
    combo = "combo"
    stack = False

    if re.search('/', var):
        stack = True

    if re.search('GigabitEthernet', var):
        if stack:
            unit, var = var.split('GigabitEthernet')
            unit = unit + "g"
            return unit, var
        else:
            _, var = var.split('GigabitEthernet')
            return gi, var
    if re.search('FastEthernet', var):
        if stack:
            unit, var = var.split('FastEthernet')
            unit = unit + "e"
            return unit, var
        else:
            _, var = var.split('FastEthernet')
            return fa, var
    if re.match('combo', var):
        _, var = var.split('combo')
        return combo, var
    if re.match('ether', var):
        _, var = var.split('ether')
        return gi, var
    if re.match('port', var):
        _, var = var.split('port')
        return gi, var
    if re.match('sfp-sfpplus', var):
        _, var = var.split('sfp-sfpplus')
        return sfp_plus, var
    if re.match('sfp', var):
        _, var = var.split('sfp')
        return [sfp, var]


def normalize_port(model, port, type):
    stack = False

    if re.search('/', type):
        stack = True

    if re.match('at-8000', model):
        if stack:
            if type == "gi":
                return type + port
            else:
                return type + port

        else:
            if type == "gi":
                return "g" + port
            else:
                return "e" + port

    if re.match('at-fs', model) or re.match('at-x', model) or re.match('at-gs', model):
        return 'port' + port

    if re.match('sg', model) or re.match('sf', model):
        if type == "gi":
            return "gi" + port
        else:
            return "gi" + port

    if re.match('ccr', model) or re.match('crs', model) or re.match('rb', model):
        if type == "gi":
            return "ether" + port
        if type == "sfp":
            return "sfp" + port
        if type == "combo":
            return "combo" + port
        else:
            return "sfp-sfpplus" + port


def ip_strip(line):
    """
    Strip /32 part of IP-address

    line: [STRING] IP-address with netmask

    :return [STRING] IP-address without netmask
    """
    ip, _ = line.split('/')
    return ip


def no_api(url):
    """
    Strip /api part of URL

    line: [STRING] URL with /api

    :return [STRING] URL without /api
    """
    left, right = url.split('/api')
    return left + right
