from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import typing
from ..db import get_session
from ..schemas import ReportCreate, ReportOut
from ..models import Report
from ..utils import validate_image_filename, token_bucket_allow, validate_upload_mime_and_size
from ..storage import storage
from ..tasks import run_inference_and_update, should_run_sync
from ..tasks import inference_task
from ..config import settings

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=dict)
async def upload_image(
    session: AsyncSession = Depends(get_session),
    file: UploadFile = File(...),
    crop_type: typing.Optional[str] = Form(None),
    lat: typing.Optional[float] = Form(None),
    lon: typing.Optional[float] = Form(None),
    farmer_id: typing.Optional[int] = Form(None),
    consent_for_training: bool = Form(False),
):
    # Rate limit per IP/simple key
    from fastapi import Request
    # we need request but avoid changing signature widely; fetch from context
    # Starlette provides state, but simplest: rely on client host header via dependency override in real app
    ok, _ = validate_image_filename(file.filename)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid image type")

    # Use farmer_id if provided, else a generic key
    key = f"upload:{farmer_id or 'anon'}"
    if not token_bucket_allow(key, settings.UPLOAD_RATE_PER_MIN):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    data = await file.read()
    if not validate_upload_mime_and_size(file.content_type or "", len(data)):
        raise HTTPException(status_code=400, detail="Invalid file type or size")
    import io
    saved_path = storage.save_file(io.BytesIO(data), file.filename)

    report = Report(
        farmer_id=farmer_id,
        image_path=saved_path,
        status="queued",
        crop_type=crop_type,
        lat=lat,
        lon=lon,
        consent_for_training=bool(consent_for_training),
    )
    session.add(report)
    await session.commit()
    await session.refresh(report)

    if should_run_sync():
        await run_inference_and_update(session, report.id)
    else:
        inference_task.delay(report.id)

    return {"report_id": report.id, "status": report.status}
