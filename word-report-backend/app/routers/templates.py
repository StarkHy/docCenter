from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import get_db

router = APIRouter()

from app.services.template_service import template_service


@router.get("/")
async def get_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db)
):
    return await template_service.get_templates_paginated(page, page_size, session)


@router.get("/{template_id}")
async def get_template(template_id: int, session: AsyncSession = Depends(get_db)):
    template = await template_service.get_template(template_id, session)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template


@router.post("/")
async def upload_template(
    name: str = Form(...),
    category: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db)
):
    try:
        template = await template_service.upload_template(file, name, category, session)
        return template
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.delete("/{template_id}")
async def delete_template(template_id: int, session: AsyncSession = Depends(get_db)):
    success = await template_service.delete_template(template_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {"message": "删除成功"}


@router.get("/{template_id}/variables")
async def get_template_variables(template_id: int, session: AsyncSession = Depends(get_db)):
    template = await template_service.get_template(template_id, session)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {"variables": template.get("variables", [])}


@router.get("/{template_id}/download")
async def download_template(template_id: int, session: AsyncSession = Depends(get_db)):
    file_path = await template_service.get_template_file(template_id, session)
    if not file_path:
        raise HTTPException(status_code=404, detail="模板文件不存在")

    template = await template_service.get_template(template_id, session)
    from fastapi.responses import FileResponse
    return FileResponse(
        file_path,
        filename=template["file_name"],
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
