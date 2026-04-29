import pytest
from app.models import DataSource
from app.repositories.datasource_repository import DataSourceRepository


@pytest.mark.asyncio
async def test_get_by_id_returns_datasource(test_session):
    """Test that get_by_id returns the correct datasource"""
    datasource = DataSource(
        name="Test DataSource",
        type="json",
        config={"json_text": '{"key": "value"}'},
        status="active"
    )
    test_session.add(datasource)
    await test_session.commit()
    
    repo = DataSourceRepository(test_session)
    result = await repo.get_by_id(datasource.id)
    
    assert result is not None
    assert result.id == datasource.id
    assert result.name == "Test DataSource"
    assert result.type == "json"
    assert result.status == "active"


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_missing(test_session):
    """Test that get_by_id returns None for invalid ID"""
    repo = DataSourceRepository(test_session)
    result = await repo.get_by_id(9999)
    
    assert result is None


@pytest.mark.asyncio
async def test_get_all_returns_all_datasources(test_session):
    """Test that get_all returns list of datasources"""
    datasources = [
        DataSource(name="DataSource 1", type="json", config={}),
        DataSource(name="DataSource 2", type="api", config={}),
        DataSource(name="DataSource 3", type="form", config={}),
    ]
    for ds in datasources:
        test_session.add(ds)
    await test_session.commit()
    
    repo = DataSourceRepository(test_session)
    result = await repo.get_all()
    
    assert len(result) == 3
    assert result[0].name == "DataSource 1"
    assert result[1].type == "api"
    assert result[2].type == "form"


@pytest.mark.asyncio
async def test_add_creates_datasource(test_session):
    """Test that add creates and returns datasource with ID"""
    datasource = DataSource(
        name="New DataSource",
        type="json",
        config={"json_text": '{"new": "data"}'},
        status="inactive"
    )
    
    repo = DataSourceRepository(test_session)
    result = await repo.add(datasource)
    
    assert result is not None
    assert result.id is not None
    assert result.name == "New DataSource"
    assert result.type == "json"
    assert result.create_time is not None


@pytest.mark.asyncio
async def test_update_modifies_datasource(test_session):
    """Test that update modifies datasource"""
    datasource = DataSource(
        name="Original Name",
        type="json",
        config={"original": "config"}
    )
    test_session.add(datasource)
    await test_session.commit()
    
    datasource.name = "Updated Name"
    datasource.type = "api"
    datasource.status = "active"
    
    repo = DataSourceRepository(test_session)
    result = await repo.update(datasource)
    
    assert result.name == "Updated Name"
    assert result.type == "api"
    assert result.status == "active"


@pytest.mark.asyncio
async def test_delete_removes_datasource(test_session):
    """Test that delete returns True for existing, False for missing"""
    datasource = DataSource(
        name="To Delete",
        type="json",
        config={}
    )
    test_session.add(datasource)
    await test_session.commit()
    ds_id = datasource.id
    
    repo = DataSourceRepository(test_session)
    
    result = await repo.delete(ds_id)
    assert result is True
    
    result = await repo.delete(9999)
    assert result is False


@pytest.mark.asyncio
async def test_get_by_type_filters_datasources(test_session):
    """Test that get_by_type filters correctly"""
    datasources = [
        DataSource(name="JSON Source", type="json", config={}),
        DataSource(name="API Source", type="api", config={}),
        DataSource(name="Another JSON", type="json", config={}),
        DataSource(name="Form Source", type="form", config={}),
    ]
    for ds in datasources:
        test_session.add(ds)
    await test_session.commit()
    
    repo = DataSourceRepository(test_session)
    
    json_results = await repo.get_by_type("json")
    assert len(json_results) == 2
    assert all(ds.type == "json" for ds in json_results)
    
    api_results = await repo.get_by_type("api")
    assert len(api_results) == 1
    assert api_results[0].name == "API Source"
    
    form_results = await repo.get_by_type("form")
    assert len(form_results) == 1


@pytest.mark.asyncio
async def test_get_paginated_returns_datasources_and_count(test_session):
    """Test that pagination works correctly"""
    for i in range(12):
        ds = DataSource(
            name=f"DataSource {i}",
            type="json",
            config={}
        )
        test_session.add(ds)
    await test_session.commit()
    
    repo = DataSourceRepository(test_session)
    
    datasources, total = await repo.get_paginated(page=1, page_size=5)
    
    assert total == 12
    assert len(datasources) == 5
    assert datasources[0].name == "DataSource 0"
    
    datasources, total = await repo.get_paginated(page=3, page_size=5)
    
    assert len(datasources) == 2
    assert datasources[0].name == "DataSource 10"