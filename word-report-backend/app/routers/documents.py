from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import get_db
from app.core.dependencies import DependencyContainer
from app.services.document_generation_service import DocumentGenerationService
from app.services.datasource_service import data_source_service
from app.services.mapping_service import mapping_service

router = APIRouter()


class DocumentGenerateByMappingRequest(BaseModel):
    mapping_id: int
    output_name: Optional[str] = None
    params: Optional[dict] = None


class DocumentResponse(BaseModel):
    id: int
    name: str
    template: str
    datasource: str
    status: str
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    file_size: Optional[str] = None
    create_time: str


class HistoryItemResponse(BaseModel):
    id: int
    name: str
    template: str
    datasource: str
    status: str
    file_size: str
    create_time: str


def get_document_service(session: AsyncSession = Depends(get_db)) -> DocumentGenerationService:
    return DependencyContainer.get_document_generation_service(session)


@router.post("/generate", response_model=DocumentResponse)
async def generate_document(
    request: DocumentGenerateByMappingRequest,
    session: AsyncSession = Depends(get_db),
    service: DocumentGenerationService = Depends(get_document_service)
):
    try:
        result = await service.generate_document(
            mapping_id=request.mapping_id,
            output_name=request.output_name,
            runtime_params=request.params or {},
            session=session
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败：{str(e)}")


@router.get("/mapping/{mapping_id}/params")
async def get_mapping_params(
    mapping_id: int,
    session: AsyncSession = Depends(get_db)
):
    mapping = await mapping_service.get_mapping(mapping_id, session)
    if not mapping:
        raise HTTPException(status_code=404, detail="映射配置不存在")
    
    datasource_ids = mapping.get("datasource_ids", [])
    params = await data_source_service.get_datasource_params(datasource_ids, session)
    
    return {"params": params}


@router.get("/history", response_model=dict)
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
    service: DocumentGenerationService = Depends(get_document_service)
):
    return await service.get_history(page, page_size, search, status, session)


@router.get("/history/{history_id}", response_model=HistoryItemResponse)
async def get_history_item(
    history_id: int,
    session: AsyncSession = Depends(get_db),
    service: DocumentGenerationService = Depends(get_document_service)
):
    item = await service.get_history_item(history_id, session)
    if not item:
        raise HTTPException(status_code=404, detail="记录不存在")
    return item


@router.delete("/history/{history_id}")
async def delete_history(
    history_id: int,
    session: AsyncSession = Depends(get_db),
    service: DocumentGenerationService = Depends(get_document_service)
):
    success = await service.delete_history_item(history_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"message": "删除成功"}


@router.post("/history/{history_id}/regenerate", response_model=DocumentResponse)
async def regenerate_document(
    history_id: int,
    session: AsyncSession = Depends(get_db),
    service: DocumentGenerationService = Depends(get_document_service)
):
    try:
        result = await service.regenerate_document(history_id, session)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新生成失败：{str(e)}")


@router.get("/{doc_id}/download")
async def download_document(
    doc_id: int,
    session: AsyncSession = Depends(get_db),
    service: DocumentGenerationService = Depends(get_document_service)
):
    file_path = await service.download_document(doc_id, session)
    if not file_path:
        raise HTTPException(status_code=404, detail="文档不存在")

    from fastapi.responses import FileResponse
    history_item = await service.get_history_item(doc_id, session)
    filename = history_item.get("name", f"document_{doc_id}.docx") if history_item else f"document_{doc_id}.docx"

    return FileResponse(
        file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@router.get("/preview")
async def preview_data(
    data_source_id: int,
    sql: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    from app.services.datasource_service import data_source_service

    try:
        datasource = await data_source_service.get_datasource(data_source_id, session)
        if not datasource:
            raise HTTPException(status_code=404, detail="数据源不存在")

        ds_type = datasource.get("type")
        config = datasource.get("config", {})

        if ds_type == "http_api":
            import requests
            method = config.get("method", "GET").upper()
            url = config.get("url", "")
            headers = config.get("headers", {})
            params = config.get("params", {})
            body = config.get("body", {})
            timeout = config.get("timeout", 10)

            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            else:
                response = requests.post(url, headers=headers, params=params, json=body, timeout=timeout)

            data = response.json()
            if isinstance(data, dict):
                return {"data": data}
            elif isinstance(data, list):
                return {"columns": list(data[0].keys()) if data else [], "data": data}
            return {"data": data}

        elif ds_type == "json":
            import json
            json_text = config.get("json_text", "")
            data = json.loads(json_text) if json_text else {}
            if isinstance(data, dict):
                return {"data": data}
            elif isinstance(data, list):
                return {"columns": list(data[0].keys()) if data else [], "data": data}
            return {"data": data}

        elif ds_type == "form":
            fields = config.get("fields", {})
            return {"data": fields}

        elif ds_type in ("postgresql", "mysql", "kingbase", "oracle"):
            if sql:
                config["test_sql"] = sql
            result = await data_source_service.test_datasource({"type": ds_type, "config": config}, session)
            if result.get("success"):
                data = result.get("data", {})
                return {"columns": data.get("columns", []), "data": data.get("rows", [])}
            return {"error": result.get("message", "查询失败")}

        elif ds_type == "sql":
            db_id = config.get("database_id")
            if not db_id:
                return {"error": "请先选择数据库"}
            sql_query = sql or config.get("test_sql") or config.get("sql", "")
            if not sql_query:
                return {"error": "请配置 SQL 查询语句"}
            result = await data_source_service.test_datasource({
                "type": "sql",
                "config": {**config, "test_sql": sql_query}
            }, session)
            if result.get("success"):
                data = result.get("data", {})
                return {"columns": data.get("columns", []), "data": data.get("rows", [])}
            return {"error": result.get("message", "查询失败")}

        raise HTTPException(status_code=400, detail=f"不支持的数据源类型：{ds_type}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"预览失败：{str(e)}")
