"""
Veo3 Video Generation Service using Google GenAI SDK
"""
import asyncio
import time
import os
from typing import Optional
from google import genai
from ..config import settings


class VeoService:
    """Service for generating videos using Google Veo3"""
    
    def __init__(self):
        """Initialize Veo service"""
        self.api_key = settings.GEMINI_API_KEY
        # Set API key as environment variable for genai client
        if self.api_key:
            os.environ['GOOGLE_API_KEY'] = self.api_key
        self.client = None
        self.use_fast = settings.USE_VEO3_FAST
        self.default_duration = settings.VIDEO_DURATION
    
    def _get_client(self):
        """Get or create GenAI client"""
        if self.client is None:
            self.client = genai.Client(api_key=self.api_key)
        return self.client
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = None,
        aspect_ratio: str = "16:9"
    ) -> Optional[str]:
        """
        Generate a video using Veo3 with Google GenAI SDK
        
        Args:
            prompt: Text description of the video
            duration: Video duration in seconds (ignored for now)
            aspect_ratio: Video aspect ratio (ignored for now)
        
        Returns:
            Video file path or None if generation fails
        """
        if not self.api_key:
            print("⚠️  No Gemini API key configured for Veo3")
            return None
        
        try:
            client = self._get_client()
            
            # Use veo-3.0-fast-generate-001 model
            model = "veo-3.0-fast-generate-001"
            
            print(f"🎬 Generating video with {model}")
            print(f"📝 Prompt: {prompt[:100]}...")
            
            # Start video generation
            # Note: Resolution config not available in current API version
            operation = client.models.generate_videos(
                model=model,
                prompt=prompt
            )
            
            print(f"⏳ Video generation started, polling for completion...")
            
            # Poll for completion (run in thread pool to not block)
            loop = asyncio.get_event_loop()
            video_path = await loop.run_in_executor(
                None,
                self._wait_for_video,
                client,
                operation
            )
            
            return video_path
                    
        except Exception as e:
            print(f"❌ Veo3 video generation error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _wait_for_video(self, client, operation):
        """Wait for video generation to complete and upload to Supabase (blocking)"""
        max_wait = 180  # 3 minutes max (Veo3 can be slow)
        start_time = time.time()
        
        while not operation.done:
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                print(f"⏱️  Video generation timeout after {max_wait}s")
                return None
            
            print(f"⏳ Waiting... ({int(elapsed)}s)")
            time.sleep(10)
            operation = client.operations.get(operation)
        
        # Download and upload the generated video
        try:
            generated_video = operation.response.generated_videos[0]
            
            # Save to temp file first
            import uuid
            
            video_id = str(uuid.uuid4())
            temp_path = f"/tmp/{video_id}.mp4"
            
            client.files.download(file=generated_video.video)
            generated_video.video.save(temp_path)
            
            print(f"✅ Video downloaded to {temp_path}")
            
            # Upload to Supabase
            from ..services.supabase_service import supabase_service
            
            with open(temp_path, 'rb') as f:
                video_data = f.read()
            
            # Upload to Supabase storage
            file_path = f"{video_id}.mp4"
            
            try:
                result = supabase_service.client.storage.from_(settings.SUPABASE_BUCKET).upload(
                    file_path,
                    video_data,
                    file_options={"content-type": "video/mp4"}
                )
                
                if result:
                    # Get public URL
                    video_url = supabase_service.client.storage.from_(settings.SUPABASE_BUCKET).get_public_url(file_path)
                    print(f"✅ Video uploaded to Supabase: {video_url}")
                    
                    # Clean up temp file
                    import os
                    os.remove(temp_path)
                    
                    return video_url
                else:
                    print(f"❌ Failed to upload to Supabase")
                    return None
                    
            except Exception as upload_error:
                print(f"❌ Supabase upload error: {upload_error}")
                print(f"⚠️  Returning local file path as fallback")
                return temp_path
            
        except Exception as e:
            print(f"❌ Error processing video: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _poll_for_video(
        self,
        operation_name: str,
        max_attempts: int = 60,
        poll_interval: int = 1
    ) -> Optional[str]:
        """
        Poll for video generation completion
        
        Args:
            operation_name: The operation name from initial request
            max_attempts: Maximum number of polling attempts (60 = 1 min)
            poll_interval: Seconds between polls (1 sec for faster feedback)
        
        Returns:
            Video URL or None if timeout/error
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(max_attempts):
                try:
                    response = await client.get(
                        f"{self.base_url}/{operation_name}",
                        params={"key": self.api_key}
                    )
                    
                    if response.status_code != 200:
                        print(f"⚠️  Poll attempt {attempt + 1} failed: {response.status_code}")
                        await asyncio.sleep(poll_interval)
                        continue
                    
                    data = response.json()
                    
                    # Check if done
                    if data.get("done"):
                        if "response" in data and "videoUrl" in data["response"]:
                            print(f"✅ Video generated successfully after {attempt + 1} attempts")
                            return data["response"]["videoUrl"]
                        elif "error" in data:
                            print(f"❌ Video generation failed: {data['error']}")
                            return None
                    
                    # Still processing
                    print(f"⏳ Video generation in progress... ({attempt + 1}/{max_attempts})")
                    await asyncio.sleep(poll_interval)
                    
                except Exception as e:
                    print(f"⚠️  Poll error on attempt {attempt + 1}: {e}")
                    await asyncio.sleep(poll_interval)
        
        print(f"❌ Video generation timed out after {max_attempts} attempts")
        return None
    
    async def generate_video_for_cards(
        self,
        black_card_text: str,
        white_card_texts: list[str],
        prompt_generator=None
    ) -> Optional[str]:
        """
        Generate video for a card combination
        
        Args:
            black_card_text: The black card text
            white_card_texts: List of white card texts
            prompt_generator: Optional function to generate better prompts
        
        Returns:
            Video URL or None
        """
        # Generate prompt
        if prompt_generator:
            prompt = await prompt_generator(black_card_text, white_card_texts)
        else:
            # Simple prompt generation
            result = black_card_text
            for white_text in white_card_texts:
                result = result.replace('_', white_text, 1)
            prompt = f"A humorous short video scene: {result}"
        
        print(f"🎬 Generating video with prompt: {prompt[:100]}...")
        
        # Generate video
        video_url = await self.generate_video(prompt)
        
        if video_url:
            print(f"✅ Video URL: {video_url}")
        else:
            print(f"❌ Failed to generate video")
        
        return video_url


# Singleton instance
veo_service = VeoService()
