from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import get_db
from app.repositories.datasource_repository import DataSourceRepository

router = APIRouter()


class DataSourceCreate(BaseModel):
    name: str
    type: str
    config: Dict[str, Any]


class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class DataSourceTest(BaseModel):
    type: str
    config: Dict[str, Any]
    ds_id: Optional[int] = None


from app.services.datasource_service import data_source_service


@router.get("/")
async def get_datasources(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    type_filter: Optional[str] = Query(None, description="Filter by type: 'datasource' or 'database'"),
    session: AsyncSession = Depends(get_db)
):
    datasources = await data_source_service.get_datasources(session, type_filter)
    total = len(datasources)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = datasources[start:end]
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": paginated
    }


@router.get("/{ds_id}")
async def get_datasource(ds_id: int, session: AsyncSession = Depends(get_db)):
    ds = await data_source_service.get_datasource(ds_id, session)
    if not ds:
        raise HTTPException(status_code=404, detail="数据源不存在")
    return ds


@router.post("/")
async def create_datasource(data: DataSourceCreate, session: AsyncSession = Depends(get_db)):
    try:
        return await data_source_service.create_datasource(data.model_dump(), session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{ds_id}")
async def update_datasource(ds_id: int, data: DataSourceUpdate, session: AsyncSession = Depends(get_db)):
    result = await data_source_service.update_datasource(ds_id, data.model_dump(exclude_unset=True), session)
    if not result:
        raise HTTPException(status_code=404, detail="数据源不存在")
    return result


@router.delete("/{ds_id}")
async def delete_datasource(ds_id: int, session: AsyncSession = Depends(get_db)):
    success = await data_source_service.delete_datasource(ds_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="数据源不存在")
    return {"message": "删除成功"}


@router.post("/test")
async def test_datasource(data: DataSourceTest, session: AsyncSession = Depends(get_db)):
    import logging
    logging.warning(f"DataSourceTest received: type={data.type}, config={data.config}, ds_id={data.ds_id}")
    
    ds_dict = {
        "type": data.type,
        "config": data.config
    }

    try:
        logging.warning(f"Calling test_datasource with ds_dict: {ds_dict}")
        result = await data_source_service.test_datasource(ds_dict, session)
        logging.warning(f"Result: {result}")

        if result.get("success") and data.ds_id:
            await data_source_service.update_datasource_status(data.ds_id, "success", session)
            
            ds_repo = DataSourceRepository(session)
            ds = await ds_repo.get_by_id(data.ds_id)
            if ds and result.get("data"):
                config = dict(ds.config or {})
                test_data = result.get("data", {})
                
                if isinstance(test_data, dict):
                    if test_data.get("columns"):
                        config["_fields"] = test_data["columns"]
                    elif test_data.get("data"):
                        inner_data = test_data["data"]
                        if isinstance(inner_data, dict):
                            config["_fields"] = list(inner_data.keys())
                        elif isinstance(inner_data, list) and len(inner_data) > 0:
                            if isinstance(inner_data[0], dict):
                                config["_fields"] = list(inner_data[0].keys())
                    elif test_data.get("params"):
                        config["params"] = test_data["params"]
                elif isinstance(test_data, list) and len(test_data) > 0:
                    if isinstance(test_data[0], dict):
                        config["_fields"] = list(test_data[0].keys())
                
                if data.type == "http_api" and config.get("parameters") and not config.get("params"):
                    config["params"] = config["parameters"]
                
                ds.config = config
                await session.commit()

        return result
    except Exception as e:
        import traceback
        return {"success": False, "message": str(e), "trace": traceback.format_exc()}
