from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.api.dependencies import require_tenant_id
from app.db.models import Widget
from app.db.session import SessionFactory
from app.schemas.widgets import WidgetCreate, WidgetOut

router = APIRouter(prefix="/api/v1/widgets", tags=["widgets"])


@router.post("", response_model=WidgetOut, status_code=201)
async def create_widget(body: WidgetCreate, tenant_id=Depends(require_tenant_id)):
    async with SessionFactory() as session:
        row = Widget(
            tenant_id=tenant_id, widget_type=body.widget_type, title=body.title,
            description=body.description, button_text=body.button_text,
            fields=[f.model_dump() for f in body.fields], display_options=body.display_options,
            allowed_origins=body.allowed_origins,
        )
        session.add(row)
        await session.commit(); await session.refresh(row)
        return row


@router.get("", response_model=list[WidgetOut])
async def list_widgets(tenant_id=Depends(require_tenant_id)):
    async with SessionFactory() as session:
        rows = (await session.scalars(select(Widget).where(Widget.tenant_id == tenant_id).order_by(Widget.created_at))).all()
        return list(rows)


@router.get("/{widget_id}", response_model=WidgetOut)
async def get_widget(widget_id: UUID, tenant_id=Depends(require_tenant_id)):
    async with SessionFactory() as session:
        row = await session.scalar(select(Widget).where(Widget.id == widget_id, Widget.tenant_id == tenant_id))
        if not row: raise HTTPException(status_code=404, detail="Widget not found")
        return row
