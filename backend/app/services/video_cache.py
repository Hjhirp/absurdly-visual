from typing import Optional
import hashlib
import json
from datetime import datetime, timedelta


class VideoCache:
    """In-memory video cache"""
    
    def __init__(self):
        self.cache_duration_seconds = 86400  # 24 hours
        self.memory_cache: dict = {}
        # Silent initialization - no Redis needed
    
    def _generate_key(self, black_card: str, white_cards: list) -> str:
        """Generate a cache key from card combination"""
        combination = json.dumps({
            "black": black_card,
            "white": sorted(white_cards)
        }, sort_keys=True)
        hash_key = hashlib.sha256(combination.encode()).hexdigest()
        return f"video:{hash_key}"
    
    def get(self, black_card: str, white_cards: list) -> Optional[str]:
        """Get cached video URL if exists"""
        key = self._generate_key(black_card, white_cards)
        
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if datetime.utcnow() < entry["expires_at"]:
                return entry["video_url"]
            else:
                del self.memory_cache[key]
        
        return None
    
    def set(self, black_card: str, white_cards: list, video_url: str, 
            permanent: bool = False):
        """Cache a video URL"""
        key = self._generate_key(black_card, white_cards)
        
        expires_at = datetime.max if permanent else datetime.utcnow() + timedelta(seconds=self.cache_duration_seconds)
        self.memory_cache[key] = {
            "video_url": video_url,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "permanent": permanent
        }
    
    def clear_expired(self):
        """Remove expired cache entries"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if now >= entry["expires_at"]
        ]
        for key in expired_keys:
            del self.memory_cache[key]
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = len(self.memory_cache)
        permanent = sum(1 for entry in self.memory_cache.values() if entry["permanent"])
        
        return {
            "total_entries": total,
            "permanent_entries": permanent,
            "temporary_entries": total - permanent,
            "cache_type": "memory"
        }


# Singleton instance
video_cache = VideoCache()
