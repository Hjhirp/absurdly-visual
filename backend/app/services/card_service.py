import json
import random
from typing import List, Dict, Optional
from pathlib import Path
from ..models.card import Card, BlackCard, WhiteCard
from ..config import settings


class CardService:
    """Service for managing card decks"""
    
    def __init__(self, cards_file: str = "data/cards.json", use_supabase: bool = True):
        self.cards_file = Path(__file__).parent.parent.parent / cards_file
        self.black_cards: Dict[str, BlackCard] = {}
        self.white_cards: Dict[str, WhiteCard] = {}
        self.use_supabase = use_supabase and settings.SUPABASE_URL
        self.load_cards()
    
    def load_cards(self):
        """Load cards from Supabase or fallback to JSON"""
        if self.use_supabase:
            try:
                self.load_cards_from_supabase()
                return
            except Exception as e:
                print(f"⚠️  Failed to load from Supabase: {e}")
                print("⚠️  Falling back to JSON...")
        
        # Fallback to JSON
        try:
            with open(self.cards_file, 'r') as f:
                data = json.load(f)
            
            # Load black cards
            for card_data in data.get('black_cards', []):
                card = BlackCard(**card_data)
                self.black_cards[card.id] = card
            
            # Load white cards
            for card_data in data.get('white_cards', []):
                card = WhiteCard(**card_data)
                self.white_cards[card.id] = card
            
            print(f"✅ Loaded {len(self.black_cards)} black cards and {len(self.white_cards)} white cards from JSON")
        except Exception as e:
            print(f"❌ Error loading cards: {e}")
            raise
    
    def load_cards_from_supabase(self):
        """Load cards from Supabase"""
        from ..services.supabase_service import supabase_service
        
        # Load black cards
        result = supabase_service.client.table('black_cards').select('*').execute()
        for card_data in result.data:
            card = BlackCard(
                id=card_data['id'],
                text=card_data['text'],
                type='black',
                pick=card_data.get('pick', 1),
                pack=card_data.get('pack', 'base')
            )
            self.black_cards[card.id] = card
        
        # Load white cards
        result = supabase_service.client.table('white_cards').select('*').execute()
        for card_data in result.data:
            card = WhiteCard(
                id=card_data['id'],
                text=card_data['text'],
                type='white',
                nsfw=card_data.get('nsfw', False),
                pack=card_data.get('pack', 'base')
            )
            self.white_cards[card.id] = card
        
        print(f"✅ Loaded {len(self.black_cards)} black cards and {len(self.white_cards)} white cards from Supabase")
    
    async def load_cards_from_mongodb(self, db):
        """Load cards from MongoDB (async)"""
        try:
            self.db = db
            
            # Load black cards
            async for card_data in db.black_cards.find():
                # Remove MongoDB _id field
                card_data.pop('_id', None)
                card = BlackCard(**card_data)
                self.black_cards[card.id] = card
            
            # Load white cards
            async for card_data in db.white_cards.find():
                # Remove MongoDB _id field
                card_data.pop('_id', None)
                card = WhiteCard(**card_data)
                self.white_cards[card.id] = card
            
            print(f"✅ Loaded {len(self.black_cards)} black cards and {len(self.white_cards)} white cards from MongoDB")
        except Exception as e:
            print(f"❌ Error loading cards from MongoDB: {e}")
            # Fallback to JSON
            self.load_cards()
    
    def get_black_card(self, card_id: str) -> Optional[BlackCard]:
        """Get a specific black card"""
        return self.black_cards.get(card_id)
    
    def get_white_card(self, card_id: str) -> Optional[WhiteCard]:
        """Get a specific white card"""
        return self.white_cards.get(card_id)
    
    def get_random_black_cards(self, count: int, exclude: List[str] = None, topic: Optional[str] = None) -> List[str]:
        """Get random black card IDs with optional topic filtering"""
        exclude = exclude or []
        
        # Filter by topic if specified (using pack column)
        available = []
        for cid, card in self.black_cards.items():
            if cid in exclude:
                continue
            
            # If specific topic is selected, use ONLY that topic
            # If no topic or 'base', include ALL cards
            if topic and topic != 'base':
                if card.pack == topic:
                    available.append(cid)
            else:
                available.append(cid)
        
        return random.sample(available, min(count, len(available)))
    
    def get_random_white_cards(self, count: int, exclude: List[str] = None, 
                               censorship_level: str = "mild", topic: Optional[str] = None) -> List[str]:
        """Get random white card IDs with censorship and topic filtering"""
        exclude = exclude or []
        
        # Filter based on censorship level and topic
        available = []
        for card_id, card in self.white_cards.items():
            if card_id in exclude:
                continue
            
            if censorship_level == "family" and card.nsfw:
                continue
            
            # If specific topic is selected, use ONLY that topic
            # If no topic or 'base', include ALL cards
            if topic and topic != 'base':
                if card.pack == topic:
                    available.append(card_id)
            else:
                available.append(card_id)
        
        return random.sample(available, min(count, len(available)))
    
    def create_shuffled_deck(self, card_type: str, censorship_level: str = "mild", topic: Optional[str] = None) -> List[str]:
        """Create a shuffled deck of card IDs with optional topic filtering"""
        if card_type == "black":
            if topic and topic != 'base':
                # Use ONLY the specified topic
                deck = [
                    card_id for card_id, card in self.black_cards.items()
                    if card.pack == topic
                ]
            else:
                # Use ALL cards
                deck = list(self.black_cards.keys())
        else:
            deck = []
            for card_id, card in self.white_cards.items():
                # Censorship filter
                if censorship_level == "family" and card.nsfw:
                    continue
                
                # Topic filter (using pack column)
                if topic and topic != 'base':
                    # Use ONLY the specified topic
                    if card.pack == topic:
                        deck.append(card_id)
                else:
                    # Use ALL cards
                    deck.append(card_id)
        
        random.shuffle(deck)
        return deck
    
    def format_combination(self, black_card_id: str, white_card_ids: List[str]) -> str:
        """Format a card combination into readable text"""
        black_card = self.get_black_card(black_card_id)
        if not black_card:
            return ""
        
        white_texts = [
            self.get_white_card(wid).text if self.get_white_card(wid) else ""
            for wid in white_card_ids
        ]
        
        return black_card.format_with_answers(white_texts)
    
    def get_all_black_cards(self) -> List[BlackCard]:
        """Get all black cards"""
        return list(self.black_cards.values())
    
    def get_all_white_cards(self) -> List[WhiteCard]:
        """Get all white cards"""
        return list(self.white_cards.values())


# Singleton instance
card_service = CardService()
