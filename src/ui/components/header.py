import streamlit as st

def styled_header():
    st.markdown("""
        <div style='display: flex; align-items: center; justify-content: center; margin-bottom: 2rem;'>
            <span style='font-size: 3rem; margin-right: 1rem;'>🎩</span>
            <h1 style='margin: 0; font-size: 3.5rem; letter-spacing: -2px;'>ZIPSA</h1>
        </div>
    """, unsafe_allow_html=True)
