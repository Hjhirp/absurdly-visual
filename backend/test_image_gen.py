#!/usr/bin/env python3
"""Test image generation with Gemini 2.5 Flash Image (Nano Banana)"""
import asyncio
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_image_generation():
    """Test Gemini image generation"""
    print("🎨 Testing Gemini 2.5 Flash Image generation (Nano Banana)...\n")
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No GEMINI_API_KEY found in environment")
        return
    
    # Create client
    client = genai.Client(api_key=api_key)
    
    # Test prompt
    prompt = "A cat wearing sunglasses riding a skateboard, digital art style"
    print(f"📝 Prompt: {prompt}\n")
    print("⏳ Generating image...\n")
    
    try:
        # Generate image using Gemini 2.5 Flash Image
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
        )
        
        # Process response
        image_saved = False
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(f"📄 Text response: {part.text}")
            elif part.inline_data is not None:
                # Save the image
                image = Image.open(BytesIO(part.inline_data.data))
                output_path = "generated_image.png"
                image.save(output_path)
                print(f"✅ Image saved to: {output_path}")
                print(f"📐 Image size: {image.size}")
                image_saved = True
        
        if image_saved:
            print("\n✅ SUCCESS! Image generation completed.")
        else:
            print("\n⚠️  No image data found in response")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_image_generation())
