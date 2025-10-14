# app.py
import streamlit as st
import cv2
import numpy as np
import time
import pandas as pd
from PIL import Image
import io
import base64
import random
import requests
import json

# Page configuration for mobile-like interface
st.set_page_config(
    page_title="ASL Mobile App Prototype",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile app styling
st.markdown("""
<style>
    /* Mobile app styling */
    .main-header {
        font-size: 2rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 10px;
    }
    
    .mobile-container {
        max-width: 400px;
        margin: 0 auto;
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 2px solid #e0e0e0;
    }
    
    .camera-feed {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        color: white;
    }
    
    .gesture-feedback {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #4ECDC4;
    }
    
    .quick-action {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 12px;
        padding: 12px;
        margin: 5px;
        text-align: center;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .quick-action:hover {
        transform: translateY(-2px);
    }
    
    .mode-indicator {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        color: white;
        padding: 10px;
        border-radius: 25px;
        text-align: center;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .virtual-key {
        display: inline-block;
        width: 35px;
        height: 35px;
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        border: none;
        border-radius: 8px;
        text-align: center;
        line-height: 35px;
        margin: 2px;
        font-weight: bold;
        cursor: pointer;
    }
    
    .virtual-key.special {
        background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
        width: 60px;
    }
    
    .virtual-key.action {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        width: 80px;
    }
    
    .chat-bubble {
        background: #e3f2fd;
        border-radius: 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
    }
    
    .chat-bubble.user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 5px;
    }
    
    .chat-bubble.bot {
        background: #f5f5f5;
        margin-right: auto;
        border-bottom-left-radius: 5px;
    }
    
    .tab-button {
        background: #f8f9fa;
        border: none;
        padding: 10px 20px;
        margin: 2px;
        border-radius: 20px;
        cursor: pointer;
    }
    
    .tab-button.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class MobileASLApp:
    def __init__(self):
        self.typed_text = ""
        self.current_mode = "typing"
        self.gesture_history = []
        self.feedback_message = ""
        self.chat_history = []
        self.current_tab = "communication"
        self.quick_phrases = [
            "Hello, how are you?",
            "I need help",
            "Thank you",
            "Where is the bathroom?",
            "I use sign language"
        ]
        
        # Mobile-optimized gestures
        self.mobile_gestures = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 
            'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 
            'W', 'X', 'Y', 'Z', 'SPACE', 'DELETE', 'ENTER', 'VOICE',
            'EMOJI', 'SWITCH', 'HELP'
        ]
        
        # Mobile virtual keyboard
        self.mobile_keyboard = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'DEL'],
            ['SPACE', 'VOICE', 'ENTER', '😊']
        ]
        
        # App integrations
        self.app_integrations = {
            'messages': "Send as text message",
            'whatsapp': "Share on WhatsApp", 
            'email': "Compose email",
            'social': "Post to social media",
            'translate': "Translate to text"
        }

    def simulate_gesture_detection(self):
        """Simulate real gesture detection"""
        return random.choice(self.mobile_gestures)

    def process_gesture(self, gesture):
        """Process detected gesture with mobile-specific actions"""
        if gesture in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 
                      'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 
                      'W', 'X', 'Y', 'Z']:
            self.typed_text += gesture
            self.feedback_message = f"📝 Typed: {gesture}"
            
        elif gesture == 'SPACE':
            self.typed_text += ' '
            self.feedback_message = "␣ Space added"
            
        elif gesture == 'DELETE':
            self.typed_text = self.typed_text[:-1] if self.typed_text else ""
            self.feedback_message = "🗑️ Deleted"
            
        elif gesture == 'ENTER':
            if self.typed_text.strip():
                self.send_message()
            else:
                self.feedback_message = "Type a message first"
                
        elif gesture == 'VOICE':
            self.feedback_message = "🎤 Voice mode activated"
            # Simulate voice input
            voice_responses = ["Hello there!", "How can I help?", "What's the weather?", "Call my mom"]
            self.typed_text = random.choice(voice_responses)
            
        elif gesture == 'EMOJI':
            emojis = ["😊", "👍", "❤️", "🎉", "🙏"]
            self.typed_text += random.choice(emojis)
            self.feedback_message = "😊 Emoji added"
            
        elif gesture == 'SWITCH':
            self.current_mode = 'mouse' if self.current_mode == 'typing' else 'typing'
            self.feedback_message = f"🔄 Switched to {self.current_mode} mode"
            
        elif gesture == 'HELP':
            self.feedback_message = "❓ Help: Make gestures in front of camera"
        
        self.gesture_history.append((gesture, time.time()))

    def send_message(self):
        """Send message and get AI response"""
        if self.typed_text.strip():
            # Add user message
            self.chat_history.append({
                'type': 'user',
                'message': self.typed_text,
                'time': time.time()
            })
            
            # Get AI response
            ai_response = self.get_ai_response(self.typed_text)
            
            # Add AI response
            self.chat_history.append({
                'type': 'bot', 
                'message': ai_response,
                'time': time.time()
            })
            
            self.feedback_message = "✅ Message sent!"
            self.typed_text = ""

    def get_ai_response(self, user_message):
        """Get simulated AI response"""
        responses = {
            "hello": "👋 Hello! I'm your ASL assistant. How can I help you communicate today?",
            "help": "🤖 I can help you:\n• Type with gestures\n• Control your phone\n• Send messages\n• Use voice commands\nMake a gesture or use the keyboard!",
            "weather": "🌤️ To check weather, I can help you search online or use your weather app!",
            "emergency": "🆘 Emergency mode activated! I can help you contact emergency services or your emergency contacts.",
            "thank you": "😊 You're welcome! I'm here to help you communicate easily.",
            "default": "💡 That's interesting! In the full app, I'd understand your gestures and help you communicate effectively."
        }
        
        user_lower = user_message.lower()
        for key in responses:
            if key in user_lower:
                return responses[key]
        return responses["default"]

    def get_camera_feed(self):
        """Generate simulated camera feed with hand tracking"""
        # Create a realistic camera feed simulation
        img = np.zeros((300, 400, 3), dtype=np.uint8)
        
        # Gradient background
        for i in range(300):
            color = int(50 + (i / 300) * 100)
            cv2.line(img, (0, i), (400, i), (color, color, color + 50), 1)
        
        # Camera UI elements
        cv2.putText(img, "ASL CAMERA", (140, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Animated hand visualization
        center_x, center_y = 200, 150
        pulse = int(10 * np.sin(time.time() * 3))
        
        # Hand outline
        cv2.circle(img, (center_x, center_y), 50 + pulse, (0, 255, 0), 2)
        
        # Finger points (animated)
        for i, angle in enumerate([30, 90, 150, 210, 270]):
            rad = np.radians(angle + pulse * 5)
            fx = int(center_x + 40 * np.cos(rad))
            fy = int(center_y + 40 * np.sin(rad))
            cv2.circle(img, (fx, fy), 8, (255, 100, 100), -1)
        
        # Status text
        cv2.putText(img, "Hand Detected ✓", (140, 250), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(img, "Make ASL Gestures", (120, 280), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 255), 1)
        
        return img

def main():
    st.markdown('<h1 class="main-header">📱 ASL Mobile App Prototype</h1>', 
                unsafe_allow_html=True)
    
    # Initialize session state
    if 'mobile_app' not in st.session_state:
        st.session_state.mobile_app = MobileASLApp()
    
    app = st.session_state.mobile_app
    
    # Mobile container
    st.markdown('<div class="mobile-container">', unsafe_allow_html=True)
    
    # Tab navigation (mobile-style)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        tab1_active = "active" if app.current_tab == "communication" else ""
        st.markdown(f'<button class="tab-button {tab1_active}" onclick="alert(\'Switching to Communication tab\')">💬</button>', 
                   unsafe_allow_html=True)
    with col2:
        tab2_active = "active" if app.current_tab == "control" else ""
        st.markdown(f'<button class="tab-button {tab2_active}" onclick="alert(\'Switching to Control tab\')">🎮</button>', 
                   unsafe_allow_html=True)
    with col3:
        tab3_active = "active" if app.current_tab == "quick" else ""
        st.markdown(f'<button class="tab-button {tab3_active}" onclick="alert(\'Switching to Quick Actions\')">⚡</button>', 
                   unsafe_allow_html=True)
    with col4:
        tab4_active = "active" if app.current_tab == "settings" else ""
        st.markdown(f'<button class="tab-button {tab4_active}" onclick="alert(\'Switching to Settings\')">⚙️</button>', 
                   unsafe_allow_html=True)
    
    # Camera feed section
    st.markdown('<div class="camera-feed">', unsafe_allow_html=True)
    st.subheader("📷 ASL Camera")
    
    camera_feed = app.get_camera_feed()
    st.image(camera_feed, use_column_width=True, caption="Live Hand Tracking - Make gestures to communicate")
    
    # Gesture controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 Detect Gesture", use_container_width=True):
            gesture = app.simulate_gesture_detection()
            app.process_gesture(gesture)
            st.toast(f"Gesture Detected: {gesture}", icon="✅")
            
    with col2:
        if st.button("🔄 Switch Mode", use_container_width=True):
            app.process_gesture('SWITCH')
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Current mode and feedback
    st.markdown(f'''
    <div class="mode-indicator">
        📱 {app.current_mode.upper()} MODE | 🎯 {len(app.gesture_history)} Gestures Detected
    </div>
    ''', unsafe_allow_html=True)
    
    if app.feedback_message:
        st.info(app.feedback_message)
    
    # Communication interface
    st.subheader("💬 Communication")
    
    # Text input display
    st.text_input("Your Message (Use gestures or keyboard):", 
                 value=app.typed_text, key="message_display", disabled=True)
    
    # Virtual Keyboard
    st.markdown("### ⌨️ Virtual Keyboard")
    for row in app.mobile_keyboard:
        cols = st.columns(len(row))
        for i, key in enumerate(row):
            with cols[i]:
                key_class = "virtual-key"
                if key in ['SPACE', 'VOICE', 'ENTER']:
                    key_class += " action"
                elif key in ['DEL', '😊']:
                    key_class += " special"
                    
                if st.button(key, key=f"key_{key}_{i}", use_container_width=True):
                    app.process_gesture(key)
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    quick_cols = st.columns(3)
    actions = [
        ("📞 Call Mom", "Calling Mom..."),
        ("📍 Share Location", "Location shared!"),
        ("🆘 Emergency", "Emergency mode activated!"),
        ("🌤️ Weather", "Checking weather..."),
        ("🍕 Food", "Opening food delivery..."),
        ("🚗 Transport", "Booking transport...")
    ]
    
    for i, (action, response) in enumerate(actions):
        with quick_cols[i % 3]:
            if st.button(action, use_container_width=True):
                st.toast(response, icon="✅")
                app.feedback_message = response
    
    # Quick Phrases
    st.subheader("💬 Quick Phrases")
    phrase_cols = st.columns(2)
    for i, phrase in enumerate(app.quick_phrases):
        with phrase_cols[i % 2]:
            if st.button(phrase, use_container_width=True):
                app.typed_text = phrase
                app.feedback_message = f"📝 Quick phrase: {phrase}"
    
    # Chat History
    if app.chat_history:
        st.subheader("📝 Conversation History")
        for msg in app.chat_history[-3:]:  # Show last 3 messages
            bubble_class = "chat-bubble user" if msg['type'] == 'user' else "chat-bubble bot"
            sender = "You" if msg['type'] == 'user' else "ASL Assistant"
            st.markdown(f'''
            <div class="{bubble_class}">
                <strong>{sender}:</strong> {msg['message']}
                <div style="font-size: 0.8em; opacity: 0.7;">
                    {time.strftime('%H:%M', time.localtime(msg['time']))}
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    # App Integrations
    st.subheader("🔗 Share To...")
    int_cols = st.columns(3)
    integrations = list(app.app_integrations.items())[:6]  # First 6 integrations
    
    for i, (app_name, description) in enumerate(integrations):
        with int_cols[i % 3]:
            if st.button(f"📲 {app_name.title()}", use_container_width=True):
                if app.typed_text:
                    st.toast(f"Sharing to {app_name}: {app.typed_text}", icon="✅")
                else:
                    st.warning("Type a message first!")
    
    # Gesture History
    with st.expander("📊 Recent Gestures"):
        if app.gesture_history:
            for gesture, timestamp in reversed(app.gesture_history[-5:]):
                st.write(f"🎯 {gesture} - {time.strftime('%H:%M:%S', time.localtime(timestamp))}")
        else:
            st.write("No gestures yet. Make a gesture in front of the camera!")
    
    # Demo Instructions
    with st.expander("🎯 How to Use This Demo"):
        st.markdown("""
        ### 🎮 **Live Demo Features:**
        
        1. **🎯 Click 'Detect Gesture'** - Simulates random ASL gesture detection
        2. **⌨️ Use Virtual Keyboard** - Type messages manually
        3. **⚡ Quick Actions** - One-tap common tasks
        4. **💬 Quick Phrases** - Pre-written common phrases
        5. **🔗 App Integration** - Share to different apps
        
        ### 📱 **Mobile App Features Demonstrated:**
        - Real-time camera hand tracking
        - Gesture-to-text conversion
        - Voice command integration
        - Quick action shortcuts
        - Multi-app sharing
        - Conversation history
        - Emergency features
        
        *In full mobile app: Actual camera processing with MediaPipe + real gesture recognition*
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
