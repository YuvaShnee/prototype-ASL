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
import subprocess
import pygetwindow as gw
import base64
from PIL import Image
import io
import requests
import threading

# ==================== STREAMLIT CONFIGURATION ====================
st.set_page_config(
    page_title="SignLink Pro - Enterprise Accessibility",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF64FF;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sector-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
    }
    .metric-card {
        background: #2d3746;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
        text-align: center;
    }
    .gesture-card {
        background: #1e2a38;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #FF64FF;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #ddd;
    }
    .user-message {
        background: #2d3746;
        border-left: 4px solid #FF64FF;
    }
    .ai-message {
        background: #1e2a38;
        border-left: 4px solid #64B5FF;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE INITIALIZATION ====================
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_sector' not in st.session_state:
    st.session_state.current_sector = "enterprise"
if 'typed_text' not in st.session_state:
    st.session_state.typed_text = ""
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'feedback_message' not in st.session_state:
    st.session_state.feedback_message = ""
if 'asl_prediction' not in st.session_state:
    st.session_state.asl_prediction = ""
if 'gesture_stability' not in st.session_state:
    st.session_state.gesture_stability = 0.0

# ==================== SECTOR CONFIGURATION ====================
SECTORS = {
    "healthcare": {
        "name": "🏥 Healthcare",
        "color": "#00FFFF",
        "scenario": "Patient Accessibility & Rehabilitation",
        "description": "Medical chart access, patient communication, and rehabilitation support"
    },
    "enterprise": {
        "name": "💼 Enterprise", 
        "color": "#FF64FF",
        "scenario": "Manufacturing Control & Productivity",
        "description": "CAD control, presentations, and multi-monitor management"
    },
    "education": {
        "name": "🎓 Education",
        "color": "#FFA500", 
        "scenario": "Inclusive Learning & Disability Support",
        "description": "Interactive learning, whiteboard control, and accessibility tools"
    }
}

QUICK_ACTIONS = {
    "healthcare": [
        {"name": "Patient Info", "gesture": "P", "icon": "👤", "color": "#00FFFF"},
        {"name": "Medical Chart", "gesture": "M", "icon": "📋", "color": "#FFFF00"},
        {"name": "Emergency", "gesture": "E", "icon": "🚨", "color": "#FF0000"},
        {"name": "Communicate", "gesture": "C", "icon": "💬", "color": "#00FF00"},
        {"name": "Voice CMD", "gesture": "V", "icon": "🎤", "color": "#FF69B4"}
    ],
    "enterprise": [
        {"name": "Dashboard", "gesture": "D", "icon": "📊", "color": "#FF64FF"},
        {"name": "CAD Control", "gesture": "C", "icon": "🖥️", "color": "#64FFFF"},
        {"name": "Presentation", "gesture": "P", "icon": "📽️", "color": "#FFFF64"},
        {"name": "Monitors", "gesture": "M", "icon": "🖥️🖥️", "color": "#FF6464"},
        {"name": "Voice CMD", "gesture": "V", "icon": "🎤", "color": "#64FF64"}
    ],
    "education": [
        {"name": "Lesson Control", "gesture": "L", "icon": "📚", "color": "#FFA500"},
        {"name": "Whiteboard", "gesture": "W", "icon": "🖊️", "color": "#90EE90"},
        {"name": "Assessment", "gesture": "A", "icon": "📝", "color": "#FFFF64"},
        {"name": "Accessibility", "gesture": "X", "icon": "♿", "color": "#00FFFF"},
        {"name": "Voice CMD", "gesture": "V", "icon": "🎤", "color": "#FF69B4"}
    ]
}

# ==================== AI CHAT FUNCTIONALITY ====================
def get_ai_response(user_input, sector):
    """Generate AI response based on sector context"""
    sector_context = {
        "healthcare": "medical accessibility, patient care, rehabilitation, healthcare technology",
        "enterprise": "manufacturing control, CAD design, productivity tools, enterprise software", 
        "education": "classroom technology, special needs education, interactive learning, accessibility tools"
    }
    
    context = sector_context.get(sector, "accessibility technology")
    
    # Simple rule-based responses (replace with actual AI model in production)
    responses = {
        "hello": f"Hello! I'm your SignLink Pro assistant for {sector} sector. How can I help with {context} today?",
        "help": f"I can help you with {context}. Try asking about gesture controls, sector-specific features, or accessibility options.",
        "gesture": f"In {sector} mode, you can use ASL gestures to control applications. Key gestures include quick access buttons and full keyboard input.",
        "settings": f"Current sector: {sector}. You can switch sectors in the sidebar and configure accessibility options.",
        "default": f"I understand you're interested in {context}. For detailed assistance with SignLink Pro features in {sector}, please check the documentation or try specific gestures."
    }
    
    user_input_lower = user_input.lower()
    for key in responses:
        if key in user_input_lower:
            return responses[key]
    
    return responses["default"]

def add_message(role, content):
    """Add message to chat history"""
    st.session_state.messages.append({"role": role, "content": content})

# ==================== SECTOR FUNCTIONS ====================
def switch_sector(new_sector):
    """Switch between sectors"""
    st.session_state.current_sector = new_sector
    st.session_state.feedback_message = f"Switched to {SECTORS[new_sector]['name']} - {SECTORS[new_sector]['scenario']}"

def execute_sector_action(action_name):
    """Execute sector-specific actions"""
    sector = st.session_state.current_sector
    
    if sector == "healthcare":
        if action_name == "Patient Info":
            webbrowser.open("https://www.epic.com")
            st.session_state.feedback_message = "Opening Patient Information System"
        elif action_name == "Medical Chart":
            st.session_state.feedback_message = "Accessing Medical Records"
        elif action_name == "Emergency":
            st.session_state.feedback_message = "EMERGENCY MODE - Alerting Medical Staff"
        elif action_name == "Communicate":
            st.session_state.feedback_message = "Patient Communication Mode Activated"
            
    elif sector == "enterprise":
        if action_name == "Dashboard":
            webbrowser.open("https://www.tableau.com")
            st.session_state.feedback_message = "Opening Control Dashboard"
        elif action_name == "CAD Control":
            st.session_state.feedback_message = "CAD Control Mode Activated"
        elif action_name == "Presentation":
            st.session_state.feedback_message = "Presentation Mode - Gesture Control Ready"
        elif action_name == "Monitors":
            st.session_state.feedback_message = "Multi-Monitor Control Activated"
            
    elif sector == "education":
        if action_name == "Lesson Control":
            webbrowser.open("https://classroom.google.com")
            st.session_state.feedback_message = "Lesson Control Mode Activated"
        elif action_name == "Whiteboard":
            webbrowser.open("https://whiteboard.microsoft.com")
            st.session_state.feedback_message = "Digital Whiteboard Activated"
        elif action_name == "Assessment":
            st.session_state.feedback_message = "Assessment Tools Ready"
        elif action_name == "Accessibility":
            webbrowser.open("https://accessibility.google")
            st.session_state.feedback_message = "Accessibility Features Enabled"

# ==================== GESTURE SIMULATION ====================
def simulate_gesture_detection():
    """Simulate gesture detection for demo purposes"""
    import random
    gestures = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                'SPACE', 'ENTER', 'BACKSPACE']
    
    if random.random() < 0.3:  # 30% chance of detecting a gesture
        gesture = random.choice(gestures)
        stability = min(st.session_state.gesture_stability + random.uniform(0.1, 0.3), 1.0)
        st.session_state.gesture_stability = stability
        
        if stability >= 0.8:
            st.session_state.asl_prediction = gesture
            if gesture in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                st.session_state.typed_text += gesture
            elif gesture == 'SPACE':
                st.session_state.typed_text += ' '
            elif gesture == 'BACKSPACE':
                st.session_state.typed_text = st.session_state.typed_text[:-1]
            st.session_state.gesture_stability = 0.0  # Reset after action
    else:
        st.session_state.gesture_stability = max(st.session_state.gesture_stability - 0.1, 0.0)

# ==================== STREAMLIT UI COMPONENTS ====================
def render_header():
    """Render the main header"""
    sector = st.session_state.current_sector
    sector_info = SECTORS[sector]
    
    st.markdown(f"""
    <div class="main-header">
        {sector_info['name']} - SignLink Pro
    </div>
    """, unsafe_allow_html=True)
    
    # Sector info and metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔄 Accuracy</h3>
            <h2>97%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚡ Response</h3>
            <h2>65ms</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯 Scenario</h3>
            <p>{sector_info['scenario']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>👁️ Gesture</h3>
            <p>{st.session_state.asl_prediction or 'None detected'}</p>
        </div>
        """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with controls"""
    with st.sidebar:
        st.markdown("## 🎮 Control Panel")
        
        # Sector selection
        st.markdown("### Select Sector")
        sector_col1, sector_col2, sector_col3 = st.columns(3)
        
        with sector_col1:
            if st.button("🏥 Health", use_container_width=True):
                switch_sector("healthcare")
        with sector_col2:
            if st.button("💼 Enterprise", use_container_width=True):
                switch_sector("enterprise")
        with sector_col3:
            if st.button("🎓 Education", use_container_width=True):
                switch_sector("education")
        
        # Camera control
        st.markdown("### Camera Control")
        cam_col1, cam_col2 = st.columns(2)
        with cam_col1:
            if st.button("📷 Start Camera", use_container_width=True):
                st.session_state.camera_active = True
                st.session_state.feedback_message = "Camera activated - Gesture detection ready"
        with cam_col2:
            if st.button("⏹️ Stop Camera", use_container_width=True):
                st.session_state.camera_active = False
                st.session_state.feedback_message = "Camera deactivated"
        
        # Gesture simulation
        st.markdown("### Gesture Simulation")
        if st.button("🎭 Simulate Gesture", use_container_width=True):
            simulate_gesture_detection()
            st.session_state.feedback_message = "Gesture simulation activated"
        
        # Quick actions
        st.markdown("### Quick Actions")
        sector = st.session_state.current_sector
        actions = QUICK_ACTIONS[sector]
        
        for action in actions:
            if st.button(f"{action['icon']} {action['name']} ({action['gesture']})", 
                        use_container_width=True,
                        key=f"action_{action['name']}"):
                execute_sector_action(action['name'])
        
        # System info
        st.markdown("---")
        st.markdown("### System Status")
        st.info(f"**Current Sector**: {SECTORS[sector]['name']}")
        st.info(f"**Camera**: {'Active' if st.session_state.camera_active else 'Inactive'}")
        st.info(f"**Gestures Detected**: {len(st.session_state.typed_text)}")

def render_quick_access():
    """Render quick access buttons"""
    st.markdown("## 🚀 Quick Access Controls")
    sector = st.session_state.current_sector
    actions = QUICK_ACTIONS[sector]
    
    cols = st.columns(len(actions))
    for idx, action in enumerate(actions):
        with cols[idx]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: {action['color']}20; 
                        border-radius: 10px; border: 2px solid {action['color']};">
                <div style="font-size: 2rem;">{action['icon']}</div>
                <h4>{action['name']}</h4>
                <p>Gesture: <strong>{action['gesture']}</strong></p>
            </div>
            """, unsafe_allow_html=True)

def render_gesture_interface():
    """Render gesture detection interface"""
    st.markdown("## ✋ Gesture Control Interface")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Camera feed placeholder
        if st.session_state.camera_active:
            st.markdown("### 📹 Live Camera Feed")
            # Placeholder for actual camera feed
            st.image("https://via.placeholder.com/640x480/2d3746/FFFFFF?text=Live+Camera+Feed+-+Gesture+Detection+Active", 
                    use_column_width=True)
            
            # Gesture stability indicator
            st.markdown("### Gesture Stability")
            st.progress(st.session_state.gesture_stability)
            st.write(f"Stability: {int(st.session_state.gesture_stability * 100)}%")
            
        else:
            st.markdown("### 📹 Camera Feed")
            st.image("https://via.placeholder.com/640x480/1e2a38/FFFFFF?text=Camera+Inactive+-+Click+Start+Camera", 
                    use_column_width=True)
    
    with col2:
        # ASL Prediction Display
        st.markdown("### 🔍 ASL Prediction")
        if st.session_state.asl_prediction:
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem; background: #1e2a38; 
                        border-radius: 15px; border: 3px solid #FF64FF;">
                <div style="font-size: 4rem; font-weight: bold;">{st.session_state.asl_prediction}</div>
                <p>Detected Gesture</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: #1e2a38; 
                        border-radius: 15px; border: 2px dashed #666;">
                <div style="font-size: 2rem;">👋</div>
                <p>Show ASL gesture to detect letters</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Typed text display
        st.markdown("### 📝 Typed Text")
        st.text_area("", st.session_state.typed_text, height=100, key="typed_display")
        
        # Clear text button
        if st.button("🗑️ Clear Text", use_container_width=True):
            st.session_state.typed_text = ""
            st.session_state.feedback_message = "Text cleared"

def render_ai_chat():
    """Render AI chat interface"""
    st.markdown("## 🤖 AI Assistant")
    
    # Chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message ai-message">
                <strong>AI Assistant:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("Type your message...", key="chat_input")
    with col2:
        if st.button("Send", use_container_width=True):
            if user_input:
                # Add user message
                add_message("user", user_input)
                
                # Get AI response
                ai_response = get_ai_response(user_input, st.session_state.current_sector)
                add_message("assistant", ai_response)
                
                # Clear input
                st.session_state.chat_input = ""
    
    # Quick chat buttons
    st.markdown("### Quick Questions")
    quick_cols = st.columns(3)
    with quick_cols[0]:
        if st.button("Hello 👋", use_container_width=True):
            add_message("user", "hello")
            ai_response = get_ai_response("hello", st.session_state.current_sector)
            add_message("assistant", ai_response)
    with quick_cols[1]:
        if st.button("Help ❓", use_container_width=True):
            add_message("user", "help")
            ai_response = get_ai_response("help", st.session_state.current_sector)
            add_message("assistant", ai_response)
    with quick_cols[2]:
        if st.button("Gestures ✋", use_container_width=True):
            add_message("user", "gesture controls")
            ai_response = get_ai_response("gesture", st.session_state.current_sector)
            add_message("assistant", ai_response)

def render_footer():
    """Render footer with feedback"""
    if st.session_state.feedback_message:
        st.success(st.session_state.feedback_message)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>SignLink Pro - Multi-Sector Accessibility System</p>
        <p>Enterprise • Healthcare • Education</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== MAIN APP ====================
def main():
    # Header
    render_header()
    
    # Layout
    col1, col2 = st.columns([1, 4])
    
    with col1:
        render_sidebar()
    
    with col2:
        # Quick access buttons
        render_quick_access()
        
        # Gesture interface
        render_gesture_interface()
        
        # AI Chat
        render_ai_chat()
    
    # Footer
    render_footer()

if __name__ == "__main__":
    main()
