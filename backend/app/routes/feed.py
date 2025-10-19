from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from ..services.supabase_service import supabase_service
from ..services.feed_service import feed_service


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


@router.get("/videos")
async def get_videos_feed(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get video feed (TikTok/Reel style) - All videos from storage bucket (randomized)"""
    try:
        import random
        
        # List all files from videos storage bucket
        result = supabase_service.client.storage.from_('videos').list()
        
        # Convert to video objects with public URLs
        videos = []
        for file in result:
            if file.get('name') and file['name'].endswith('.mp4'):
                video_url = supabase_service.client.storage.from_('videos').get_public_url(file['name'])
                # Remove trailing ?
                if video_url.endswith('?'):
                    video_url = video_url[:-1]
                
                videos.append({
                    'id': file['name'].replace('.mp4', ''),
                    'video_url': video_url,
                    'black_card_text': 'Generated Content',
                    'white_card_texts': [],
                    'winner_name': 'Player',
                    'created_at': file.get('created_at', ''),
                    'likes': 0,
                    'views': 0
                })
        
        # Shuffle videos randomly
        random.shuffle(videos)
        
        # Apply pagination
        start = offset
        end = offset + limit
        return videos[start:end]
    except Exception as e:
        print(f"❌ Error fetching videos from storage: {e}")
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


@router.get("/trending")
async def get_trending_videos(limit: int = Query(10, ge=1, le=20)):
    """Get trending videos (most liked/viewed)"""
    try:
        videos = await feed_service.get_trending(limit=limit)
        return videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/view/{video_id}")
async def increment_video_view(video_id: str):
    """Increment video view count"""
    try:
        # For storage-only videos, just return success without incrementing
        # (no database record exists)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
