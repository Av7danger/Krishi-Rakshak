from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel
from typing import Optional
from ..db import get_session
from .. import crud
from ..models import Farmer
from ..schemas import FarmerCreate, FarmerOut, LoginRequest, Token
from ..auth import create_access_token, hash_password, verify_password, decode_token
from ..config import settings
from fastapi import Response

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=FarmerOut)
async def register_farmer(payload: FarmerCreate, session: AsyncSession = Depends(get_session)):
    existing = await crud.get_farmer_by_phone(session, payload.phone)
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")
    farmer = Farmer(
        phone=payload.phone,
        name=payload.name,
        hashed_password=hash_password(payload.password),
        consent_for_training=payload.consent_for_training,
    )
    farmer = await crud.create_farmer(session, farmer)
    return farmer


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session), response: Response = None):
    farmer = await crud.get_farmer_by_phone(session, payload.phone)
    if not farmer or not verify_password(payload.password, farmer.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(farmer.id))
    # Set cookie for web session convenience
    if response is not None:
        response.set_cookie(key="krishi_token", value=token, httponly=True, samesite="lax")
    return Token(access_token=token)


async def get_current_farmer(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session),
    response: Response = None
) -> Farmer:
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise ValueError("Invalid token subject")
        farmer_id = int(sub)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # basic retrieval
    result = await session.get(Farmer, farmer_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return result


@router.get("/me", response_model=FarmerOut)
async def me(current: Farmer = Depends(get_current_farmer)):
    return current


@router.delete("/me", response_model=dict)
async def delete_me(current: Farmer = Depends(get_current_farmer), session: AsyncSession = Depends(get_session)):
    await session.delete(current)
    await session.commit()
    return {"ok": True}
