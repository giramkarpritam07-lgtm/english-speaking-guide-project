#!/usr/bin/env python3
"""
Setup script to configure API keys for English Speaking Guide
"""

import os
from pathlib import Path

def setup_api_keys():
    """Interactive setup for API keys."""
    
    print("\n" + "="*60)
    print("🌟 English Speaking Guide - API Key Setup")
    print("="*60 + "\n")
    
    env_path = Path(".env")
    
    # Check if .env exists
    if env_path.exists():
        print(f"✅ Found .env file")
    else:
        print(f"📝 Creating .env file...")
        env_path.write_text("# Environment variables for English Speaking Guide\n\n")
    
    # Read current .env
    current_content = env_path.read_text()
    
    print("\n📌 **API Key Sources:**")
    print("   OpenAI:     https://platform.openai.com/api-keys")
    print("   Groq (Free): https://console.groq.com/keys\n")
    
    # Setup OpenAI
    print("1️⃣ **OpenAI GPT-3.5 Setup**")
    print("   - OpenAI gives you $5 free credits for 3 months")
    openai_choice = input("   Do you want to add OpenAI API key? (y/n): ").strip().lower()
    
    if openai_choice == 'y':
        openai_key = input("   📌 Enter your OpenAI API key (sk-...): ").strip()
        if openai_key and not openai_key.startswith('your'):
            # Update .env
            if 'OPENAI_API_KEY=' in current_content:
                current_content = current_content.replace(
                    current_content.split('OPENAI_API_KEY=')[1].split('\n')[0],
                    openai_key,
                    1
                )
            else:
                current_content += f"\n# OpenAI API Key\nOPENAI_API_KEY={openai_key}\n"
            print("   ✅ OpenAI key saved!")
        else:
            print("   ❌ Invalid key!")
    
    print()
    
    # Setup Groq
    print("2️⃣ **Groq API Setup (FREE - Recommended!)**")
    print("   - Completely free with no payment method required")
    print("   - Very fast inference")
    print("   - Generous rate limits")
    groq_choice = input("   Do you want to add Groq API key? (y/n): ").strip().lower()
    
    if groq_choice == 'y':
        groq_key = input("   📌 Enter your Groq API key (gsk_...): ").strip()
        if groq_key and not groq_key.startswith('your'):
            # Update .env
            if 'GROQ_API_KEY=' in current_content:
                current_content = current_content.replace(
                    current_content.split('GROQ_API_KEY=')[1].split('\n')[0],
                    groq_key,
                    1
                )
            else:
                current_content += f"\n# Groq API Key\nGROQ_API_KEY={groq_key}\n"
            print("   ✅ Groq key saved!")
        else:
            print("   ❌ Invalid key!")
    
    print()
    
    # Save .env
    env_path.write_text(current_content)
    
    print("="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\n📌 **Next Steps:**")
    print("   1. Restart the Streamlit app:")
    print("      python -m streamlit run streamlit_app.py")
    print("   2. Open http://localhost:8501 in your browser")
    print("   3. Start practicing your English! 🌟\n")

if __name__ == "__main__":
    try:
        setup_api_keys()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
