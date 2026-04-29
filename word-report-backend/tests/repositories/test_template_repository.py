import pytest
from unittest.mock import AsyncMock
from app.models import Template
from app.repositories.template_repository import TemplateRepository


@pytest.mark.asyncio
async def test_get_by_id_returns_template(test_session):
    """Test that get_by_id returns the correct template"""
    # Create a test template
    template = Template(
        name="Test Template",
        category="Test Category",
        file_name="test.docx",
        file_path="/path/to/test.docx",
        file_size=1024,
        variables=["var1", "var2"]
    )
    test_session.add(template)
    await test_session.commit()
    
    # Test the repository
    repo = TemplateRepository(test_session)
    result = await repo.get_by_id(template.id)
    
    assert result is not None
    assert result.id == template.id
    assert result.name == "Test Template"
    assert result.category == "Test Category"
    assert result.file_name == "test.docx"


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_missing(test_session):
    """Test that get_by_id returns None for invalid ID"""
    repo = TemplateRepository(test_session)
    result = await repo.get_by_id(9999)
    
    assert result is None


@pytest.mark.asyncio
async def test_get_all_returns_all_templates(test_session):
    """Test that get_all returns list of templates"""
    # Create multiple test templates
    templates = [
        Template(name="Template 1", category="Category 1", file_name="file1.docx"),
        Template(name="Template 2", category="Category 2", file_name="file2.docx"),
        Template(name="Template 3", category="Category 3", file_name="file3.docx"),
    ]
    for template in templates:
        test_session.add(template)
    await test_session.commit()
    
    # Test the repository
    repo = TemplateRepository(test_session)
    result = await repo.get_all()
    
    assert len(result) == 3
    assert result[0].name == "Template 1"
    assert result[1].name == "Template 2"
    assert result[2].name == "Template 3"


@pytest.mark.asyncio
async def test_add_creates_template(test_session):
    """Test that add creates and returns template with ID"""
    template = Template(
        name="New Template",
        category="New Category",
        file_name="new.docx",
        file_path="/path/to/new.docx",
        file_size=2048,
        variables=["new_var"]
    )
    
    repo = TemplateRepository(test_session)
    result = await repo.add(template)
    
    assert result is not None
    assert result.id is not None
    assert result.name == "New Template"
    assert result.create_time is not None


@pytest.mark.asyncio
async def test_update_modifies_template(test_session):
    """Test that update modifies template"""
    # Create a template
    template = Template(
        name="Original Name",
        category="Original Category",
        file_name="original.docx"
    )
    test_session.add(template)
    await test_session.commit()
    
    # Update the template
    template.name = "Updated Name"
    template.category = "Updated Category"
    
    repo = TemplateRepository(test_session)
    result = await repo.update(template)
    
    assert result.name == "Updated Name"
    assert result.category == "Updated Category"


@pytest.mark.asyncio
async def test_delete_removes_template(test_session):
    """Test that delete returns True for existing, False for missing"""
    # Create a template
    template = Template(
        name="To Delete",
        category="Test",
        file_name="delete.docx"
    )
    test_session.add(template)
    await test_session.commit()
    template_id = template.id
    
    repo = TemplateRepository(test_session)
    
    # Test deleting existing template
    result = await repo.delete(template_id)
    assert result is True
    
    # Test deleting non-existing template
    result = await repo.delete(9999)
    assert result is False


@pytest.mark.asyncio
async def test_get_paginated_returns_templates_and_count(test_session):
    """Test that pagination works correctly"""
    # Create multiple templates
    for i in range(15):
        template = Template(
            name=f"Template {i}",
            category="Category",
            file_name=f"file{i}.docx"
        )
        test_session.add(template)
    await test_session.commit()
    
    repo = TemplateRepository(test_session)
    
    # Get first page
    templates, total = await repo.get_paginated(page=1, page_size=10)
    
    assert total == 15
    assert len(templates) == 10
    assert templates[0].name == "Template 0"
    
    # Get second page
    templates, total = await repo.get_paginated(page=2, page_size=10)
    
    assert len(templates) == 5
    assert templates[0].name == "Template 10"


@pytest.mark.asyncio
async def test_get_by_name_finds_template(test_session):
    """Test that get_by_name works correctly"""
    # Create templates with specific names
    templates = [
        Template(name="Unique Template Name", category="Cat1", file_name="file1.docx"),
        Template(name="Another Template", category="Cat2", file_name="file2.docx"),
    ]
    for template in templates:
        test_session.add(template)
    await test_session.commit()
    
    repo = TemplateRepository(test_session)
    
    # Test finding existing template
    result = await repo.get_by_name("Unique Template Name")
    assert result is not None
    assert result.name == "Unique Template Name"
    
    # Test finding non-existing template
    result = await repo.get_by_name("Non-existent Template")
    assert result is None