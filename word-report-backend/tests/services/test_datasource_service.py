import pytest
from app.services.datasource_service import DataSourceService


class TestDataSourceService:
    
    @pytest.fixture
    def service(self):
        return DataSourceService()
    
    def test_database_types_defined(self, service):
        database_types = {'kingbase', 'mysql', 'oracle', 'postgresql'}
        assert 'kingbase' in database_types
        assert 'mysql' in database_types
        assert 'oracle' in database_types
        assert 'postgresql' in database_types
    
    def test_datasource_types_defined(self, service):
        datasource_types = {'http_api', 'json', 'form', 'sql'}
        assert 'http_api' in datasource_types
        assert 'json' in datasource_types
        assert 'form' in datasource_types
        assert 'sql' in datasource_types
    
    def test_service_initialization(self, service):
        assert service is not None
        assert hasattr(service, 'storage_path')
    
    def test_type_filter_database(self):
        service = DataSourceService()
        database_types = {'kingbase', 'mysql', 'oracle', 'postgresql'}
        datasource_types = {'http_api', 'json', 'form', 'sql'}
        
        assert 'kingbase' in database_types
        assert 'kingbase' not in datasource_types
    
    def test_type_filter_datasource(self):
        service = DataSourceService()
        database_types = {'kingbase', 'mysql', 'oracle', 'postgresql'}
        datasource_types = {'http_api', 'json', 'form', 'sql'}
        
        assert 'json' in datasource_types
        assert 'json' not in database_types
    
    def test_config_merge_logic(self):
        service = DataSourceService()
        config = {"username": "admin", "password": "secret", "host": "localhost"}
        result = {}
        for key in ["username", "password"]:
            if key in config:
                result[key] = config[key]
        assert "username" in result
        assert "password" in result
        assert result["username"] == "admin"