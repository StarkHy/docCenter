"""Repository 层 - 数据访问抽象"""

from app.repositories.base import BaseRepository
from app.repositories.template_repository import TemplateRepository
from app.repositories.datasource_repository import DataSourceRepository
from app.repositories.mapping_repository import MappingRepository
from app.repositories.document_history_repository import DocumentHistoryRepository

__all__ = [
    "BaseRepository",
    "TemplateRepository",
    "DataSourceRepository",
    "MappingRepository",
    "DocumentHistoryRepository",
]
