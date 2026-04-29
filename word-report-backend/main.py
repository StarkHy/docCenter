from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import templates, datasources, documents, history, auth, mappings, charts, databases
from app.core.config import settings
from app.models import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Word Report Backend",
    description="Word Report Generator Backend API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(templates.router, prefix="/api/templates", tags=["模板管理"])
app.include_router(databases.router, prefix="/api/databases", tags=["数据库配置"])
app.include_router(datasources.router, prefix="/api/datasources", tags=["数据源管理"])
app.include_router(mappings.router, prefix="/api/mappings", tags=["参数映射"])
app.include_router(charts.router, prefix="/api/charts", tags=["图表生成"])
app.include_router(documents.router, prefix="/api/documents", tags=["文档生成"])
app.include_router(history.router, prefix="/api/history", tags=["历史记录"])


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "服务运行正常",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
