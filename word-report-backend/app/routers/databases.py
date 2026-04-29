from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import get_db, Database
from app.services.datasource_service import data_source_service

router = APIRouter()


class DatabaseCreate(BaseModel):
    name: str
    db_type: str
    host: Optional[str] = None
    port: Optional[str] = None
    database: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    service_name: Optional[str] = None
    connect_mode: Optional[str] = None
    test_sql: Optional[str] = "SELECT 1"


class DatabaseUpdate(BaseModel):
    name: Optional[str] = None
    db_type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[str] = None
    database: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    service_name: Optional[str] = None
    connect_mode: Optional[str] = None
    test_sql: Optional[str] = None


class DatabaseResponse(BaseModel):
    id: int
    name: str
    db_type: str
    host: Optional[str] = None
    port: Optional[str] = None
    database: Optional[str] = None
    user: Optional[str] = None
    service_name: Optional[str] = None
    connect_mode: Optional[str] = None
    status: str = "inactive"
    create_time: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/", response_model=dict)
async def get_databases(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db)
):
    result = await session.execute(select(Database))
    databases = result.scalars().all()
    
    total = len(databases)
    offset = (page - 1) * page_size
    items = databases[offset:offset + page_size]
    
    def to_response(db):
        return DatabaseResponse(
            id=db.id,
            name=db.name,
            db_type=db.db_type,
            host=db.host,
            port=db.port,
            database=db.database,
            user=db.user,
            service_name=db.service_name,
            connect_mode=db.connect_mode,
            status=db.status,
            create_time=db.create_time.strftime("%Y-%m-%d %H:%M:%S") if db.create_time else ""
        )
    
    return {
        "items": [to_response(db) for db in items],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{db_id}", response_model=DatabaseResponse)
async def get_database(db_id: int, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Database).where(Database.id == db_id))
    db = result.scalar_one_or_none()
    if not db:
        raise HTTPException(status_code=404, detail="数据库配置不存在")
    return DatabaseResponse(
        id=db.id,
        name=db.name,
        db_type=db.db_type,
        host=db.host,
        port=db.port,
        database=db.database,
        user=db.user,
        service_name=db.service_name,
        connect_mode=db.connect_mode,
        status=db.status,
        create_time=db.create_time.strftime("%Y-%m-%d %H:%M:%S") if db.create_time else ""
    )


@router.post("/", response_model=DatabaseResponse)
async def create_database(data: DatabaseCreate, session: AsyncSession = Depends(get_db)):
    db = Database(
        name=data.name,
        db_type=data.db_type,
        host=data.host,
        port=data.port,
        database=data.database,
        user=data.user,
        password=data.password,
        service_name=data.service_name,
        connect_mode=data.connect_mode,
        status="inactive"
    )
    session.add(db)
    await session.commit()
    await session.refresh(db)
    return DatabaseResponse(
        id=db.id,
        name=db.name,
        db_type=db.db_type,
        host=db.host,
        port=db.port,
        database=db.database,
        user=db.user,
        service_name=db.service_name,
        connect_mode=db.connect_mode,
        status=db.status,
        create_time=db.create_time.strftime("%Y-%m-%d %H:%M:%S") if db.create_time else ""
    )


@router.put("/{db_id}", response_model=DatabaseResponse)
async def update_database(db_id: int, data: DatabaseUpdate, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Database).where(Database.id == db_id))
    db = result.scalar_one_or_none()
    if not db:
        raise HTTPException(status_code=404, detail="数据库配置不存在")
    
    if data.name is not None:
        db.name = data.name
    if data.db_type is not None:
        db.db_type = data.db_type
    if data.host is not None:
        db.host = data.host
    if data.port is not None:
        db.port = data.port
    if data.database is not None:
        db.database = data.database
    if data.user is not None:
        db.user = data.user
    if data.password is not None:
        db.password = data.password
    if data.service_name is not None:
        db.service_name = data.service_name
    if data.connect_mode is not None:
        db.connect_mode = data.connect_mode
    
    await session.commit()
    await session.refresh(db)
    return DatabaseResponse(
        id=db.id,
        name=db.name,
        db_type=db.db_type,
        host=db.host,
        port=db.port,
        database=db.database,
        user=db.user,
        service_name=db.service_name,
        connect_mode=db.connect_mode,
        status=db.status,
        create_time=db.create_time.strftime("%Y-%m-%d %H:%M:%S") if db.create_time else ""
    )


@router.delete("/{db_id}")
async def delete_database(db_id: int, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Database).where(Database.id == db_id))
    db = result.scalar_one_or_none()
    if not db:
        raise HTTPException(status_code=404, detail="数据库配置不存在")
    
    await session.delete(db)
    await session.commit()
    return {"message": "删除成功"}


@router.post("/test")
async def test_database_connection(data: DatabaseCreate):
    """测试数据库连接（无需保存）"""
    config = {
        "host": data.host,
        "port": data.port,
        "database": data.database,
        "user": data.user,
        "password": data.password,
        "service_name": data.service_name,
        "connect_mode": data.connect_mode,
        "test_sql": data.test_sql or "SELECT 1"
    }
    
    if data.db_type == "kingbase":
        result = data_source_service._test_kingbase(config)
    elif data.db_type == "postgresql":
        result = data_source_service._test_postgresql(config)
    elif data.db_type == "mysql":
        result = data_source_service._test_mysql(config)
    elif data.db_type == "oracle":
        result = data_source_service._test_oracle(config)
    else:
        return {"success": False, "message": f"不支持的数据库类型: {data.db_type}"}
    
    return result


@router.post("/{db_id}/test")
async def test_database(db_id: int, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Database).where(Database.id == db_id))
    db = result.scalar_one_or_none()
    if not db:
        raise HTTPException(status_code=404, detail="数据库配置不存在")
    
    config = {
        "host": db.host,
        "port": db.port,
        "database": db.database,
        "user": db.user,
        "password": db.password,
        "service_name": db.service_name,
        "connect_mode": db.connect_mode
    }
    
    if db.db_type == "kingbase":
        result = data_source_service._test_kingbase(config)
    elif db.db_type == "postgresql":
        result = data_source_service._test_postgresql(config)
    elif db.db_type == "mysql":
        result = data_source_service._test_mysql(config)
    elif db.db_type == "oracle":
        result = data_source_service._test_oracle(config)
    else:
        return {"success": False, "message": f"不支持的数据库类型: {db.db_type}"}
    
    if result.get("success"):
        db.status = "success"
        await session.commit()
    
    return result