#!/usr/bin/env python3

import json
import os
import sys
import argparse
from samsync.logger import get_logger
from samanage3 import Samanage, User, Hardware


if not os.path.exists('logs'): os.mkdir('logs')
logger = get_logger('logs/samsync.log')

def load_json(path):
    """Loads a json file of local devices, along with their owners
    as samanage3.Hardware objects.

    Args:
        path (str): The file path to the input file
    
    Returns:
        (list): of samanage3.Hardware device objects
    """
    device_list = []
    with open(path, 'r') as file:
        content = file.read()
    json_device_list = json.loads(content)
    
    for item in json_device_list:
        device = Hardware({
            'name': item['name'], 
            'owner': None if item['owner'] is None else {'name': item['owner']}
        })
        device_list.append(device)

    return device_list

def fetch_resource(client, record, record_type):
    """Fetches a resource item from the Samanage api"""
    if record_type == 'hardwares':
        target = record.name
    elif record_type == 'users':
        if record.owner is None:
            return None
        target = record.owner.get('name', None)

    try:
        return client.get(record_type=record_type, 
                          search={'name': f'{target}'})[0]
    except IndexError:
        return None

def is_updated(local, remote, user):
    """Returns True if the remote device attributes are up-to-date
    with the local device attributes. False otherwise.
    """
    # If any of these values are None, return False to avoid calling .get
    # on a NoneType (when it should be a dict)
    if local.owner is None or remote.owner is None or user.department is None:
        return False

    local_owner = local.owner.get('name').lower()
    remote_owner = remote.owner.get('name').lower()
    remote_dept = remote.department.get('name').lower()
    user_dept = user.department.get('name').lower()

    if local_owner == remote_owner:
        if remote_dept == user_dept:
            return True

    return False

def _build_payload(user):
    """Builds the payload object to update the remote resource"""
    if not isinstance(user.department, dict):
        user.department = {'name': None}

    return {
        'owner': {'email': f'{user.email}'},
        'department': {'name': '%s' % user.department.get('name', None)}
    }

def update(client, local_device, remote_device, user=None):        
    """Update resource metadata"""
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
        logger.debug('Device: %s - Owner: %s' % (local_device.name, local_device.owner))
        remote_device = fetch_resource(client, local_device, 'hardwares')
        if remote_device:
            user = fetch_resource(client, local_device, 'users')
            if user is None:
                user = User({'owner': None, 'department': None})
            if not is_updated(local_device, remote_device, user):
                update(client, local_device, remote_device, user)
        