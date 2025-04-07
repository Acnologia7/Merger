from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import DataA, DataCResponse
from app.services.data import DataService, get_data_service
from app.docs.openapidocs import (
    data_a_post_description,
    data_a_post_summary,
    data_a_post_responses,
    data_a_post_tags,
    data_c_get_description,
    data_c_get_responses,
    data_c_get_summary,
    data_c_get_tags,
)


router = APIRouter()


@router.post(
    "/data-a",
    responses=data_a_post_responses,
    summary=data_a_post_summary,
    description=data_a_post_description,
    tags=data_a_post_tags,
)
async def post_data_a(data: DataA, service: DataService = Depends(get_data_service)):

    await service.save_data("data_a", data.model_dump())
    await service.merge_data()
    return JSONResponse(content={"status": "ok"})


@router.get(
    "/data-c",
    response_model=DataCResponse,
    responses=data_c_get_responses,
    summary=data_c_get_summary,
    description=data_c_get_description,
    tags=data_c_get_tags,
)
async def get_data_c(service: DataService = Depends(get_data_service)):

    data_c = await service.load_data("data_c")
    if data_c:
        return JSONResponse(content=data_c)
    raise HTTPException(status_code=404, detail="DATA C not available")
