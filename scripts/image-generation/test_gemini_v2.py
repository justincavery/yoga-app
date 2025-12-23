#!/usr/bin/env python3
"""
Test script to verify Gemini API integration using google-generativeai library
Generates a single test image
"""

import google.generativeai as genai
from PIL import Image
from io import BytesIO
from pathlib import Path

API_KEY = "AIzaSyB3dFFtrAYYXVdePiWTSbrN0eRKWxxojck"
MODEL = "gemini-2.5-flash-image"

def test_generation():
    """Test generating a single image"""

    # Configure the API
    genai.configure(api_key=API_KEY)

    # Simple test prompt
    prompt = "blonde yoga instructor, 25-30 years old, wearing yoga leggings, standing in mountain pose with feet together, arms at sides, perfect upright posture, full body visible, yoga studio, natural lighting, professional photo"

    print("Testing Gemini Image Generation API...")
    print(f"Model: {MODEL}")
    print(f"Prompt: {prompt[:100]}...")
    print()

    try:
        print("Generating image...")

        # Create model instance
        model = genai.GenerativeModel(MODEL)

        # Generate image
        response = model.generate_content(prompt)

        print(f"✓ Got response from API")
        print(f"Candidates: {len(response.candidates)}")
        print()

        # Extract image from response
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data is not None:
                    print("✓ Found image in response")
                    print(f"  Mime type: {part.inline_data.mime_type}")
                    print(f"  Data type: {type(part.inline_data.data)}")
                    print(f"  Data size: {len(part.inline_data.data)} bytes")

                    # Save raw data directly
                    output_path = Path("test_output.png")
                    with open(output_path, 'wb') as f:
                        f.write(part.inline_data.data)

                    print(f"✓ Saved test image to: {output_path}")

                    # Try to verify it's a valid image
                    try:
                        img = Image.open(output_path)
                        print(f"  Image size: {img.size}")
                        print(f"  Image format: {img.format}")
                    except Exception as e:
                        print(f"  Warning: Could not verify image: {e}")

                    return True

                elif part.text is not None:
                    print(f"Text response: {part.text}")

        print("✗ No image found in response")
        return False

    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_generation()
    exit(0 if success else 1)
