from typing import Optional, List, Tuple

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DocumentHistory
from app.repositories.base import BaseRepository


class DocumentHistoryRepository(BaseRepository[DocumentHistory]):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: int) -> Optional[DocumentHistory]:
        result = await self.session.execute(
            select(DocumentHistory).where(DocumentHistory.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[DocumentHistory]:
        result = await self.session.execute(
            select(DocumentHistory).order_by(DocumentHistory.create_time.desc())
        )
        return list(result.scalars().all())
    
    async def add(self, entity: DocumentHistory) -> DocumentHistory:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
    
    async def update(self, entity: DocumentHistory) -> DocumentHistory:
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
    
    async def delete(self, id: int) -> bool:
        entity = await self.get_by_id(id)
        if not entity:
            return False
        await self.session.delete(entity)
        await self.session.flush()
        return True
    
    async def get_max_id(self) -> int:
        result = await self.session.execute(select(func.max(DocumentHistory.id)))
        return result.scalar() or 0
    
    async def get_paginated(
        self, 
        page: int, 
        page_size: int, 
        search: Optional[str] = None, 
        status: Optional[str] = None
    ) -> Tuple[List[DocumentHistory], int]:
        query = select(DocumentHistory).order_by(DocumentHistory.create_time.desc())
        
        if search:
            search_lower = search.lower()
            query = query.where(
                or_(
                    DocumentHistory.output_filename.ilike(f"%{search_lower}%")
                )
            )
        
        if status:
            query = query.where(DocumentHistory.status == status)
        
        count_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        
        return items, total