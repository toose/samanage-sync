import pytest
import os
from samsync import load_json, fetch_hardware


@pytest.mark.usefixtures('create_sample_data', 'client')
class TestSamSync:
    def test_load_json_data(self, create_sample_data):
        """samsync.load_json should return a json object"""
        # GIVEN a sample configuration file
        # WHEN it is loaded
        # THEN there should be three items, with specific attributes
        self.json_data = load_json(create_sample_data)

        assert len(self.json_data) == 3
        assert self.json_data[0]['name'] == 'PC01'
        assert self.json_data[0]['description'] == 'John Smith'
        assert self.json_data[1]['name'] == 'PC02'
        assert self.json_data[1]['description'] == 'Tom Jones'
        assert self.json_data[2]['name'] == 'PC03'
        assert self.json_data[2]['description'] is None
   
    def test_fetch_hardware(self):
        hardware = fetch_hardware(self.client)
