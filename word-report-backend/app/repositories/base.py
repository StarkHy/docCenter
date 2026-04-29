"""Repository 基础接口"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Repository 基础接口
    
    提供通用的 CRUD 操作接口，所有 Repository 都应实现此接口。
    使用泛型 T 表示具体的实体类型。
    """
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        """
        根据 ID 获取实体
        
        Args:
            id: 实体 ID
            
        Returns:
            实体对象，不存在则返回 None
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """
        获取所有实体
        
        Returns:
            实体列表
        """
        pass
    
    @abstractmethod
    async def add(self, entity: T) -> T:
        """
        添加实体
        
        Args:
            entity: 要添加的实体对象
            
        Returns:
            添加后的实体对象（包含生成的 ID 等）
        """
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """
        更新实体
        
        Args:
            entity: 要更新的实体对象
            
        Returns:
            更新后的实体对象
        """
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        """
        删除实体
        
        Args:
            id: 实体 ID
            
        Returns:
            删除成功返回 True，实体不存在返回 False
        """
        pass
