from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import get_db

router = APIRouter()


class MappingCreate(BaseModel):
    name: str
    template_id: int
    datasource_ids: List[int] = []
    mappings: List[Dict[str, Any]] = []
    charts: List[Dict[str, Any]] = []


class MappingUpdate(BaseModel):
    name: Optional[str] = None
    template_id: Optional[int] = None
    datasource_ids: Optional[List[int]] = None
    mappings: Optional[List[Dict[str, Any]]] = None
    charts: Optional[List[Dict[str, Any]]] = None


from app.services.mapping_service import mapping_service


@router.get("/")
async def get_mappings(
    template_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db)
):
    if template_id:
        return await mapping_service.get_mappings_by_template(template_id, session)
    return await mapping_service.get_mappings_paginated(page, page_size, session)


@router.get("/{mapping_id}")
async def get_mapping(mapping_id: int, session: AsyncSession = Depends(get_db)):
    mapping = await mapping_service.get_mapping(mapping_id, session)
    if not mapping:
        raise HTTPException(status_code=404, detail="映射配置不存在")
    return mapping


@router.post("/")
async def create_mapping(data: MappingCreate, session: AsyncSession = Depends(get_db)):
    try:
        return await mapping_service.create_mapping(data.model_dump(), session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{mapping_id}")
async def update_mapping(mapping_id: int, data: MappingUpdate, session: AsyncSession = Depends(get_db)):
    mapping = await mapping_service.update_mapping(mapping_id, data.model_dump(exclude_unset=True), session)
    if not mapping:
        raise HTTPException(status_code=404, detail="映射配置不存在")
    return mapping


@router.delete("/{mapping_id}")
async def delete_mapping(mapping_id: int, session: AsyncSession = Depends(get_db)):
    success = await mapping_service.delete_mapping(mapping_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="映射配置不存在")
    return {"message": "删除成功"}