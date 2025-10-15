from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..models import Feedback
from ..schemas import FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackOut)
async def create_feedback(payload: FeedbackCreate, session: AsyncSession = Depends(get_session)):
    fb = Feedback(report_id=payload.report_id, rating=payload.rating, comments=payload.comments)
    session.add(fb)
    await session.commit()
    await session.refresh(fb)
    return fb
