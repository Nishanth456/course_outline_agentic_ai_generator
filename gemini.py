#!/usr/bin/env python3
"""
Quick test script to verify Gemini API is working
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key and model
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
model = os.getenv("LLM_MODEL", "gemini-2.5-flash")

print(f"🔧 Testing Gemini API...")
print(f"   Model: {model}")
print(f"   API Key: {'✅ Found' if api_key else '❌ Not found'}")
print()

if not api_key:
    print("❌ API Key not found! Set GOOGLE_API_KEY or GEMINI_API_KEY in .env")
    exit(1)

try:
    print("📦 Importing google.genai...")
    from google import genai
    print("   ✅ Import successful")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    exit(1)

try:
    print("\n🔌 Creating Gemini client...")
    client = genai.Client(api_key=api_key)
    print("   ✅ Client created")
except Exception as e:
    print(f"   ❌ Client creation failed: {e}")
    exit(1)

try:
    print(f"\n📤 Sending request: 'HI' to {model}...")
    response = client.models.generate_content(
        model=model,
        contents="Say HI"
    )
    print("   ✅ Response received!")
    print()
    print("=" * 60)
    print(f"Response: {response.text}")
    print("=" * 60)
    print()
    print("✅ API IS WORKING!")
except Exception as e:
    print(f"   ❌ API call failed: {e}")
    exit(1)
