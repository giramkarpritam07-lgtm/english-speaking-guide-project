# English Speaking Guide - AI Powered

A comprehensive English learning platform with AI integration for Indian learners.

## Features

✅ **Web Interface** - Built with Streamlit
✅ **AI-Powered Analysis** - OpenAI GPT-3.5 or Google Gemini
✅ **Speech-to-Text** - Google Speech Recognition or Whisper
✅ **Text-to-Speech** - gTTS or pyttsx3
✅ **Dual Input Methods** - Text or Voice
✅ **5-Step Feedback Format** - Structured learning approach
✅ **Session History** - Track your progress

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup API Keys

Create a `.env` file in the project directory and add your API keys:

```
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
**Windows:**
```powershell
# Install PyAudio for microphone support
pip install pipwin
pipwin install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

## Running the App

### Web Version (Streamlit)

```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

### Command-Line Version

```bash
python app.py
```

## How to Use

1. **Choose AI Model**: Select OpenAI GPT-3.5 or Google Gemini from sidebar
2. **Select Input Method**: Text or Voice input
3. **Enable Audio Output** (optional): Get spoken feedback
4. **Practice**: Enter your sentence or speak
5. **Receive Feedback**: Get corrected version, explanation, tips, and follow-up questions

## Feedback Format (5 Steps)

1. **📝 Your Sentence** - Shows what you said
2. **✏️ Corrected Sentence** - Shows the corrected version (if needed)
3. **📚 Explanation** - Brief explanation in simple words
4. **🎤 Speaking Tips** - Tips to improve your English
5. **❓ Follow-up Question** - Question to continue conversation

## Project Structure

```
e:\AI english guide\
├── app.py                 # Command-line version
├── streamlit_app.py       # Web version (Streamlit)
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create this)
└── README.md             # This file
```

## API Integration

### OpenAI GPT-3.5
- Advanced English analysis
- Grammar, fluency, and naturalness feedback
- Conversational follow-up questions

### Google Gemini
- Similar to OpenAI, powered by Google
- Real-time analysis
- No waiting time for API calls

### Speech Recognition
- Google Speech Recognition API (free, built-in)
- Supports multiple languages
- Real-time audio processing

### Text-to-Speech
- gTTS (Google Text-to-Speech): Cloud-based, high quality
- pyttsx3: Offline, works without internet

## Tips for Best Results

1. **Speak Clearly**: For voice input, speak at normal speed
2. **Use Natural English**: Speak like you would in daily conversation
3. **Practice Regularly**: Use the app daily for best results
4. **Enable Audio**: Listen to feedback for pronunciation
5. **Review History**: Check past corrections to avoid repeating mistakes

## Troubleshooting

### "No microphone detected"
- Check if microphone is connected and enabled
- On Windows, ensure microphone is set as default input device
- On Linux, install ALSA: `sudo apt-get install alsa-utils`

### "API key not configured"
- Verify `.env` file exists in the project directory
- Check if API keys are correct and have proper permissions
- Ensure you haven't exceeded API limits

### "No audio playing"
- Install ffmpeg: `choco install ffmpeg` (Windows), `brew install ffmpeg` (macOS)
- Or disable audio and use text feedback only

## Future Features

- 🎯 Vocabulary building exercises
- 🎬 Movie dialogue practice
- 📖 Reading comprehension
- 🎧 Pronunciation scoring
- 📈 Progress tracking dashboard
- 🌐 Multi-language support

## License

Open source - Feel free to use and modify!

## Support

For issues or suggestions, check the documentation or create an issue.

Happy learning! 🌟
