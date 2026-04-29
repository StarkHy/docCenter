from typing import Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DataSource
from app.repositories.base import BaseRepository


class DataSourceRepository(BaseRepository[DataSource]):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: int) -> Optional[DataSource]:
        result = await self.session.execute(select(DataSource).where(DataSource.id == id))
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[DataSource]:
        result = await self.session.execute(select(DataSource))
        return list(result.scalars().all())
    
    async def add(self, datasource: DataSource) -> DataSource:
        self.session.add(datasource)
        await self.session.flush()
        await self.session.refresh(datasource)
        return datasource
    
    async def update(self, datasource: DataSource) -> DataSource:
        await self.session.flush()
        await self.session.refresh(datasource)
        return datasource
    
    async def delete(self, id: int) -> bool:
        datasource = await self.get_by_id(id)
        if not datasource:
            return False
        await self.session.delete(datasource)
        await self.session.flush()
        return True
    
    async def get_by_type(self, ds_type: str) -> List[DataSource]:
        result = await self.session.execute(
            select(DataSource).where(DataSource.type == ds_type)
        )
        return list(result.scalars().all())
    
    async def get_paginated(self, page: int, page_size: int) -> Tuple[List[DataSource], int]:
        count_result = await self.session.execute(select(func.count(DataSource.id)))
        total = count_result.scalar() or 0
        
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(DataSource).offset(offset).limit(page_size)
        )
        datasources = list(result.scalars().all())
        
        return datasources, total
