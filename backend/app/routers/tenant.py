"""Tenant management endpoints."""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Tenant
from ..utils.db import get_session

router = APIRouter(prefix="/tenants", tags=["tenants"])


class TenantCreate(BaseModel):
    name: str


class TenantRead(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True


@router.post("/", response_model=TenantRead)
async def create_tenant(data: TenantCreate, session: AsyncSession = Depends(get_session)):
    existing = await session.execute(select(Tenant).where(Tenant.name == data.name))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Tenant already exists")
    tenant = Tenant(name=data.name)
    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)
    return TenantRead.from_orm(tenant)
