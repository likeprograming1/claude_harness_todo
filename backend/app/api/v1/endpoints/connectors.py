import dataclasses
from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.api.v1.deps import get_connector_service
from app.models.connector import ConnectorModel
from app.schemas.connector import ConnectorCreate, ConnectorResponse, ConnectorUpdate
from app.services.connector_service import ConnectorService

router = APIRouter(prefix="/connectors", tags=["connectors"])


class MateResponse(BaseModel):
    a: ConnectorResponse
    b: ConnectorResponse


def _to_response(model: ConnectorModel) -> ConnectorResponse:
    d = dataclasses.asdict(model)
    d["id"] = d.pop("mongo_id") or ""
    return ConnectorResponse.model_validate(d)


@router.get("", response_model=list[ConnectorResponse])
async def list_connectors(
    svc: Annotated[ConnectorService, Depends(get_connector_service)],
) -> list[ConnectorResponse]:
    return [_to_response(c) for c in await svc.list_connectors()]


@router.get("/{connector_id}", response_model=ConnectorResponse)
async def get_connector(
    connector_id: str,
    svc: Annotated[ConnectorService, Depends(get_connector_service)],
) -> ConnectorResponse:
    return _to_response(await svc.get_connector(connector_id))


@router.post("", response_model=ConnectorResponse, status_code=status.HTTP_201_CREATED)
async def create_connector(
    body: ConnectorCreate,
    svc: Annotated[ConnectorService, Depends(get_connector_service)],
) -> ConnectorResponse:
    return _to_response(await svc.create_connector(body.model_dump()))


@router.put("/{connector_id}", response_model=ConnectorResponse)
async def update_connector(
    connector_id: str,
    body: ConnectorUpdate,
    svc: Annotated[ConnectorService, Depends(get_connector_service)],
) -> ConnectorResponse:
    return _to_response(
        await svc.update_connector(connector_id, body.model_dump(exclude_none=True))
    )


@router.delete("/{connector_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connector(
    connector_id: str,
    svc: Annotated[ConnectorService, Depends(get_connector_service)],
) -> None:
    await svc.delete_connector(connector_id)


@router.post("/{a_id}/mate/{b_id}", response_model=MateResponse)
async def mate_connectors(
    a_id: str,
    b_id: str,
    svc: Annotated[ConnectorService, Depends(get_connector_service)],
) -> MateResponse:
    a, b = await svc.link_mating_connector(a_id, b_id)
    return MateResponse(a=_to_response(a), b=_to_response(b))
