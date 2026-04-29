import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health endpoint"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ok", "healthy"]


@pytest.mark.asyncio
async def test_http_api_datasource_get_success():
    """Test HTTP API datasource with GET method - successful request"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Use a public API for testing (JSONPlaceholder)
        response = await client.post(
            "/api/datasources/test",
            json={
                "type": "http_api",
                "config": {
                    "url": "https://jsonplaceholder.typicode.com/posts/1",
                    "method": "GET",
                    "timeout": 10
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("status_code") == 200
        assert "data" in data


@pytest.mark.asyncio
async def test_http_api_datasource_post_success():
    """Test HTTP API datasource with POST method - successful request"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/datasources/test",
            json={
                "type": "http_api",
                "config": {
                    "url": "https://jsonplaceholder.typicode.com/posts",
                    "method": "POST",
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "title": "test",
                        "body": "test body",
                        "userId": 1
                    },
                    "timeout": 10
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("status_code") == 201
        assert "data" in data


@pytest.mark.asyncio
async def test_http_api_datasource_missing_url():
    """Test HTTP API datasource - missing URL should fail"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/datasources/test",
            json={
                "type": "http_api",
                "config": {
                    "url": "",
                    "method": "GET"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False
        assert "请配置接口地址" in data.get("message", "")


@pytest.mark.asyncio
async def test_http_api_datasource_with_headers():
    """Test HTTP API datasource with custom headers"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/datasources/test",
            json={
                "type": "http_api",
                "config": {
                    "url": "https://jsonplaceholder.typicode.com/headers",
                    "method": "GET",
                    "headers": {
                        "X-Custom-Header": "test-value"
                    },
                    "timeout": 10
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True


@pytest.mark.asyncio
async def test_http_api_datasource_with_params():
    """Test HTTP API datasource with URL parameters"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/datasources/test",
            json={
                "type": "http_api",
                "config": {
                    "url": "https://jsonplaceholder.typicode.com/posts",
                    "method": "GET",
                    "params": {
                        "userId": 1
                    },
                    "timeout": 10
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        # Should return posts with userId=1
        assert isinstance(data.get("data"), list)


@pytest.mark.asyncio
async def test_http_api_datasource_with_parameters_placeholder():
    """Test HTTP API datasource with parameters substitution"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/datasources/test",
            json={
                "type": "http_api",
                "config": {
                    "url": "https://jsonplaceholder.typicode.com/posts/:postId",
                    "method": "GET",
                    "parameters": [
                        {"name": "postId", "default": "1"}
                    ],
                    "timeout": 10
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True


@pytest.mark.asyncio
async def test_http_api_datasource_invalid_url():
    """Test HTTP API datasource with invalid URL"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/datasources/test",
            json={
                "type": "http_api",
                "config": {
                    "url": "https://invalid-domain-that-does-not-exist-12345.com/api",
                    "method": "GET",
                    "timeout": 5
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False
        assert "请求失败" in data.get("message", "") or "Failed to establish a new connection" in data.get("message", "")


@pytest.mark.asyncio
async def test_json_datasource_success():
    """Test JSON datasource - successful parsing"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/datasources/test",
            json={
                "type": "json",
                "config": {
                    "json_text": "{\"name\": \"test\", \"value\": 123}"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("data") == {"name": "test", "value": 123}


@pytest.mark.asyncio
async def test_json_datasource_invalid():
    """Test JSON datasource - invalid JSON format"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/datasources/test",
            json={
                "type": "json",
                "config": {
                    "json_text": "{invalid json}"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False
        assert "JSON格式错误" in data.get("message", "")


@pytest.mark.asyncio
async def test_form_datasource_success():
    """Test form datasource - valid fields"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/datasources/test",
            json={
                "type": "form",
                "config": {
                    "fields": {
                        "field1": "value1",
                        "field2": "value2"
                    }
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("data") == {"field1": "value1", "field2": "value2"}


@pytest.mark.asyncio
async def test_unsupported_datasource_type():
    """Test unsupported datasource type"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/datasources/test",
            json={
                "type": "unsupported_type",
                "config": {}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False
        assert "不支持的数据源类型" in data.get("message", "") or "不支持" in data.get("message", "")