"""
Feed Service - TikTok-like content feed
Manages generated content for public viewing
"""
from typing import List, Dict, Optional
from datetime import datetime
from .supabase_service import supabase_service


class FeedService:
    """Service for managing content feed"""
    
    def __init__(self):
        """Initialize feed service"""
        pass
    
    async def get_feed(
        self,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "created_at"
    ) -> List[Dict]:
        """
        Get content feed items (TikTok-like)
        
        Args:
            limit: Number of items to return
            offset: Pagination offset
            sort_by: Sort field (created_at, likes, views)
        
        Returns:
            List of feed items with video, image, narration
        """
        try:
            # Query Supabase for videos
            response = supabase_service.client.table('videos').select(
                '*'
            ).order(
                sort_by, desc=True
            ).range(
                offset, offset + limit - 1
            ).execute()
            
            if response.data:
                return response.data
            return []
            
        except Exception as e:
            print(f"❌ Error fetching feed: {e}")
            return []
    
    async def get_trending(self, limit: int = 10) -> List[Dict]:
        """Get trending content (most liked/viewed)"""
        try:
            response = supabase_service.client.table('videos').select(
                '*'
            ).order(
                'likes', desc=True
            ).limit(limit).execute()
            
            if response.data:
                return response.data
            return []
            
        except Exception as e:
            print(f"❌ Error fetching trending: {e}")
            return []
    
    async def get_video_by_id(self, video_id: str) -> Optional[Dict]:
        """Get single video by ID"""
        try:
            response = supabase_service.client.table('videos').select(
                '*'
            ).eq('id', video_id).single().execute()
            
            return response.data if response.data else None
            
        except Exception as e:
            print(f"❌ Error fetching video: {e}")
            return None
    
    async def like_video(self, video_id: str) -> bool:
        """Increment video likes"""
        try:
            # Get current likes
            video = await self.get_video_by_id(video_id)
            if not video:
                return False
            
            current_likes = video.get('likes', 0)
            
            # Update likes
            response = supabase_service.client.table('videos').update({
                'likes': current_likes + 1
            }).eq('id', video_id).execute()
            
            return bool(response.data)
            
        except Exception as e:
            print(f"❌ Error liking video: {e}")
            return False
    
    async def increment_views(self, video_id: str) -> bool:
        """Increment video views"""
        try:
            # Get current views
            video = await self.get_video_by_id(video_id)
            if not video:
                return False
            
            current_views = video.get('views', 0)
            
            # Update views
            response = supabase_service.client.table('videos').update({
                'views': current_views + 1
            }).eq('id', video_id).execute()
            
            return bool(response.data)
            
        except Exception as e:
            print(f"❌ Error incrementing views: {e}")
            return False
    
    async def add_to_feed(self, content: Dict) -> Optional[str]:
        """
        Add generated content to feed
        
        Args:
            content: Dict with video_url, image_url, narration, etc.
        
        Returns:
            Feed item ID or None
        """
        try:
            feed_item = {
                'black_card_text': content.get('black_card'),
                'white_card_texts': content.get('white_cards'),
                'video_url': content.get('video_url'),
                'image_url': content.get('image_url'),
                'narration_script': content.get('narration', {}).get('script'),
                'narration_audio_url': content.get('narration', {}).get('audio_url'),
                'winner_name': content.get('winner', {}).get('player_id'),
                'likes': 0,
                'views': 0,
                'created_at': datetime.utcnow().isoformat()
            }
            
            response = supabase_service.client.table('videos').insert(
                feed_item
            ).execute()
            
            if response.data:
                print(f"✅ Added to feed: {response.data[0].get('id')}")
                return response.data[0].get('id')
            
            return None
            
        except Exception as e:
            print(f"❌ Error adding to feed: {e}")
            import traceback
            traceback.print_exc()
            return None


# Singleton instance
feed_service = FeedService()
