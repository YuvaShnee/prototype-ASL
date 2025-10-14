# app.py
import streamlit as st
import numpy as np
import time
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import random

# Page configuration
st.set_page_config(
    page_title="ASL Recognition Prototype",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile-app like interface
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .mode-button {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
        width: 100%;
    }
    .mode-button.active {
        background-color: #45a049;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }
    .gesture-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .keyboard-key {
        display: inline-block;
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        text-align: center;
        line-height: 40px;
        margin: 2px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .keyboard-key:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .keyboard-key.space {
        width: 200px;
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .keyboard-key.special {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    }
    .keyboard-key.action {
        background: linear-gradient(135deg, #10ac84 0%, #1dd1a1 100%);
    }
    .prediction-badge {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: #2d3436;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        margin: 2px;
        display: inline-block;
    }
    .camera-feed {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        color: white;
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
</style>
""", unsafe_allow_html=True)

class ASLPrototype:
    def __init__(self):
        self.typed_text = ""
        self.current_mode = "typing"
        self.gesture_history = []
        self.feedback_message = ""
        self.feedback_time = 0
        self.chat_history = []
        
        # Simulated gesture predictions
        self.gestures = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                        'SPACE', 'DELETE', 'ENTER', 'MOUSE', 'VOICE', 'HELP']
        
        # Keyboard layout for mobile
        self.mobile_keyboard = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'DEL'],
            ['SPACE', 'ENTER', 'VOICE', 'HELP']
        ]
    
    def simulate_gesture_prediction(self):
        """Simulate gesture prediction for demo purposes"""
        return random.choice(self.gestures)
    
    def process_gesture(self, gesture):
        """Process detected gesture and perform action"""
        current_time = time.time()
        
        if gesture in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                      'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            self.typed_text += gesture
            self.feedback_message = f"📝 Typed: {gesture}"
            
        elif gesture == 'SPACE':
            self.typed_text += ' '
            self.feedback_message = "␣ Space added"
            
        elif gesture == 'DELETE':
            self.typed_text = self.typed_text[:-1] if self.typed_text else ""
            self.feedback_message = "🗑️ Deleted character"
            
        elif gesture == 'ENTER':
            self.send_message()
            
        elif gesture == 'MOUSE':
            self.current_mode = 'mouse' if self.current_mode == 'typing' else 'typing'
            self.feedback_message = f"🔄 Switched to {self.current_mode} mode"
            
        elif gesture == 'VOICE':
            self.feedback_message = "🎤 Voice command activated"
            # Simulate voice input
            voice_commands = ["Hello there!", "Open Google", "What's the weather?", "Call my mom"]
            self.typed_text = random.choice(voice_commands)
            
        elif gesture == 'HELP':
            self.feedback_message = "❓ Help: Make ASL gestures in front of camera"
        
        self.feedback_time = current_time
        self.gesture_history.append((gesture, current_time))
        
        # Keep only last 10 gestures
        if len(self.gesture_history) > 10:
            self.gesture_history = self.gesture_history[-10:]
    
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
            
            self.feedback_message = "✅ Message sent to AI!"
            self.typed_text = ""
    
    def get_ai_response(self, user_message):
        """Get simulated AI response"""
        responses = {
            "hello": "👋 Hello! I'm your ASL assistant. How can I help you communicate today?",
            "help": "🤖 I can help you:\n• Type with ASL gestures\n• Control your device\n• Send messages\n• Use voice commands",
            "weather": "🌤️ To check weather, I can help you search online or use weather apps!",
            "google": "🌐 Opening Google... Search anything you need!",
            "thank you": "😊 You're welcome! I'm here to help you communicate easily.",
            "default": "💡 Great! I understood your ASL gesture. In the full app, I'd provide more detailed responses."
        }
        
        user_lower = user_message.lower()
        for key in responses:
            if key in user_lower:
                return responses[key]
        return responses["default"]
    
    def create_camera_image(self):
        """Create a camera-like image using PIL"""
        # Create a blank image with gradient background
        width, height = 400, 300
        image = Image.new('RGB', (width, height), color='#2c3e50')
        draw = ImageDraw.Draw(image)
        
        # Create gradient background
        for y in range(height):
            # Simple gradient from dark to light blue
            r = int(44 + (y / height) * 50)
            g = int(62 + (y / height) * 50)
            b = int(80 + (y / height) * 50)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add camera UI elements
        try:
            # Try to use a default font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        except:
            font_large = None
            font_small = None
        
        # Camera title
        draw.text((120, 30), "ASL CAMERA FEED", fill='white', font=font_large)
        
        # Hand visualization with animation
        center_x, center_y = 200, 150
        pulse = int(10 * abs(np.sin(time.time() * 3)))
        
        # Draw hand circle
        draw.ellipse([center_x-50-pulse, center_y-50-pulse, 
                     center_x+50+pulse, center_y+50+pulse], 
                    outline='#00ff00', width=3)
        
        # Draw finger points
        for angle in [30, 90, 150, 210, 270]:
            rad = np.radians(angle)
            fx = center_x + int(40 * np.cos(rad))
            fy = center_y + int(40 * np.sin(rad))
            draw.ellipse([fx-8, fy-8, fx+8, fy+8], fill='#ff6b6b')
        
        # Status text
        draw.text((140, 220), "Hand Detected ✓", fill='#00ff00', font=font_small)
        draw.text((120, 250), "Make ASL Gestures", fill='#ccccff', font=font_small)
        
        return image

def display_chat_messages(chat_history):
    """Display chat messages in a beautiful format"""
    if not chat_history:
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <h3>🤖 Welcome to ASL AI Assistant!</h3>
            <p>Start communicating using ASL gestures or the virtual keyboard</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    for msg in chat_history[-5:]:  # Show last 5 messages
        if msg['type'] == 'user':
            st.markdown(f'''
            <div class='chat-bubble user'>
                <strong>You (ASL):</strong> {msg['message']}
                <div style='font-size: 0.8em; opacity: 0.7; text-align: right;'>
                    {time.strftime('%H:%M', time.localtime(msg['time']))}
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class='chat-bubble bot'>
                <strong>AI Assistant:</strong> {msg['message']}
                <div style='font-size: 0.8em; opacity: 0.7;'>
                    {time.strftime('%H:%M', time.localtime(msg['time']))}
                </div>
            </div>
            ''', unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">👋 ASL Recognition Mobile Prototype</h1>', 
                unsafe_allow_html=True)
    
    # Initialize session state
    if 'asl_app' not in st.session_state:
        st.session_state.asl_app = ASLPrototype()
    
    asl_app = st.session_state.asl_app
    
    # Create layout similar to mobile app
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Webcam feed section
        st.markdown('<div class="camera-feed">', unsafe_allow_html=True)
        st.subheader("📷 ASL Camera Input")
        
        # Create and display camera image using PIL
        camera_image = asl_app.create_camera_image()
        st.image(camera_image, use_column_width=True, 
                caption="Live ASL Camera Simulation - Show hand gestures here")
        
        # Control buttons
        col1a, col1b, col1c = st.columns(3)
        
        with col1a:
            if st.button("🎥 Start Camera", use_container_width=True):
                st.success("Camera activated - ASL gesture detection running")
                
        with col1b:
            if st.button("🔄 Detect Gesture", use_container_width=True):
                # Simulate gesture detection
                gesture = asl_app.simulate_gesture_prediction()
                asl_app.process_gesture(gesture)
                st.toast(f"Gesture Detected: {gesture}", icon="✅")
                
        with col1c:
            if st.button("🗣️ Voice Command", use_container_width=True):
                asl_app.process_gesture('VOICE')
                st.toast("Voice command simulated", icon="🎤")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Mode display
        mode_color = "🟢" if asl_app.current_mode == "typing" else "🔵"
        st.subheader(f"{mode_color} Current Mode: {asl_app.current_mode.upper()}")
        
        if asl_app.current_mode == "typing":
            # Text display
            st.markdown("### ✍️ Your Message")
            st.text_area("Typed Text (from ASL gestures):", 
                        asl_app.typed_text, height=100, key="typed_text")
            
            # Virtual Keyboard
            st.markdown("### ⌨️ Virtual Keyboard")
            for row in asl_app.mobile_keyboard:
                cols = st.columns(len(row))
                for i, key in enumerate(row):
                    with cols[i]:
                        key_class = "keyboard-key"
                        if key == 'SPACE':
                            key_class += " space"
                        elif key in ['DEL', 'HELP']:
                            key_class += " special"
                        elif key in ['ENTER', 'VOICE']:
                            key_class += " action"
                        
                        if st.button(key, key=f"key_{key}_{i}", use_container_width=True):
                            if key == 'DEL':
                                asl_app.process_gesture('DELETE')
                            else:
                                asl_app.process_gesture(key)
            
            # Send button
            if st.button("📤 Send Message", use_container_width=True):
                asl_app.send_message()
                
        else:  # Mouse mode
            st.markdown("### 🖱️ Mouse Control Mode")
            
            # Mouse control simulation
            mouse_col1, mouse_col2, mouse_col3, mouse_col4 = st.columns(4)
            
            with mouse_col1:
                if st.button("⬅️ Left", use_container_width=True):
                    st.info("Cursor moved left")
                    
            with mouse_col2:
                if st.button("🖱️ Click", use_container_width=True):
                    st.success("Mouse clicked!")
                    
            with mouse_col3:
                if st.button("➡️ Right", use_container_width=True):
                    st.info("Cursor moved right")
                    
            with mouse_col4:
                if st.button("🔄 Scroll", use_container_width=True):
                    st.info("Page scrolled")
            
            st.slider("Cursor Sensitivity", 1, 10, 5, key="cursor_speed")
            
        # Chat History
        st.markdown("### 💬 Conversation")
        display_chat_messages(asl_app.chat_history)
    
    with col2:
        # Gesture recognition panel
        st.subheader("🎯 Gesture Recognition")
        
        # Current prediction
        if st.button("Detect Current ASL Gesture", use_container_width=True):
            current_gesture = asl_app.simulate_gesture_prediction()
            st.markdown(f'<div class="gesture-card">Current Gesture: <span class="prediction-badge">{current_gesture}</span></div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="gesture-card">Current Gesture: <span style="color: #666;">Show ASL gesture to camera</span></div>', 
                       unsafe_allow_html=True)
        
        # Feedback message
        if asl_app.feedback_message:
            st.info(f"💡 {asl_app.feedback_message}")
        
        # Gesture history
        st.subheader("📊 Recent Gestures")
        if asl_app.gesture_history:
            for gesture, timestamp in reversed(asl_app.gesture_history[-5:]):
                time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
                st.markdown(f'<div class="gesture-card">🎯 {gesture} <small>({time_str})</small></div>', 
                           unsafe_allow_html=True)
        else:
            st.write("No gestures detected yet")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        quick_col1, quick_col2 = st.columns(2)
        
        with quick_col1:
            if st.button("🌐 Google", use_container_width=True):
                asl_app.typed_text = "google"
                asl_app.send_message()
                
            if st.button("📺 YouTube", use_container_width=True):
                asl_app.typed_text = "Open YouTube"
                asl_app.send_message()
                
            if st.button("❓ Help", use_container_width=True):
                asl_app.process_gesture('HELP')
                
        with quick_col2:
            if st.button("🗑️ Clear", use_container_width=True):
                asl_app.typed_text = ""
                st.success("Text cleared!")
                
            if st.button("🔊 Speak", use_container_width=True):
                if asl_app.typed_text:
                    st.success(f"Speaking: {asl_app.typed_text}")
                else:
                    st.warning("No text to speak")
                    
            if st.button("🔄 Mode", use_container_width=True):
                asl_app.process_gesture('MOUSE')
        
        # Statistics
        st.subheader("📈 Usage Stats")
        stats_data = {
            'Metric': ['Gestures Today', 'Words Typed', 'Mode Switches', 'Accuracy'],
            'Value': [
                f"{len(asl_app.gesture_history)}", 
                f"{len(asl_app.typed_text.split())}", 
                f"{len([g for g in asl_app.gesture_history if g[0] == 'MOUSE'])}", 
                "92%"
            ]
        }
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True)
        
        # Quick Phrases
        st.subheader("💬 Quick Phrases")
        quick_phrases = [
            "Hello, how are you?",
            "Thank you very much", 
            "I use sign language",
            "Where is the restroom?",
            "Nice to meet you",
            "I need help please"
        ]
        
        for phrase in quick_phrases:
            if st.button(phrase, use_container_width=True):
                asl_app.typed_text = phrase
                asl_app.feedback_message = f"📝 Quick phrase: {phrase}"
    
    # Footer with instructions
    st.markdown("---")
    st.markdown("""
    ### 📱 Mobile App Features Demo:
    - **ASL Gesture Typing**: Convert hand signs to text in real-time
    - **Mouse Control**: Navigate and control your device with gestures  
    - **Voice Commands**: Integrated voice recognition
    - **AI Chat Assistant**: Get intelligent responses
    - **Virtual Keyboard**: Touch-friendly fallback input
    - **Quick Actions**: One-tap access to common functions
    
    *Note: This is a simulation prototype. Full mobile app includes real camera processing with MediaPipe.*
    """)

if __name__ == "__main__":
    main()
