import httpx
from ..config import settings
from typing import Optional, Dict, Any
from .content_sanitizer import content_sanitizer


class FetchAIService:
    def __init__(self):
        self.agent_address = settings.FETCHAI_AGENT_ADDRESS
        self.agent_endpoint = settings.FETCHAI_AGENT_ENDPOINT
    
    async def generate_video(self, prompt: str, black_card: str, white_cards: list) -> Optional[Dict[str, str]]:
        """
        Generate video using Veo3 API with LLM-based content sanitization
        
        Args:
            prompt: The video generation prompt
            black_card: The black card text
            white_cards: List of white card texts
        
        Returns:
            Dict with video_id, supabase_url, and message
        """
        try:
            # Sanitize content using LLM before generation
            print(f"🤖 Using LLM to sanitize content...")
            sanitized_black, sanitized_whites = await content_sanitizer.sanitize_cards_with_llm(black_card, white_cards)
            sanitized_prompt = await content_sanitizer.sanitize_with_llm(prompt)
            
            print(f"🧹 Sanitized content for safe generation")
            if sanitized_black != black_card:
                print(f"   Black: {black_card} → {sanitized_black}")
            if sanitized_whites != white_cards:
                print(f"   Whites: {white_cards} → {sanitized_whites}")
            
            # Call Veo3 directly for testing
            from ..services.veo_service import veo_service
            import uuid
            
            video_id = str(uuid.uuid4())
            print(f"🎬 Generating video with Veo3: {video_id}")
            print(f"📝 Prompt: {sanitized_prompt}")
            
            # Generate video using Veo3
            video_url = await veo_service.generate_video(sanitized_prompt)
            
            if video_url:
                print(f"✅ Video generated successfully: {video_url}")
                return {
                    "video_id": video_id,
                    "supabase_url": video_url,
                    "message": "Video generated with Veo3"
                }
            else:
                print(f"❌ Veo3 generation failed - using placeholder")
                from ..config import settings
                return {
                    "video_id": video_id,
                    "supabase_url": settings.VIDEO_PLACEHOLDER_URL,
                    "message": "Veo3 generation failed"
                }
            
            # COMMENTED OUT: Fetch.ai agent integration
            # if not self.agent_endpoint:
            #     print("⚠️  Fetch.ai agent endpoint not configured - using placeholder")
            #     from ..config import settings
            #     import uuid
            #     video_id = str(uuid.uuid4())
            #     return {
            #         "video_id": video_id,
            #         "supabase_url": settings.VIDEO_PLACEHOLDER_URL,
            #         "message": "Agent not configured - using placeholder"
            #     }
            # 
            # # Prepare request matching agent's VideoGenerationRequest model
            # payload = {
            #     "prompt": sanitized_prompt,
            #     "model": "veo-3.0-fast-generate-001"
            # }
            # 
            # print(f"🤖 Calling Fetch.ai uAgent at {self.agent_endpoint}")
            # print(f"📝 Sanitized Prompt: {sanitized_prompt}")
            # 
            # async with httpx.AsyncClient(timeout=settings.VIDEO_GENERATION_TIMEOUT) as client:
            #     response = await client.post(
            #         self.agent_endpoint,
            #         json=payload,
            #         headers={
            #             "Content-Type": "application/json",
            #             "X-Agent-Address": self.agent_address
            #         }
            #     )
            #     
            #     if response.status_code == 200:
            #         data = response.json()
            #         video_id = data.get("video_id")
            #         supabase_url = data.get("supabase_url")
            #         message = data.get("message", "Video generation started")
            #         
            #         if video_id and supabase_url:
            #             print(f"✅ Video generation started: {video_id}")
            #             print(f"📍 Supabase URL: {supabase_url}")
            #             return {
            #                 "video_id": video_id,
            #                 "supabase_url": supabase_url,
            #                 "message": message
            #             }
            #         else:
            #             print(f"❌ Invalid response from agent: {data}")
            #             return None
            #     else:
            #         print(f"❌ Fetch.ai agent returned error: {response.status_code}")
            #         print(f"Response: {response.text}")
            #         return None
                    
        except httpx.TimeoutException:
            print(f"⏱️  Timeout calling Fetch.ai agent")
            return None
        except Exception as e:
            print(f"❌ Error calling Fetch.ai agent: {e}")
            return None
    
    async def check_agent_status(self) -> Dict[str, Any]:
        """Check if the Fetch.ai agent is available"""
        try:
            if not self.agent_endpoint:
                return {"status": "not_configured", "available": False}
            
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.agent_endpoint}/status")
                
                if response.status_code == 200:
                    return {"status": "online", "available": True, "data": response.json()}
                else:
                    return {"status": "error", "available": False, "code": response.status_code}
                    
        except Exception as e:
            return {"status": "offline", "available": False, "error": str(e)}


# Singleton instance
fetchai_service = FetchAIService()
