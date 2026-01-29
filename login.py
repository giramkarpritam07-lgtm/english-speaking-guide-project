import streamlit as st
from database import DatabaseManager
import re
import json
from pathlib import Path
from language_support import get_text, TRANSLATIONS

# Path for storing remembered credentials (local file)
CREDENTIALS_FILE = Path.home() / ".english_guide_credentials.json"

def validate_email(email):
    """Simple email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Password is valid"

def save_credentials(username, password):
    """Save login credentials to local file (browser-like persistent storage)."""
    try:
        credentials = {
            "username": username,
            "password": password
        }
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f)
    except Exception as e:
        st.warning(f"Could not save credentials: {e}")

def load_remembered_credentials():
    """Load saved credentials if they exist."""
    try:
        if CREDENTIALS_FILE.exists():
            with open(CREDENTIALS_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return None

def clear_remembered_credentials():
    """Clear saved credentials."""
    try:
        if CREDENTIALS_FILE.exists():
            CREDENTIALS_FILE.unlink()
    except Exception:
        pass

def language_selection_page():
    """Display language selection page after login."""
    st.set_page_config(
        page_title="English Speaking Guide - Language Selection",
        page_icon="🌟",
        layout="centered"
    )
    
    # Professional styling
    st.markdown("""
        <style>
        .stApp {
            background: #f8f9fa;
        }
        .language-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #2c5aa0;
            margin: 10px 0;
            cursor: pointer;
            transition: all 0.3s;
        }
        .language-card:hover {
            background: #f3f5f7;
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align: center; margin: 2rem 0;'>
                <h1 style='color: #2c5aa0;'>🌟 English Speaking Guide</h1>
                <p style='color: #666; font-size: 18px;'><strong>भाषा चुनें / भाषा निवडा</strong></p>
                <p style='color: #888; font-size: 14px;'>Choose Your Language</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🇮🇳 हिंदी (Hindi)", use_container_width=True, key="select_hindi"):
            st.session_state.user_language = "Hindi"
            db = DatabaseManager()
            db.set_user_language(st.session_state.user_id, "Hindi")
            st.success("✅ Language changed to हिंदी (Hindi)")
            st.rerun()
    
    with col2:
        if st.button("🇮🇳 मराठी (Marathi)", use_container_width=True, key="select_marathi"):
            st.session_state.user_language = "Marathi"
            db = DatabaseManager()
            db.set_user_language(st.session_state.user_id, "Marathi")
            st.success("✅ Language changed to मराठी (Marathi)")
            st.rerun()
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🇮🇳 हिंदी (Hindi)**
        - सभी इंटरफेस हिंदी में
        - आसान और समझने में सरल
        - भारतीय भाषा
        """)
    
    with col2:
        st.markdown("""
        **🇮🇳 मराठी (Marathi)**
        - सभी इंटरफेस मराठी में
        - स्थानीय भाषा समर्थन
        - महाराष्ट्र की भाषा
        """)

def login_page():
    """Display login/register page."""
    
    st.set_page_config(
        page_title="English Speaking Guide - Login",
        page_icon="🌟",
        layout="centered"
    )
    
    # Professional background styling
    st.markdown("""
        <style>
        .stApp {
            background: #f8f9fa;
        }
        
        .main-content {
            position: relative;
            z-index: 10;
        }
        
        .login-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f0f0f0;
            border-radius: 4px 4px 0px 0px;
            padding: 10px;
            font-weight: bold;
            color: #666;
        }
        
        .stTabs [aria-selected="true"] [data-baseweb="tab"] {
            background: #2c5aa0;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize database
    db = DatabaseManager()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class="main-content">
            <div style='text-align: center; margin-top: 2rem;'>
                <h1 style='color: #2c5aa0; font-size: 48px;'>🌟</h1>
                <h1 style='color: #2c5aa0;'>English Speaking Guide</h1>
                <p style='color: #666666; font-size: 16px;'>Learn English with AI Corrections</p>
            </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
    
    # Tabs for Login and Register
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    # LOGIN TAB
    with tab1:
        st.subheader("Welcome Back!")
        
        # Load remembered credentials
        remembered = load_remembered_credentials()
        default_username = remembered.get("username", "") if remembered else ""
        default_password = remembered.get("password", "") if remembered else ""
        
        username = st.text_input("Username", placeholder="Enter your username", value=default_username)
        password = st.text_input("Password", type="password", placeholder="Enter your password", value=default_password)
        
        # Remember me checkbox
        col_remember, col_forget = st.columns(2)
        with col_remember:
            remember_me = st.checkbox("🔐 Remember me", value=(remembered is not None))
        with col_forget:
            if st.button("🗑️ Forget password", use_container_width=True):
                clear_remembered_credentials()
                st.success("✅ Credentials cleared!")
                st.rerun()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔓 Login", use_container_width=True):
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    success, user = db.authenticate_user(username, password)
                    
                    if success:
                        st.success(f"✅ Welcome back, {username}!")
                        
                        # Save credentials if "Remember me" is checked
                        if remember_me:
                            save_credentials(username, password)
                        else:
                            clear_remembered_credentials()
                        
                        # Store in session state
                        st.session_state.logged_in = True
                        st.session_state.user_id = user[0]
                        st.session_state.username = user[1]
                        st.session_state.email = user[2]
                        st.session_state.show_language_selection = True
                        
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
        
        with col2:
            if st.button("🆘 Forgot Password?", use_container_width=True):
                st.info("💡 Contact support or use the password reset feature (coming soon)")
        
        st.markdown("---")
        st.markdown("Don't have an account? **Register below** →")
    
    # REGISTER TAB
    with tab2:
        st.subheader("Create New Account")
        
        reg_username = st.text_input("Username", placeholder="Choose a username (3-20 characters)", key="reg_username")
        reg_email = st.text_input("Email", placeholder="Enter your email address", key="reg_email")
        reg_password = st.text_input("Password", type="password", placeholder="Enter a strong password (min 6 chars)", key="reg_password")
        reg_password_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="reg_password_confirm")
        
        if st.button("📝 Register", use_container_width=True):
            # Validation
            if not reg_username or not reg_email or not reg_password:
                st.error("❌ Please fill in all fields")
            elif len(reg_username) < 3 or len(reg_username) > 20:
                st.error("❌ Username must be 3-20 characters long")
            elif not validate_email(reg_email):
                st.error("❌ Please enter a valid email address")
            elif not validate_password(reg_password)[0]:
                st.error(f"❌ {validate_password(reg_password)[1]}")
            elif reg_password != reg_password_confirm:
                st.error("❌ Passwords do not match")
            elif db.user_exists(reg_username):
                st.error("❌ Username already taken")
            elif db.email_exists(reg_email):
                st.error("❌ Email already registered")
            else:
                success, message = db.register_user(reg_username, reg_email, reg_password)
                
                if success:
                    st.success(message)
                    st.info("✅ Now you can login with your credentials in the Login tab")
                else:
                    st.error(message)
        
        st.markdown("---")
        st.markdown("Already have an account? **Login above** ←")
    
    # Footer with statistics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Users", db.get_all_users_count())
    
    with col2:
        st.markdown("""
        <div style='text-align: center'>
        <p><strong>📚 Learn English</strong></p>
        <p>Improve with AI</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='text-align: center'>
        <p><strong>🎯 Free</strong></p>
        <p>No Signup Fees</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    login_page()
