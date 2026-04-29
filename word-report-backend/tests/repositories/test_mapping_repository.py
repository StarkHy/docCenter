import pytest
from app.models import Mapping, Template, DataSource, MappingDataSource, MappingChart
from app.repositories.mapping_repository import MappingRepository


@pytest.mark.asyncio
async def test_get_by_id_returns_mapping(test_session):
    """Test that get_by_id returns the correct mapping"""
    template = Template(name="Test Template", category="Test", file_name="test.docx")
    test_session.add(template)
    await test_session.commit()
    
    mapping = Mapping(
        name="Test Mapping",
        template_id=template.id
    )
    test_session.add(mapping)
    await test_session.commit()
    
    repo = MappingRepository(test_session)
    result = await repo.get_by_id(mapping.id)
    
    assert result is not None
    assert result.id == mapping.id
    assert result.name == "Test Mapping"
    assert result.template_id == template.id


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_missing(test_session):
    """Test that get_by_id returns None for invalid ID"""
    repo = MappingRepository(test_session)
    result = await repo.get_by_id(9999)
    
    assert result is None


@pytest.mark.asyncio
async def test_get_all_returns_all_mappings(test_session):
    """Test that get_all returns list of mappings"""
    template = Template(name="Template", category="Test", file_name="test.docx")
    test_session.add(template)
    await test_session.commit()
    
    mappings = [
        Mapping(name="Mapping 1", template_id=template.id),
        Mapping(name="Mapping 2", template_id=template.id),
        Mapping(name="Mapping 3", template_id=template.id),
    ]
    for m in mappings:
        test_session.add(m)
    await test_session.commit()
    
    repo = MappingRepository(test_session)
    result = await repo.get_all()
    
    assert len(result) == 3
    assert result[0].name == "Mapping 1"
    assert result[1].name == "Mapping 2"


@pytest.mark.asyncio
async def test_add_creates_mapping(test_session):
    """Test that add creates and returns mapping"""
    template = Template(name="Template", category="Test", file_name="test.docx")
    test_session.add(template)
    await test_session.commit()
    
    mapping = Mapping(
        name="New Mapping",
        template_id=template.id
    )
    
    repo = MappingRepository(test_session)
    result = await repo.add(mapping)
    
    assert result is not None
    assert result.id is not None
    assert result.name == "New Mapping"
    assert result.create_time is not None


@pytest.mark.asyncio
async def test_update_modifies_mapping(test_session):
    """Test that update modifies mapping"""
    template = Template(name="Template", category="Test", file_name="test.docx")
    test_session.add(template)
    await test_session.commit()
    
    mapping = Mapping(
        name="Original Name",
        template_id=template.id
    )
    test_session.add(mapping)
    await test_session.commit()
    
    mapping.name = "Updated Name"
    
    repo = MappingRepository(test_session)
    result = await repo.update(mapping)
    
    assert result.name == "Updated Name"


@pytest.mark.asyncio
async def test_delete_removes_mapping(test_session):
    """Test that delete returns True for existing, False for missing"""
    template = Template(name="Template", category="Test", file_name="test.docx")
    test_session.add(template)
    await test_session.commit()
    
    mapping = Mapping(
        name="To Delete",
        template_id=template.id
    )
    test_session.add(mapping)
    await test_session.commit()
    mapping_id = mapping.id
    
    repo = MappingRepository(test_session)
    
    result = await repo.delete(mapping_id)
    assert result is True
    
    result = await repo.delete(9999)
    assert result is False


@pytest.mark.asyncio
async def test_get_by_template_filters_mappings(test_session):
    """Test that get_by_template filters correctly"""
    template1 = Template(name="Template 1", category="Test", file_name="test1.docx")
    template2 = Template(name="Template 2", category="Test", file_name="test2.docx")
    test_session.add(template1)
    test_session.add(template2)
    await test_session.commit()
    
    mappings = [
        Mapping(name="Mapping 1", template_id=template1.id),
        Mapping(name="Mapping 2", template_id=template1.id),
        Mapping(name="Mapping 3", template_id=template2.id),
    ]
    for m in mappings:
        test_session.add(m)
    await test_session.commit()
    
    repo = MappingRepository(test_session)
    
    results = await repo.get_by_template(template1.id)
    assert len(results) == 2
    assert all(m.template_id == template1.id for m in results)
    
    results = await repo.get_by_template(template2.id)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_get_paginated_returns_mappings_and_count(test_session):
    """Test that pagination works correctly"""
    template = Template(name="Template", category="Test", file_name="test.docx")
    test_session.add(template)
    await test_session.commit()
    
    for i in range(18):
        mapping = Mapping(
            name=f"Mapping {i}",
            template_id=template.id
        )
        test_session.add(mapping)
    await test_session.commit()
    
    repo = MappingRepository(test_session)
    
    mappings, total = await repo.get_paginated(page=1, page_size=10)
    
    assert total == 18
    assert len(mappings) == 10
    
    mappings, total = await repo.get_paginated(page=2, page_size=10)
    
    assert len(mappings) == 8
    assert mappings[0].name == "Mapping 10"


@pytest.mark.asyncio
async def test_add_datasource_link_creates_link(test_session):
    """Test that add_datasource_link creates association"""
    template = Template(name="Template", category="Test", file_name="test.docx")
    test_session.add(template)
    
    datasource1 = DataSource(name="DS 1", type="json", config={})
    datasource2 = DataSource(name="DS 2", type="api", config={})
    test_session.add(datasource1)
    test_session.add(datasource2)
    await test_session.commit()
    
    mapping = Mapping(name="Mapping", template_id=template.id)
    test_session.add(mapping)
    await test_session.commit()
    
    repo = MappingRepository(test_session)
    
    link1 = await repo.add_datasource_link(mapping.id, datasource1.id, order=0)
    link2 = await repo.add_datasource_link(mapping.id, datasource2.id, order=1)
    
    assert link1.mapping_id == mapping.id
    assert link1.datasource_id == datasource1.id
    assert link1.order == 0
    
    assert link2.datasource_id == datasource2.id
    assert link2.order == 1


@pytest.mark.asyncio
async def test_add_chart_config_creates_chart(test_session):
    """Test that add_chart_config creates chart config"""
    template = Template(name="Template", category="Test", file_name="test.docx")
    test_session.add(template)
    await test_session.commit()
    
    mapping = Mapping(name="Mapping", template_id=template.id)
    test_session.add(mapping)
    await test_session.commit()
    
    chart_data = {
        "id": "revenue_chart",
        "type": "bar",
        "title": "Revenue Chart",
        "x_data": ["Q1", "Q2", "Q3"],
        "y_data": [100, 200, 300]
    }
    
    repo = MappingRepository(test_session)
    result = await repo.add_chart_config(mapping.id, chart_data)
    
    assert result.mapping_id == mapping.id
    assert result.chart_id == "revenue_chart"
    assert result.chart_type == "bar"
    assert result.chart_title == "Revenue Chart"