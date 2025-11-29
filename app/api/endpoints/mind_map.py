from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.dto.content import MindMapRead
from app.services.mind_map_service import generate_mind_map_card

router = APIRouter(prefix="/mindmap", tags=["Mind Map"])


class MindMapRequest(BaseModel):
    material: str


@router.post("/generate", response_model=MindMapRead)
async def generate_mind_map(request: MindMapRequest):
    """Generate a mind map card: text + image."""
    if not request.material.strip():
        raise HTTPException(status_code=400, detail="Material cannot be empty")

    result = generate_mind_map_card(request.material)

    return MindMapRead(
        mind_map_text=result["mind_map_text"],
        image_path=result["image_path"],
    )
