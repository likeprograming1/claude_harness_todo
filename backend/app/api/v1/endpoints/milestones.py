from fastapi import APIRouter

from app.models.milestone import MilestoneModel
from app.schemas.milestone import MilestoneResponse
from app.services.milestone_service import MilestoneService

router = APIRouter(prefix="/milestones", tags=["milestones"])


def _to_response(m: MilestoneModel) -> MilestoneResponse:
    return MilestoneResponse(
        id=m.mongo_id or "",
        milestone_id=m.milestone_id,
        title=m.title,
        description=m.description,
        achieved_at=m.achieved_at,
    )


@router.get("", response_model=list[MilestoneResponse])
async def list_milestones() -> list[MilestoneResponse]:
    milestones = await MilestoneService().list_milestones()
    return [_to_response(m) for m in milestones]
