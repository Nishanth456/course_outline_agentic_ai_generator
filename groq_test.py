#!/usr/bin/env python3
"""
Quick test script to verify Groq API is working
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key and model
api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

print(f"🔧 Testing Groq API...")
print(f"   Model: {model}")
print(f"   API Key: {'✅ Found' if api_key else '❌ Not found'}")
print()

if not api_key:
    print("❌ API Key not found! Set GROQ_API_KEY in .env")
    exit(1)

try:
    print("📦 Importing groq...")
    from groq import Groq
    print("   ✅ Import successful")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    exit(1)

try:
    print("\n🔌 Creating Groq client...")
    client = Groq(api_key=api_key)
    print("   ✅ Client created")
except Exception as e:
    print(f"   ❌ Client creation failed: {e}")
    exit(1)

try:
    print(f"\n📤 Sending request: 'Say HI' to {model}...")
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Say HI"
            }
        ]
    )
    print("   ✅ Response received!")
    print()
    print("=" * 60)
    print(f"Response: {completion.choices[0].message.content}")
    print("=" * 60)
    print()
    print("✅ GROQ API IS WORKING!")
except Exception as e:
    print(f"   ❌ API call failed: {e}")
    exit(1)
