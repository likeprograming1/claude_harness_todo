import dataclasses
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_drawing_service
from app.models.harness_drawing import HarnessDrawingModel
from app.schemas.harness_drawing import (
    HarnessDrawingCreate,
    HarnessDrawingResponse,
    HarnessDrawingUpdate,
    ValidationReport,
)
from app.services.harness_drawing_service import HarnessDrawingService

router = APIRouter(prefix="/harness/drawings", tags=["harness-drawings"])


def _to_response(model: HarnessDrawingModel) -> HarnessDrawingResponse:
    d = dataclasses.asdict(model)
    d["id"] = d.pop("mongo_id") or ""
    return HarnessDrawingResponse.model_validate(d)


@router.get("", response_model=list[HarnessDrawingResponse])
async def list_drawings(
    svc: Annotated[HarnessDrawingService, Depends(get_drawing_service)],
) -> list[HarnessDrawingResponse]:
    return [_to_response(d) for d in await svc.list_drawings()]


@router.get("/{drawing_id}", response_model=HarnessDrawingResponse)
async def get_drawing(
    drawing_id: str,
    svc: Annotated[HarnessDrawingService, Depends(get_drawing_service)],
) -> HarnessDrawingResponse:
    return _to_response(await svc.get_drawing(drawing_id))


@router.post("", response_model=HarnessDrawingResponse, status_code=status.HTTP_201_CREATED)
async def create_drawing(
    body: HarnessDrawingCreate,
    svc: Annotated[HarnessDrawingService, Depends(get_drawing_service)],
) -> HarnessDrawingResponse:
    return _to_response(await svc.create_drawing(body.model_dump()))


@router.put("/{drawing_id}", response_model=HarnessDrawingResponse)
async def update_drawing(
    drawing_id: str,
    body: HarnessDrawingUpdate,
    svc: Annotated[HarnessDrawingService, Depends(get_drawing_service)],
) -> HarnessDrawingResponse:
    return _to_response(
        await svc.update_drawing(drawing_id, body.model_dump(exclude_none=True))
    )


@router.delete("/{drawing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_drawing(
    drawing_id: str,
    svc: Annotated[HarnessDrawingService, Depends(get_drawing_service)],
) -> None:
    await svc.delete_drawing(drawing_id)


@router.post("/{drawing_id}/validate", response_model=ValidationReport)
async def validate_drawing(
    drawing_id: str,
    svc: Annotated[HarnessDrawingService, Depends(get_drawing_service)],
) -> ValidationReport:
    return await svc.validate_drawing(drawing_id)
