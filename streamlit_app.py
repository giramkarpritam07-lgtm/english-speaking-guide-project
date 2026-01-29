import streamlit as st
import os
from dotenv import load_dotenv
import speech_recognition as sr
from io import BytesIO
from gtts import gTTS
import json
from datetime import datetime
import tempfile
import wave
from database import DatabaseManager
from login import login_page
from language_support import get_text
from PIL import Image
import io
import hashlib
import time

# Import PDF handling
try:
    from PyPDF2 import PdfReader
    pypdf_available = True
except:
    pypdf_available = False

# Import AI model APIs
try:
    from openai import OpenAI
    openai_available = True
except:
    openai_available = False

try:
    from groq import Groq
    groq_available = True
except:
    groq_available = False

# Load environment variables
load_dotenv()

# Initialize database
db = DatabaseManager()

# Check if user is logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Initialize language if not set
if 'user_language' not in st.session_state:
    st.session_state.user_language = "English"

# If not logged in, show login page
if not st.session_state.logged_in:
    login_page()
    st.stop()

# Helper function to check if API key is valid
def is_valid_api_key(key):
    """Check if API key is not a placeholder."""
    if not key:
        return False
    if 'your_' in key.lower() or 'here' in key.lower():
        return False
    if key.startswith('your'):
        return False
    return True

# Page configuration
st.set_page_config(
    page_title="English Speaking Guide",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Professional Background
st.markdown("""
    <style>
    .stApp {
        background: #f8f9fa;
        min-height: 100vh;
    }
    
    .main {
        padding: 2rem;
        background: #ffffff;
        border-radius: 8px;
        margin: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    .stTitle {
        color: #1f3a57;
        text-align: center;
        font-size: 48px;
    }
    
    .stSubheader {
        color: #2c5aa0;
    }
    
    .feedback-box {
        background: #f0f4f8;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #2c5aa0;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .correct-box {
        background: #f0f8f4;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #2d7a3e;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

class EnglishGuideStreamlit:
    """Streamlit-based English Speaking Guide with AI integration."""
    
    # Class-level cache to avoid duplicate API calls
    _analysis_cache = {}
    _cache_max_size = 100
    _last_api_call = {}
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.session_history = []
        self.setup_ai_models()
    
    def setup_ai_models(self):
        """Setup AI model configurations."""
        self.openai_client = None
        self.groq_client = None
        self.openai_key_valid = False
        self.groq_key_valid = False
        
        openai_key = os.getenv('OPENAI_API_KEY', '').strip()
        groq_key = os.getenv('GROQ_API_KEY', '').strip()
        
        if openai_available and is_valid_api_key(openai_key):
            try:
                self.openai_client = OpenAI(api_key=openai_key)
                self.openai_key_valid = True
            except Exception as e:
                st.error(f"❌ OpenAI API key validation failed: {str(e)[:100]}")
        
        if groq_available and is_valid_api_key(groq_key):
            try:
                self.groq_client = Groq(api_key=groq_key)
                self.groq_key_valid = True
                st.success("✅ Groq API connected successfully!")
            except Exception as e:
                st.warning(f"⚠️ Groq setup issue: {str(e)[:100]}")
    
    def capture_voice_input(self):
        """Capture audio from microphone and convert to text."""
        try:
            # Check if pyaudio is available
            try:
                import pyaudio
            except ImportError:
                st.error("❌ PyAudio is not installed on Python 3.13")
                st.info("💡 **Solution:** Use the **Browser Audio Input** option instead - no installation needed!")
                st.markdown("""
                #### Why Browser Audio Input is Better:
                - ✅ No installation required
                - ✅ Works on all devices
                - ✅ Same functionality as microphone
                - ✅ No PyAudio dependency issues
                """)
                return None
            
            # Check if microphone is available
            try:
                with sr.Microphone() as source:
                    # Set noise level adjustment time
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    
                    st.info("🎤 Listening... Please speak now! (10 seconds timeout)")
                    
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                    
                st.info("🔄 Processing speech...")
                
                # Recognize speech using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                return text
                
            except sr.UnknownValueError:
                st.error("❌ Could not understand audio. Please speak clearly and try again.")
                return None
            except sr.RequestError as e:
                st.error(f"❌ Speech recognition API error: {str(e)[:100]}")
                return None
            except OSError as e:
                st.error(f"❌ Microphone not found. Please check your audio device. Error: {str(e)[:100]}")
                return None
                
        except Exception as e:
            st.error(f"❌ Voice input error: {str(e)[:100]}")
            return None
    
    def capture_browser_voice_input(self, audio_key="default_audio"):
        """Capture voice using browser's Web Speech API."""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e8f5e9 0%, #f0f8f4 100%); padding: 20px; border-radius: 10px; border-left: 5px solid #2d7a3e; margin: 1rem 0;">
            <h3>🎤 Voice Input (Like Copilot)</h3>
            <p><strong>How it works:</strong></p>
            <ul>
                <li>Click the microphone button below</li>
                <li>Speak clearly in English</li>
                <li>Your speech will be converted to text</li>
                <li>AI will analyze and respond with voice</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Use Streamlit's audio input with unique key
        audio_data = st.audio_input("🎙️ Record your voice:", label_visibility="collapsed", key=audio_key)
        
        if audio_data is not None:
            st.success("✅ Audio captured! Processing your speech...")
            
            try:
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_data.getbuffer())
                    tmp_path = tmp_file.name
                
                # Use speech recognition on the saved file
                recognizer = sr.Recognizer()
                with sr.AudioFile(tmp_path) as source:
                    audio = recognizer.record(source)
                
                # Recognize speech
                text = recognizer.recognize_google(audio)
                st.success(f"✅ Recognized: **{text}**")
                
                # Clean up
                os.remove(tmp_path)
                
                return text
            
            except sr.UnknownValueError:
                st.error("❌ Could not understand audio. Please speak clearly and try again.")
                return None
            except sr.RequestError as e:
                st.error(f"❌ Speech recognition error: {str(e)[:80]}")
                return None
            except Exception as e:
                st.error(f"❌ Error: {str(e)[:80]}")
                return None
        
        return None
    
    def voice_conversation_mode(self, ai_model: str):
        """Interactive voice conversation mode like Google Assistant - friendly, simple, one-to-one conversation."""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; color: white; margin: 1rem 0; box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);">
            <h2 style="color: white; margin: 0;">🎤 Voice Conversation Assistant</h2>
            <p style="margin: 10px 0 0 0; font-size: 16px;">Talk naturally with your AI English teacher - just like Google Assistant!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize conversation history
        if 'voice_conversation_history' not in st.session_state:
            st.session_state.voice_conversation_history = []
        
        # Display conversation in a chat-like format
        st.markdown("### 💬 Your Conversation")
        st.markdown("""
        <style>
        .user-message {
            background: #e3f2fd;
            padding: 12px 15px;
            border-radius: 12px;
            margin: 12px 0;
            width: fit-content;
            max-width: 80%;
            margin-left: auto;
            border-left: 4px solid #667eea;
        }
        .ai-message {
            background: #f3e5f5;
            padding: 12px 15px;
            border-radius: 12px;
            margin: 12px 0;
            width: fit-content;
            max-width: 80%;
            border-left: 4px solid #764ba2;
        }
        .conversation-pair {
            margin-bottom: 16px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create container for conversation
        conversation_container = st.container()
        
        # Display conversation history with user input immediately followed by AI output
        if st.session_state.voice_conversation_history:
            with conversation_container:
                i = 0
                while i < len(st.session_state.voice_conversation_history):
                    msg = st.session_state.voice_conversation_history[i]
                    
                    # Display user message
                    if msg['type'] == 'user':
                        st.markdown(f"""
                        <div class="user-message">
                            <strong>You:</strong> {msg['text']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display corresponding AI response immediately below
                        if i + 1 < len(st.session_state.voice_conversation_history) and st.session_state.voice_conversation_history[i + 1]['type'] == 'ai':
                            ai_msg = st.session_state.voice_conversation_history[i + 1]
                            st.markdown(f"""
                            <div class="ai-message">
                                <strong>🤖 AI:</strong> {ai_msg['text']}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Display voice response if it exists
                            if 'voice_buffer' in ai_msg:
                                st.audio(ai_msg['voice_buffer'], format="audio/mp3", autoplay=True)
                            
                            i += 2  # Skip the next message since we already displayed it
                        else:
                            i += 1
                    else:
                        i += 1
        else:
            st.info("👋 **Ready to chat?** Click the microphone button below and start speaking in English!")
        
        st.markdown("---")
        
        # Voice input section
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🎙️ Click to Speak")
            audio_data = st.audio_input("🎤", label_visibility="collapsed", key=f"voice_conv_{len(st.session_state.voice_conversation_history)}")
        
        if audio_data is not None:
            # Processing with spinner
            with st.spinner("🎵 Listening..."):
                try:
                    # Save audio to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(audio_data.getbuffer())
                        tmp_path = tmp_file.name
                    
                    # Recognize speech
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(tmp_path) as source:
                        audio = recognizer.record(source)
                    
                    user_text = recognizer.recognize_google(audio)
                    
                    # Clean up
                    os.remove(tmp_path)
                    
                    # Add user message to history
                    st.session_state.voice_conversation_history.append({
                        'type': 'user',
                        'text': user_text,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    
                    # Get AI response
                    with st.spinner("🤖 AI is thinking..."):
                        if ai_model == "OpenAI GPT-3.5":
                            analysis = self.analyze_with_openai(user_text)
                        elif ai_model == "Groq Mixtral (Free)":
                            analysis = self.analyze_with_groq(user_text)
                        else:
                            st.error("❌ Please select an AI model first!")
                            return
                        
                        if analysis:
                            # Create a SHORT, FRIENDLY AI response (simple and easy to understand)
                            is_correct = analysis.get('is_correct', False)
                            
                            if is_correct:
                                # If correct, keep response short
                                ai_response = f"Perfect! That's great! Your sentence is correct. {analysis.get('tips', ['Try to use more advanced vocabulary next time.'])[0]}"
                            else:
                                # If incorrect, give short correction
                                correction = analysis.get('corrected', user_text)
                                explanation = analysis.get('explanation', 'Good try!')
                                ai_response = f"Nice try! Instead of '{user_text}', you could say '{correction}'. {explanation} {analysis.get('followup_question', 'Can you try again?')}"
                            
                            # Add AI response to history
                            st.session_state.voice_conversation_history.append({
                                'type': 'ai',
                                'text': ai_response,
                                'timestamp': datetime.now().strftime('%H:%M:%S'),
                                'analysis': analysis
                            })
                            
                            # Save to database
                            db.save_learning_history(st.session_state.user_id, user_text, analysis.get('corrected', user_text))
                            
                            # Generate AI voice response
                            audio_buffer = None
                            try:
                                audio_buffer = self.text_to_speech(ai_response, use_gtts=True)
                            except Exception as e:
                                st.warning(f"⚠️ Could not generate voice: {str(e)[:50]}")
                            
                            # Store audio buffer in the AI message for persistent display
                            if audio_buffer:
                                st.session_state.voice_conversation_history[-1]['voice_buffer'] = audio_buffer
                            
                            # Refresh to show updated conversation
                            st.rerun()
                
                except sr.UnknownValueError:
                    st.error("❌ I didn't catch that. Can you speak a bit clearer?")
                except sr.RequestError as e:
                    st.error(f"❌ Network issue: {str(e)[:50]}")
                except Exception as e:
                    st.error(f"❌ Something went wrong: {str(e)[:50]}")
    
    
    def analyze_with_openai(self, sentence: str) -> dict:
        """Analyze English using OpenAI API."""
        if not self.openai_client:
            st.error("❌ OpenAI API key not configured!")
            return None
        
        try:
            prompt = f"""You are a friendly English teacher for Indian learners. Analyze this sentence and respond ONLY with valid JSON (no other text before or after):

SENTENCE: {sentence}

{{
    "is_correct": true/false,
    "original": "{sentence}",
    "corrected": "improved and more natural version",
    "explanation": "brief explanation",
    "tips": ["tip 1", "tip 2"],
    "followup_question": "one short question"
}}"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a friendly English teacher. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content
            analysis = json.loads(response_text)
            return analysis
        
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "invalid_api_key" in error_msg:
                st.error("❌ Invalid OpenAI API Key!")
            else:
                st.error(f"❌ Error with OpenAI: {error_msg[:150]}")
            return None
    
    def analyze_with_groq(self, sentence: str) -> dict:
        """Analyze English using Groq API (fast and free!)."""
        if not self.groq_client:
            st.error("❌ Groq API key not configured!")
            return None
        
        # Check cache first
        cache_key = hashlib.md5(sentence.lower().strip().encode()).hexdigest()
        
        if cache_key in self._analysis_cache:
            cached_result = self._analysis_cache[cache_key]
            st.info("💾 Using cached analysis")
            return cached_result
        
        # Rate limiting: Wait if we're making too many calls
        current_time = time.time()
        if 'groq_last_call' in self._last_api_call:
            time_since_last_call = current_time - self._last_api_call['groq_last_call']
            if time_since_last_call < 1:  # Min 1 second between API calls
                wait_time = 1 - time_since_last_call
                with st.spinner(f"⏳ Processing... {wait_time:.1f}s"):
                    time.sleep(wait_time)
        
        self._last_api_call['groq_last_call'] = current_time
        
        try:
            prompt = f"""You are a friendly English teacher for Indian learners. Analyze this sentence and respond ONLY with valid JSON (no other text before or after):

SENTENCE: {sentence}

{{
    "is_correct": true/false,
    "original": "{sentence}",
    "corrected": "improved and more natural version (always provide an enhanced version even if grammatically correct)",
    "explanation": "brief explanation in simple words about what was improved",
    "tips": ["tip 1", "tip 2"],
    "followup_question": "one short question to continue conversation"
}}

IMPORTANT: Always provide a more natural, fluent, or enhanced version in the 'corrected' field. Even if the sentence is grammatically correct, suggest a more natural way to express it."""
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a friendly English teacher. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON with better error handling
            import json as json_lib
            import re
            
            # First, try direct parsing
            try:
                analysis = json_lib.loads(response_text)
                # Cache the result
                if len(self._analysis_cache) > self._cache_max_size:
                    self._analysis_cache.pop(next(iter(self._analysis_cache)))
                self._analysis_cache[cache_key] = analysis
                return analysis
            except json_lib.JSONDecodeError:
                pass
            
            # Try to extract JSON object from response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    analysis = json_lib.loads(json_match.group())
                    # Cache the result
                    if len(self._analysis_cache) > self._cache_max_size:
                        self._analysis_cache.pop(next(iter(self._analysis_cache)))
                    self._analysis_cache[cache_key] = analysis
                    return analysis
                except json_lib.JSONDecodeError:
                    pass
            
            # If all parsing fails, create a fallback response
            st.warning("⚠️ Could not parse AI response. Using fallback feedback.")
            fallback = {
                "is_correct": False,
                "original": sentence,
                "corrected": f"Let's make it more natural: {sentence}",
                "explanation": "Please rephrase your sentence for better analysis.",
                "tips": ["Speak slowly and clearly", "Use simple sentences"],
                "followup_question": "Can you try saying that again?"
            }
            # Cache fallback too
            if len(self._analysis_cache) > self._cache_max_size:
                self._analysis_cache.pop(next(iter(self._analysis_cache)))
            self._analysis_cache[cache_key] = fallback
            return fallback
        
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Error with Groq: {error_msg[:150]}")
            return None
    
    def text_to_speech(self, text: str, use_gtts: bool = True):
        """Convert text to speech and return audio buffer."""
        try:
            if use_gtts:
                # Use gTTS for better quality
                tts = gTTS(text=text, lang='en', slow=False, tld='com')
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                return audio_buffer
            else:
                # Using pyttsx3
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                return None
        except Exception as e:
            st.error(f"❌ Text-to-speech error: {e}")
            return None
    
    def extract_text_from_document(self, file):
        """Extract text from image or PDF file using Gemini vision or PyPDF2."""
        try:
            extracted_text = ""
            
            if file.type == "application/pdf":
                # Handle PDF files with PyPDF2
                try:
                    if not pypdf_available:
                        st.error("❌ PyPDF2 not available. Install with: pip install PyPDF2")
                        return None
                    
                    pdf_file = BytesIO(file.read())
                    pdf_reader = PdfReader(pdf_file)
                    
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            extracted_text += text + "\n"
                    
                    if extracted_text.strip():
                        return extracted_text
                    else:
                        st.warning("⚠️ PDF has no extractable text. It might be image-based.")
                        return None
                        
                except Exception as e:
                    st.error(f"❌ Could not extract from PDF: {str(e)[:60]}")
                    return None
            
            elif file.type in ["image/jpeg", "image/png", "image/jpg", "image/gif"]:
                # Note: Groq doesn't support vision/image analysis
                st.warning("""
⚠️ **Image Text Extraction Not Available**

The current AI backend (Groq) doesn't support image analysis.

**Alternatives:**
1. Use OCR tools to convert image to text first
2. Upload text as a PDF instead
3. Copy-paste the text directly
                """)
                return None
            
            else:
                st.error("❌ Unsupported file format. Please upload JPG, PNG, or PDF.")
                return None
                
        except Exception as e:
            st.error(f"❌ Error processing document: {str(e)[:100]}")
            return None
    
    def detect_language_and_translate(self, text: str) -> tuple:
        """Detect if text is in Hindi/Marathi and translate to English using Groq."""
        try:
            # Use Groq to detect language
            detection_prompt = f"""Analyze this text and respond ONLY with JSON:
"{text[:500]}"

{{
    "language": "detected language (English/Hindi/Marathi/Other)",
    "is_english": true/false,
    "translated_text": "if not English, provide English translation. If already English, copy original text"
}}"""
            
            if self.groq_client:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a language detection AI. Always respond with valid JSON only."},
                        {"role": "user", "content": detection_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=200
                )
                response_text = response.choices[0].message.content.strip()
                
                try:
                    result = json.loads(response_text)
                    return result.get('translated_text', text), result.get('language', 'Unknown')
                except:
                    # If JSON parsing fails, return original text
                    return text, "Unknown"
            else:
                return text, "English"
                
        except Exception as e:
            st.warning(f"⚠️ Could not detect language: {str(e)[:50]}")
            return text, "English"
    
    def analyze_document(self, text: str) -> dict:
        """Analyze document for spelling, grammar, and writing style using Groq."""
        try:
            prompt = f"""You are a professional English editor. Analyze this document and respond ONLY with JSON:

TEXT: "{text[:1000]}"

Provide feedback in JSON format:
{{
    "has_errors": true/false,
    "spelling_errors": ["error1", "error2"],
    "grammar_issues": ["issue1", "issue2"],
    "corrected_version": "complete corrected text (short version if long)",
    "main_issues": "brief summary of main problems (1-2 sentences)",
    "how_to_improve": ["tip1", "tip2"],
    "overall_quality": "Poor/Fair/Good/Excellent"
}}

Be concise and practical."""
            
            if self.groq_client:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a professional English editor. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=500
                )
                response_text = response.choices[0].message.content.strip()
                
                try:
                    import re
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group())
                        return analysis
                except:
                    pass
                
                # Fallback response
                return {
                    "has_errors": True,
                    "spelling_errors": [],
                    "grammar_issues": [],
                    "corrected_version": text,
                    "main_issues": "Please review your document carefully.",
                    "how_to_improve": ["Check spelling", "Verify grammar", "Use simple language"],
                    "overall_quality": "Fair"
                }
            else:
                st.error("❌ Groq API not configured!")
                return None
                
        except Exception as e:
            st.error(f"❌ Analysis error: {str(e)[:100]}")
            return None
    
    def display_feedback(self, analysis: dict, show_audio: bool = False, autoplay: bool = False):
        """Display feedback in 5-step format with automatic voice response."""
        if not analysis:
            return
        
        # STEP 1: Original sentence
        st.markdown("### 📝 Your Sentence:")
        st.write(f'**"{analysis.get("original", "")}"**')
        
        # STEP 2 & 3: Correction and explanation
        if analysis.get("is_correct"):
            st.markdown('<div class="correct-box">', unsafe_allow_html=True)
            st.success("✅ Great job! Your sentence is correct!")
            st.write(f"💡 **More natural version:** {analysis.get('corrected', analysis.get('original'))}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
            st.markdown("### ✏️ Corrected Sentence:")
            st.write(f'**"{analysis.get("corrected", "")}"**')
            
            st.markdown("### 📚 Why?")
            st.write(analysis.get("explanation", ""))
            st.markdown('</div>', unsafe_allow_html=True)
        
        # STEP 4: Speaking tips
        st.markdown("### 🎤 Speaking Tips:")
        tips = analysis.get("tips", [])
        for i, tip in enumerate(tips[:2], 1):
            st.write(f"{i}. {tip}")
        
        # STEP 5: Follow-up question (ALWAYS SHOWN)
        st.markdown("### ❓ Keep Practicing!")
        followup = analysis.get("followup_question", "Tell me more!")
        st.markdown(f"<h2 style='color: #2c5aa0; font-size: 24px; font-weight: bold;'>{followup}</h2>", unsafe_allow_html=True)
        
        # Always show voice response section (both audio and text)
        st.markdown("---")
        st.markdown("### 🔊 AI Voice Response:")
        
        # Prepare voice response text
        voice_response = f"Great job! {analysis.get('explanation', '')}. "
        voice_response += f"Remember: {' '.join(analysis.get('tips', []))}. "
        voice_response += f"Now, {analysis.get('followup_question', 'tell me more about this topic')}"
        
        # Show text version
        st.write(f"📢 *{voice_response}*")
        
        # Generate and play audio (with or without autoplay based on parameter)
        with st.spinner("🎵 Generating voice..."):
            audio_buffer = self.text_to_speech(voice_response, use_gtts=True)
            if audio_buffer:
                st.audio(audio_buffer, format="audio/mp3", autoplay=autoplay)
                if not autoplay:
                    st.info("🔊 Click the play button above to hear the response")
            else:
                st.warning("⚠️ Could not generate audio. Check your internet connection.")


def main():
    lang = st.session_state.user_language
    
    # Motivational header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <div style='text-align: center; margin: 2rem 0;'>
                <h1 style='color: #2c5aa0; font-size: 48px;'>🌟</h1>
                <h1 style='color: #2c5aa0;'>{get_text('practice', lang)}</h1>
                <p style='color: #666666; font-size: 18px; font-weight: bold;'>✨ {get_text('keep_practicing', lang)} ✨</p>
                <p style='color: #666; font-size: 14px;'>{get_text('master_english', lang)}</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize session state
    if 'guide' not in st.session_state:
        st.session_state.guide = EnglishGuideStreamlit()
    
    if 'session_history' not in st.session_state:
        st.session_history = []
    
    guide = st.session_state.guide
    
    # Sidebar configuration
    with st.sidebar:
        st.header(f"⚙️ {get_text('settings', lang)}")
        
        # User info
        st.markdown("---")
        st.subheader(f"👤 {get_text('user_profile', lang)}")
        st.write(f"**{get_text('username', lang)}:** {st.session_state.username}")
        st.write(f"**{get_text('email', lang)}:** {st.session_state.email}")
        
        # Language selector
        st.markdown("---")
        st.subheader(f"🌐 {get_text('language_selection', lang)}")
        language_options = {
            "English": "English",
            "हिंदी": "Hindi",
            "मराठी": "Marathi"
        }
        selected_lang = st.selectbox(
            get_text('select_language', lang),
            list(language_options.keys()),
            index=["English", "Hindi", "Marathi"].index(lang),
            label_visibility="collapsed"
        )
        
        # Update language if changed
        if language_options[selected_lang] != lang:
            new_lang = language_options[selected_lang]
            st.session_state.user_language = new_lang
            # Save to database
            if hasattr(st.session_state, 'user_id'):
                db.set_user_language(st.session_state.user_id, new_lang)
            st.success(f"✅ {get_text('language_changed', new_lang)}")
            st.rerun()
        
        # Logout button
        if st.button(f"🚪 {get_text('logout', lang)}", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.email = None
            st.rerun()
        
        st.markdown("---")
        
        # AI Model selection
        st.subheader(f"🤖 {get_text('ai_model', lang)}")
        available_models = []
        
        openai_key = os.getenv('OPENAI_API_KEY', '').strip()
        groq_key = os.getenv('GROQ_API_KEY', '').strip()
        
        if openai_available and is_valid_api_key(openai_key):
            available_models.append("OpenAI GPT-3.5")
        if groq_available and is_valid_api_key(groq_key):
            available_models.append("Groq Mixtral (Free)")
        
        if not available_models:
            st.error(f"❌ {get_text('no_api_keys', lang)}")
            st.markdown(f"""
### {get_text('how_to_setup', lang)}

**Option 1: OpenAI (Requires payment method)**
1. Go to: https://platform.openai.com/api-keys
2. Create a new API key
3. Copy it

**Option 2: Groq (FREE - No payment needed!)**
1. Go to: https://console.groq.com/keys
2. Create a new API key
3. Copy it

### Edit `.env` file:
Edit the `.env` file in your project folder and replace placeholders:

```
OPENAI_API_KEY=sk-proj-... (your actual key)
GROQ_API_KEY=gsk_... (your actual key)
```

Then **restart** the Streamlit app (Ctrl+C and run again).
            """)
            ai_model = "No Model Available"
        else:
            ai_model = st.selectbox(f"{get_text('select_model', lang)}", available_models)
        
        # Input method selection with search
        st.subheader(f"🎙️ {get_text('input_method', lang)}")
        
        # Define available input methods
        available_methods = {
            f"📝 {get_text('text', lang)}": f"{get_text('type_sentences', lang)}",
            f"🎙️ {get_text('voice_browser', lang)}": f"{get_text('record_browser', lang)}",
            f"💬 {get_text('voice_conversation', lang)}": f"{get_text('conversation_desc', lang)}"
        }
        
        # Search/filter input methods
        st.markdown("""
        <style>
        .method-card {
            background: #f0f4f8;
            padding: 10px;
            border-radius: 8px;
            margin: 5px 0;
            border-left: 4px solid #2c5aa0;
            cursor: pointer;
            transition: all 0.3s;
        }
        .method-card:hover {
            background: #e3f2fd;
            transform: translateX(5px);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Search bar for input methods
        search_query = st.text_input(f"🔍 {get_text('search_methods', lang)}", placeholder=f"{get_text('search_placeholder', lang)}")
        
        # Filter methods based on search
        filtered_methods = {}
        search_lower = search_query.lower()
        for method, description in available_methods.items():
            if search_lower == "" or search_lower in method.lower() or search_lower in description.lower():
                filtered_methods[method] = description
        
        # Display filtered methods with descriptions
        st.markdown(f"**{get_text('available_methods', lang)}:**")
        
        col_select, col_info = st.columns([1, 2])
        
        with col_select:
            if filtered_methods:
                input_method = st.radio(
                    f"{get_text('select_method', lang)}",
                    list(filtered_methods.keys()),
                    label_visibility="collapsed"
                )
            else:
                st.warning(f"❌ {get_text('no_matching_methods', lang)}")
                input_method = f"📝 {get_text('text', lang)}"
        
        with col_info:
            # Show description of selected method
            if input_method in available_methods:
                st.markdown(f"""
                <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; border-left: 4px solid #2d7a3e;">
                <strong>{input_method}</strong><br>
                {available_methods[input_method]}
                </div>
                """, unsafe_allow_html=True)
        
        # Convert method names for backend use
        method_mapping = {
            f"📝 {get_text('text', lang)}": "Text",
            f"🎤 {get_text('voice_microphone', lang)}": "Voice (Microphone)",
            f"🎙️ {get_text('voice_browser', lang)}": "Voice (Browser Audio)",
            f"💬 {get_text('voice_conversation', lang)}": "Voice Conversation"
        }
        
        selected_method = method_mapping.get(input_method, input_method)
        
        # Text-to-speech option
        st.subheader(f"📢 {get_text('output', lang)}")
        enable_audio = st.checkbox(f"🔊 {get_text('voice_output', lang)}", value=True)
        
        # Session info
        st.markdown("---")
        st.subheader(f"📊 {get_text('session_info', lang)}")
        st.write(f"{get_text('sentences_analyzed', lang)}: {len(st.session_history)}")
    
    # Show warning if no models available
    if not available_models:
        st.warning(f"🔴 {get_text('configure_keys', lang)}")
        return
    
    # Main content area with tabs for different input methods
    st.markdown("---")
    st.subheader(f"📝 {get_text('practice', lang)}")
    
    # Create tabs for input methods
    tab_list = [f"📝 {get_text('text', lang)}", f"🎙️ {get_text('browser_audio', lang)}", f"💬 {get_text('conversation', lang)}", "📄 Document Analysis"]
    
    tabs = st.tabs(tab_list)
    
    # Tab 0: Text Input
    with tabs[0]:
        st.markdown(f"### 📝 {get_text('text_input', lang)}")
        st.info(f"ℹ️ {get_text('type_sentences_for_feedback', lang)}")
        user_input = st.text_area(f"{get_text('enter_sentence', lang)}:", height=120, placeholder=f"{get_text('type_english', lang)}", key="text_input_0")
        
        if st.button(f"🔍 {get_text('analyze', lang)}", use_container_width=True, key="analyze_text_0"):
            if user_input.strip():
                with st.spinner(f"⏳ {get_text('analyzing', lang)}"):
                    if ai_model == "OpenAI GPT-3.5":
                        analysis = guide.analyze_with_openai(user_input)
                    elif ai_model == "Groq Mixtral (Free)":
                        analysis = guide.analyze_with_groq(user_input)
                    else:
                        st.info(f"ℹ️ {get_text('using_local_analysis', lang)}")
                        analysis = None
                    
                    if analysis:
                        st.session_history.append({
                            'input': user_input,
                            'analysis': analysis,
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                        
                        # Store analysis in session state for continuous practice
                        st.session_state.text_tab_analysis = analysis
                        st.session_state.text_tab_attempt_count = st.session_state.get('text_tab_attempt_count', 0) + 1
        
        # Show feedback and input for continuous practice
        if 'text_tab_analysis' in st.session_state:
            guide.display_feedback(st.session_state.text_tab_analysis, show_audio=False, autoplay=False)
            
            # Input box directly below question
            st.markdown("---")
            attempt_num = st.session_state.get('text_tab_attempt_count', 1)
            next_input = st.text_area(
                f"**Practice Attempt #{attempt_num}:** Try the correction or similar sentence:",
                height=100,
                placeholder="Type your practice sentence here...",
                key=f"text_practice_{attempt_num}"
            )
            
            # Create container for feedback output
            feedback_container = st.container()
            
            if st.button("✅ Submit & Get Feedback", use_container_width=True, key=f"text_submit_{attempt_num}"):
                if next_input.strip():
                    with st.spinner(f"⏳ {get_text('analyzing', lang)}"):
                        if ai_model == "OpenAI GPT-3.5":
                            next_analysis = guide.analyze_with_openai(next_input)
                        elif ai_model == "Groq Mixtral (Free)":
                            next_analysis = guide.analyze_with_groq(next_input)
                        else:
                            next_analysis = None
                        
                        if next_analysis:
                            st.session_history.append({
                                'input': next_input,
                                'analysis': next_analysis,
                                'timestamp': datetime.now().strftime('%H:%M:%S')
                            })
                            st.session_state.text_tab_analysis = next_analysis
                            st.session_state.text_tab_attempt_count += 1
                    
                    # Display feedback immediately below button
                    with feedback_container:
                        st.markdown("---")
                        guide.display_feedback(st.session_state.text_tab_analysis, show_audio=False, autoplay=False)
                else:
                    st.warning("Please enter a sentence to analyze.")
    
    # Tab 1: Browser Audio Input
    with tabs[1]:
        st.markdown("### 🎙️ Browser Audio Input")
        st.info("Record using your browser's audio recorder")
        user_input = guide.capture_browser_voice_input(audio_key="initial_audio_input_tab1")
        if user_input:
            with st.spinner("Analyzing..."):
                if ai_model == "OpenAI GPT-3.5":
                    analysis = guide.analyze_with_openai(user_input)
                elif ai_model == "Groq Mixtral (Free)":
                    analysis = guide.analyze_with_groq(user_input)
                else:
                    st.info("Using local analysis (API not configured)")
                    analysis = None
                
                if analysis:
                    st.session_history.append({
                        'input': user_input,
                        'analysis': analysis,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    
                    # Save to database
                    correction = analysis.get('corrected', user_input)
                    db.save_learning_history(st.session_state.user_id, user_input, correction)
                    
                    # Store analysis for continuous practice
                    st.session_state.audio_tab_analysis = analysis
                    st.session_state.audio_tab_attempt_count = st.session_state.get('audio_tab_attempt_count', 0) + 1
        
        # Show feedback and input for continuous practice
        if 'audio_tab_analysis' in st.session_state:
            # Display feedback WITH text and buttons, but NO autoplay
            guide.display_feedback(st.session_state.audio_tab_analysis, show_audio=False, autoplay=False)
            
            # Input box directly below question
            st.markdown("---")
            attempt_num = st.session_state.get('audio_tab_attempt_count', 1)
            st.markdown(f"### 🎙️ Practice Attempt #{attempt_num}:")
            st.info("Record your next attempt using the suggested correction")
            
            # Simpler audio input without the elaborate function wrapper
            audio_data = st.audio_input("🎙️ Record your voice:", label_visibility="collapsed", key=f"audio_practice_{attempt_num}")
            
            if audio_data is not None:
                try:
                    # Save audio to temporary file and process
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(audio_data.getbuffer())
                        tmp_path = tmp_file.name
                    
                    # Recognize speech
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(tmp_path) as source:
                        audio = recognizer.record(source)
                    
                    next_input = recognizer.recognize_google(audio)
                    
                    # Clean up
                    os.remove(tmp_path)
                    
                    # Analyze the input
                    with st.spinner("Analyzing..."):
                        if ai_model == "OpenAI GPT-3.5":
                            next_analysis = guide.analyze_with_openai(next_input)
                        elif ai_model == "Groq Mixtral (Free)":
                            next_analysis = guide.analyze_with_groq(next_input)
                        else:
                            next_analysis = None
                        
                        if next_analysis:
                            st.session_history.append({
                                'input': next_input,
                                'analysis': next_analysis,
                                'timestamp': datetime.now().strftime('%H:%M:%S')
                            })
                            # Save to database
                            correction = next_analysis.get('corrected', next_input)
                            db.save_learning_history(st.session_state.user_id, next_input, correction)
                            
                            st.session_state.audio_tab_analysis = next_analysis
                            st.session_state.audio_tab_attempt_count += 1
                    
                    # Display feedback immediately and directly (not in container)
                    st.write("")  # Add spacing
                    st.markdown("---")
                    st.success(f"✅ Recognized: **{next_input}**")
                    st.write("")  # Add spacing
                    guide.display_feedback(st.session_state.audio_tab_analysis, show_audio=False, autoplay=False)
                
                except sr.UnknownValueError:
                    st.error("❌ I didn't catch that. Please speak clearly and try again.")
                except sr.RequestError as e:
                    st.error(f"❌ Speech recognition error: {str(e)[:80]}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)[:80]}")
    
    # Tab 2: Voice Conversation
    with tabs[2]:
        st.markdown(f"### 💬 {get_text('voice_conversation', lang)}")
        st.info(f"ℹ️ {get_text('conversation_with_ai', lang)}")
        guide.voice_conversation_mode(ai_model)
    
    # Tab 3: Document Analysis
    with tabs[3]:
        st.markdown("### 📄 Document Analysis")
        st.info("📤 Upload an image or PDF document to analyze for spelling & grammar mistakes")
        
        uploaded_file = st.file_uploader(
            "Choose a document (JPG, PNG, PDF):",
            type=["jpg", "jpeg", "png", "pdf"],
            help="Upload a document with text to analyze"
        )
        
        if uploaded_file is not None:
            file_details = f"**File:** {uploaded_file.name} | **Size:** {uploaded_file.size / 1024:.2f} KB"
            st.markdown(file_details)
            
            # Progress indicators
            with st.spinner("📖 Extracting text from document..."):
                extracted_text = guide.extract_text_from_document(uploaded_file)
            
            if extracted_text:
                st.success("✅ Text extracted successfully!")
                
                # Show extracted text preview
                with st.expander("👀 Preview Extracted Text"):
                    st.text_area("Extracted Text:", value=extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text, height=150, disabled=True)
                
                st.markdown("---")
                
                # Detect language and translate if needed
                with st.spinner("🌐 Checking language..."):
                    translated_text, detected_lang = guide.detect_language_and_translate(extracted_text)
                
                if detected_lang.lower() != "english":
                    st.info(f"🔤 **Detected Language:** {detected_lang} | ✅ **Translated to English**")
                    analysis_text = translated_text
                else:
                    analysis_text = extracted_text
                
                # Analyze document
                st.markdown("---")
                if st.button("🔍 Analyze Document", use_container_width=True, key="analyze_doc"):
                    with st.spinner("🤖 Analyzing document..."):
                        analysis = guide.analyze_document(analysis_text)
                    
                    if analysis:
                        st.markdown("---")
                        st.markdown("## 📊 Analysis Results")
                        
                        # Overall Quality Badge
                        quality = analysis.get('overall_quality', 'Unknown')
                        quality_colors = {
                            'Excellent': '🟢',
                            'Good': '🟡',
                            'Fair': '🟠',
                            'Poor': '🔴'
                        }
                        st.markdown(f"### {quality_colors.get(quality, '⚪')} Overall Quality: **{quality}**")
                        
                        # Main Issues Summary
                        st.markdown("### 📌 Main Issues:")
                        st.write(analysis.get('main_issues', 'No major issues found.'))
                        
                        # Spelling Errors
                        spelling = analysis.get('spelling_errors', [])
                        if spelling:
                            st.markdown("### ❌ Spelling Errors:")
                            for error in spelling[:5]:  # Show first 5
                                st.write(f"• {error}")
                        else:
                            st.success("✅ No spelling errors found!")
                        
                        # Grammar Issues
                        grammar = analysis.get('grammar_issues', [])
                        if grammar:
                            st.markdown("### ⚠️ Grammar Issues:")
                            for issue in grammar[:5]:  # Show first 5
                                st.write(f"• {issue}")
                        else:
                            st.success("✅ Grammar looks good!")
                        
                        # Corrected Version
                        st.markdown("### ✏️ Corrected Version:")
                        corrected = analysis.get('corrected_version', analysis_text)
                        st.text_area("Corrected Text:", value=corrected if len(corrected) < 1000 else corrected[:1000] + "...", height=150, disabled=True)
                        
                        # Improvement Tips
                        st.markdown("### 💡 How to Improve:")
                        tips = analysis.get('how_to_improve', [])
                        for i, tip in enumerate(tips, 1):
                            st.write(f"{i}. {tip}")
                        
                        # Save to database
                        db.save_learning_history(st.session_state.user_id, f"Document: {uploaded_file.name}", analysis.get('corrected_version', analysis_text)[:100])
                        st.success("✅ Analysis saved to your learning history!")
            else:
                st.error("❌ Could not extract text from document. Please try another file.")
    
    # Right sidebar: Quick Tips
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader(f"💡 {get_text('quick_tips', lang)}")
        tips = [
            f"🔹 {get_text('tip_speak_slowly', lang)}",
            f"🔹 {get_text('tip_tenses', lang)}",
            f"🔹 {get_text('tip_practice_daily', lang)}",
            f"🔹 {get_text('tip_native_speakers', lang)}",
            f"🔹 {get_text('tip_dont_fear', lang)}",
            f"🔹 {get_text('tip_read_news', lang)}",
            f"🔹 {get_text('tip_watch_movies', lang)}"
        ]
        for tip in tips:
            st.write(tip)
    
    # History section
    st.markdown("---")
    if st.session_history:
        st.subheader(f"📋 {get_text('session_history', lang)}")
        for i, item in enumerate(st.session_history[-5:], 1):
            with st.expander(f"#{i} - {item['timestamp']}: {item['input'][:50]}..."):
                st.write(f"**{get_text('original', lang)}:** {item['input']}")
                st.write(f"**{get_text('corrected', lang)}:** {item['analysis'].get('corrected', item['input'])}")
                st.write(f"**{get_text('explanation', lang)}:** {item['analysis'].get('explanation', 'N/A')}")


if __name__ == "__main__":
    main()
