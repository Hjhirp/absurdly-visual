"""
AI Service for card selection and video generation
"""
import random
import asyncio
from typing import List, Optional
import google.generativeai as genai
from ..config import settings


class AIService:
    """Service for AI player decisions and video generation"""
    
    PERSONALITIES = [
        "absurd", "edgy", "wholesome", "chaotic", 
        "sarcastic", "punny", "dark_humor", "innocent"
    ]
    
    def __init__(self):
        """Initialize AI service with Gemini"""
        self.system_prompt =  """
        You will receive a short description of a scenario from the game Cards Against Humanity.
        Your task is to interpret this scenario and generate a humorous, absurd, and visually engaging
        video that captures the comedic tone and timing of the scene. Use cinematic creativity, playful
        exaggeration, and expressive character actions to bring the humor to life.
        Description:

        """
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None
    
    def get_random_personality(self) -> str:
        """Get a random AI personality for variety"""
        return random.choice(self.PERSONALITIES)
    
    async def generate_text(self, prompt: str) -> str:
        """
        Generate text using Gemini
        
        Args:
            prompt: The text generation prompt
            
        Returns:
            Generated text
        """
        if not self.model:
            raise Exception("Gemini API not configured")
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            return response.text
        except Exception as e:
            print(f"❌ Gemini text generation error: {e}")
            raise
    
    async def select_cards(
        self, 
        black_card_text: str, 
        white_cards: List[dict], 
        pick_count: int,
        personality: str = "absurd"
    ) -> List[str]:
        """
        AI selects cards to play using Gemini for intelligent selection
        
        Args:
            black_card_text: The black card text
            white_cards: List of available white cards
            pick_count: Number of cards to select
            personality: AI personality (absurd, edgy, wholesome)
        
        Returns:
            List of selected card IDs
        """
        available_cards = [card for card in white_cards if card]
        
        if len(available_cards) < pick_count:
            return [card['id'] for card in available_cards]
        
        # Use Gemini for intelligent selection
        if self.model:
            try:
                # Create prompt for Gemini
                cards_text = "\n".join([f"{i+1}. {card['text']}" for i, card in enumerate(available_cards)])
                
                personality_instructions = {
                    "absurd": "Choose the most absurd, unexpected, and hilarious combinations. Be weird and random.",
                    "edgy": "Choose the darkest, most controversial, and edgy combinations. Push boundaries.",
                    "wholesome": "Choose the most wholesome, heartwarming, and funny combinations. Keep it sweet.",
                    "chaotic": "Choose the most chaotic, nonsensical, and unpredictable combinations. Embrace chaos.",
                    "sarcastic": "Choose the most sarcastic, ironic, and deadpan combinations. Be cynical.",
                    "punny": "Choose combinations that create puns, wordplay, or clever references.",
                    "dark_humor": "Choose combinations with dark, morbid humor. Be twisted but funny.",
                    "innocent": "Choose combinations that sound innocent but have double meanings."
                }
                
                prompt = f"""You are playing Cards Against Humanity. Select the {pick_count} funniest white card(s) to complete this black card.

Black Card: "{black_card_text}"

Available White Cards:
{cards_text}

Personality: {personality_instructions.get(personality, personality_instructions['absurd'])}

Respond with ONLY the numbers of the cards you select (e.g., "3, 7, 12" or just "5" if picking one card).
Choose cards that create the funniest, most creative combination."""

                response = await asyncio.to_thread(
                    self.model.generate_content,
                    prompt
                )
                
                # Parse response to get card numbers
                selected_numbers = []
                response_text = response.text.strip()
                
                # Extract numbers from response
                import re
                numbers = re.findall(r'\d+', response_text)
                selected_numbers = [int(n) for n in numbers[:pick_count]]
                
                # Convert to card IDs
                selected_ids = []
                for num in selected_numbers:
                    if 1 <= num <= len(available_cards):
                        selected_ids.append(available_cards[num - 1]['id'])
                
                # If we got valid selections, return them
                if len(selected_ids) == pick_count:
                    print(f"🤖 AI selected cards: {selected_ids}")
                    return selected_ids
                else:
                    print(f"⚠️  AI selection incomplete, falling back to random")
                    
            except Exception as e:
                print(f"❌ Gemini card selection error: {e}")
        
        # Fallback to random selection
        print(f"🎲 Using random card selection")
        selected = random.sample(available_cards, pick_count)
        return [card['id'] for card in selected]
    
    async def judge_submissions(
        self,
        black_card_text: str,
        submissions: List[dict],
        personality: str = "absurd"
    ) -> int:
        """
        AI judges submissions and picks a winner using Gemini
        
        Args:
            black_card_text: The black card text
            submissions: List of submissions with cards
            personality: AI personality type
        
        Returns:
            Index of winning submission
        """
        if not submissions:
            return 0
        
        # Use Gemini for intelligent judging
        if self.model and len(submissions) > 1:
            try:
                # Format submissions for Gemini
                submissions_text = ""
                for i, sub in enumerate(submissions):
                    cards_text = ", ".join(sub.get('cards', []))
                    submissions_text += f"{i+1}. {cards_text}\n"
                
                personality_criteria = {
                    "absurd": "most absurd, unexpected, and hilarious",
                    "edgy": "darkest, most controversial, and edgy",
                    "wholesome": "most wholesome, heartwarming, and funny"
                }
                
                prompt = f"""You are judging Cards Against Humanity submissions. Pick the winner.

Black Card: "{black_card_text}"

Submissions:
{submissions_text}

Criteria: Choose the {personality_criteria.get(personality, personality_criteria['absurd'])} combination.

Respond with ONLY the number of the winning submission (e.g., "2" or "5"). No explanation needed."""

                response = await asyncio.to_thread(
                    self.model.generate_content,
                    prompt
                )
                
                # Parse response to get winner number
                import re
                numbers = re.findall(r'\d+', response.text.strip())
                if numbers:
                    winner_num = int(numbers[0])
                    if 1 <= winner_num <= len(submissions):
                        winner_index = winner_num - 1
                        print(f"🏆 AI judge selected winner: submission {winner_num}")
                        return winner_index
                
                print(f"⚠️  AI judging failed, using random")
                
            except Exception as e:
                print(f"❌ Gemini judging error: {e}")
        
        # Fallback to random selection
        print(f"🎲 Using random winner selection")
        return random.randint(0, len(submissions) - 1)
    
    async def generate_video_prompt(
        self,
        black_card: str,
        white_cards: List[str]
    ) -> str:
        """
        Generate a video prompt from the card combination
        
        Args:
            black_card: The black card text
            white_cards: List of white card texts
        
        Returns:
            Video generation prompt
        """
        # Replace blanks with white cards
        result = black_card
        for white_card in white_cards:
            result = result.replace('_', white_card, 1)
        
        # Use Gemini to create a better video prompt
        if self.model:
            try:
                prompt = f"""Convert this Cards Against Humanity combination into a SHORT, vivid 4-second video scene (max 50 words):

"{result}"

Focus on ONE clear visual action or scene. Be specific and concrete. Keep it simple for fast video generation."""

                response = await asyncio.to_thread(
                    self.model.generate_content,
                    self.system_prompt + prompt
                )
                
                generated = response.text.strip()
                # Limit to 50 words for faster generation
                words = generated.split()
                if len(words) > 50:
                    generated = ' '.join(words[:50])
                
                return generated
            except Exception as e:
                print(f"Gemini prompt generation failed: {e}")
                # Fallback to simple prompt
                return f"A humorous scene: {result[:100]}"
        
        # Fallback if no Gemini - keep it short
        return f"A humorous scene: {result[:100]}"


# Singleton instance
ai_service = AIService()
