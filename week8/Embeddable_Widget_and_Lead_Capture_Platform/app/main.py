from fastapi import FastAPI
from app.api.routes_owner import router as owner_router
from app.api.routes_public import router as public_router

app = FastAPI(title="FlyRank Widget Platform", version="0.2.0")
app.include_router(owner_router)
app.include_router(public_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
