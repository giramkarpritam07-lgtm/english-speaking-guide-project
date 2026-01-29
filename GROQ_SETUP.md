# 🚀 Groq API Setup Guide

## Why Groq?
- ✅ **Completely FREE** - No payment method required
- ✅ **Very Fast** - Lightning-fast LLM inference
- ✅ **Generous Limits** - High rate limits on free tier
- ✅ **No Quota Issues** - Unlike Gemini's quota overages

## Quick Setup (2 minutes)

### Step 1: Get Your Groq API Key
1. Visit: **https://console.groq.com/keys**
2. Sign up or log in (free account)
3. Click **"Create New API Key"**
4. Copy your API key (starts with `gsk_`)

### Step 2: Add to .env File
Open `.env` file in your project folder and add:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

### Step 3: Restart App
Stop the app and run:
```bash
streamlit run streamlit_app.py
```

## Using Groq in the App
- Select **"Groq Mixtral (Free)"** from the AI model dropdown
- That's it! It will use the fast Groq API

## Available Models
Groq supports these models with free tier:
- **mixtral-8x7b-32768** (Default) - Fast, good quality
- **llama-3.1-70b-versatile** - More advanced
- **llama-3.1-8b-instant** - Smaller, faster

## Troubleshooting

### "Invalid API Key"
- Make sure you copied the full key (starts with `gsk_`)
- Restart the app after adding the key

### "Rate Limited"
- Free tier has limits, but they're generous
- If you hit limits, just wait a few minutes

### "API Error"
- Check your internet connection
- Verify your API key is correct

## Switching Between APIs
You can use both OpenAI and Groq:
- **Groq** (Free) - Great for basic analysis
- **OpenAI** (Paid) - More advanced features

Just set both API keys in `.env` and pick which one to use!

---
**Need more info?** Visit https://console.groq.com
