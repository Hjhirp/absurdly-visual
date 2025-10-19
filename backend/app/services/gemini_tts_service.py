"""
Gemini Text-to-Speech Service
Generates humorous narration for card combinations
"""
import asyncio
import uuid
import os
import wave
from typing import Optional
from google import genai
from google.genai import types
from ..config import settings


class GeminiTTSService:
    """Service for generating speech using Gemini TTS"""
    
    def __init__(self):
        """Initialize Gemini TTS service"""
        pass
    
    def _get_client(self):
        """Get or create GenAI client with fresh API key"""
        api_key = settings.GEMINI_API_KEY
        if api_key:
            os.environ['GOOGLE_API_KEY'] = api_key
        return genai.Client(api_key=api_key)
    
    async def generate_narration_script(
        self,
        black_card_text: str,
        white_cards: list[str],
        style: str = "humorous"
    ) -> str:
        """
        Generate a narration script for the card combination
        
        Args:
            black_card_text: The black card text
            white_cards: List of white card texts
            style: Narration style (humorous, dramatic, sarcastic)
        
        Returns:
            Narration script text
        """
        # Just fill in the blanks - simple and direct
        result = black_card_text
        for white_card in white_cards:
            result = result.replace('_', white_card, 1)
        
        print(f"📝 Narration script: {result}")
        return result
    
    def _save_wave_file(self, filename: str, pcm: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2):
        """Save PCM audio data as WAV file"""
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm)
    
    async def generate_speech(
        self,
        text: str,
        voice: str = "Kore"  # Cheerful voice, good for humor
    ) -> Optional[str]:
        """
        Generate speech audio from text using Gemini TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice name to use (Kore, Puck, Charon, Aoede)
        
        Returns:
            Audio file URL or None if generation fails
        """
        if not settings.GEMINI_API_KEY:
            print("⚠️  No Gemini API key configured")
            return None
        
        try:
            client = self._get_client()
            
            print(f"🎙️  Generating speech with Gemini TTS")
            print(f"📝 Text: {text[:100]}...")
            print(f"🎤 Voice: {voice}")
            
            # Generate speech using Gemini TTS with humorous tone
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=f"Say this in a fun, humorous way with good comedic timing: {text}",
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice
                                )
                            )
                        )
                    )
                )
            )
            
            # Extract audio data from response
            audio_data = response.candidates[0].content.parts[0].inline_data.data
            
            # Save audio to temp file
            audio_id = str(uuid.uuid4())
            temp_path = f"/tmp/{audio_id}.wav"
            
            # Save as WAV file
            self._save_wave_file(temp_path, audio_data)
            
            print(f"✅ Audio generated: {temp_path}")
            
            # Upload to Supabase
            audio_url = await self._upload_to_supabase(temp_path)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return audio_url
                
        except Exception as e:
            print(f"❌ Gemini TTS error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _upload_to_supabase(self, audio_path: str) -> Optional[str]:
        """Upload audio file to Supabase storage"""
        try:
            from ..services.supabase_service import supabase_service
            
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            # Upload to Supabase audio bucket
            audio_id = os.path.basename(audio_path)
            file_path = audio_id
            
            try:
                result = supabase_service.client.storage.from_('audio').upload(
                    file_path,
                    audio_data,
                    file_options={"content-type": "audio/wav"}
                )
                print(f"📤 Audio upload result: {result}")
            except Exception as upload_error:
                print(f"⚠️  Audio upload exception: {upload_error}")
                # File might already exist, try to get URL anyway
                pass
            
            # Always try to get public URL
            public_url = supabase_service.client.storage.from_('audio').get_public_url(file_path)
            print(f"✅ Audio URL from Supabase: {public_url}")
            return public_url
                
        except Exception as e:
            print(f"⚠️  Supabase upload error: {e}")
            return None
    
    async def generate_narrated_script(
        self,
        black_card_text: str,
        white_cards: list[str],
        style: str = "humorous"
    ) -> dict:
        """
        Generate both script and audio narration
        
        Args:
            black_card_text: The black card text
            white_cards: List of white card texts
            style: Narration style
        
        Returns:
            Dict with 'script' and 'audio_url' keys
        """
        # Generate script
        script = await self.generate_narration_script(black_card_text, white_cards, style)
        
        # Generate audio
        audio_url = await self.generate_speech(script)
        
        return {
            'script': script,
            'audio_url': audio_url
        }


# Singleton instance
gemini_tts_service = GeminiTTSService()
