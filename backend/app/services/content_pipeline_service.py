"""
Content Pipeline Service
Orchestrates the full content creation workflow:
1. Generate images in parallel for multiple card combinations
2. Select winning combination
3. Generate video with Veo3
4. Add TTS narration
"""
import asyncio
from typing import List, Optional, Dict
from .nanobanana_service import nanobanana_service
from .gemini_tts_service import gemini_tts_service
from .veo_service import veo_service
from .ai_service import ai_service
from .feed_service import feed_service


class ContentPipelineService:
    """Service for orchestrating the full content creation pipeline"""
    
    def __init__(self):
        """Initialize content pipeline service"""
        pass
    
    async def generate_content_for_round(
        self,
        black_card_text: str,
        submissions: List[Dict],  # List of {player_id, cards: [white_card_texts]}
        narration_style: str = "humorous"
    ) -> Dict:
        """
        Full content generation pipeline for a game round
        
        Args:
            black_card_text: The black card text
            submissions: List of player submissions with white cards
            narration_style: Style for TTS narration
        
        Returns:
            Dict with winner info, images, video, and audio
        """
        print("🎬 Starting content generation pipeline...")
        
        # Step 1: Select winning submission first (AI judge)
        print("\n🏆 Step 1: Selecting winning submission...")
        winner_index = await self._select_winner(
            black_card_text,
            submissions,
            []  # No images yet
        )
        
        winner_submission = submissions[winner_index]
        
        print(f"✅ Winner: {winner_submission.get('player_id', 'Unknown')}")
        print(f"   Cards: {winner_submission['cards']}")
        
        # Step 2: Generate images + narration in parallel
        print("\n⚡ Step 2: Generating images + narration in parallel...")
        
        # Create parallel tasks
        image_task = self._generate_images_for_submissions(black_card_text, submissions)
        narration_task = gemini_tts_service.generate_narrated_script(
            black_card_text,
            winner_submission['cards'],
            style=narration_style
        )
        
        # Run in parallel
        image_results, narration = await asyncio.gather(image_task, narration_task)
        
        winner_image = image_results[winner_index]
        
        # Step 3: Generate video for winning combination
        print("\n🎥 Step 3: Generating video with Veo3...")
        video_url = await self._generate_video_for_winner(
            black_card_text,
            winner_submission['cards']
        )
        
        # Compile final result
        result = {
            'winner': {
                'player_id': winner_submission.get('player_id'),
                'cards': winner_submission['cards'],
                'index': winner_index
            },
            'all_images': image_results,
            'winning_image': winner_image,
            'video_url': video_url,
            'narration': narration,
            'black_card': black_card_text
        }
        
        print("\n✅ Content generation pipeline complete!")
        print(f"   - Images generated: {sum(1 for img in image_results if img.get('image_url'))}/{len(image_results)}")
        print(f"   - Video URL: {video_url or 'Failed'}")
        print(f"   - Audio URL: {narration.get('audio_url') or 'Failed'}")
        
        # Add to public feed
        if video_url:
            print("\n📱 Adding to TikTok-like feed...")
            feed_content = {
                'black_card': black_card_text,
                'white_cards': winner_submission['cards'],
                'video_url': video_url,
                'image_url': winner_image.get('image_url'),
                'narration': narration,
                'winner': winner_submission
            }
            feed_id = await feed_service.add_to_feed(feed_content)
            if feed_id:
                result['feed_id'] = feed_id
                print(f"✅ Added to feed: {feed_id}")
        
        return result
    
    async def _generate_images_for_submissions(
        self,
        black_card_text: str,
        submissions: List[Dict]
    ) -> List[Dict]:
        """Generate images for all submissions in parallel"""
        white_card_options = [sub['cards'] for sub in submissions]
        
        # Use AI service to generate better prompts
        image_results = await nanobanana_service.generate_images_for_cards(
            black_card_text,
            white_card_options,
            prompt_generator=ai_service.generate_video_prompt
        )
        
        return image_results
    
    async def _select_winner(
        self,
        black_card_text: str,
        submissions: List[Dict],
        image_results: List[Dict]
    ) -> int:
        """
        Select winning submission
        Can use AI judging or human voting
        """
        # For now, use AI judging
        winner_index = await ai_service.judge_submissions(
            black_card_text,
            submissions,
            personality="absurd"
        )
        
        return winner_index
    
    async def _generate_video_for_winner(
        self,
        black_card_text: str,
        white_cards: List[str]
    ) -> Optional[str]:
        """Generate video for the winning combination"""
        video_url = await veo_service.generate_video_for_cards(
            black_card_text,
            white_cards,
            prompt_generator=ai_service.generate_video_prompt
        )
        
        return video_url
    
    async def generate_social_media_content(
        self,
        black_card_text: str,
        white_cards: List[str],
        narration_style: str = "humorous"
    ) -> Dict:
        """
        Generate complete social media content (TikTok/Reels ready)
        Sequential generation: image -> narration -> video
        
        Args:
            black_card_text: The black card text
            white_cards: Winning white cards
            narration_style: Style for narration
        
        Returns:
            Dict with all content URLs and metadata
        """
        print("🎬 Generating social media content...")
        
        # Step 1: Generate image
        print("📸 Step 1: Generating image...")
        prompt = await ai_service.generate_video_prompt(black_card_text, white_cards)
        image_url = await nanobanana_service.generate_image(prompt, aspect_ratio="9:16")
        
        # Step 2: Generate narration
        print("🎙️  Step 2: Generating narration...")
        narration = await gemini_tts_service.generate_narrated_script(
            black_card_text,
            white_cards,
            style=narration_style
        )
        
        # Step 3: Generate video
        print("🎥 Step 3: Generating video...")
        video_url = await veo_service.generate_video_for_cards(
            black_card_text,
            white_cards,
            prompt_generator=ai_service.generate_video_prompt
        )
        
        return {
            'image_url': image_url,
            'video_url': video_url,
            'narration': narration,
            'black_card': black_card_text,
            'white_cards': white_cards,
            'format': '9:16',  # Vertical for TikTok/Reels
            'ready_for_social': True
        }
    
    async def generate_batch_content(
        self,
        card_combinations: List[Dict],  # List of {black_card, white_cards}
        narration_style: str = "humorous"
    ) -> List[Dict]:
        """
        Generate content for multiple card combinations sequentially
        Useful for batch content creation
        
        Args:
            card_combinations: List of card combinations
            narration_style: Style for narration
        
        Returns:
            List of content results
        """
        print(f"🎬 Generating content for {len(card_combinations)} combinations...")
        
        # Generate content sequentially to avoid rate limits
        results = []
        for i, combo in enumerate(card_combinations):
            print(f"\n📦 Processing combination {i+1}/{len(card_combinations)}...")
            try:
                result = await self.generate_social_media_content(
                    combo['black_card'],
                    combo['white_cards'],
                    narration_style
                )
                results.append(result)
            except Exception as e:
                print(f"❌ Content {i+1} generation failed: {e}")
                results.append(None)
        
        successful = sum(1 for r in results if r is not None)
        print(f"\n✅ Generated {successful}/{len(card_combinations)} content pieces successfully")
        
        return results


# Singleton instance
content_pipeline_service = ContentPipelineService()
