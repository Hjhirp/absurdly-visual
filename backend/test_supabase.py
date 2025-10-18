#!/usr/bin/env python3
"""
Quick test script to verify Supabase connection
Run: python test_supabase.py
"""

import asyncio
from app.config import settings
from app.services.supabase_service import supabase_service


async def test_supabase():
    print("🔍 Testing Supabase Connection...")
    print(f"📍 Supabase URL: {settings.SUPABASE_URL}")
    print(f"🔑 API Key configured: {'✅' if settings.SUPABASE_KEY else '❌'}")
    print(f"📦 Bucket: {settings.SUPABASE_BUCKET}")
    print()
    
    try:
        # Test 1: Fetch videos (should return empty list initially)
        print("Test 1: Fetching videos...")
        videos = await supabase_service.get_videos_feed(limit=5)
        print(f"✅ Successfully connected! Found {len(videos)} videos")
        
        if videos:
            print("\n📹 Recent videos:")
            for video in videos[:3]:
                print(f"  - {video.get('winner_name', 'Unknown')}: {video.get('black_card_text', 'N/A')[:50]}...")
        else:
            print("  (No videos yet - play some games to generate videos!)")
        
        print("\n✅ All tests passed! Supabase is ready to use.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error connecting to Supabase:")
        print(f"   {str(e)}")
        print("\n💡 Make sure:")
        print("   1. SUPABASE_URL is correct in .env")
        print("   2. SUPABASE_KEY is correct in .env")
        print("   3. SQL schema was executed in Supabase")
        print("   4. Tables (videos, likes, comments) exist")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_supabase())
    exit(0 if success else 1)
