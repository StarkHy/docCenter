from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any

router = APIRouter()


class ChartData(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    type: str = 'bar'
    title: str = ''
    x_label: str = ''
    y_label: str = ''
    x_data: List[Any] = []
    y_data: List[Any] = []
    color_scheme: str = 'default'


class ChartGenerateRequest(BaseModel):
    charts: List[ChartData]


class ChartGenerateResponse(BaseModel):
    results: List[Dict[str, Any]]


from app.services.chart_service import chart_service
from fastapi.responses import FileResponse


@router.post("/generate")
async def generate_charts(request: ChartGenerateRequest):
    try:
        results = chart_service.generate_charts([c.model_dump() for c in request.charts])
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图表生成失败: {str(e)}")


@router.get("/list")
async def list_charts():
    return {"charts": chart_service.list_charts()}


@router.get("/{filename}")
async def get_chart(filename: str):
    filepath = chart_service.get_chart_file(filename)
    if not filepath:
        raise HTTPException(status_code=404, detail="图表文件不存在")
    return FileResponse(
        filepath,
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


@router.delete("/{filename}")
async def delete_chart(filename: str):
    success = chart_service.delete_chart(filename)
    if not success:
        raise HTTPException(status_code=404, detail="图表文件不存在")
    return {"message": "删除成功"}