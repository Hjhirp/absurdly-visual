#!/usr/bin/env python3
"""
Test Veo3 video generation
Run: python test_veo3.py
"""

import asyncio
from app.services.veo_service import veo_service
from app.services.content_sanitizer import content_sanitizer


async def test_veo3():
    print("🎬 Testing Veo3 Video Generation\n")
    
    # Test 1: Simple prompt
    print("=" * 60)
    print("Test 1: Simple Prompt")
    print("=" * 60)
    
    simple_prompt = "A banana dancing in a disco with flashing lights"
    print(f"Prompt: {simple_prompt}\n")
    
    try:
        video_url = await veo_service.generate_video(simple_prompt)
        if video_url:
            print(f"✅ Success! Video URL: {video_url}\n")
        else:
            print(f"❌ Failed to generate video\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Test 2: Cards Against Humanity style
    print("=" * 60)
    print("Test 2: Cards Against Humanity Style")
    print("=" * 60)
    
    black_card = "What's the secret to a lasting marriage?"
    white_cards = ["My crippling loneliness", "Being covered in dirty underpants"]
    
    print(f"Black Card: {black_card}")
    print(f"White Cards: {white_cards}\n")
    
    # Sanitize with LLM
    print("🧹 Sanitizing content with LLM...")
    try:
        sanitized_black, sanitized_whites = await content_sanitizer.sanitize_cards_with_llm(
            black_card, 
            white_cards
        )
        
        print(f"Sanitized Black: {sanitized_black}")
        print(f"Sanitized Whites: {sanitized_whites}\n")
        
        # Create video prompt
        combined = f"{sanitized_black} Answer: {', '.join(sanitized_whites)}"
        video_prompt = f"A funny comedy sketch showing: {combined}. Make it absurd and humorous."
        
        print(f"Video Prompt: {video_prompt}\n")
        
        # Generate video
        print("🎬 Generating video with Veo3...")
        video_url = await veo_service.generate_video(video_prompt)
        
        if video_url:
            print(f"✅ Success! Video URL: {video_url}\n")
        else:
            print(f"❌ Failed to generate video\n")
            
    except Exception as e:
        print(f"❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
    
    # Test 3: Check Veo3 configuration
    print("=" * 60)
    print("Test 3: Configuration Check")
    print("=" * 60)
    
    from app.config import settings
    
    print(f"Gemini API Key configured: {'✅' if settings.GEMINI_API_KEY else '❌'}")
    print(f"Video duration: {settings.VIDEO_DURATION} seconds")
    print(f"Use Veo3 Fast: {settings.USE_VEO3_FAST}")
    print(f"Video timeout: {settings.VIDEO_GENERATION_TIMEOUT} seconds\n")
    
    if not settings.GEMINI_API_KEY:
        print("⚠️  GEMINI_API_KEY not set in .env file!")
        print("   Add your Gemini API key to enable video generation\n")
    
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_veo3())
