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

def fetch_resource(client, record, record_type):
    """Fetches a resource item from the Samanage api"""
    if record_type == 'hardwares':
        target = record['name']
    elif record_type == 'users':
        target = record['owner']
    else:
        raise ValueError('record_type must be "hardwares" or "users"')
    try:
        return client.get(record_type=record_type, search={'name': f'{target}'})[0]
    except IndexError:
        return None

def is_updated(local_device, remote_device):
    """Returns True if the remote_device attributes are up-to-date
    with the local_device attributes. False otherwise.
    """
    if remote_device.owner is None:
        return False
    elif local_device['owner'].lower() == remote_device.owner['name'].lower():
        return True
    return False

def _build_payload(user):
    """Builds the payload object to update the remote resource"""
    return {'owner': {'email': f'{user.email}'}}

def update(client, local_device, remote_device):
    """Update the resource metadata"""
    user = fetch_resource(client, local_device, 'users')
    if user:
        payload = _build_payload(user)
        client.put('hardwares', payload, remote_device.id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', required=True)
    parser.add_argument('-i', '--input', required=True)
    args = parser.parse_args()

    client = Samanage(token=args.token)
    local_devices = load_json(args.input)
    
    for local_device in local_devices:
        remote_device = fetch_resource(client, local_device, 'hardwares')
        if remote_device:
            if not is_updated(local_device, remote_device):
                update(client, local_device, remote_device)
        

if __name__ == '__main__':
    main()
