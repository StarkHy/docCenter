from typing import Optional, List, Tuple, Dict, Any

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Mapping, MappingDataSource, MappingChart
from app.repositories.base import BaseRepository


class MappingRepository(BaseRepository[Mapping]):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: int, eager_load: bool = True) -> Optional[Mapping]:
        query = select(Mapping).where(Mapping.id == id)
        
        if eager_load:
            query = query.options(
                selectinload(Mapping.datasource_links),
                selectinload(Mapping.chart_configs)
            )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(self, eager_load: bool = False) -> List[Mapping]:
        query = select(Mapping)
        if eager_load:
            query = query.options(
                selectinload(Mapping.datasource_links),
                selectinload(Mapping.chart_configs)
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def add(self, mapping: Mapping) -> Mapping:
        self.session.add(mapping)
        await self.session.flush()
        await self.session.refresh(mapping)
        return mapping
    
    async def update(self, mapping: Mapping) -> Mapping:
        await self.session.flush()
        await self.session.refresh(mapping)
        return mapping
    
    async def delete(self, id: int) -> bool:
        mapping = await self.get_by_id(id)
        if not mapping:
            return False
        await self.session.delete(mapping)
        await self.session.flush()
        return True
    
    async def get_by_template(self, template_id: int) -> List[Mapping]:
        result = await self.session.execute(
            select(Mapping).where(Mapping.template_id == template_id)
        )
        return list(result.scalars().all())
    
    async def get_paginated(self, page: int, page_size: int) -> Tuple[List[Mapping], int]:
        count_result = await self.session.execute(select(func.count(Mapping.id)))
        total = count_result.scalar() or 0
        
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Mapping).offset(offset).limit(page_size)
        )
        mappings = list(result.scalars().all())
        
        return mappings, total
    
    async def add_datasource_link(self, mapping_id: int, datasource_id: int, order: int = 0) -> MappingDataSource:
        link = MappingDataSource(
            mapping_id=mapping_id,
            datasource_id=datasource_id,
            order=order
        )
        self.session.add(link)
        await self.session.flush()
        return link
    
    async def clear_datasource_links(self, mapping_id: int):
        result = await self.session.execute(
            select(MappingDataSource).where(MappingDataSource.mapping_id == mapping_id)
        )
        links = result.scalars().all()
        for link in links:
            await self.session.delete(link)
        await self.session.flush()
    
    async def add_chart_config(self, mapping_id: int, chart_data: Dict[str, Any]) -> MappingChart:
        chart = MappingChart(
            mapping_id=mapping_id,
            chart_id=chart_data.get("id", f"chart_{len(chart_data)}"),
            chart_type=chart_data.get("type"),
            chart_title=chart_data.get("title"),
            chart_config=chart_data
        )
        self.session.add(chart)
        await self.session.flush()
        return chart
    
    async def clear_chart_configs(self, mapping_id: int):
        result = await self.session.execute(
            select(MappingChart).where(MappingChart.mapping_id == mapping_id)
        )
        charts = result.scalars().all()
        for chart in charts:
            await self.session.delete(chart)
        await self.session.flush()
