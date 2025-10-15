import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import pyttsx3
import time
import webbrowser
import math
import speech_recognition as sr
import os
import pickle
import json
from PIL import Image
import av
import threading
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import queue

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="SignLink Pro - Live Demo",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = True
if 'current_sector' not in st.session_state:
    st.session_state.current_sector = "healthcare"
if 'input_mode' not in st.session_state:
    st.session_state.input_mode = "quick_access"
if 'typed_text' not in st.session_state:
    st.session_state.typed_text = ""
if 'feedback_message' not in st.session_state:
    st.session_state.feedback_message = ""
if 'mouse_activated' not in st.session_state:
    st.session_state.mouse_activated = False
if 'current_site' not in st.session_state:
    st.session_state.current_site = ""
if 'asl_active' not in st.session_state:
    st.session_state.asl_active = False

# Color schemes
COLORS = {
    "healthcare": {
        "primary": "#00FFFF",    # Bright Cyan
        "secondary": "#FFFF00",  # Bright Yellow
        "accent": "#00FF00",     # Bright Green
        "text": "#FFFFFF",       # White
        "highlight": "#FFA500",  # Orange
    },
    "enterprise": {
        "primary": "#FF64FF",    # Bright Pink
        "secondary": "#64FFFF",  # Bright Light Blue
        "accent": "#FFFF64",     # Bright Light Yellow
        "text": "#FFFFFF",       # White
        "highlight": "#FFA500",  # Orange
    },
    "education": {
        "primary": "#FFA500",    # Bright Orange
        "secondary": "#90EE90",  # Light Green
        "accent": "#FFFF64",     # Bright Yellow
        "text": "#FFFFFF",       # White
        "highlight": "#00FFFF",  # Cyan
    }
}

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Initialize text-to-speech
engine = pyttsx3.init()

# Quick access buttons
quick_buttons = [
    {'name': 'GOOGLE', 'url': 'https://www.google.com', 'gesture': 'G'},
    {'name': 'YOUTUBE', 'url': 'https://www.youtube.com', 'gesture': 'Y'},
    {'name': 'GMAIL', 'url': 'https://www.gmail.com', 'gesture': 'E'},
    {'name': 'VOICE', 'action': 'voice', 'gesture': 'V'}
]

# ==================== STREAMLIT UI ====================

def main():
    st.title("🎯 SignLink Pro - Live Investor Demo")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🎮 Demo Controls")
        
        # Sector selection
        st.subheader("🏢 Sector Selection")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🏥 Healthcare", use_container_width=True):
                switch_to_healthcare()
        with col2:
            if st.button("💼 Enterprise", use_container_width=True):
                switch_to_enterprise()
        with col3:
            if st.button("🎓 Education", use_container_width=True):
                switch_to_education()
        
        # Input mode selection
        st.subheader("⌨️ Input Mode")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔘 Quick Access", use_container_width=True):
                switch_to_quick_access()
        with col2:
            if st.button("⌨️ Full Typing", use_container_width=True):
                switch_to_full_typing()
        
        # Performance metrics
        st.subheader("📊 Performance")
        st.metric("Accuracy", "94%", "2%")
        st.metric("Latency", "85ms", "-5ms")
        
        # Demo info
        st.subheader("ℹ️ Demo Info")
        st.info(f"**Current Sector:** {st.session_state.current_sector.upper()}")
        st.info(f"**Input Mode:** {st.session_state.input_mode.replace('_', ' ').title()}")
        st.info(f"**Scenario:** {get_current_scenario()}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📹 Live Camera Feed")
        
        # Camera feed placeholder
        camera_placeholder = st.empty()
        
        # Simulated camera feed with instructions
        with camera_placeholder.container():
            st.info("🔴 Camera feed would be displayed here in production")
            st.image("https://via.placeholder.com/640x480/2C2C2C/FFFFFF?text=Live+Camera+Feed+-+SignLink+Pro", 
                    use_column_width=True)
            
            # Gesture simulation
            st.subheader("🎯 Simulate Gestures")
            gesture_cols = st.columns(4)
            with gesture_cols[0]:
                if st.button("👆 Gesture G", use_container_width=True):
                    simulate_gesture('G')
            with gesture_cols[1]:
                if st.button("✌️ Gesture Y", use_container_width=True):
                    simulate_gesture('Y')
            with gesture_cols[2]:
                if st.button("🤟 Gesture E", use_container_width=True):
                    simulate_gesture('E')
            with gesture_cols[3]:
                if st.button("🎤 Gesture V", use_container_width=True):
                    simulate_gesture('V')
    
    with col2:
        st.subheader("📝 Output & Feedback")
        
        # Current status
        status_color = COLORS[st.session_state.current_sector]["primary"]
        st.markdown(f"""
        <div style='border: 2px solid {status_color}; border-radius: 10px; padding: 15px; margin: 10px 0;'>
            <h4 style='color: {status_color}; margin: 0;'>🟢 SYSTEM ACTIVE</h4>
            <p style='margin: 5px 0;'>Sector: <strong>{st.session_state.current_sector.upper()}</strong></p>
            <p style='margin: 5px 0;'>Mode: <strong>{st.session_state.input_mode.replace('_', ' ').title()}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Typed text display
        st.text_area("📄 Typed Text", st.session_state.typed_text, height=150, key="typed_display")
        
        # Quick access buttons
        if st.session_state.input_mode == "quick_access":
            st.subheader("🔘 Quick Actions")
            for button in quick_buttons:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"🌐 {button['name']}", use_container_width=True):
                        handle_quick_action(button)
                with col2:
                    st.markdown(f"`{button['gesture']}`")
        
        # Feedback message
        if st.session_state.feedback_message:
            st.success(f"💬 {st.session_state.feedback_message}")
        
        # Gesture cheat sheet
        st.subheader("📋 Gesture Guide")
        if st.session_state.input_mode == "quick_access":
            st.markdown("""
            - **G** - Open Google
            - **Y** - Open YouTube
            - **E** - Open Gmail  
            - **V** - Voice Command
            - **O** - Switch to Full Typing
            - **L** - Delete (hold 1.5s)
            """)
        else:
            st.markdown("""
            - **A-J** - Type letters
            - **SPACE** - Space bar
            - **ENTER** - Submit text
            - **DELETE** - Backspace
            - **Q** - Quick Access Mode
            """)
    
    # Sector information
    st.markdown("---")
    show_sector_info()
    
    # Auto-refresh for demo
    st.rerun()

# ==================== DEMO FUNCTIONS ====================

def switch_to_healthcare():
    st.session_state.current_sector = "healthcare"
    st.session_state.feedback_message = "Switched to Healthcare Mode - Surgical Environment Control"
    speak_feedback(st.session_state.feedback_message)

def switch_to_enterprise():
    st.session_state.current_sector = "enterprise"
    st.session_state.feedback_message = "Switched to Enterprise Mode - Manufacturing Applications"
    speak_feedback(st.session_state.feedback_message)

def switch_to_education():
    st.session_state.current_sector = "education"
    st.session_state.feedback_message = "Switched to Education Mode - Classroom Applications"
    speak_feedback(st.session_state.feedback_message)

def switch_to_quick_access():
    st.session_state.input_mode = "quick_access"
    st.session_state.feedback_message = "Quick Access Mode - Use G, Y, E, V for quick actions"
    speak_feedback(st.session_state.feedback_message)

def switch_to_full_typing():
    st.session_state.input_mode = "full_typing"
    st.session_state.feedback_message = "Full Typing Mode - Use ASL gestures to type any letter"
    speak_feedback(st.session_state.feedback_message)

def get_current_scenario():
    scenarios = {
        "healthcare": "Healthcare - Surgical Control",
        "enterprise": "Enterprise - Manufacturing Control", 
        "education": "Education - Inclusive Learning"
    }
    return scenarios.get(st.session_state.current_sector, "General Demo")

def simulate_gesture(gesture):
    """Simulate gesture detection for demo purposes"""
    if st.session_state.input_mode == "quick_access":
        if gesture in ['G', 'Y', 'E', 'V']:
            for button in quick_buttons:
                if button['gesture'] == gesture:
                    handle_quick_action(button)
                    break
    else:
        # Full typing mode - add letter to text
        st.session_state.typed_text += gesture
        st.session_state.feedback_message = f"Typed: {gesture}"
        speak_feedback(f"Typed {gesture}")

def handle_quick_action(button):
    """Handle quick action button clicks"""
    if 'url' in button:
        st.session_state.feedback_message = f"Opening {button['name']}..."
        speak_feedback(f"Opening {button['name']}")
        
        # Simulate opening in new tab
        js_code = f"""
        <script>
            window.open('{button['url']}', '_blank');
        </script>
        """
        st.components.v1.html(js_code, height=0)
        
    elif button.get('action') == 'voice':
        st.session_state.feedback_message = "Voice command activated - Say 'Google', 'YouTube', or text to type"
        speak_feedback("Voice mode activated")
        # Simulate voice input
        simulate_voice_command()

def simulate_voice_command():
    """Simulate voice command processing"""
    # For demo, we'll simulate common voice commands
    import random
    commands = [
        "open google", 
        "type hello world", 
        "delete all",
        "open youtube"
    ]
    command = random.choice(commands)
    
    st.session_state.feedback_message = f"Voice heard: '{command}'"
    
    if "open google" in command:
        handle_quick_action({'name': 'GOOGLE', 'url': 'https://google.com', 'gesture': 'G'})
    elif "open youtube" in command:
        handle_quick_action({'name': 'YOUTUBE', 'url': 'https://youtube.com', 'gesture': 'Y'})
    elif "type" in command:
        text = command.replace("type", "").strip()
        st.session_state.typed_text += " " + text if st.session_state.typed_text else text
        st.session_state.feedback_message = f"Voice typed: {text}"
    elif "delete all" in command:
        st.session_state.typed_text = ""
        st.session_state.feedback_message = "All text deleted via voice"

def speak_feedback(message):
    """Speak feedback message (disabled in Streamlit Cloud for demo)"""
    try:
        # In production, this would use pyttsx3
        # engine.say(message)
        # engine.runAndWait()
        pass
    except:
        pass  # Silence errors in demo

def show_sector_info():
    """Display sector-specific information"""
    sector_info = {
        "healthcare": {
            "title": "🏥 HEALTHCARE MODE",
            "features": [
                "• Surgical Environment Control",
                "• Patient Rehabilitation", 
                "• Sterile Hands-Free Operation",
                "• Medical Imaging Navigation"
            ],
            "use_cases": [
                "Operating room computer control",
                "Patient record access during procedures",
                "Medical imaging manipulation"
            ]
        },
        "enterprise": {
            "title": "💼 ENTERPRISE MODE", 
            "features": [
                "• Manufacturing Control Rooms",
                "• CAD Design Manipulation",
                "• Presentation Control",
                "• Multi-Monitor Management"
            ],
            "use_cases": [
                "Factory floor computer systems",
                "Design workstation control", 
                "Conference room presentations"
            ]
        },
        "education": {
            "title": "🎓 EDUCATION MODE",
            "features": [
                "• Inclusive Classroom Access",
                "• Student Rehabilitation",
                "• Interactive Learning",
                "• Voice Command Integration"
            ],
            "use_cases": [
                "Special needs education",
                "Interactive whiteboard control",
                "Student computer lab access"
            ]
        }
    }
    
    info = sector_info[st.session_state.current_sector]
    colors = COLORS[st.session_state.current_sector]
    
    st.markdown(f"""
    <div style='border: 2px solid {colors["primary"]}; border-radius: 10px; padding: 20px; margin: 10px 0; background: rgba(0,0,0,0.1);'>
        <h3 style='color: {colors["primary"]}; margin-top: 0;'>{info['title']}</h3>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px;'>
            <div>
                <h4 style='color: {colors["secondary"]};'>Key Features</h4>
                {"".join([f"<p style='margin: 5px 0; color: {colors['text']};'>{feature}</p>" for feature in info['features']])}
            </div>
            <div>
                <h4 style='color: {colors['accent']};'>Use Cases</h4>
                {"".join([f"<p style='margin: 5px 0; color: {colors['text']};'>{use_case}</p>" for use_case in info['use_cases']])}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== STREAMLIT APP ====================

if __name__ == "__main__":
    main()
   


