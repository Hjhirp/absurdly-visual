"""
Card Generator Service - Uses AI to generate new black and white cards
"""
import random
import asyncio
import re
from typing import List, Dict, Optional
import google.generativeai as genai
from ..config import settings
from ..models.card import BlackCard, WhiteCard


class CardGeneratorService:
    """Service for generating new Cards Against Humanity style cards using AI"""
    
    def __init__(self):
        """Initialize card generator with Gemini"""
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            print("⚠️  Warning: Gemini API not configured. Card generation will not work.")
    
    def _get_next_card_id(self, card_type: str, existing_cards: List[str]) -> str:
        """
        Generate next card ID
        
        Args:
            card_type: 'black' or 'white'
            existing_cards: List of existing card IDs
            
        Returns:
            New unique card ID
        """
        prefix = 'b' if card_type == 'black' else 'w'
        
        # Extract numbers from existing IDs
        numbers = []
        for card_id in existing_cards:
            match = re.match(rf'{prefix}(\d+)', card_id)
            if match:
                numbers.append(int(match.group(1)))
        
        # Get next number
        next_num = max(numbers) + 1 if numbers else 1
        
        return f"{prefix}{next_num:03d}"
    
    async def generate_black_cards(
        self, 
        count: int = 1,
        pack: str = "ai-generated",
        temperature: float = 1.0,
        existing_cards: Optional[List[BlackCard]] = None
    ) -> List[BlackCard]:
        """
        Generate new black cards (question/prompt cards) using AI
        
        Args:
            count: Number of black cards to generate
            pack: Pack name for the cards
            temperature: AI creativity level (0.0-2.0, higher = more creative)
            existing_cards: List of existing black cards for context
            
        Returns:
            List of generated BlackCard objects
        """
        if not self.model:
            raise Exception("Gemini API not configured. Cannot generate cards.")
        
        # Sample existing cards for context
        sample_cards = []
        if existing_cards and len(existing_cards) > 0:
            sample_size = min(15, len(existing_cards))
            sample_cards = random.sample(existing_cards, sample_size)
        
        # Create prompt with examples
        examples = "\n".join([f"- {card.text} (pick: {card.pick})" for card in sample_cards])
        
        prompt = f"""You are generating BLACK CARDS for Cards Against Humanity, an adult party game.

BLACK CARDS are prompts/questions that contain blanks (_) where players fill in funny white cards.

RULES:
1. Each card MUST contain at least one underscore (_) as a blank
2. Most cards should have pick: 1 (one blank)
3. Some cards can have pick: 2 (two blanks) or pick: 3 (rare, three blanks)
4. Match the style: absurd, dark humor, inappropriate, unexpected
5. Keep cards short and punchy (usually one sentence)
6. Mix topics: pop culture, awkward situations, taboo subjects, daily life
7. End with periods, not question marks (unless it's clearly a question)

Here are EXAMPLES of existing black cards:
{examples if examples else '''- This quarantine really got me horny for _.
- Most people use their pantry to store food, I use mine to store _.
- Ew, I just stepped in _.
- While I was in the bathroom I saw _.
- I found the Hulk doing terrible things to _.
- Before I die I want to see _.
- Mom, Dad, there's something I need to tell you: I'm _.
- _ and _ , that's how I want to die. (pick: 2)
- I never understood _ until I encountered _. (pick: 2)'''}

Generate {count} NEW black cards in this format:
[TEXT] | [PICK_NUMBER]

For example:
My therapist says I need to stop _ | 1
The secret to happiness is _ and _ | 2
In my defense, I was left completely alone with _ | 1

Generate {count} cards NOW (one per line):"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=1000,
                )
            )
            
            generated_text = response.text.strip()
            lines = [line.strip() for line in generated_text.split('\n') if line.strip()]
            
            # Parse generated cards
            cards = []
            existing_ids = [card.id for card in existing_cards] if existing_cards else []
            
            for line in lines[:count]:  # Only take requested count
                # Parse format: "text | pick_number"
                parts = line.split('|')
                if len(parts) >= 2:
                    text = parts[0].strip()
                    try:
                        pick = int(parts[1].strip())
                    except:
                        pick = 1
                else:
                    # Fallback: assume pick=1 if not specified
                    text = line.strip()
                    pick = text.count('_') if '_' in text else 1
                
                # Clean up text
                text = text.strip('- ').strip()
                
                # Ensure it has blanks
                if '_' not in text:
                    text = text + " _"
                    pick = 1
                
                # Generate unique ID
                card_id = self._get_next_card_id('black', existing_ids)
                existing_ids.append(card_id)
                
                # Create card
                card = BlackCard(
                    id=card_id,
                    text=text,
                    type="black",
                    pick=pick,
                    pack=pack
                )
                cards.append(card)
                print(f"✅ Generated black card: {text[:50]}...")
            
            return cards
            
        except Exception as e:
            print(f"❌ Error generating black cards: {e}")
            raise
    
    async def generate_white_cards(
        self,
        count: int = 1,
        pack: str = "ai-generated",
        nsfw: bool = False,
        temperature: float = 1.0,
        existing_cards: Optional[List[WhiteCard]] = None
    ) -> List[WhiteCard]:
        """
        Generate new white cards (answer cards) using AI
        
        Args:
            count: Number of white cards to generate
            pack: Pack name for the cards
            nsfw: Whether to generate NSFW content
            temperature: AI creativity level (0.0-2.0, higher = more creative)
            existing_cards: List of existing white cards for context
            
        Returns:
            List of generated WhiteCard objects
        """
        if not self.model:
            raise Exception("Gemini API not configured. Cannot generate cards.")
        
        # Sample existing cards for context
        sample_cards = []
        if existing_cards and len(existing_cards) > 0:
            # Filter by NSFW preference for better examples
            filtered = [card for card in existing_cards if card.nsfw == nsfw]
            if not filtered:
                filtered = existing_cards
            sample_size = min(20, len(filtered))
            sample_cards = random.sample(filtered, sample_size)
        
        # Create prompt with examples
        examples = "\n".join([f"- {card.text}" for card in sample_cards])
        
        nsfw_instruction = "NSFW/mature content is ALLOWED and encouraged." if nsfw else "Keep content PG-13 (edgy but not explicitly sexual)."
        
        prompt = f"""You are generating WHITE CARDS for Cards Against Humanity, an adult party game.

WHITE CARDS are answers/nouns/phrases that players use to fill in black card blanks.

RULES:
1. Each card is a SHORT phrase or noun (usually 2-8 words)
2. NO blanks or underscores
3. Match the style: absurd, dark humor, unexpected, relatable
4. Mix topics: bodily functions, awkward situations, pop culture, objects, actions, people
5. Be specific and vivid (not generic)
6. Can be nouns, gerunds (verb+ing), or short phrases
7. {nsfw_instruction}

Here are EXAMPLES of existing white cards:
{examples if examples else '''- My crippling loneliness
- A pubic hair
- Ticks all over your body
- Pierced nipples
- Urine
- Projectile vomit
- Danny DeVito
- Sprite Cranberry
- Extreme nose hair
- The hostages
- Unfortunately, Zeus was horny
- 18 naked cowboys in the showers
- A sentient pineapple
- My Gandalf the Grey body pillow
- Colonoscopies
- Walking like an Egyptian'''}

Generate {count} NEW white cards (one per line, just the text):"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=800,
                )
            )
            
            generated_text = response.text.strip()
            lines = [line.strip() for line in generated_text.split('\n') if line.strip()]
            
            # Parse generated cards
            cards = []
            existing_ids = [card.id for card in existing_cards] if existing_cards else []
            
            for line in lines[:count]:  # Only take requested count
                # Clean up text
                text = line.strip('- •*').strip()
                
                # Skip if empty or too long
                if not text or len(text) > 100:
                    continue
                
                # Skip if it looks like a black card (has blanks)
                if '_' in text:
                    continue
                
                # Generate unique ID
                card_id = self._get_next_card_id('white', existing_ids)
                existing_ids.append(card_id)
                
                # Create card
                card = WhiteCard(
                    id=card_id,
                    text=text,
                    type="white",
                    nsfw=nsfw,
                    pack=pack
                )
                cards.append(card)
                print(f"✅ Generated white card: {text}")
            
            return cards
            
        except Exception as e:
            print(f"❌ Error generating white cards: {e}")
            raise
    
    async def generate_card_pack(
        self,
        black_count: int = 10,
        white_count: int = 30,
        pack_name: str = "ai-generated",
        nsfw_ratio: float = 0.3,
        temperature: float = 1.0,
        existing_black: Optional[List[BlackCard]] = None,
        existing_white: Optional[List[WhiteCard]] = None
    ) -> Dict[str, List]:
        """
        Generate a complete pack of cards
        
        Args:
            black_count: Number of black cards to generate
            white_count: Number of white cards to generate
            pack_name: Name for the card pack
            nsfw_ratio: Ratio of NSFW white cards (0.0-1.0)
            temperature: AI creativity level
            existing_black: Existing black cards for context
            existing_white: Existing white cards for context
            
        Returns:
            Dictionary with 'black_cards' and 'white_cards' lists
        """
        print(f"🎲 Generating card pack '{pack_name}'...")
        print(f"   Black cards: {black_count}, White cards: {white_count}")
        
        # Generate black cards
        black_cards = await self.generate_black_cards(
            count=black_count,
            pack=pack_name,
            temperature=temperature,
            existing_cards=existing_black
        )
        
        # Generate white cards (split between SFW and NSFW)
        nsfw_count = int(white_count * nsfw_ratio)
        sfw_count = white_count - nsfw_count
        
        white_cards = []
        
        if sfw_count > 0:
            sfw_cards = await self.generate_white_cards(
                count=sfw_count,
                pack=pack_name,
                nsfw=False,
                temperature=temperature,
                existing_cards=existing_white
            )
            white_cards.extend(sfw_cards)
        
        if nsfw_count > 0:
            nsfw_cards = await self.generate_white_cards(
                count=nsfw_count,
                pack=pack_name,
                nsfw=True,
                temperature=temperature,
                existing_cards=existing_white
            )
            white_cards.extend(nsfw_cards)
        
        print(f"✅ Generated pack '{pack_name}': {len(black_cards)} black, {len(white_cards)} white cards")
        
        return {
            "black_cards": black_cards,
            "white_cards": white_cards
        }


# Singleton instance
card_generator_service = CardGeneratorService()
