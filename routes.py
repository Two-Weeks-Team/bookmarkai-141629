import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models import Bookmark, Tag, get_db, Base
from ai_service import generate_summary, suggest_tags

router = APIRouter()

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------
class CreateBookmarkRequest(BaseModel):
    url: str = Field(..., description="The URL to bookmark")
    title: Optional[str] = Field(None, description="Optional title; if omitted we use the URL")
    detail_level: Optional[str] = Field("one_sentence", description="one_sentence or expanded")

class BookmarkResponse(BaseModel):
    id: str
    url: str
    title: str
    short_summary: Optional[str]
    detailed_summary: Optional[str]
    tags: List[str]

class SummaryRequest(BaseModel):
    url: str
    detail_level: Optional[str] = Field("one_sentence", description="one_sentence or expanded")

class SummaryResponse(BaseModel):
    summary: str

class TagRequest(BaseModel):
    text: str

class TagResponse(BaseModel):
    tags: List[str]

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
def _extract_tag_names(tag_objs: List[Tag]) -> List[str]:
    return [t.name for t in tag_objs]

# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------
@router.post("/bookmarks", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(payload: CreateBookmarkRequest, db: Session = Depends(get_db)):
    # Simple existence check
    existing = db.query(Bookmark).filter(Bookmark.url == payload.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bookmark already exists")

    # Generate a UUID for the new bookmark
    bookmark_id = str(uuid.uuid4())
    title = payload.title or payload.url

    # Call AI services (fallback handled inside service)
    summary_data = await generate_summary(payload.url, payload.detail_level)
    tags_data = await suggest_tags(payload.url)  # we pass URL – the service can fetch if needed

    # Create DB record
    bookmark = Bookmark(
        id=bookmark_id,
        url=payload.url,
        title=title,
        short_summary=summary_data.get("summary"),
        detailed_summary=summary_data.get("detailed_summary"),
    )
    db.add(bookmark)
    db.flush()  # make sure ID is available for relationships

    # Process tags – create Tag rows if they don't exist
    tag_names = tags_data.get("tags", [])
    tag_objects: List[Tag] = []
    for name in tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(id=str(uuid.uuid4()), name=name)
            db.add(tag)
            db.flush()
        tag_objects.append(tag)
        # Associate via the association table – SQLAlchemy handles it automatically
        bookmark.tags.append(tag)

    db.commit()
    db.refresh(bookmark)
    return BookmarkResponse(
        id=bookmark.id,
        url=bookmark.url,
        title=bookmark.title,
        short_summary=bookmark.short_summary,
        detailed_summary=bookmark.detailed_summary,
        tags=_extract_tag_names(tag_objects),
    )

@router.get("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
def get_bookmark(bookmark_id: str, db: Session = Depends(get_db)):
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return BookmarkResponse(
        id=bookmark.id,
        url=bookmark.url,
        title=bookmark.title,
        short_summary=bookmark.short_summary,
        detailed_summary=bookmark.detailed_summary,
        tags=_extract_tag_names(bookmark.tags),
    )

@router.get("/bookmarks", response_model=List[BookmarkResponse])
def list_bookmarks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bookmarks = db.query(Bookmark).offset(skip).limit(limit).all()
    return [
        BookmarkResponse(
            id=b.id,
            url=b.url,
            title=b.title,
            short_summary=b.short_summary,
            detailed_summary=b.detailed_summary,
            tags=_extract_tag_names(b.tags),
        )
        for b in bookmarks
    ]

@router.post("/ai/summarize", response_model=SummaryResponse)
async def ai_summarize(request: SummaryRequest):
    result = await generate_summary(request.url, request.detail_level)
    # The AI service returns a dict with a "summary" key (fallback also follows same shape)
    return SummaryResponse(summary=result.get("summary", ""))

@router.post("/ai/tag", response_model=TagResponse)
async def ai_tag(request: TagRequest):
    result = await suggest_tags(request.text)
    return TagResponse(tags=result.get("tags", []))
