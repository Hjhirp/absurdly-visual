#!/usr/bin/env python3
"""
Import cards from JSON to MongoDB
"""

import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "absurdly_visual")


async def import_cards():
    """Import cards from JSON to MongoDB"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Read cards from JSON
    with open('data/cards.json', 'r') as f:
        cards_data = json.load(f)
    
    # Clear existing cards
    await db.black_cards.delete_many({})
    await db.white_cards.delete_many({})
    
    print("📦 Importing cards to MongoDB...")
    
    # Import black cards
    if cards_data['black_cards']:
        result = await db.black_cards.insert_many(cards_data['black_cards'])
        print(f"✅ Imported {len(result.inserted_ids)} black cards")
    
    # Import white cards
    if cards_data['white_cards']:
        result = await db.white_cards.insert_many(cards_data['white_cards'])
        print(f"✅ Imported {len(result.inserted_ids)} white cards")
    
    # Create indexes for better performance
    await db.black_cards.create_index("id", unique=True)
    await db.black_cards.create_index("pack")
    await db.white_cards.create_index("id", unique=True)
    await db.white_cards.create_index("pack")
    await db.white_cards.create_index("nsfw")
    
    print("✅ Created indexes")
    
    # Verify counts
    black_count = await db.black_cards.count_documents({})
    white_count = await db.white_cards.count_documents({})
    
    print(f"\n📊 Database Summary:")
    print(f"   Black cards: {black_count}")
    print(f"   White cards: {white_count}")
    print(f"   Total cards: {black_count + white_count}")
    
    # Show pack distribution
    print(f"\n📦 Pack Distribution:")
    for pack in ["pg", "pg13"]:
        black = await db.black_cards.count_documents({"pack": pack})
        white = await db.white_cards.count_documents({"pack": pack})
        print(f"   {pack}: {black} black, {white} white")
    
    client.close()
    print("\n✅ Import complete!")


if __name__ == "__main__":
    asyncio.run(import_cards())
