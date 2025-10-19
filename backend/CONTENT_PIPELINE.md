# Content Pipeline Documentation

## Overview

The content pipeline generates TikTok/Instagram Reels-ready content from Cards Against Humanity combinations using:

1. **Gemini 2.5 Flash Image** - Parallel image generation for multiple card combinations
2. **Gemini AI Judging** - Selects the winning combination
3. **Google Veo3** - Generates video for the winner
4. **Gemini TTS** - Creates humorous narration

**All powered by a single Gemini API key!**

## Architecture

```
Card Combinations
    ↓
[Parallel Image Generation] → Gemini 2.5 Flash Image
    ↓
[Winner Selection] → Gemini AI Judge
    ↓
[Video Generation] → Google Veo3
    ↓
[TTS Narration] → Gemini TTS
    ↓
Social Media Ready Content (9:16 vertical)
```

## Services

### 1. NanobananaService (`nanobanana_service.py`)

Generates images in parallel using Gemini 2.5 Flash Image model.

**Key Methods:**
- `generate_image(prompt, aspect_ratio="9:16")` - Single image generation using Gemini
- `generate_images_parallel(prompts)` - Parallel batch generation
- `generate_images_for_cards(black_card, white_card_options)` - Generate images for card combinations

**Note:** Despite the filename, this service now uses Gemini's native image generation instead of external APIs.

### 2. GeminiTTSService (`gemini_tts_service.py`)

Creates narration scripts and converts them to speech.

**Key Methods:**
- `generate_narration_script(black_card, white_cards, style)` - Create narration text
- `generate_speech(text, voice)` - Convert text to speech
- `generate_narrated_script(black_card, white_cards, style)` - Complete narration with audio

**Styles:** `humorous`, `dramatic`, `sarcastic`

### 3. ContentPipelineService (`content_pipeline_service.py`)

Orchestrates the full content creation workflow.

**Key Methods:**
- `generate_social_media_content(black_card, white_cards, style)` - Complete content for one combination
- `generate_content_for_round(black_card, submissions, style)` - Full game round with winner selection
- `generate_batch_content(combinations, style)` - Batch processing for multiple combinations

## API Endpoints

### POST `/api/content/generate`

Generate complete social media content for a single card combination.

**Request:**
```json
{
  "black_card": "What's the secret to a good relationship? _",
  "white_cards": ["Spontaneous combustion"],
  "narration_style": "humorous"
}
```

**Response:**
```json
{
  "image_url": "https://...",
  "video_url": "https://...",
  "narration": {
    "script": "The secret to a good relationship? Spontaneous combustion!",
    "audio_url": "https://..."
  },
  "black_card": "What's the secret to a good relationship? _",
  "white_cards": ["Spontaneous combustion"],
  "format": "9:16",
  "ready_for_social": true
}
```

### POST `/api/content/round`

Generate content for a full game round with multiple submissions.

**Request:**
```json
{
  "black_card": "What's the secret to a good relationship? _",
  "submissions": [
    {"player_id": "player1", "cards": ["Spontaneous combustion"]},
    {"player_id": "player2", "cards": ["A gentle caress"]},
    {"player_id": "player3", "cards": ["Explosive diarrhea"]}
  ],
  "narration_style": "humorous"
}
```

**Response:**
```json
{
  "winner": {
    "player_id": "player1",
    "cards": ["Spontaneous combustion"],
    "index": 0
  },
  "all_images": [
    {"cards": ["Spontaneous combustion"], "image_url": "https://..."},
    {"cards": ["A gentle caress"], "image_url": "https://..."},
    {"cards": ["Explosive diarrhea"], "image_url": "https://..."}
  ],
  "winning_image": {"cards": ["Spontaneous combustion"], "image_url": "https://..."},
  "video_url": "https://...",
  "narration": {
    "script": "...",
    "audio_url": "https://..."
  },
  "black_card": "What's the secret to a good relationship? _"
}
```

### POST `/api/content/batch`

Generate content for multiple combinations in parallel.

**Request:**
```json
{
  "combinations": [
    {
      "black_card": "What's the secret to a good relationship? _",
      "white_cards": ["Spontaneous combustion"]
    },
    {
      "black_card": "What's that smell? _",
      "white_cards": ["Dead parents"]
    }
  ],
  "narration_style": "humorous"
}
```

### POST `/api/images/generate`

Generate a single image using Gemini 2.5 Flash Image.

**Request:**
```json
{
  "black_card": "What's the secret to a good relationship? _",
  "white_cards": ["Spontaneous combustion"]
}
```

### POST `/api/narration/generate`

Generate TTS narration for a card combination.

**Request:**
```json
{
  "black_card": "What's the secret to a good relationship? _",
  "white_cards": ["Spontaneous combustion"],
  "narration_style": "humorous"
}
```

## Configuration

Add to your `.env` file:

```env
# Single API key for everything!
GEMINI_API_KEY=your_gemini_api_key
```

That's it! The Gemini API key powers:
- Image generation (Gemini 2.5 Flash Image)
- Video generation (Veo3)
- Text generation and AI judging (Gemini Pro)
- Text-to-speech narration (Gemini TTS)

## Workflow Example

### 1. Game Round Content Generation

```python
# During a game round, after players submit cards
submissions = [
    {"player_id": "alice", "cards": ["Spontaneous combustion"]},
    {"player_id": "bob", "cards": ["A gentle caress"]},
    {"player_id": "charlie", "cards": ["Explosive diarrhea"]}
]

# Generate images for all submissions in parallel
# Select winner using AI
# Generate video for winner
# Add narration
result = await content_pipeline_service.generate_content_for_round(
    black_card="What's the secret to a good relationship? _",
    submissions=submissions,
    narration_style="humorous"
)

# Result contains:
# - winner info
# - all images (for display during voting)
# - winning video (for social media)
# - narration audio
```

### 2. Social Media Content Creation

```python
# Create TikTok/Reels ready content
content = await content_pipeline_service.generate_social_media_content(
    black_card="What's that smell? _",
    white_cards=["Dead parents"],
    narration_style="humorous"
)

# Upload to TikTok/Instagram
# content.video_url - 9:16 vertical video
# content.narration.audio_url - humorous narration
```

### 3. Batch Content Creation

```python
# Generate content for multiple combinations
combinations = [
    {"black_card": "What's the secret to a good relationship? _", 
     "white_cards": ["Spontaneous combustion"]},
    {"black_card": "What's that smell? _", 
     "white_cards": ["Dead parents"]},
    # ... more combinations
]

results = await content_pipeline_service.generate_batch_content(
    combinations,
    narration_style="humorous"
)

# Each result is ready for social media posting
```

## Performance

- **Image Generation**: ~5-10 seconds per image (parallel)
- **Video Generation**: ~30-60 seconds (Veo3)
- **TTS Narration**: ~2-5 seconds
- **Total Pipeline**: ~40-75 seconds for complete content

### Parallel Processing

The pipeline maximizes parallelization:
- All submission images generate simultaneously
- Narration script and image generation run in parallel
- Only video generation is sequential (due to API limitations)

## Output Format

All content is optimized for TikTok/Instagram Reels:
- **Aspect Ratio**: 9:16 (vertical)
- **Video Duration**: 4-8 seconds
- **Image Format**: PNG
- **Audio Format**: MP3
- **Storage**: Supabase (with public URLs)

## Error Handling

Each service has fallback behavior:
- **Image Generation Fails**: Returns None, pipeline continues
- **Video Generation Fails**: Returns placeholder or None
- **TTS Fails**: Returns simple text without audio
- **Batch Processing**: Individual failures don't stop other items

## Future Enhancements

- [ ] Video editing to overlay narration on video
- [ ] Automatic posting to TikTok/Instagram APIs
- [ ] Custom voice selection for TTS
- [ ] Image style customization
- [ ] Video effects and transitions
- [ ] Subtitle generation
