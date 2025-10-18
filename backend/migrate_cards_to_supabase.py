#!/usr/bin/env python3
"""
Migrate cards from JSON to Supabase
Run: python migrate_cards_to_supabase.py
"""

import json
from app.config import settings
from app.services.supabase_service import supabase_service


def migrate_cards():
    print("🔄 Migrating cards to Supabase...")
    
    # Load cards from JSON
    with open('data/cards.json', 'r') as f:
        data = json.load(f)
    
    black_cards = data.get('black_cards', [])
    white_cards = data.get('white_cards', [])
    
    print(f"📥 Found {len(black_cards)} black cards and {len(white_cards)} white cards")
    
    # Migrate black cards
    print("\n📤 Uploading black cards...")
    black_data = []
    for card in black_cards:
        black_data.append({
            'id': card['id'],
            'text': card['text'],
            'pick': card.get('pick', 1),
            'pack': card.get('pack', 'base')
        })
    
    try:
        result = supabase_service.client.table('black_cards').upsert(black_data).execute()
        print(f"✅ Uploaded {len(black_data)} black cards")
    except Exception as e:
        print(f"❌ Error uploading black cards: {e}")
        return False
    
    # Migrate white cards in batches (Supabase has limits)
    print("\n📤 Uploading white cards...")
    batch_size = 100
    white_data = []
    for card in white_cards:
        white_data.append({
            'id': card['id'],
            'text': card['text'],
            'nsfw': card.get('nsfw', False),
            'pack': card.get('pack', 'base')
        })
    
    try:
        for i in range(0, len(white_data), batch_size):
            batch = white_data[i:i+batch_size]
            supabase_service.client.table('white_cards').upsert(batch).execute()
            print(f"  ✅ Uploaded batch {i//batch_size + 1} ({len(batch)} cards)")
        
        print(f"✅ Uploaded {len(white_data)} white cards")
    except Exception as e:
        print(f"❌ Error uploading white cards: {e}")
        return False
    
    print("\n🎉 Migration complete!")
    print(f"   Black cards: {len(black_data)}")
    print(f"   White cards: {len(white_data)}")
    return True


if __name__ == "__main__":
    success = migrate_cards()
    exit(0 if success else 1)
