from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
import os

router = APIRouter()

IMAGE_BASE_DIR = os.path.abspath("images")


@router.get("/image")
def get_image(path: str = Query(..., description="Relative image path like 'scenarios/foo.png'")):
    # Previene path traversal
    if ".." in path or path.startswith("/") or "\\" in path:
        raise HTTPException(status_code=400, detail="Invalid path")

    full_path = os.path.join(IMAGE_BASE_DIR, path)

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(full_path, media_type="image/png")
