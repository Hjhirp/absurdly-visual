#!/usr/bin/env python3
"""Test NanoBanana service image generation"""
import asyncio
from app.services.nanobanana_service import nanobanana_service

async def test():
    print("🎨 Testing NanoBanana Service...\n")
    
    # Test single image generation
    prompt = "A cat wearing sunglasses riding a skateboard, digital art style"
    print(f"Prompt: {prompt}")
    print("⏳ Generating image...\n")
    
    image_url = await nanobanana_service.generate_image(prompt)
    
    if image_url:
        print(f"\n✅ SUCCESS!")
        print(f"🖼️  Image URL: {image_url}")
    else:
        print(f"\n❌ Failed to generate image")
    
    # Test parallel generation
    print("\n" + "="*60)
    print("🎨 Testing parallel image generation...\n")
    
    prompts = [
        "A dog playing guitar on stage, concert lighting",
        "A robot chef cooking pasta, kitchen scene",
        "A penguin surfing a wave, tropical beach"
    ]
    
    print(f"Generating {len(prompts)} images in parallel...")
    image_urls = await nanobanana_service.generate_images_parallel(prompts)
    
    print(f"\n✅ Results:")
    for i, (prompt, url) in enumerate(zip(prompts, image_urls), 1):
        status = "✅" if url else "❌"
        print(f"{status} Image {i}: {prompt[:50]}...")
        if url:
            print(f"   URL: {url}")

if __name__ == "__main__":
    asyncio.run(test())
