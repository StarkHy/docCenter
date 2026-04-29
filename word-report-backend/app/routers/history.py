from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import get_db
from app.core.dependencies import DependencyContainer
from app.services.document_generation_service import DocumentGenerationService

router = APIRouter()


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


@router.get("/", response_model=dict)
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
    service: DocumentGenerationService = Depends(get_document_service)
):
    return await service.get_history(page, page_size, search, status, session)


@router.get("/{history_id}", response_model=HistoryItemResponse)
async def get_history_item(
    history_id: int,
    session: AsyncSession = Depends(get_db),
    service: DocumentGenerationService = Depends(get_document_service)
):
    item = await service.get_history_item(history_id, session)
    if not item:
        raise HTTPException(status_code=404, detail="记录不存在")
    return item


@router.delete("/{history_id}")
async def delete_history(
    history_id: int,
    session: AsyncSession = Depends(get_db),
    service: DocumentGenerationService = Depends(get_document_service)
):
    success = await service.delete_history_item(history_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"message": "删除成功"}


@router.post("/{history_id}/regenerate")
async def regenerate_document(
    history_id: int,
    session: AsyncSession = Depends(get_db),
    service: DocumentGenerationService = Depends(get_document_service)
):
    try:
        result = await service.regenerate_document(history_id, session)
        return {"message": "重新生成成功", "new_id": result.get("id")}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新生成失败：{str(e)}")
