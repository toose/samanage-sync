#!/usr/bin/env python3
import json
import sys
import argparse
from samanage3 import Samanage


def load_json(path):
    """Loads a json file of local devices, along with their owners"""
    with open(path, 'r') as file:
        content = file.read()
    return json.loads(content)


def fetch_hardware(client, device):
    """Fetches a hardware item from Samanage api"""



def main(token):
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', required=True)
    parser.add_argument('-i', '--input', required=True)
    args = parser.parse_args()

    client = Samanage(token=args.token)
    local_devices = load_json(args.path)
    
    for local_device in local_devices:
        remote_device = fetch_hardware(client, local_device)
    


if __name__ == '__main__':
    main(sys.argv[1])
