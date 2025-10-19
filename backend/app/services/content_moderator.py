"""
Content Moderation Service
Uses Gemini to sanitize content before image/video generation
"""
import google.generativeai as genai
from ..config import settings


class ContentModerator:
    """Moderate and sanitize content before generation"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def sanitize_prompt(self, prompt: str) -> str:
        """
        Sanitize prompt to avoid policy violations while keeping humor
        
        Args:
            prompt: Original prompt
            
        Returns:
            Sanitized prompt safe for image/video generation
        """
        try:
            sanitize_instruction = f"""You are a content moderator for a comedy game. 
Your job is to rewrite prompts to be safe for image/video generation APIs while keeping the humor.

Rules:
- Remove explicit sexual content, violence, gore, hate speech
- Keep the joke/humor intact but make it PG-13 appropriate
- Replace problematic words with creative alternatives
- Keep it funny and absurd
- If the prompt is already safe, return it unchanged

Original prompt: {prompt}

Return ONLY the sanitized prompt, nothing else."""

            response = self.model.generate_content(sanitize_instruction)
            sanitized = response.text.strip()
            
            print(f"🛡️ Moderated: '{prompt[:50]}...' → '{sanitized[:50]}...'")
            return sanitized
            
        except Exception as e:
            print(f"❌ Moderation error: {e}")
            # Fallback: return original if moderation fails
            return prompt
    
    async def is_safe(self, text: str) -> bool:
        """
        Quick check if content is safe
        
        Returns:
            True if safe, False if needs moderation
        """
        try:
            check_instruction = f"""Is this text safe for a PG-13 audience? 
Answer only YES or NO.

Text: {text}"""

            response = self.model.generate_content(check_instruction)
            result = response.text.strip().upper()
            
            return "YES" in result
            
        except Exception as e:
            print(f"❌ Safety check error: {e}")
            return True  # Default to safe if check fails


# Singleton
content_moderator = ContentModerator()
