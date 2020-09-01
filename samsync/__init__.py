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
    """Loads a json file of local devices, along with their owners"""
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
        target = record['name']
    elif record_type == 'users':
        target = record['owner']
    else:
        raise ValueError('record_type must be "hardwares" or "users"')
    try:
        return client.get(record_type=record_type, search={'name': f'{target}'})[0]
    except IndexError:
        return None

def is_updated(local_device, remote_device, user):
    """Returns True if the remote_device attributes are up-to-date
    with the local_device attributes. False otherwise.
    """
    u_dept = user.department
    l_owner = local_device['owner']
    r_owner = remote_device.owner
    r_dept = remote_device.department

    if r_owner is None or l_owner is None or u_dept is None:
        return False
    elif r_owner.get('name', '').lower() == l_owner.lower():
        if u_dept.get('name').lower() == r_dept.get('name').lower():
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
        #logger.debug('Device: %s - Owner: %s' % (local_device['name'], local_device['owner']))
        remote_device = fetch_resource(client, local_device, 'hardwares')
        user = fetch_resource(client, local_device, 'users')
        if user is None:
            user = User({'owner': {'name': None}, 'department': {'name': None}})
        if remote_device:
            if not is_updated(local_device, remote_device, user):
                update(client, local_device, remote_device, user)
