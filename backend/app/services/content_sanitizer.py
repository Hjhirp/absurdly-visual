"""
Content Sanitization Service
Uses LLM to convert NSFW/inappropriate content to safe, funny alternatives for video generation
"""

from typing import Dict, List, Tuple
import re


class ContentSanitizer:
    """Sanitizes content for safe video generation while keeping it funny"""
    
    def __init__(self):
        # Dictionary of replacements (case-insensitive)
        self.replacements = {
            # Explicit content
            "dick": "banana",
            "cock": "rooster",
            "penis": "cucumber",
            "balls": "tennis balls",
            "testicles": "stress balls",
            "vagina": "flower",
            "pussy": "kitten",
            "boobs": "balloons",
            "breasts": "pillows",
            "nipples": "buttons",
            "ass": "donkey",
            "butt": "peach",
            "anus": "donut",
            
            # Bodily functions
            "poop": "chocolate",
            "shit": "chocolate pudding",
            "pee": "lemonade",
            "piss": "apple juice",
            "fart": "toot",
            "vomit": "chunky soup",
            "puke": "smoothie",
            
            # Violence
            "kill": "tickle",
            "murder": "surprise party for",
            "stab": "poke",
            "shoot": "squirt water at",
            "blood": "ketchup",
            "dead": "sleeping",
            "die": "take a nap",
            
            # Drugs
            "cocaine": "sugar",
            "heroin": "candy",
            "meth": "rock candy",
            "weed": "oregano",
            "marijuana": "herbs",
            "drugs": "vitamins",
            
            # Profanity
            "fuck": "heck",
            "fucking": "hecking",
            "bitch": "puppy",
            "bastard": "rascal",
            "damn": "darn",
            "hell": "heck",
            
            # Sexual content
            "sex": "hugging",
            "sexual": "friendly",
            "orgasm": "sneeze",
            "masturbate": "high-five yourself",
            "porn": "art",
            "naked": "wearing invisible clothes",
            "nude": "in their birthday suit",
        }
        
        # Compile regex patterns for efficient matching
        self.patterns = {}
        for word, replacement in self.replacements.items():
            # Word boundary matching (case-insensitive)
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            self.patterns[pattern] = replacement
    
    def sanitize(self, text: str) -> str:
        """
        Sanitize text by replacing inappropriate content with funny alternatives
        
        Args:
            text: Original text to sanitize
            
        Returns:
            Sanitized text safe for video generation
        """
        sanitized = text
        
        # Apply all replacements
        for pattern, replacement in self.patterns.items():
            sanitized = pattern.sub(replacement, sanitized)
        
        return sanitized
    
    async def sanitize_with_llm(self, text: str) -> str:
        """
        Use LLM to sanitize content intelligently
        
        Args:
            text: Original text to sanitize
            
        Returns:
            Sanitized text that's safe but still funny
        """
        try:
            from ..services.ai_service import ai_service
            
            prompt = f"""You are a content moderator for a comedy video generator. Your job is to make inappropriate content safe for video generation while keeping it funny.

Original text: "{text}"

Rules:
1. Replace explicit sexual content with funny food metaphors (dick → banana, boobs → balloons)
2. Replace violence with silly alternatives (kill → tickle, stab → poke)
3. Replace drugs with candy/sweets (cocaine → sugar, weed → oregano)
4. Replace profanity with mild alternatives (fuck → heck, shit → poop)
5. Keep the humor and absurdity intact
6. If the text is already safe, return it unchanged
7. Be creative and funny with replacements

Return ONLY the sanitized text, nothing else."""

            sanitized = await ai_service.generate_text(prompt)
            return sanitized.strip().strip('"').strip("'")
            
        except Exception as e:
            print(f"⚠️  LLM sanitization failed, using rule-based: {e}")
            # Fallback to rule-based sanitization
            return self.sanitize(text)
    
    async def sanitize_cards_with_llm(self, black_card: str, white_cards: List[str]) -> Tuple[str, List[str]]:
        """
        Sanitize both black and white cards using LLM in a single batch call
        
        Args:
            black_card: Black card text
            white_cards: List of white card texts
            
        Returns:
            Tuple of (sanitized_black_card, sanitized_white_cards)
        """
        try:
            from ..services.ai_service import ai_service
            import json
            
            # Create batch request
            cards_list = [black_card] + white_cards
            cards_json = json.dumps(cards_list, indent=2)
            
            prompt = f"""You are a content moderator for a comedy video generator. Sanitize ALL the following cards in one batch to make them safe for video generation while keeping them funny.

Cards to sanitize:
{cards_json}

Rules:
1. Replace explicit sexual content with funny food metaphors (dick → banana, boobs → balloons)
2. Replace violence with silly alternatives (kill → tickle, stab → poke)
3. Replace drugs with candy/sweets (cocaine → sugar, weed → oregano)
4. Replace profanity with mild alternatives (fuck → heck, shit → poop)
5. Keep the humor and absurdity intact
6. If a card is already safe, return it unchanged
7. Be creative and funny with replacements

Return ONLY a JSON array of sanitized cards in the same order, nothing else. Example format:
["sanitized card 1", "sanitized card 2", ...]"""

            response = await ai_service.generate_text(prompt)
            
            # Parse JSON response
            sanitized_cards = json.loads(response.strip())
            
            if len(sanitized_cards) != len(cards_list):
                raise ValueError(f"Expected {len(cards_list)} cards, got {len(sanitized_cards)}")
            
            sanitized_black = sanitized_cards[0]
            sanitized_whites = sanitized_cards[1:]
            
            print(f"✅ Batch sanitized {len(cards_list)} cards in single LLM call")
            return sanitized_black, sanitized_whites
            
        except Exception as e:
            print(f"⚠️  LLM batch sanitization failed, using rule-based: {e}")
            # Fallback to rule-based sanitization
            return self.sanitize_cards(black_card, white_cards)
    
    def sanitize_cards(self, black_card: str, white_cards: List[str]) -> tuple[str, List[str]]:
        """
        Sanitize both black and white cards (rule-based fallback)
        
        Args:
            black_card: Black card text
            white_cards: List of white card texts
            
        Returns:
            Tuple of (sanitized_black_card, sanitized_white_cards)
        """
        sanitized_black = self.sanitize(black_card)
        sanitized_whites = [self.sanitize(card) for card in white_cards]
        
        return sanitized_black, sanitized_whites
    
    def get_sanitization_report(self, original: str, sanitized: str) -> Dict:
        """
        Get a report of what was changed
        
        Args:
            original: Original text
            sanitized: Sanitized text
            
        Returns:
            Dictionary with changes made
        """
        if original == sanitized:
            return {"changed": False, "original": original, "sanitized": sanitized}
        
        return {
            "changed": True,
            "original": original,
            "sanitized": sanitized,
            "note": "Content was sanitized for safe video generation"
        }


# Singleton instance
content_sanitizer = ContentSanitizer()
