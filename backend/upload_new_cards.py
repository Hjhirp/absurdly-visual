#!/usr/bin/env python3
"""
Upload new cards to Supabase using requests/curl
Usage: python upload_new_cards.py <json_file_path>
Example: python upload_new_cards.py data/new_pack_cards.json
"""

import json
import sys
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')


def upload_cards(json_file_path: str):
    """Upload cards from JSON file to Supabase using REST API"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in environment")
        return False
    
    print(f"📂 Reading cards from {json_file_path}...")
    
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {json_file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON: {e}")
        return False
    
    black_cards = data.get('black_cards', [])
    white_cards = data.get('white_cards', [])
    
    print(f"📥 Found {len(black_cards)} black cards and {len(white_cards)} white cards")
    
    if not black_cards and not white_cards:
        print("⚠️  No cards found in file")
        return False
    
    # Headers for Supabase REST API
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
    }
    
    # Upload black cards
    if black_cards:
        print("\n📤 Uploading black cards...")
        black_data = []
        for card in black_cards:
            black_data.append({
                'id': card['id'],
                'text': card['text'],
                'pick': card.get('pick', 1),
                'pack': card.get('pack', 'custom')
            })
        
        try:
            response = requests.post(
                f'{SUPABASE_URL}/rest/v1/black_cards',
                headers=headers,
                json=black_data
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Uploaded {len(black_data)} black cards")
            else:
                print(f"❌ Error uploading black cards: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error uploading black cards: {e}")
            return False
    
    # Upload white cards in batches
    if white_cards:
        print("\n📤 Uploading white cards...")
        batch_size = 100
        white_data = []
        for card in white_cards:
            white_data.append({
                'id': card['id'],
                'text': card['text'],
                'nsfw': card.get('nsfw', False),
                'pack': card.get('pack', 'custom')
            })
        
        try:
            for i in range(0, len(white_data), batch_size):
                batch = white_data[i:i+batch_size]
                
                response = requests.post(
                    f'{SUPABASE_URL}/rest/v1/white_cards',
                    headers=headers,
                    json=batch
                )
                
                if response.status_code in [200, 201]:
                    print(f"  ✅ Uploaded batch {i//batch_size + 1} ({len(batch)} cards)")
                else:
                    print(f"❌ Error uploading white cards batch: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
            
            print(f"✅ Uploaded {len(white_data)} white cards")
        except Exception as e:
            print(f"❌ Error uploading white cards: {e}")
            return False
    
    print("\n🎉 Upload complete!")
    print(f"   Black cards: {len(black_cards)}")
    print(f"   White cards: {len(white_cards)}")
    
    # Print equivalent curl commands
    print("\n📋 Equivalent curl commands:")
    if black_cards:
        print(f"\n# Upload black cards:")
        print(f"curl -X POST '{SUPABASE_URL}/rest/v1/black_cards' \\")
        print(f"  -H 'apikey: {SUPABASE_KEY}' \\")
        print(f"  -H 'Authorization: Bearer {SUPABASE_KEY}' \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -H 'Prefer: resolution=merge-duplicates' \\")
        print(f"  -d @{json_file_path}")
    
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_new_cards.py <json_file_path>")
        print("Example: python upload_new_cards.py data/tech_pack.json")
        print("\nMake sure SUPABASE_URL and SUPABASE_KEY are set in your .env file")
        sys.exit(1)
    
    json_file = sys.argv[1]
    success = upload_cards(json_file)
    sys.exit(0 if success else 1)
