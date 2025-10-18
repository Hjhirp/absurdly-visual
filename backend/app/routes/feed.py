from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from ..services.supabase_service import supabase_service


router = APIRouter(prefix="/api/feed", tags=["feed"])


class LikeRequest(BaseModel):
    video_id: str
    user_id: str


class CommentRequest(BaseModel):
    video_id: str
    user_id: str
    user_name: str
    text: str


class VideoResponse(BaseModel):
    id: str
    black_card_text: str
    white_card_texts: List[str]
    video_url: str
    prompt: Optional[str]
    winner_name: Optional[str]
    created_at: str
    likes_count: int
    comments_count: int


@router.get("/videos", response_model=List[VideoResponse])
async def get_videos_feed(
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    """Get video feed (TikTok/Reel style) - Only winning videos"""
    try:
        # Only fetch videos that have been copied to winning bucket
        # These are the videos that won rounds
        videos = await supabase_service.get_videos_feed(limit=limit, offset=offset)
        
        # Filter to only include videos with winner_id (winning videos)
        winning_videos = [v for v in videos if v.get('winner_id')]
        
        return winning_videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos/{video_id}")
async def get_video(video_id: str):
    """Get a specific video"""
    try:
        video = await supabase_service.get_video(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return video
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/like")
async def like_video(request: LikeRequest):
    """Like or unlike a video"""
    try:
        liked = await supabase_service.like_video(request.video_id, request.user_id)
        likes_count = await supabase_service.get_video_likes(request.video_id)
        return {
            "success": True,
            "liked": liked,
            "likes_count": likes_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/comment")
async def add_comment(request: CommentRequest):
    """Add a comment to a video"""
    try:
        comment = await supabase_service.add_comment(
            request.video_id,
            request.user_id,
            request.user_name,
            request.text
        )
        if not comment:
            raise HTTPException(status_code=500, detail="Failed to add comment")
        return comment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comments/{video_id}")
async def get_comments(video_id: str, limit: int = Query(50, ge=1, le=100)):
    """Get comments for a video"""
    try:
        comments = await supabase_service.get_video_comments(video_id, limit=limit)
        return comments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
