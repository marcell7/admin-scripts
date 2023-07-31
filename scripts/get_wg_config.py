# Works with Python 3.6 or greater
# Works on Mikrotik RouterOS 7 or greater
# This script assumes Wireguard VPN on Mikrotik is implemented as specified in setup_wg.py
# Mikrotik router is accessed via http, thus it is not safe to use this script over the internet. Check: https://help.mikrotik.com/docs/display/ROS/REST+API
# Works for my usecase. Run at your own risk. Not responsible for any complaints from your VPN users :)

# This script adds a client/peer to wg server and generates a client wg config.

import subprocess
import argparse
import sys
import requests
from datetime import date


def get_client_private_key():
    pk = subprocess.run(["wg", "genkey"], capture_output=True)
    return pk.stdout


def get_client_public_key(pk):
    pubk = subprocess.run(["wg", "pubkey"], input=pk, stdout=subprocess.PIPE)
    return pubk.stdout


def get_wg_server_public_key(auth, base_uri, wg_name):
    pubk = None
    r = requests.get(f"{base_uri}/rest/interface/wireguard", auth=auth, verify=False)
    wgs = r.json()
    for wg in wgs:
        if wg["name"] == wg_name:
            pubk = wg["public-key"]
    return pubk


def get_wg_ips(auth, base_uri, wg_name):
    r = requests.get(f"{base_uri}/rest/ip/address", auth=auth, verify=False)
    addresses = r.json()
    for address in addresses:
        if address["actual-interface"] == wg_name:
            return address["address"]


def get_available_client_address(auth, base_uri, wg_name):
    r = requests.get(f"{base_uri}/rest/interface/wireguard/peers", auth=auth, verify=False)
    peers = r.json()
    # A little messy. It grabs all addresses and gets the last set of numbers in IP address
    used_addresses = [int(peer["allowed-address"].split(".")[-1].split("/")[0]) for peer in peers]
    for i in range(2, 255):
        if i not in used_addresses:
            address = get_wg_ips(auth, base_uri, wg_name)
            if address is not None:
                return f"{'.'.join(address.split('.')[:3])}.{i}"


def add_peer_to_server(auth, base_uri, wg_name, client_public_key, client_address, comment):
    data = f'{{"interface": "{wg_name}", "public-key": "{client_public_key}", "allowed-address": "{client_address}", "comment": "{comment}"}}'
    r = requests.put(f"{base_uri}/rest/interface/wireguard/peers", auth=auth, verify=False, data=data)
    return r

def generate_config(client_private_key, client_address, server_public_key, allowed_ips, server_ip, dns, output_path):
    template = \
    f"""[Interface]
    PrivateKey = {client_private_key}
    Address = {client_address}
    DNS = {dns}

    [Peer]
    PublicKey = {server_public_key}
    AllowedIPs = {allowed_ips}
    Endpoint = {server_ip}
    PersistentKeepalive = 10"""

    with open(output_path, "w") as conf:
        conf.write(template)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="get_wg_config", description="This script adds a client/peer to wg server and generates a client wg config.")
    parser.add_argument("--address", default="192.168.88.1", help="Mikrotik router address. Default is 192.168.88.1")
    parser.add_argument("--username", default="admin", help="Mikrotik router username. Default is admin")
    parser.add_argument("--password", help="Mikrotik router password")
    parser.add_argument("--allowed_ips", default="0.0.0.0/0", help="IPs that will be tunneled. Check WG documentation. Default is 0.0.0.0/0")
    parser.add_argument("--server_ip", help="Mikrotik public facing IP and port in format {ip:port}. Default port is 13231")
    parser.add_argument("--wg_name", default="wireguard1", help="Wireguard interface name. Check in RouterOS. Default is wireguard1")
    parser.add_argument("--dns", default="8.8.8.8", help="DNS address. Default is Google dns server 8.8.8.8")
    parser.add_argument("--output_path", default="wg0.conf", help="File output path. Default is wg0.conf. File is saved in the working dir")
    parser.add_argument("--comment", default=f"{date.today()}", help="Comment to add to a peer. Default is today's date.")
    args = parser.parse_args()
    print(args)
    wg_version = subprocess.run(["wg", "--version"], capture_output=True, text=True)
    if wg_version.returncode != 0:
        print("Wireguard not installed.")
        sys.exit()
    else:
        print(f"Installed wireguard version: {wg_version.stdout}")

    auth = (args.username, args.password)
    base_uri = f"http://{args.address}"


    client_private_key = get_client_private_key()
    client_address = get_available_client_address(auth, base_uri, args.wg_name)
    server_public_key = get_wg_server_public_key(auth, base_uri, args.wg_name)

    print("Generating config...")
    generate_config(
        client_private_key=client_private_key.decode("utf-8").strip(),
        client_address=client_address,
        server_public_key=server_public_key,
        allowed_ips=args.allowed_ips,
        server_ip=args.server_ip,
        dns=args.dns,
        output_path=args.output_path
    )

    print("Adding peer to the server...")
    client_public_key = get_client_public_key(client_private_key)
    add_peer_to_server(
        auth=auth,
        base_uri=base_uri,
        wg_name=args.wg_name,
        client_public_key=client_public_key.decode("utf-8").strip(),
        client_address=client_address,
        comment=args.comment
    )

    print("FINISHED")








