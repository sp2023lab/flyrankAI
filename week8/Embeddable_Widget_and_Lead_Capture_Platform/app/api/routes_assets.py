from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(tags=["assets"])

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


@router.get("/assets/widget.v1.js", include_in_schema=False)
async def widget_bundle():
    path = STATIC_DIR / "widget.v1.js"

    if not path.is_file():
        raise HTTPException(status_code=404, detail="Widget bundle not found")

    return FileResponse(
        path,
        media_type="application/javascript",
        headers={
            "Cache-Control": "public, max-age=31536000, immutable"
        },
    )