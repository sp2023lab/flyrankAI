from __future__ import annotations

import asyncio, os
from sqlalchemy import select
from app.core.security import hash_api_key
from app.db.models import Tenant, Widget
from app.db.session import SessionFactory


async def main():
    tenant_name = os.getenv("SEED_TENANT_NAME", "Demo Tenant")
    api_key = os.getenv("SEED_TENANT_API_KEY", "replace-me")
    origin = os.getenv("SEED_WIDGET_ORIGIN", "http://localhost:5500")
    async with SessionFactory() as session:
        tenant = await session.scalar(select(Tenant).where(Tenant.name == tenant_name))
        if not tenant:
            tenant = Tenant(name=tenant_name, api_key_hash=hash_api_key(api_key))
            session.add(tenant); await session.flush()
        widget = await session.scalar(select(Widget).where(Widget.tenant_id == tenant.id, Widget.title == "Demo Contact Form"))
        if not widget:
            widget = Widget(
                tenant_id=tenant.id, widget_type="contact_form", title="Demo Contact Form",
                description="Phase 2 seeded widget", button_text="Contact us",
                fields=[
                    {"name":"name","label":"Name","type":"text","required":True,"max_length":100},
                    {"name":"email","label":"Email","type":"email","required":True,"max_length":254},
                    {"name":"message","label":"Message","type":"textarea","required":False,"max_length":1000},
                ],
                display_options={}, allowed_origins=[origin],
            )
            session.add(widget)
        await session.commit(); await session.refresh(widget)
        print(f"Seed complete. widget_public_id={widget.public_id} allowed_origin={origin}")
        print("API key was read from SEED_TENANT_API_KEY and was not printed.")


if __name__ == "__main__": asyncio.run(main())
