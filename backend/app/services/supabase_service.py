from supabase import create_client, Client
from ..config import settings
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class SupabaseService:
    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket = settings.SUPABASE_BUCKET
    
    # Video Management
    async def save_video(self, video_data: Dict[str, Any]) -> Optional[str]:
        """Save video metadata to Supabase"""
        try:
            video_id = str(uuid.uuid4())
            data = {
                "id": video_id,
                "black_card_text": video_data.get("black_card_text"),
                "white_card_texts": video_data.get("white_card_texts"),
                "video_url": video_data.get("video_url"),
                "prompt": video_data.get("prompt"),
                "game_id": video_data.get("game_id"),
                "winner_id": video_data.get("winner_id"),
                "winner_name": video_data.get("winner_name"),
                "created_at": datetime.utcnow().isoformat(),
                "likes_count": 0,
                "comments_count": 0
            }
            
            result = self.client.table("videos").insert(data).execute()
            return video_id if result.data else None
        except Exception as e:
            print(f"❌ Error saving video: {e}")
            return None
    
    async def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video by ID"""
        try:
            result = self.client.table("videos").select("*").eq("id", video_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Error getting video: {e}")
            return None
    
    async def get_videos_feed(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get videos for feed (TikTok/Reel style)"""
        try:
            result = (
                self.client.table("videos")
                .select("*")
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return result.data if result.data else []
        except Exception as e:
            print(f"❌ Error getting videos feed: {e}")
            return []
    
    # Likes Management
    async def like_video(self, video_id: str, user_id: str) -> bool:
        """Like a video"""
        try:
            # Check if already liked
            existing = (
                self.client.table("likes")
                .select("*")
                .eq("video_id", video_id)
                .eq("user_id", user_id)
                .execute()
            )
            
            if existing.data:
                # Unlike
                self.client.table("likes").delete().eq("video_id", video_id).eq("user_id", user_id).execute()
                # Decrement count
                self.client.rpc("decrement_likes", {"video_id": video_id}).execute()
                return False
            else:
                # Like
                self.client.table("likes").insert({
                    "video_id": video_id,
                    "user_id": user_id,
                    "created_at": datetime.utcnow().isoformat()
                }).execute()
                # Increment count
                self.client.rpc("increment_likes", {"video_id": video_id}).execute()
                return True
        except Exception as e:
            print(f"❌ Error liking video: {e}")
            return False
    
    async def get_video_likes(self, video_id: str) -> int:
        """Get like count for a video"""
        try:
            result = self.client.table("videos").select("likes_count").eq("id", video_id).execute()
            return result.data[0]["likes_count"] if result.data else 0
        except Exception as e:
            print(f"❌ Error getting likes: {e}")
            return 0
    
    # Comments Management
    async def add_comment(self, video_id: str, user_id: str, user_name: str, text: str) -> Optional[Dict[str, Any]]:
        """Add a comment to a video"""
        try:
            comment_id = str(uuid.uuid4())
            data = {
                "id": comment_id,
                "video_id": video_id,
                "user_id": user_id,
                "user_name": user_name,
                "text": text,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("comments").insert(data).execute()
            
            if result.data:
                # Increment comment count
                self.client.rpc("increment_comments", {"video_id": video_id}).execute()
                return result.data[0]
            return None
        except Exception as e:
            print(f"❌ Error adding comment: {e}")
            return None
    
    async def get_video_comments(self, video_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get comments for a video"""
        try:
            result = (
                self.client.table("comments")
                .select("*")
                .eq("video_id", video_id)
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            return result.data if result.data else []
        except Exception as e:
            print(f"❌ Error getting comments: {e}")
            return []
    
    # Storage Management
    async def upload_video_file(self, file_path: str, file_data: bytes) -> Optional[str]:
        """Upload video file to Supabase storage"""
        try:
            result = self.client.storage.from_(self.bucket).upload(file_path, file_data)
            if result:
                # Get public URL
                url = self.client.storage.from_(self.bucket).get_public_url(file_path)
                return url
            return None
        except Exception as e:
            print(f"❌ Error uploading video: {e}")
            return None
    
    async def get_video_url_by_uuid(self, video_uuid: str) -> Optional[str]:
        """Get video URL from Supabase storage by UUID"""
        try:
            # Check if file exists in storage
            file_path = f"{video_uuid}.mp4"
            url = self.client.storage.from_(self.bucket).get_public_url(file_path)
            return url
        except Exception as e:
            print(f"❌ Error getting video URL: {e}")
            return None
    
    async def check_video_exists(self, video_uuid: str) -> bool:
        """Check if video exists in Supabase storage"""
        try:
            file_path = f"{video_uuid}.mp4"
            # Try to get file info
            files = self.client.storage.from_(self.bucket).list(path="")
            return any(f['name'] == file_path for f in files)
        except Exception as e:
            print(f"❌ Error checking video: {e}")
            return False
    
    async def copy_to_winning_bucket(self, video_uuid: str, video_id: str) -> Optional[str]:
        """
        Copy video from videos bucket to winning-videos bucket for feed
        
        Args:
            video_uuid: UUID of the video file
            video_id: Database ID for the video metadata
            
        Returns:
            URL of the video in winning bucket
        """
        try:
            source_path = f"{video_uuid}.mp4"
            dest_path = f"{video_id}.mp4"
            
            # Download from videos bucket
            data = self.client.storage.from_(self.bucket).download(source_path)
            
            if data:
                # Upload to winning-videos bucket
                result = self.client.storage.from_(settings.SUPABASE_WINNING_BUCKET).upload(
                    dest_path, 
                    data
                )
                
                if result:
                    # Get public URL from winning bucket
                    url = self.client.storage.from_(settings.SUPABASE_WINNING_BUCKET).get_public_url(dest_path)
                    print(f"✅ Copied winning video to feed bucket: {url}")
                    return url
            
            return None
        except Exception as e:
            print(f"❌ Error copying to winning bucket: {e}")
            return None


# Singleton instance
supabase_service = SupabaseService()
