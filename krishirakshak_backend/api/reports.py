from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from .. import crud
from ..schemas import ReportOut
from ..storage import storage

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{report_id}", response_model=ReportOut)
async def get_report(report_id: int, session: AsyncSession = Depends(get_session)):
    report = await crud.get_report(session, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("", response_model=list[ReportOut])
async def list_reports(farmer_id: int = Query(...), session: AsyncSession = Depends(get_session)):
    return await crud.list_reports_for_farmer(session, farmer_id)


@router.get("/{report_id}/signed_url", response_model=dict)
async def get_report_signed_url(report_id: int, session: AsyncSession = Depends(get_session)):
    report = await crud.get_report(session, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    url = storage.generate_signed_url(report.image_path) or report.image_path
    return {"url": url}
