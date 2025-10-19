#!/usr/bin/env python3
"""Quick test for Veo3 and Supabase"""
import asyncio
from app.services.veo_service import veo_service

async def test():
    print("🎬 Testing Veo3 video generation...\n")
    
    prompt = "A cat wearing sunglasses riding a skateboard"
    print(f"Prompt: {prompt}")
    print("⏳ Generating (1-3 minutes)...\n")
    
    video_url = await veo_service.generate_video(prompt)
    
    if video_url:
        print(f"\n✅ SUCCESS!")
        print(f"📹 Video URL: {video_url}")
    else:
        print(f"\n❌ Failed")

if __name__ == "__main__":
    asyncio.run(test())
