import dataclasses
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_wire_service
from app.models.wire import WireModel
from app.schemas.wire import WireCreate, WireResponse, WireUpdate
from app.services.wire_service import WireService

router = APIRouter(prefix="/wires", tags=["wires"])


def _to_response(model: WireModel) -> WireResponse:
    d = dataclasses.asdict(model)
    d["id"] = d.pop("mongo_id") or ""
    return WireResponse.model_validate(d)


@router.get("", response_model=list[WireResponse])
async def list_wires(
    svc: Annotated[WireService, Depends(get_wire_service)],
) -> list[WireResponse]:
    return [_to_response(w) for w in await svc.list_wires()]


@router.get("/{wire_id}", response_model=WireResponse)
async def get_wire(
    wire_id: str,
    svc: Annotated[WireService, Depends(get_wire_service)],
) -> WireResponse:
    return _to_response(await svc.get_wire(wire_id))


@router.post("", response_model=WireResponse, status_code=status.HTTP_201_CREATED)
async def create_wire(
    body: WireCreate,
    svc: Annotated[WireService, Depends(get_wire_service)],
) -> WireResponse:
    return _to_response(await svc.create_wire(body.model_dump()))


@router.put("/{wire_id}", response_model=WireResponse)
async def update_wire(
    wire_id: str,
    body: WireUpdate,
    svc: Annotated[WireService, Depends(get_wire_service)],
) -> WireResponse:
    return _to_response(
        await svc.update_wire(wire_id, body.model_dump(exclude_none=True))
    )


@router.delete("/{wire_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wire(
    wire_id: str,
    svc: Annotated[WireService, Depends(get_wire_service)],
) -> None:
    await svc.delete_wire(wire_id)
