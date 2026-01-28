import streamlit as st
import os
import sys
import importlib
from dotenv import load_dotenv

# 1. Path Setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))

# 2. Load Environment Variables (CRITICAL: MUST BE BEFORE AGENT IMPORTS)
dotenv_path = os.path.join(PROJECT_ROOT, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# 3. Add UI directory and Project Root to path
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Set page config
st.set_page_config(
    page_title="Zipsa: AI Head Butler v2.0",
    page_icon="🎩",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load CSS
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

CSS_PATH = os.path.join(CURRENT_DIR, "style.css")
if os.path.exists(CSS_PATH):
    load_css(CSS_PATH)

import uuid
# Session State Initialization
if "page" not in st.session_state:
    st.session_state.page = "onboarding"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
if "initialized" not in st.session_state:
    st.session_state.initialized = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

def show_loading():
    st.markdown("""
        <div class='loading-container animate-fade'>
            <div class='loading-butler'>🎩</div>
            <div class='loading-text'>INITIALIZING ZIPSA...</div>
        </div>
    """, unsafe_allow_html=True)

def main():
    # 4. Check API Key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("🔑 OPENAI_API_KEY를 찾을 수 없습니다. 루트 디렉토리의 .env 파일을 확인해주세요.")
        st.stop()

    # 5. Initialization / Loading Screen
    if not st.session_state.initialized:
        show_loading()
        import time
        time.sleep(1.5) # Minimum splash duration for "Wow" factor
        st.session_state.initialized = True
        st.rerun()

    import components.header as header
    header.styled_header()

    # Sidebar navigation for debugging/resetting
    with st.sidebar:
        st.title("🎩 Zipsa Admin")
        st.warning("App Version: 2.1 (Live)")
        if st.button("🔄 Reset & Clear Cache"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    # Page Routing
    if st.session_state.page == "onboarding":
        import pages.onboarding as onboarding
        importlib.reload(onboarding)
        onboarding.show_onboarding()
    elif st.session_state.page == "chat":
        import pages.chat as chat
        # Force reload to ensure latest agent logic is picked up
        importlib.reload(chat)
        chat.show_chat()

if __name__ == "__main__":
    main()
