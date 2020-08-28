import pytest
import os
import samsync
from samsync import load_json, fetch_resource, is_updated, _build_payload, update
from samanage3 import Hardware, User


@pytest.mark.usefixtures('create_sample_data')
class TestSamSync:
    def test_load_json_data(self, create_sample_data):
        """samsync.load_json should return a json object"""
        # GIVEN a sample configuration file
        # WHEN it is loaded
        # THEN there should be three items, with specific attributes
        self.json_data = load_json(create_sample_data)

        assert len(self.json_data) == 3
        assert self.json_data[0] == {'name': 'PC01', 'description': 'John Smith'}
        assert self.json_data[1] == {'name': 'PC02', 'description': 'Tom Jones'}
        assert self.json_data[2] == {'name': 'PC03', 'description': None}
   
    def test_fetch_resource_hardware(self, client):
        """Should invoke client.get() with record_type == hardwares"""
        # GIVEN a mock client object
        # WHEN fetch_resource is called
        # THEN assert  client.get() is called with specific arguments
        local_device = {'name': 'PC01'}
        resource = fetch_resource(client, local_device, 'hardwares')
        samsync.Samanage.get.assert_called_with(record_type='hardwares', 
                                                search={'name': 'PC01'})

    def test_fetch_resource_user(self, client):
        """Should invoke client.get() with record_type == users"""
        # GIVEN a mock client object
        # WHEN fetch_resource is called
        # THEN assert  client.get() is called with specific arguments
        local_device = {'owner': 'Tom Jones'}
        resource = fetch_resource(client, local_device, 'users')
        samsync.Samanage.get.assert_called_with(record_type='users', 
                                                search={'name': 'Tom Jones'})

    def test_fetch_hardware_returns_none_when_index_error_occurs(self, client, mocker):
        """Should return None when IndexError is encountered"""
        # GIVEN a mock client object
        # WHEN fetch_resource is called and an IndexError occurs
        # THEN fetch_resource returns None
        mocker.patch.object(samsync.Samanage, 'get', return_value=[])
        local_device = {'name': 'PC01'}
        resource = fetch_resource(client, local_device, 'hardwares')

        assert resource is None
    
    device_test_case = [
        {
            'local_device': {'name': 'PC01', 'owner': 'John Smith'},
            'remote_device': {'owner': {'name': 'John Smith'}},
            'is_updated': True
        },
        {
            'local_device': {'name': 'PC01', 'owner': 'John Smith'},
            'remote_device': {'owner': {'name': 'Steve Jones'}},
            'is_updated': False
        },
        {
            'local_device': {'name': 'PC01', 'owner': None},
            'remote_device': {'owner': {'name': 'Steve Jones'}},
            'is_updated': False
        },
        {
            'local_device': {'name': 'PC01', 'owner': 'John Smith'},
            'remote_device': {'owner': None},
            'is_updated': False
        }
        
    ]
    @pytest.mark.parametrize('case', device_test_case)
    def test_is_updated(self, case):
        """Should return True or False"""
        # GIVEN mock local and remote device objects
        # WHEN remote_device needs updating
        # THEN return False, otherwise return True
        remote_device = Hardware(case['remote_device'])
        local_device = case['local_device']
        assert is_updated(local_device, remote_device) is case['is_updated']

    build_payload_test_cases = [
        {'user': {'email': 'testuser@email.com'}},
        {'user': {'email': 'johnkerry@gmail.com'}},
        {'user': {'email': 'jmokey@hdnet.com'}},
    ]
    @pytest.mark.parametrize('case', build_payload_test_cases)
    def test_build_payload(self, case):
        """Should build a data structure representing update payload"""
        # GIVEN a few test cases
        # WHEN input a user object retrieved from samanage
        # THEN return a payload data structure that will be used to update
        # the resouce via rest API
        user = User(case['user'])
        expected_payload = {'owner': {'email': f'{user.email}'}}
        actual_payload = _build_payload(user)
        
        assert expected_payload == actual_payload

    def test_build_payload_when_user_is_none(self):
        user = None
        expected_payload = {'owner': None}
        actual_payload = _build_payload()

        assert expected_payload == actual_payload
    
    def test_update(self, client, mocker):
        """Should call client.post"""
        # GIVEN a mock client and a mock user resource object
        # WHEN invoking update()
        # THEN client.put() is invoked with specific parameters
        payload = {'owner': {'email': 'mtorres@email.com'}}
        local_device = {'name': 'PC01', 'owner': 'Michael Torres'}
        remote_device = Hardware({
            'name': 'PC01', 
            'id': 11, 
            'owner': {
                'name': 'John Davies'
            }
        })

        return_value = User({'name': 'Michael Torres', 'email': 'mtorres@email.com'})
        mocker.patch.object(samsync, 'fetch_resource', return_value=return_value)
        
        update(client, local_device, remote_device)
        samsync.Samanage.put.assert_called_with('hardwares', 
                                                payload,
                                                remote_device.id)

    def test_update_when_initial_user_lookup_returns_none(self, client, mocker):
        """fetch_resource should return a spare user to assign to the hardware"""
        pass
