from fastapi import FastAPI

from app.api.routes_assets import router as asset_router
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_demo import router as demo_router
from app.api.routes_owner import router as owner_router
from app.api.routes_public import router as public_router


app = FastAPI(
    title="FlyRank Widget Platform",
    version="0.3.0",
)

app.include_router(asset_router)
app.include_router(owner_router)
app.include_router(public_router)
app.include_router(dashboard_router)
app.include_router(demo_router)


@app.get("/health")
async def health():
    return {"status": "ok"}