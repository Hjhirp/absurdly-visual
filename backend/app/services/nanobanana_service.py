"""
Gemini Image Generation Service
Generates images in parallel for card combinations using Gemini 2.5 Flash Image
"""
import asyncio
import uuid
import os
from typing import Optional, List
from google import genai
from PIL import Image
from io import BytesIO
from ..config import settings


class NanobananaService:
    """Service for generating images using Gemini Image Generation"""
    
    def __init__(self):
        """Initialize Gemini image generation service"""
        pass
    
    def _get_client(self):
        """Get or create GenAI client with fresh API key"""
        api_key = settings.GEMINI_API_KEY
        if api_key:
            os.environ['GOOGLE_API_KEY'] = api_key
        return genai.Client(api_key=api_key)
    
    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "9:16"  # Vertical for TikTok/Reels
    ) -> Optional[str]:
        """
        Generate a single image using Gemini 2.5 Flash Image
        
        Args:
            prompt: Text description of the image
            aspect_ratio: Image aspect ratio (9:16 for vertical video)
        
        Returns:
            Image URL or None if generation fails
        """
        if not settings.GEMINI_API_KEY:
            print("⚠️  No Gemini API key configured")
            return None
        
        try:
            client = self._get_client()
            
            print(f"🎨 Generating image with Gemini 2.5 Flash Image")
            print(f"📝 Prompt: {prompt[:100]}...")
            
            # Generate image using Gemini 2.5 Flash Image
            # Run in executor since the SDK call is synchronous
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=[prompt]
                )
            )
            
            # Process response - extract image from inline data
            image_saved = False
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    print(f"📄 Text response: {part.text}")
                elif part.inline_data is not None:
                    # Convert inline data to PIL Image
                    image = Image.open(BytesIO(part.inline_data.data))
                    
                    # Save to temp file
                    image_id = str(uuid.uuid4())
                    temp_path = f"/tmp/{image_id}.png"
                    image.save(temp_path)
                    
                    print(f"✅ Image generated: {temp_path} (size: {image.size})")
                    
                    # Upload to Supabase for persistence
                    uploaded_url = await self._upload_to_supabase_from_file(temp_path)
                    
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    image_saved = True
                    return uploaded_url
            
            if not image_saved:
                print(f"❌ No image data found in response")
            return None
                
        except Exception as e:
            print(f"❌ Gemini image generation error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _upload_to_supabase_from_file(self, file_path: str) -> Optional[str]:
        """Upload image file to Supabase storage"""
        try:
            from ..services.supabase_service import supabase_service
            
            # Read the image file
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            # Upload to Supabase images bucket
            image_id = os.path.basename(file_path)
            storage_path = image_id
            
            try:
                result = supabase_service.client.storage.from_('images').upload(
                    storage_path,
                    image_data,
                    file_options={"content-type": "image/png"}
                )
                print(f"📤 Upload result: {result}")
            except Exception as upload_error:
                print(f"⚠️  Upload exception: {upload_error}")
                # File might already exist, try to get URL anyway
                pass
            
            # Always try to get public URL
            public_url = supabase_service.client.storage.from_('images').get_public_url(storage_path)
            # Remove trailing ? if present
            if public_url and public_url.endswith('?'):
                public_url = public_url[:-1]
            print(f"✅ Image URL from Supabase: {public_url}")
            return public_url
                
        except Exception as e:
            print(f"⚠️  Supabase upload error: {e}")
            return None
    
    async def generate_images_parallel(
        self,
        prompts: List[str],
        aspect_ratio: str = "9:16"
    ) -> List[Optional[str]]:
        """
        Generate multiple images in parallel
        
        Args:
            prompts: List of text descriptions
            aspect_ratio: Image aspect ratio
        
        Returns:
            List of image URLs (None for failed generations)
        """
        print(f"🎨 Generating {len(prompts)} images in parallel...")
        
        # Create tasks for parallel generation
        tasks = [
            self.generate_image(prompt, aspect_ratio)
            for prompt in prompts
        ]
        
        # Run all generations in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and convert to URLs
        image_urls = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Image {i+1} generation failed: {result}")
                image_urls.append(None)
            else:
                image_urls.append(result)
        
        successful = sum(1 for url in image_urls if url is not None)
        print(f"✅ Generated {successful}/{len(prompts)} images successfully")
        
        return image_urls
    
    async def generate_images_for_cards(
        self,
        black_card_text: str,
        white_card_options: List[List[str]],
        prompt_generator=None
    ) -> List[dict]:
        """
        Generate images for multiple card combinations
        
        Args:
            black_card_text: The black card text
            white_card_options: List of white card combinations (each is a list of strings)
            prompt_generator: Optional function to generate better prompts
        
        Returns:
            List of dicts with 'cards' and 'image_url' keys
        """
        # Generate prompts for each combination
        prompts = []
        for white_cards in white_card_options:
            if prompt_generator:
                prompt = await prompt_generator(black_card_text, white_cards)
            else:
                # Simple prompt generation
                result = black_card_text
                for white_text in white_cards:
                    result = result.replace('_', white_text, 1)
                prompt = f"A humorous visual scene: {result}"
            prompts.append(prompt)
        
        # Generate all images in parallel
        image_urls = await self.generate_images_parallel(prompts)
        
        # Combine results
        results = []
        for i, (white_cards, image_url) in enumerate(zip(white_card_options, image_urls)):
            results.append({
                'cards': white_cards,
                'image_url': image_url,
                'prompt': prompts[i]
            })
        
        return results


# Singleton instance
nanobanana_service = NanobananaService()
