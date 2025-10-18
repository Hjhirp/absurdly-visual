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
    
    def __init__(self):
        """Initialize AI service with Gemini"""
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    async def select_cards(
        self, 
        black_card_text: str, 
        white_cards: List[dict], 
        pick_count: int,
        personality: str = "absurd"
    ) -> List[str]:
        """
        AI selects cards to play
        
        Args:
            black_card_text: The black card text with blanks
            white_cards: List of available white cards
            pick_count: Number of cards to pick
            personality: AI personality type
        
        Returns:
            List of selected card IDs
        """
        # For now, use simple random selection
        # TODO: Use Gemini to make intelligent selections
        available_cards = [card for card in white_cards if card]
        
        if len(available_cards) < pick_count:
            return [card['id'] for card in available_cards]
        
        selected = random.sample(available_cards, pick_count)
        return [card['id'] for card in selected]
    
    async def judge_submissions(
        self,
        black_card_text: str,
        submissions: List[dict],
        personality: str = "absurd"
    ) -> int:
        """
        AI judges submissions and picks a winner
        
        Args:
            black_card_text: The black card text
            submissions: List of submissions with cards
            personality: AI personality type
        
        Returns:
            Index of winning submission
        """
        # For now, use random selection
        # TODO: Use Gemini to judge based on humor/absurdity
        if not submissions:
            return 0
        
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
                    prompt
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
