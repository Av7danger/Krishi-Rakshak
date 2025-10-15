from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlmodel import SQLModel
from .models import Farmer, Report, Feedback, MessageLog


async def get_farmer_by_phone(session: AsyncSession, phone: str) -> Optional[Farmer]:
    res = await session.execute(select(Farmer).where(Farmer.phone == phone))
    return res.scalar_one_or_none()


async def create_farmer(session: AsyncSession, farmer: Farmer) -> Farmer:
    session.add(farmer)
    await session.commit()
    await session.refresh(farmer)
    return farmer


async def create_report(session: AsyncSession, report: Report) -> Report:
    session.add(report)
    await session.commit()
    await session.refresh(report)
    return report


async def get_report(session: AsyncSession, report_id: int) -> Optional[Report]:
    res = await session.execute(select(Report).where(Report.id == report_id))
    return res.scalar_one_or_none()


async def list_reports_for_farmer(session: AsyncSession, farmer_id: int, limit: int = 50):
    res = await session.execute(
        select(Report).where(Report.farmer_id == farmer_id).order_by(Report.created_at.desc()).limit(limit)
    )
    return list(res.scalars())


async def create_feedback(session: AsyncSession, feedback: Feedback) -> Feedback:
    session.add(feedback)
    await session.commit()
    await session.refresh(feedback)
    return feedback


async def create_message_log(session: AsyncSession, ml: MessageLog) -> MessageLog:
    session.add(ml)
    await session.commit()
    await session.refresh(ml)
    return ml
