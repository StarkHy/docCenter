import pytest
from app.models import Template


@pytest.mark.asyncio
async def test_create_template(test_session):
    template = Template(
        id=1,
        name="Test Template",
        category="test",
        file_name="test.docx",
        file_path="/test/path.docx",
        file_size=1024,
        variables=["var1", "var2"]
    )
    test_session.add(template)
    await test_session.commit()
    await test_session.refresh(template)
    
    assert template.id == 1
    assert template.name == "Test Template"
    assert template.variables == ["var1", "var2"]


@pytest.mark.asyncio
async def test_get_template(test_session):
    template = Template(
        id=1,
        name="Test Template",
        category="test",
        file_name="test.docx",
        file_path="/test/path.docx",
        file_size=1024
    )
    test_session.add(template)
    await test_session.commit()
    
    from sqlalchemy import select
    result = await test_session.execute(select(Template).where(Template.id == 1))
    found = result.scalar_one_or_none()
    
    assert found is not None
    assert found.name == "Test Template"


@pytest.mark.asyncio
async def test_delete_template(test_session):
    template = Template(
        id=1,
        name="Test Template",
        category="test",
        file_name="test.docx",
        file_path="/test/path.docx",
        file_size=1024
    )
    test_session.add(template)
    await test_session.commit()
    
    await test_session.delete(template)
    await test_session.commit()
    
    from sqlalchemy import select
    result = await test_session.execute(select(Template).where(Template.id == 1))
    found = result.scalar_one_or_none()
    
    assert found is None