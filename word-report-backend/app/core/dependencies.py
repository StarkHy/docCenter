from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.template_repository import TemplateRepository
from app.repositories.datasource_repository import DataSourceRepository
from app.repositories.mapping_repository import MappingRepository
from app.repositories.document_history_repository import DocumentHistoryRepository

from app.services.document_generation_service import DocumentGenerationService


class DependencyContainer:
    
    @staticmethod
    def get_template_repository(session: AsyncSession) -> TemplateRepository:
        return TemplateRepository(session)
    
    @staticmethod
    def get_datasource_repository(session: AsyncSession) -> DataSourceRepository:
        return DataSourceRepository(session)
    
    @staticmethod
    def get_mapping_repository(session: AsyncSession) -> MappingRepository:
        return MappingRepository(session)
    
    @staticmethod
    def get_document_history_repository(session: AsyncSession) -> DocumentHistoryRepository:
        return DocumentHistoryRepository(session)
    
    @staticmethod
    def get_document_generation_service(
        session: AsyncSession
    ) -> DocumentGenerationService:
        return DocumentGenerationService(
            template_repo=DependencyContainer.get_template_repository(session),
            datasource_repo=DependencyContainer.get_datasource_repository(session),
            mapping_repo=DependencyContainer.get_mapping_repository(session),
            history_repo=DependencyContainer.get_document_history_repository(session)
        )
