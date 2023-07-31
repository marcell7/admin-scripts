# Configure Wireguard VPN on Mikrotik RouterOS
# Works on Mikrotik RouterOS 7 or greater
# Works for my usecase. Run at your own risk. Not responsible for any complaints from your VPN users :)

# This script create a wg server and adds two basic firewall rules.

import argparse
import requests


def set_wg_server(base_uri, auth, wg_name):
    data = f'{{"name": "{wg_name}"}}'
    r = requests.put(f"{base_uri}/rest/interface/wireguard", auth=auth, verify=False, data=data)
    return r

def add_ip_address_range(base_uri, auth, wg_ip_range, wg_name):
    data = f'{{"address": "{wg_ip_range}", "interface":"{wg_name}"}}'
    r = requests.put(f"{base_uri}/rest/ip/address", auth=auth, verify=False, data=data)
    return r


def add_firewall_rules(base_uri, auth, wg_ip_range):
    rule_open_wg_port = '{"action": "accept", "chain":"input", "dst-port":"13231", "protocol":"udp", "comment":"Open udp port 13231 for wg connections", "place-before":"1"}'
    rule_access_lan = f'{{"action": "accept", "chain":"input", "src-address":"{wg_ip_range}", "comment":"VPN clients can access devices connected on the router", "place-before":"1"}}'
    rs = [
        requests.put(f"{base_uri}/rest/ip/firewall/filter", auth=auth, verify=False, data=rule_open_wg_port),
        requests.put(f"{base_uri}/rest/ip/firewall/filter", auth=auth, verify=False, data=rule_access_lan),
    ]
    return rs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Setup Wireguard server on Mikrotik Router")
    parser.add_argument("--address", default="192.168.88.1", help="Mikrotik router address. Default is 192.168.88.1")
    parser.add_argument("--username", default="admin", help="Mikrotik router username. Default is admin")
    parser.add_argument("--password", help="Mikrotik router password")
    parser.add_argument("--wg_name", default="wireguard1", help="Wireguard interface name. Default is wireguard1")
    parser.add_argument("--wg_ip_range", default="192.168.100.1/24", help="IP address range for wireguard. Default is 192.168.100.0/24")
    args = parser.parse_args()

    base_uri = f"http://{args.address}"
    auth = (args.username, args.password)

    set_wg_server(base_uri, auth, args.wg_name)
    add_ip_address_range(base_uri, auth, args.wg_ip_range, args.wg_name)
    rs = add_firewall_rules(base_uri, auth, args.wg_ip_range)
