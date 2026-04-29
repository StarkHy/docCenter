from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from datetime import datetime
from app.core.config import settings


class Base(DeclarativeBase):
    pass


class Template(Base):
    __tablename__ = 'templates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    file_name = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    variables = Column(JSON, default=list)
    create_time = Column(DateTime, default=func.now())


class Database(Base):
    __tablename__ = 'databases'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    db_type = Column(String(50), nullable=False)
    host = Column(String(255))
    port = Column(String(10))
    database = Column(String(255))
    user = Column(String(255))
    password = Column(String(255))
    service_name = Column(String(255))
    connect_mode = Column(String(50))
    test_sql = Column(Text, default='SELECT 1')
    status = Column(String(50), default='inactive')
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())


class DataSource(Base):
    __tablename__ = 'datasources'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    config = Column(JSON, default=dict)
    database_id = Column(Integer, ForeignKey('databases.id', ondelete='SET NULL'))
    status = Column(String(50), default='inactive')
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())


class Mapping(Base):
    __tablename__ = 'mappings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    template_id = Column(Integer, ForeignKey('templates.id', ondelete='CASCADE'))
    create_time = Column(DateTime, default=func.now())
    
    # 新增关系
    datasource_links = relationship(
        "MappingDataSource",
        back_populates="mapping",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    chart_configs = relationship(
        "MappingChart",
        back_populates="mapping",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    @property
    def datasource_ids(self):
        return [link.datasource_id for link in self.datasource_links]
    
    @property
    def charts(self):
        return [chart.chart_config for chart in self.chart_configs]
    
    _mappings_json = Column(Text, name='mappings', default='[]')
    
    @hybrid_property
    def mappings(self):
        import json
        try:
            data = json.loads(self._mappings_json or '[]')
            if data:
                return data
        except:
            pass
        return [{"datasource_id": link.datasource_id, "source": "", "target": ""} for link in self.datasource_links]
    
    @mappings.setter
    def mappings(self, value):
        import json
        self._mappings_json = json.dumps(value) if isinstance(value, list) else '[]'


class DocumentHistory(Base):
    __tablename__ = 'document_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mapping_id = Column(Integer, ForeignKey('mappings.id', ondelete='SET NULL'))
    template_id = Column(Integer, ForeignKey('templates.id', ondelete='SET NULL'))
    datasource_ids = Column(JSON, default=list)
    output_filename = Column(String(255))
    file_path = Column(String(500))
    status = Column(String(50), default='pending')
    error_message = Column(Text)
    create_time = Column(DateTime, default=func.now())



class MappingDataSource(Base):
    __tablename__ = 'mapping_datasources'
    
    mapping_id = Column(Integer, ForeignKey('mappings.id', ondelete='CASCADE'), primary_key=True)
    datasource_id = Column(Integer, ForeignKey('datasources.id', ondelete='CASCADE'), primary_key=True)
    order = Column(Integer, default=0, nullable=False)
    
    mapping = relationship("Mapping", back_populates="datasource_links")
    datasource = relationship("DataSource")


class MappingChart(Base):
    __tablename__ = 'mapping_charts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mapping_id = Column(Integer, ForeignKey('mappings.id', ondelete='CASCADE'), nullable=False)
    chart_id = Column(String(100), nullable=False, index=True)
    chart_type = Column(String(50))
    chart_title = Column(String(255))
    chart_config = Column(JSON, default=dict)
    
    mapping = relationship("Mapping", back_populates="chart_configs")
    
    __table_args__ = (
        UniqueConstraint('mapping_id', 'chart_id', name='uq_mapping_chart'),
    )


class ReportParameter(Base):
    """月报参数表 - 存储从原始文档提取的参数"""
    __tablename__ = 'report_parameters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    param_name = Column(String(255), nullable=False, index=True, comment='参数名称')
    param_value = Column(Text, comment='参数值')
    param_category = Column(String(100), comment='参数类别: 基本信息/巡查统计/水位数据/采灌数据')
    param_unit = Column(String(50), comment='单位')
    description = Column(Text, comment='说明')
    report_period = Column(String(50), comment='报表周期: 2025年11月')
    source_file = Column(String(255), comment='来源文件')
    status = Column(String(50), default='active', comment='状态: active/inactive')
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())


DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
