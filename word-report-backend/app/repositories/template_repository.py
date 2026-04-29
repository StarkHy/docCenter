from typing import Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Template
from app.repositories.base import BaseRepository


class TemplateRepository(BaseRepository[Template]):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: int) -> Optional[Template]:
        result = await self.session.execute(select(Template).where(Template.id == id))
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Template]:
        result = await self.session.execute(select(Template))
        return list(result.scalars().all())
    
    async def add(self, template: Template) -> Template:
        self.session.add(template)
        await self.session.flush()
        await self.session.refresh(template)
        return template
    
    async def update(self, template: Template) -> Template:
        await self.session.flush()
        await self.session.refresh(template)
        return template
    
    async def delete(self, id: int) -> bool:
        template = await self.get_by_id(id)
        if not template:
            return False
        await self.session.delete(template)
        await self.session.flush()
        return True
    
    async def get_paginated(self, page: int, page_size: int) -> Tuple[List[Template], int]:
        count_result = await self.session.execute(select(func.count(Template.id)))
        total = count_result.scalar() or 0
        
        offset = (page - 1) * page_size
        result = await self.session.execute(select(Template).offset(offset).limit(page_size))
        templates = list(result.scalars().all())
        
        return templates, total
    
    async def get_by_name(self, name: str) -> Optional[Template]:
        result = await self.session.execute(select(Template).where(Template.name == name))
        return result.scalar_one_or_none()
