#!/usr/bin/env python3
"""
Create Supabase storage buckets
Run: python create_supabase_buckets.py
"""

from app.services.supabase_service import supabase_service
from app.config import settings


def create_buckets():
    print("📦 Creating Supabase Storage Buckets\n")
    
    buckets_to_create = [
        {
            "name": settings.SUPABASE_BUCKET,
            "public": True,
            "description": "Video storage for game submissions"
        },
        {
            "name": settings.SUPABASE_WINNING_BUCKET,
            "public": True,
            "description": "Winning videos for the feed"
        }
    ]
    
    for bucket_config in buckets_to_create:
        bucket_name = bucket_config["name"]
        
        try:
            # Check if bucket exists
            existing_buckets = supabase_service.client.storage.list_buckets()
            bucket_names = [b.name for b in existing_buckets]
            
            if bucket_name in bucket_names:
                print(f"✅ Bucket '{bucket_name}' already exists")
            else:
                # Create bucket
                result = supabase_service.client.storage.create_bucket(
                    bucket_name,
                    options={
                        "public": bucket_config["public"],
                        "file_size_limit": 104857600,  # 100MB
                        "allowed_mime_types": ["video/mp4", "video/webm"]
                    }
                )
                print(f"✅ Created bucket '{bucket_name}'")
                
        except Exception as e:
            print(f"❌ Error with bucket '{bucket_name}': {e}")
    
    print("\n✅ Bucket setup complete!")
    print("\nYou can also create buckets manually in Supabase Dashboard:")
    print("1. Go to Storage section")
    print("2. Click 'New bucket'")
    print("3. Name: 'videos' (public)")
    print("4. Name: 'winning-videos' (public)")


if __name__ == "__main__":
    create_buckets()
