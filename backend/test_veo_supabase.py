#!/usr/bin/env python3
"""
Test Veo3 to Supabase connection
Run: python test_veo_supabase.py
"""

import asyncio
from app.services.veo_service import veo_service
from app.services.supabase_service import supabase_service
from app.config import settings


async def test_veo_supabase():
    print("🧪 Testing Veo3 → Supabase Pipeline\n")
    print("=" * 60)
    
    # Test 1: Check Supabase connection
    print("Test 1: Supabase Connection")
    print("=" * 60)
    try:
        # Try to list buckets
        buckets = supabase_service.client.storage.list_buckets()
        print(f"✅ Connected to Supabase")
        print(f"📦 Available buckets: {[b.name for b in buckets]}")
        
        # Check if our bucket exists
        bucket_names = [b.name for b in buckets]
        if settings.SUPABASE_BUCKET in bucket_names:
            print(f"✅ Bucket '{settings.SUPABASE_BUCKET}' exists")
        else:
            print(f"⚠️  Bucket '{settings.SUPABASE_BUCKET}' not found!")
            print(f"   Create it in Supabase dashboard or run create_storage_bucket.sql")
            
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return
    
    print()
    
    # Test 2: Generate video with Veo3
    print("=" * 60)
    print("Test 2: Veo3 Video Generation")
    print("=" * 60)
    
    test_prompt = "A happy golden retriever playing fetch in a sunny park"
    print(f"Prompt: {test_prompt}")
    print(f"⏳ Generating video (this may take 1-3 minutes)...\n")
    
    try:
        video_url = await veo_service.generate_video(test_prompt)
        
        if video_url:
            print(f"\n✅ SUCCESS! Video generated and uploaded!")
            print(f"📹 Video URL: {video_url}")
            
            # Check if it's a Supabase URL
            if "supabase" in video_url:
                print(f"✅ Video is hosted on Supabase")
            else:
                print(f"⚠️  Video URL doesn't look like Supabase (might be local)")
            
            # Try to access the video
            print(f"\n🔍 Verifying video is accessible...")
            import httpx
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.head(video_url, timeout=10.0)
                    if response.status_code == 200:
                        print(f"✅ Video is publicly accessible!")
                        content_type = response.headers.get('content-type', '')
                        print(f"📄 Content-Type: {content_type}")
                    else:
                        print(f"⚠️  Video returned status {response.status_code}")
                except Exception as e:
                    print(f"⚠️  Could not verify video access: {e}")
        else:
            print(f"❌ Video generation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 3: Configuration check
    print("=" * 60)
    print("Test 3: Configuration")
    print("=" * 60)
    print(f"GEMINI_API_KEY: {'✅ Set' if settings.GEMINI_API_KEY else '❌ Missing'}")
    print(f"SUPABASE_URL: {'✅ Set' if settings.SUPABASE_URL else '❌ Missing'}")
    print(f"SUPABASE_KEY: {'✅ Set' if settings.SUPABASE_KEY else '❌ Missing'}")
    print(f"SUPABASE_BUCKET: {settings.SUPABASE_BUCKET}")
    print(f"USE_VEO3_FAST: {settings.USE_VEO3_FAST}")
    print(f"VIDEO_DURATION: {settings.VIDEO_DURATION}s")
    
    print()
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_veo_supabase())
