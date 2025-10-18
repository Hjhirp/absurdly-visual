import httpx
from typing import Dict, List, Optional
from ..config import settings


class FetchClient:
    """Client for communicating with Fetch.ai agents"""
    
    def __init__(self):
        self.coordinator_url = settings.FETCH_COORDINATOR_URL
        self.video_agent_url = settings.FETCH_VIDEO_AGENT_URL
        self.ai_player_url = settings.FETCH_AI_PLAYER_URL
        self.api_key = settings.FETCH_API_KEY
        self.timeout = 30.0
    
    async def _make_request(self, url: str, data: dict) -> dict:
        """Make an HTTP request to a Fetch.ai agent"""
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error communicating with Fetch.ai agent: {e}")
                return {"error": str(e)}
    
    async def coordinate_action(self, action: str, data: dict) -> dict:
        """Send a coordination request to the coordinator agent"""
        if not self.coordinator_url:
            return {"error": "Coordinator URL not configured"}
        
        payload = {
            "action": action,
            "data": data
        }
        
        return await self._make_request(self.coordinator_url, payload)
    
    async def generate_video(self, black_card: str, white_cards: List[str], 
                            style: str = "comedic") -> dict:
        """Request video generation from the video agent"""
        if not self.video_agent_url:
            # Fallback: use coordinator
            return await self.coordinate_action("generate_video", {
                "blackCard": black_card,
                "whiteCards": white_cards,
                "style": style
            })
        
        payload = {
            "blackCard": black_card,
            "whiteCards": white_cards,
            "style": style
        }
        
        return await self._make_request(self.video_agent_url, payload)
    
    async def get_video_status(self, generation_id: str) -> dict:
        """Check the status of a video generation"""
        if not self.video_agent_url:
            return {"error": "Video agent URL not configured"}
        
        url = f"{self.video_agent_url}/status/{generation_id}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error checking video status: {e}")
                return {"error": str(e)}
    
    async def ai_player_select_card(self, black_card: str, available_cards: List[str],
                                   personality: str = "absurd",
                                   game_context: dict = None) -> dict:
        """Request AI player to select a card"""
        if not self.ai_player_url:
            # Fallback: use coordinator
            return await self.coordinate_action("ai_play", {
                "blackCard": black_card,
                "availableCards": available_cards,
                "personality": personality,
                "gameContext": game_context or {}
            })
        
        payload = {
            "blackCard": black_card,
            "availableCards": available_cards,
            "personality": personality,
            "gameContext": game_context or {}
        }
        
        return await self._make_request(self.ai_player_url, payload)
    
    async def generate_video_mock(self, black_card: str, white_cards: List[str]) -> dict:
        """Mock video generation for testing without Veo3 API"""
        # Return a placeholder video URL
        import hashlib
        combination = f"{black_card}{''.join(white_cards)}"
        video_id = hashlib.md5(combination.encode()).hexdigest()[:8]
        
        return {
            "videoUrl": f"https://placeholder-video.com/{video_id}.mp4",
            "generationId": video_id,
            "status": "completed",
            "mock": True
        }
    
    async def ai_player_select_card_mock(self, available_cards: List[str]) -> dict:
        """Mock AI player selection for testing without Gemini API"""
        import random
        
        if not available_cards:
            return {"error": "No cards available"}
        
        selected = random.choice(available_cards)
        
        return {
            "selectedCardId": selected,
            "confidence": random.uniform(0.6, 0.95),
            "reasoning": "Selected based on comedic timing and absurdity factor",
            "mock": True
        }


# Singleton instance
fetch_client = FetchClient()
