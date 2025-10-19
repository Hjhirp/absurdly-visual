#!/usr/bin/env python3
"""
Setup Supabase Storage Bucket
Creates the 'videos' bucket and sets up public access policies
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.stage')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
BUCKET_NAME = 'videos'

def setup_bucket():
    """Create and configure the videos bucket"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env.stage")
        return
    
    print(f"🔗 Connecting to Supabase: {SUPABASE_URL}")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Check if bucket exists
        print(f"\n📦 Checking if bucket '{BUCKET_NAME}' exists...")
        buckets = supabase.storage.list_buckets()
        bucket_exists = any(b['name'] == BUCKET_NAME for b in buckets)
        
        if bucket_exists:
            print(f"✅ Bucket '{BUCKET_NAME}' already exists")
        else:
            # Create bucket
            print(f"📦 Creating bucket '{BUCKET_NAME}'...")
            supabase.storage.create_bucket(
                BUCKET_NAME,
                options={
                    'public': True,
                    'file_size_limit': 52428800,  # 50MB
                    'allowed_mime_types': ['image/png', 'image/jpeg', 'audio/wav', 'video/mp4']
                }
            )
            print(f"✅ Bucket '{BUCKET_NAME}' created successfully")
        
        # Set up policies
        print(f"\n🔐 Setting up storage policies...")
        
        # Note: Policies are typically set via Supabase dashboard or SQL
        # For public bucket, files are automatically accessible
        
        print(f"""
✅ Setup Complete!

Bucket: {BUCKET_NAME}
Access: Public
URL Pattern: {SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/[filename]

Next steps:
1. Images will be saved as: {BUCKET_NAME}/[uuid].png
2. Audio will be saved as: {BUCKET_NAME}/[uuid].wav
3. Videos will be saved as: {BUCKET_NAME}/[uuid].mp4

All files are publicly accessible via their URLs.
""")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_bucket()
