#!/usr/bin/env python3
import json
import os
import sys
import argparse
from samsync.logger import get_logger
from samanage3 import Samanage


if not os.path.exists('logs'): os.mkdir('logs')
logger = get_logger('logs/samsync.log')

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
    if remote_device.owner is None or local_device['owner'] is None:
        return False
    elif remote_device.owner['name'].lower() == local_device['owner'].lower():
        return True
    return False

def _build_payload(user=None):
    """Builds the payload object to update the remote resource
    If the user is None, return a payload object where the owner is
    None.
    """
    if user is None:
        return {'owner': None}
    return {'owner': {'email': f'{user.email}'}}

def update(client, local_device, remote_device):        
    """Update resource metadata"""
    user = fetch_resource(client, local_device, 'users')
    payload = _build_payload(user)
    client.put('hardwares', payload, remote_device.id)
    logger.info(f'Updating {remote_device.name} with owner {user}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', required=True)
    parser.add_argument('-i', '--input', required=True)
    args = parser.parse_args()

    client = Samanage(token=args.token)
    local_devices = load_json(args.input)
    
    for local_device in local_devices:
        logger.debug('Device: %s - Owner: %s' % (local_device['name'], local_device['owner']))
        remote_device = fetch_resource(client, local_device, 'hardwares')
        if remote_device:
            if not is_updated(local_device, remote_device):
                update(client, local_device, remote_device)
        

if __name__ == '__main__':
    main()
