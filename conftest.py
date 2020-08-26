import pytest
import json
import shutil
import samsync


@pytest.fixture(scope="class")
def create_sample_data(tmpdir_factory):
    """Creates sample json data and saves to a temporary location on disk""" 
    inventory_data = [
        {
            "name": "PC01",
            "description": "John Smith"
        },
        {
            "name": "PC02",
            "description": "Tom Jones"
        },
        {
            "name": "PC03",
            "description": None
        }
    ]

    config_dir = tmpdir_factory.mktemp('samsync_tests')
    config_file = config_dir.join('config.json')
    config_file.write(json.dumps(inventory_data))
    
    yield config_file

    shutil.rmtree(config_dir)


@pytest.fixture()
def client(mocker):
    """Returns a mock Samanage api object"""
    client_obj = mocker.patch('samsync.Samanage')
    return client_obj
