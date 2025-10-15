import asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from krishirakshak_backend.db import engine, AsyncSessionLocal
from krishirakshak_backend.models import Farmer, Report
from krishirakshak_backend.auth import hash_password


async def _create_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def test_crud_create_report():
    asyncio.get_event_loop().run_until_complete(_create_db())

    async def _runner():
        async with AsyncSessionLocal() as session:
            farmer = Farmer(phone="+1999", name="T", hashed_password=hash_password("x"))
            session.add(farmer)
            await session.commit()
            await session.refresh(farmer)

            report = Report(farmer_id=farmer.id, image_path="/tmp/x.jpg", consent_for_training=True)
            session.add(report)
            await session.commit()
            await session.refresh(report)

            assert report.id is not None
            assert report.status == "queued"

    asyncio.get_event_loop().run_until_complete(_runner())
