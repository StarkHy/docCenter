import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models import Mapping, MappingDataSource, MappingChart
from app.repositories.mapping_repository import MappingRepository


class MappingService:
    def __init__(self):
        self.storage_path = settings.MAPPING_STORAGE_PATH
        os.makedirs(self.storage_path, exist_ok=True)

    def _mapping_to_dict(self, m: Mapping) -> dict:
        return {
            "id": m.id,
            "name": m.name,
            "template_id": m.template_id,
            "datasource_ids": [link.datasource_id for link in m.datasource_links],
            "mappings": m.mappings or [],
            "charts": [chart.chart_config for chart in m.chart_configs],
            "create_time": m.create_time.strftime("%Y-%m-%d %H:%M:%S") if m.create_time else ""
        }

    async def get_mappings(self, session: AsyncSession) -> List[dict]:
        repo = MappingRepository(session)
        mappings = await repo.get_all(eager_load=True)
        return [self._mapping_to_dict(m) for m in mappings]

    async def get_mapping(self, mapping_id: int, session: AsyncSession) -> Optional[dict]:
        repo = MappingRepository(session)
        m = await repo.get_by_id(mapping_id, eager_load=True)
        if not m:
            return None
        return self._mapping_to_dict(m)

    async def get_mappings_by_template(self, template_id: int, session: AsyncSession) -> List[dict]:
        repo = MappingRepository(session)
        mappings = await repo.get_by_template(template_id)
        return [self._mapping_to_dict(m) for m in mappings]

    async def create_mapping(self, data: dict, session: AsyncSession) -> dict:
        repo = MappingRepository(session)
        all_mappings = await repo.get_all()
        max_id = max((m.id for m in all_mappings), default=0)
        new_id = max_id + 1

        import json
        
        mapping = Mapping(
            id=new_id,
            name=data.get("name", ""),
            template_id=data.get("template_id"),
        )
        mapping.mappings = data.get("mappings", [])
        session.add(mapping)
        await session.flush()
        
        datasource_ids = data.get("datasource_ids", [])
        for idx, ds_id in enumerate(datasource_ids):
            link = MappingDataSource(
                mapping_id=mapping.id,
                datasource_id=ds_id,
                order=idx
            )
            session.add(link)
        
        charts = data.get("charts", [])
        for chart in charts:
            chart_obj = MappingChart(
                mapping_id=mapping.id,
                chart_id=chart.get("id", f"chart_{len(charts)}"),
                chart_type=chart.get("type"),
                chart_title=chart.get("title"),
                chart_config=chart
            )
            session.add(chart_obj)
        
        await session.commit()
        await session.refresh(mapping)

        return self._mapping_to_dict(mapping)

    async def update_mapping(self, mapping_id: int, data: dict, session: AsyncSession) -> Optional[dict]:
        repo = MappingRepository(session)
        m = await repo.get_by_id(mapping_id, eager_load=True)
        if not m:
            return None

        m.name = data.get("name", m.name)
        if "template_id" in data:
            m.template_id = data["template_id"]
        
        if "datasource_ids" in data:
            for link in m.datasource_links:
                await session.delete(link)
            m.datasource_links = []
            
            for idx, ds_id in enumerate(data["datasource_ids"]):
                link = MappingDataSource(
                    mapping_id=mapping_id,
                    datasource_id=ds_id,
                    order=idx
                )
                session.add(link)
        
        if "charts" in data:
            for chart in m.chart_configs:
                await session.delete(chart)
            m.chart_configs = []
            
            for chart_data in data["charts"]:
                chart_obj = MappingChart(
                    mapping_id=mapping_id,
                    chart_id=chart_data.get("id", f"chart_{len(data['charts'])}"),
                    chart_type=chart_data.get("type"),
                    chart_title=chart_data.get("title"),
                    chart_config=chart_data
                )
                session.add(chart_obj)
        
        if "mappings" in data:
            m.mappings = data["mappings"]

        await session.commit()
        await session.refresh(m)

        return self._mapping_to_dict(m)

    async def delete_mapping(self, mapping_id: int, session: AsyncSession) -> bool:
        repo = MappingRepository(session)
        m = await repo.get_by_id(mapping_id)
        if not m:
            return False

        await session.delete(m)
        await session.commit()
        return True

    async def get_mappings_paginated(self, page: int = 1, page_size: int = 10, session: AsyncSession = None) -> dict:
        if session is None:
            from app.models import async_session
            async with async_session() as session:
                return await self._get_mappings_paginated(page, page_size, session)
        return await self._get_mappings_paginated(page, page_size, session)

    async def _get_mappings_paginated(self, page: int, page_size: int, session: AsyncSession) -> dict:
        repo = MappingRepository(session)
        mappings, total = await repo.get_paginated(page, page_size)

        items = [self._mapping_to_dict(m) for m in mappings]

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }


mapping_service = MappingService()