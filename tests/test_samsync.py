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
        {   # Owner and department are updated
            'local_device': {'name': 'PC01', 'owner': 'John Smith'},
            'remote_device': {
                'owner': {'name': 'John Smith'},
                'department': {'name': 'Information Technology'}
            },
            'is_updated': True
        },
        {   # Device department needs updating
            'local_device': {'name': 'PC01', 'owner': 'John Smith'},
            'remote_device': {
                'owner': {'name': 'John Smith'},
                'department': {'name': 'Accounting'}
            },
            'is_updated': False
        },
        {   # Owner and device department needs updating
            'local_device': {'name': 'PC01', 'owner': 'John Smith'},
            'remote_device': {
                'owner': {'name': 'Steve Jones'},
                'department': {'name': 'Research and Development'}
            },
            'is_updated': False
        },
        {   # Local owner is None
            'local_device': {'name': 'PC01', 'owner': None},
            'remote_device': {
                'owner': {'name': 'Steve Jones'},
                'department': {'name': 'Accounting'}
            },
            'is_updated': False
        },
        {   # Remote device owner is None
            'local_device': {'name': 'PC01', 'owner': 'John Smith'},
            'remote_device': {
                'owner': None,
                'department': {'name': 'Information Technology'}
            },
            'is_updated': False
        }
        
    ]
    @pytest.mark.parametrize('case', device_test_case)
    def test_is_updated(self, case, mock_user):
        """Should return True or False"""
        # GIVEN mock local and remote device objects
        # WHEN remote_device needs updating
        # THEN return False, otherwise return True
        remote_device = Hardware(case['remote_device'])
        local_device = case['local_device']
        assert is_updated(local_device, remote_device, mock_user) is case['is_updated']

    def test_is_updated_when_user_is_returns_none(self):
        user = User({'owner': {'name': ''}, 'department': {'name': ''}})
        local_device = {'name': 'PC01', 'owner': 'John Smith'}
        remote_device = Hardware({
            'owner': {'name': 'John Smith'},
            'department': {'name': 'Information Technology'}
        })

        assert is_updated(local_device, remote_device, user) is False


    build_payload_test_cases = [
        {
            'user': {
                'email': 'testuser@email.com',
                'department': {'name': 'Research and Development'}
            }
        },
        {
            'user': {
                'email': 'johnkerry@gmail.com',
                'department': {'name': 'Information technology'}
            }
        },
        {
            'user': {
                'email': 'jmokey@hdnet.com',
                'department': {'name': 'Finance and Accounting'}
            }
        },
        {
            'user': {
                'email': 'testuser@email.com',
                'department': None
            }
        }
    ]
    @pytest.mark.parametrize('case', build_payload_test_cases)
    def test_build_payload(self, case):
        """Should build a data structure representing update payload"""
        # GIVEN a few test cases
        # WHEN input a user object retrieved from samanage
        # THEN return a payload data structure that will be used to update
        # the resouce via rest API
        user = User(case['user'])
        actual_payload = _build_payload(user)
        expected_payload = {
            'owner': {'email': f'{user.email}'},
            'department': {'name': '%s' % user.department['name']}
            }
        
        assert expected_payload == actual_payload
    
    def test_update(self, client, mocker, mock_user):
        """Should call client.post"""
        # GIVEN a mock client and a mock user resource object
        # WHEN invoking update()
        # THEN client.put() is invoked with specific parameters
        payload = {
            'owner': {'email': 'mtorres@email.com'},
            'department': {'name': 'Information Technology'}
        }
        local_device = {'name': 'PC01', 'owner': 'Michael Torres'}
        remote_device = Hardware({
            'name': 'PC01', 
            'id': 11, 
            'owner': {
                'name': 'John Davies'
            }
        })

        update(client, local_device, remote_device, mock_user)
        samsync.Samanage.put.assert_called_with('hardwares', 
                                                payload,
                                                remote_device.id)
                                                
