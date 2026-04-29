from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


BASE_DIR = Path(__file__).parent.parent.parent.resolve()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    APP_NAME: str = "Word Report Backend"
    VERSION: str = "1.0.0"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/doccenter"
    
    TEMPLATE_STORAGE_PATH: str = str(BASE_DIR / "templates")
    DATA_SOURCE_STORAGE_PATH: str = str(BASE_DIR / "datasources")
    MAPPING_STORAGE_PATH: str = str(BASE_DIR / "mappings")
    CHART_STORAGE_PATH: str = str(BASE_DIR / "charts")
    WORD_OUTPUT_PATH: str = str(BASE_DIR / "output")
    WORD_HISTORY_PATH: str = str(BASE_DIR / "history")
    
    MAX_TEMPLATE_SIZE: int = 100 * 1024 * 1024
    CHART_DPI: int = 300
    
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "doccenter"
    MINIO_SECURE: bool = False
    
    @field_validator("PORT")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("PORT must be between 1 and 65535")
        return v
    
    @field_validator("MAX_TEMPLATE_SIZE")
    @classmethod
    def validate_max_template_size(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("MAX_TEMPLATE_SIZE must be positive")
        if v > 500 * 1024 * 1024:
            raise ValueError("MAX_TEMPLATE_SIZE cannot exceed 500MB")
        return v
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_paths()
        self._create_directories()
    
    def _validate_paths(self):
        forbidden_paths = ["/", "/root", "/home", "/etc"]
        for path_key in [
            'TEMPLATE_STORAGE_PATH',
            'DATA_SOURCE_STORAGE_PATH',
            'MAPPING_STORAGE_PATH',
            'CHART_STORAGE_PATH',
            'WORD_OUTPUT_PATH',
            'WORD_HISTORY_PATH'
        ]:
            path = Path(getattr(self, path_key)).resolve()
            if str(path) in forbidden_paths:
                raise ValueError(f"{path_key} cannot be set to system root directory")
    
    def _create_directories(self):
        for path_key in [
            'TEMPLATE_STORAGE_PATH',
            'DATA_SOURCE_STORAGE_PATH',
            'MAPPING_STORAGE_PATH',
            'CHART_STORAGE_PATH',
            'WORD_OUTPUT_PATH',
            'WORD_HISTORY_PATH'
        ]:
            path = Path(getattr(self, path_key))
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()