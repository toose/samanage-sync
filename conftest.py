import pytest
import json
import shutil
import samsync
from samanage3 import User

INVENTORY_DATA = [
    {
        "name": "PC01",
        "owner": "John Smith"
    },
    {
        "name": "PC02",
        "owner": "Tom Jones"
    },
    {
        "name": "PC03",
        "owner": None
    }
]

@pytest.fixture(scope="class")
def sample_input_data(tmpdir_factory):
    """Creates sample json data and saves to a temporary location 
    on disk
    """ 
    config_dir = tmpdir_factory.mktemp('samsync_tests')
    config_file = config_dir.join('config.json')
    config_file.write(json.dumps(INVENTORY_DATA))
    
    yield config_file

    shutil.rmtree(config_dir)

@pytest.fixture(scope="class")
def sample_output_data(sample_input_data):
    return samsync.load_json(sample_input_data)

@pytest.fixture()
def client(mocker):
    """Returns a mock Samanage api object"""
    client_obj = mocker.patch('samsync.Samanage')
    return client_obj

@pytest.fixture()
def mock_user():
    """Returns a mock Samanage api user object"""
    return User({
        'name': 'Michael Torres', 
        'email': 'mtorres@email.com',
        'department': {'name': 'Information Technology'}
    })

@pytest.fixture()
def mock_user_no_department():
    """Returns a mock Samanage api user object"""
    return User({
        'name': 'Michael Torres', 
        'email': 'mtorres@email.com',
        'department': None
    })