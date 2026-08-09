from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(tags=["demo"])

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


@router.get("/demo/dashboard", include_in_schema=False)
async def owner_dashboard():
    path = STATIC_DIR / "dashboard.html"

    if not path.is_file():
        raise HTTPException(status_code=404, detail="Dashboard page not found")

    return FileResponse(
        path,
        media_type="text/html",
        headers={"Cache-Control": "no-store"},
    )