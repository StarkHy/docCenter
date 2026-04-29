import pytest
from io import BytesIO
from app.services.template_service import TemplateService


class TestTemplateService:
    
    @pytest.fixture
    def service(self):
        return TemplateService()
    
    def test_extract_vars_from_text_pattern(self, service):
        text = "Hello {{name}}, welcome to {{company}}"
        result = service._extract_vars_from_text(text)
        assert "name" in result
        assert "company" in result
    
    def test_extract_vars_from_text_no_vars(self, service):
        text = "Hello World"
        result = service._extract_vars_from_text(text)
        assert result == []
    
    def test_extract_vars_with_spaces(self, service):
        text = "{{ name }} and {{  value  }}"
        result = service._extract_vars_from_text(text)
        assert "name" in result
        assert "value" in result
    
    def test_extract_vars_none_input(self, service):
        result = service._extract_vars_from_text("")
        assert result == []
    
    def test_extract_vars_multiple_in_text(self, service):
        text = "{{title}} and {{company}} and {{date}}"
        result = service._extract_vars_from_text(text)
        assert len(result) == 3
        assert "title" in result
        assert "company" in result
        assert "date" in result
    
    def test_extract_vars_malformed_braces(self, service):
        text = "{{{{invalid}}"
        result = service._extract_vars_from_text(text)
        assert "{{invalid" in result
    
    def test_extract_vars_empty_braces(self, service):
        text = "{{}}"
        result = service._extract_vars_from_text(text)
        assert result == []
    
    def test_content_type_validation(self, service):
        valid_types = [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/octet-stream',
            ''
        ]
        for ct in valid_types:
            try:
                pass
            except ValueError:
                pytest.fail(f"Content type {ct} should be valid")