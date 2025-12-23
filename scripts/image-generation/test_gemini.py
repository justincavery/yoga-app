#!/usr/bin/env python3
"""
Test script to verify Gemini API integration
Generates a single test image
"""

import requests
import base64
import json
from pathlib import Path

API_KEY = "AIzaSyB3dFFtrAYYXVdePiWTSbrN0eRKWxxojck"
MODEL = "models/gemini-2.5-flash-image"

def test_generation():
    """Test generating a single image"""

    # Simple test prompt
    prompt = "blonde yoga instructor, 25-30 years old, wearing yoga leggings, standing in mountain pose with feet together, arms at sides, perfect upright posture, full body visible, yoga studio, natural lighting, professional photo"

    print("Testing Gemini Image Generation API...")
    print(f"Model: {MODEL}")
    print(f"Prompt: {prompt[:100]}...")
    print()

    url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt}
            ]
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": "3:4"
            }
        }
    }

    try:
        print("Sending request to Gemini API...")
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=120
        )

        print(f"Response status: {response.status_code}")
        print()

        if response.status_code == 200:
            result = response.json()
            print("Response structure:")
            print(json.dumps({k: type(v).__name__ for k, v in result.items()}, indent=2))
            print()

            if 'candidates' in result and len(result['candidates']) > 0:
                print(f"✓ Successfully got response from API")

                # Extract image from response
                candidate = result['candidates'][0]
                parts = candidate.get('content', {}).get('parts', [])

                image_data = None
                for part in parts:
                    if 'inlineData' in part:
                        image_data = part['inlineData'].get('data')
                        break

                if image_data:
                    image_bytes = base64.b64decode(image_data)
                    output_path = Path("test_output.png")

                    with open(output_path, 'wb') as f:
                        f.write(image_bytes)

                    print(f"✓ Saved test image to: {output_path}")
                    print(f"  Image size: {len(image_bytes)} bytes")
                else:
                    print("✗ No image data in response")
                    print("Parts found:")
                    print(json.dumps(parts, indent=2))
            else:
                print("✗ No candidates in response")
                print("Full response:")
                print(json.dumps(result, indent=2))

        else:
            print(f"✗ API Error {response.status_code}")
            print("Response:")
            print(response.text)

    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_generation()
