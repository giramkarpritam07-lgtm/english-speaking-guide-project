#!/usr/bin/env python3
"""
Diagnostic script to test Gemini API key and available models
Note: google.generativeai is deprecated, consider migrating to google.genai
"""

import os
import warnings
from dotenv import load_dotenv

# Suppress the FutureWarning from deprecated google.generativeai
warnings.filterwarnings('ignore', category=FutureWarning)

def test_gemini_api():
    """Test Gemini API key and list available models."""
    
    print("\n" + "="*60)
    print("🔍 Gemini API Diagnostics")
    print("="*60 + "\n")
    
    load_dotenv()
    
    gemini_key = os.getenv('GEMINI_API_KEY', '').strip()
    
    if not gemini_key:
        print("❌ No GEMINI_API_KEY found in .env file")
        return
    
    print(f"✅ Found API key: {gemini_key[:20]}...")
    
    try:
        import google.generativeai as genai
        print("✅ google.generativeai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import google.generativeai: {e}")
        return
    
    try:
        genai.configure(api_key=gemini_key)
        print("✅ API key configured")
    except Exception as e:
        print(f"❌ Failed to configure API: {e}")
        return
    
    # Try to list models
    print("\n📋 Available Models:")
    try:
        models = genai.list_models()
        for model in models:
            print(f"  - {model.name}")
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        return
    
    # Try to generate content
    print("\n🧪 Testing Model Generation:")
    models_to_test = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-flash-latest',
        'gemini-pro-latest'
    ]
    
    for model_name in models_to_test:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello")
            print(f"  ✅ {model_name}: Working!")
        except Exception as e:
            print(f"  ❌ {model_name}: {str(e)[:60]}")
    
    print("\n" + "="*60)
    print("✅ Diagnostics Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_gemini_api()
