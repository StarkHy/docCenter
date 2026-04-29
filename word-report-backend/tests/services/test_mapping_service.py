import pytest
from datetime import datetime
from app.services.mapping_service import MappingService


class TestMappingService:
    
    @pytest.fixture
    def service(self):
        return MappingService()
    
    def test_service_initialization(self, service):
        assert service is not None
        assert hasattr(service, 'storage_path')
    
    def test_mapping_to_dict_format(self, service):
        class MockMapping:
            id = 1
            name = "Test Mapping"
            template_id = 10
            datasource_links = [type('obj', (object,), {'datasource_id': 1})()]
            mappings = [{"source": "field1", "target": "var1"}]
            chart_configs = [type('obj', (object,), {'chart_config': {'id': 'chart1'}})()]
            create_time = datetime(2024, 1, 1, 12, 0, 0)
        
        result = service._mapping_to_dict(MockMapping())
        
        assert result["id"] == 1
        assert result["name"] == "Test Mapping"
        assert result["template_id"] == 10
        assert result["datasource_ids"] == [1]
        assert result["mappings"] == [{"source": "field1", "target": "var1"}]
        assert result["charts"] == [{"id": "chart1"}]
    
    def test_mapping_to_dict_no_links(self, service):
        class MockMapping:
            id = 1
            name = "Test"
            template_id = 10
            datasource_links = []
            mappings = []
            chart_configs = []
            create_time = None
        
        result = service._mapping_to_dict(MockMapping())
        
        assert result["datasource_ids"] == []
        assert result["mappings"] == []
        assert result["charts"] == []
    
    def test_mapping_to_dict_no_create_time(self, service):
        class MockMapping:
            id = 1
            name = "Test"
            template_id = 10
            datasource_links = []
            mappings = []
            chart_configs = []
            create_time = None
        
        result = service._mapping_to_dict(MockMapping())
        
        assert result["create_time"] == ""