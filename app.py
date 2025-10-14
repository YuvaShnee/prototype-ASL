# app.py
import streamlit as st
import numpy as np
import time
import pandas as pd
from PIL import Image, ImageDraw
import io
import base64
import random

# Page configuration for mobile-like interface
st.set_page_config(
    page_title="ASL Mobile App - Complete Demo",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile app styling
st.markdown("""
<style>
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
    
    .scenario-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        color: white;
        text-align: center;
    }
    
    .demo-section {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .feedback-message {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 12px;
        margin: 8px 0;
        border-left: 5px solid #4ECDC4;
        font-weight: bold;
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
    
    .gesture-sample {
        border: 3px solid #4ECDC4;
        border-radius: 10px;
        margin: 5px;
        padding: 5px;
        text-align: center;
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

class MobileASLApp:
    def __init__(self):
        self.typed_text = ""
        self.current_mode = "typing"
        self.gesture_history = []
        self.feedback_message = ""
        self.chat_history = []
        self.current_gesture = None
        self.mouse_position = [100, 100]
        self.voice_command_active = False
        
        # ASL gesture mapping
        self.asl_gestures = {
            'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G',
            'H': 'H', 'I': 'I', 'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N',
            'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S', 'T': 'T', 'U': 'U',
            'V': 'V', 'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z',
            'SPACE': 'SPACE', 'DELETE': 'DELETE', 'ENTER': 'ENTER', 
            'MOUSE': 'MOUSE', 'VOICE': 'VOICE', 'HELP': 'HELP'
        }
        
        # Mobile virtual keyboard
        self.mobile_keyboard = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'DEL'],
            ['SPACE', 'ENTER', 'VOICE', 'HELP']
        ]
        
        # Demo images data (base64 encoded placeholder images)
        self.demo_images = self.create_demo_images()

    def create_demo_images(self):
        """Create demo images for different scenarios"""
        images = {}
        
        # Hand Gesture Typing Images
        images['typing_A'] = self.create_gesture_image("A", "👋", "Closed fist, thumb aside")
        images['typing_B'] = self.create_gesture_image("B", "✋", "Flat hand, fingers together")
        images['typing_C'] = self.create_gesture_image("C", "🤟", "Curved hand, like letter C")
        
        # Mouse Control Images
        images['mouse_move'] = self.create_mouse_image("🖐️", "Open hand moves cursor")
        images['mouse_click'] = self.create_mouse_image("👇", "Index finger taps for click")
        images['mouse_scroll'] = self.create_mouse_image("🔄", "Two fingers scroll")
        
        # Voice Control Images
        images['voice_active'] = self.create_voice_image("🎤", "Microphone active")
        images['voice_command'] = self.create_voice_image("🗣️", "Speaking command")
        
        return images

    def create_gesture_image(self, letter, emoji, description):
        """Create ASL gesture demonstration image"""
        img = Image.new('RGB', (200, 200), color='#74b9ff')
        draw = ImageDraw.Draw(img)
        
        # Draw hand circle
        draw.ellipse([50, 50, 150, 150], outline='#ffffff', width=3)
        
        # Add letter and emoji
        draw.text((100, 80), emoji, fill='#ffffff', anchor='mm', font_size=40)
        draw.text((100, 120), letter, fill='#ffffff', anchor='mm', font_size=30)
        draw.text((100, 160), description, fill='#ffffff', anchor='mm', font_size=12)
        
        return img

    def create_mouse_image(self, emoji, description):
        """Create mouse control demonstration image"""
        img = Image.new('RGB', (200, 200), color='#a29bfe')
        draw = ImageDraw.Draw(img)
        
        # Draw computer screen
        draw.rectangle([30, 30, 170, 120], fill='#2d3436', outline='#ffffff', width=2)
        
        # Add cursor
        draw.rectangle([80, 80, 90, 90], fill='#00ff00')
        
        # Add emoji and description
        draw.text((100, 150), emoji, fill='#ffffff', anchor='mm', font_size=40)
        draw.text((100, 180), description, fill='#ffffff', anchor='mm', font_size=10)
        
        return img

    def create_voice_image(self, emoji, description):
        """Create voice control demonstration image"""
        img = Image.new('RGB', (200, 200), color='#fd79a8')
        draw = ImageDraw.Draw(img)
        
        # Draw sound waves
        for i, radius in enumerate([30, 50, 70]):
            draw.ellipse([100-radius, 100-radius, 100+radius, 100+radius], 
                        outline='#ffffff', width=2)
        
        # Add emoji and description
        draw.text((100, 100), emoji, fill='#ffffff', anchor='mm', font_size=40)
        draw.text((100, 160), description, fill='#ffffff', anchor='mm', font_size=12)
        
        return img

    def create_simulated_camera_feed(self):
        """Create a simulated camera feed"""
        width, height = 300, 200
        image = Image.new('RGB', (width, height), color='#2c3e50')
        draw = ImageDraw.Draw(image)
        
        # Camera frame
        draw.rectangle([10, 10, width-10, height-10], outline='#ffffff', width=2)
        
        # Status text
        draw.text((width//2, 30), "📱 Mobile Camera", fill='#ffffff', anchor='mm')
        draw.text((width//2, height//2), "Show ASL Gesture", fill='#74b9ff', anchor='mm')
        draw.text((width//2, height-30), "Active ✓", fill='#00ff00', anchor='mm')
        
        return image

    def detect_gesture_simulation(self):
        """Simulate gesture detection"""
        gestures = list(self.asl_gestures.keys())
        return random.choice(gestures)

    def process_gesture(self, gesture):
        """Process detected gesture with detailed feedback"""
        current_time = time.time()
        
        if gesture in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 
                      'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 
                      'W', 'X', 'Y', 'Z']:
            self.typed_text += gesture
            self.feedback_message = f"✅ ASL Gesture '{gesture}' detected and typed!"
            
        elif gesture == 'SPACE':
            self.typed_text += ' '
            self.feedback_message = "␣ Space added to message"
            
        elif gesture == 'DELETE':
            self.typed_text = self.typed_text[:-1] if self.typed_text else ""
            self.feedback_message = "🗑️ Last character deleted"
            
        elif gesture == 'ENTER':
            self.send_message()
            
        elif gesture == 'MOUSE':
            self.current_mode = 'mouse' if self.current_mode == 'typing' else 'typing'
            self.feedback_message = f"🔄 Mode switched to {self.current_mode.upper()}"
            
        elif gesture == 'VOICE':
            self.activate_voice_command()
            
        elif gesture == 'HELP':
            self.feedback_message = "❓ Help: Use ASL gestures to type, or switch to mouse/voice mode"
            
        self.current_gesture = gesture
        self.gesture_history.append((gesture, current_time))

    def activate_voice_command(self):
        """Simulate voice command activation"""
        self.voice_command_active = True
        voice_commands = [
            "Hello, how are you today?",
            "Open Google search for me",
            "What's the weather forecast?",
            "Send message to mom: I'll be home soon",
            "Set alarm for 7 AM tomorrow"
        ]
        
        selected_command = random.choice(voice_commands)
        self.typed_text = selected_command
        self.feedback_message = f"🎤 Voice command: '{selected_command}'"

    def control_mouse(self, action):
        """Control mouse with detailed feedback"""
        if action == "move_left":
            self.mouse_position[0] = max(0, self.mouse_position[0] - 20)
            self.feedback_message = "🖐️ Hand gesture moved cursor LEFT"
            
        elif action == "move_right":
            self.mouse_position[0] = min(200, self.mouse_position[0] + 20)
            self.feedback_message = "🖐️ Hand gesture moved cursor RIGHT"
            
        elif action == "move_up":
            self.mouse_position[1] = max(0, self.mouse_position[1] - 20)
            self.feedback_message = "🖐️ Hand gesture moved cursor UP"
            
        elif action == "move_down":
            self.mouse_position[1] = min(200, self.mouse_position[1] + 20)
            self.feedback_message = "🖐️ Hand gesture moved cursor DOWN"
            
        elif action == "click":
            self.feedback_message = "👇 Finger tap gesture - MOUSE CLICK performed!"
            
        elif action == "scroll":
            self.feedback_message = "🔄 Two-finger scroll gesture - PAGE SCROLLED"

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
            
            self.feedback_message = "📤 Message sent to AI assistant!"
            self.typed_text = ""

    def get_ai_response(self, user_message):
        """Get simulated AI response"""
        responses = {
            "hello": "👋 Hello! I'm your ASL assistant. Great to see you using gesture controls!",
            "help": "🤖 I can help you with:\n• ASL gesture typing\n• Mouse control with hand gestures\n• Voice commands\n• Quick actions",
            "weather": "🌤️ The weather is perfect for testing ASL controls! Sunny with a chance of innovation.",
            "google": "🌐 Opening Google... Ready for your search query!",
            "youtube": "📺 Launching YouTube... Enjoy gesture-controlled browsing!",
            "thank you": "😊 You're welcome! I'm here to make mobile interaction accessible for everyone.",
            "mouse": "🖱️ Switching to mouse control mode. Use hand gestures to navigate!",
            "voice": "🎤 Voice control activated. Speak your command clearly.",
            "default": "💡 Excellent ASL communication! I understood your gesture perfectly."
        }
        
        user_lower = user_message.lower()
        for key in responses:
            if key in user_lower:
                return responses[key]
        return responses["default"]

def display_chat_messages(chat_history):
    """Display chat messages"""
    if not chat_history:
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <h3>🤖 ASL Mobile Assistant</h3>
            <p>Start communicating using gestures, voice, or mouse controls!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    for msg in chat_history[-5:]:
        if msg['type'] == 'user':
            st.markdown(f'''
            <div class='chat-bubble user'>
                <strong>You:</strong> {msg['message']}
                <div style='font-size: 0.8em; opacity: 0.7; text-align: right;'>
                    {time.strftime('%H:%M', time.localtime(msg['time']))}
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class='chat-bubble bot'>
                <strong>Assistant:</strong> {msg['message']}
                <div style='font-size: 0.8em; opacity: 0.7;'>
                    {time.strftime('%H:%M', time.localtime(msg['time']))}
                </div>
            </div>
            ''', unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">📱 ASL Mobile App - Complete Demo</h1>', 
                unsafe_allow_html=True)
    
    # Initialize session state
    if 'mobile_app' not in st.session_state:
        st.session_state.mobile_app = MobileASLApp()
    
    app = st.session_state.mobile_app
    
    # Mobile container
    st.markdown('<div class="mobile-container">', unsafe_allow_html=True)
    
    # Demo Scenarios Section
    st.markdown('<div class="scenario-card">', unsafe_allow_html=True)
    st.subheader("🎯 Demo Scenarios")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Scenario 1: Hand Gesture Typing
    with st.expander("👋 1. HAND GESTURE TYPING", expanded=True):
        st.markdown("**Type using ASL gestures captured by mobile camera**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.image(app.demo_images['typing_A'], caption="ASL 'A' Gesture")
            if st.button("Detect 'A'", use_container_width=True):
                app.process_gesture('A')
        with col2:
            st.image(app.demo_images['typing_B'], caption="ASL 'B' Gesture")
            if st.button("Detect 'B'", use_container_width=True):
                app.process_gesture('B')
        with col3:
            st.image(app.demo_images['typing_C'], caption="ASL 'C' Gesture")
            if st.button("Detect 'C'", use_container_width=True):
                app.process_gesture('C')
        
        st.markdown("💡 *Make these hand signs in front of your mobile camera*")
    
    # Scenario 2: Mouse Control
    with st.expander("🖱️ 2. MOUSE CONTROL", expanded=True):
        st.markdown("**Control cursor and clicks with finger gestures**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.image(app.demo_images['mouse_move'], caption="Move Cursor")
            if st.button("👆 Move Cursor", use_container_width=True):
                app.control_mouse("move_right")
        with col2:
            st.image(app.demo_images['mouse_click'], caption="Click Action")
            if st.button("👇 Mouse Click", use_container_width=True):
                app.control_mouse("click")
        with col3:
            st.image(app.demo_images['mouse_scroll'], caption="Scroll Page")
            if st.button("🔄 Scroll", use_container_width=True):
                app.control_mouse("scroll")
        
        # Mouse position display
        st.progress(app.mouse_position[0] / 200, text=f"Cursor Position: ({app.mouse_position[0]}, {app.mouse_position[1]})")
        
        st.markdown("💡 *Use finger gestures to control mouse movements*")
    
    # Scenario 3: Voice Control
    with st.expander("🎤 3. VOICE CONTROL", expanded=True):
        st.markdown("**Use voice commands for hands-free operation**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(app.demo_images['voice_active'], caption="Voice Active")
            if st.button("🎤 Start Voice", use_container_width=True):
                app.activate_voice_command()
        with col2:
            st.image(app.demo_images['voice_command'], caption="Speaking")
            if st.button("🗣️ Random Command", use_container_width=True):
                app.process_gesture('VOICE')
        
        st.markdown("💡 *Tap voice button and speak your command*")
    
    # Live Camera Feed
    st.markdown("---")
    st.subheader("📷 Live Mobile Camera")
    camera_feed = app.create_simulated_camera_feed()
    st.image(camera_feed, use_column_width=True)
    
    if st.button("🎯 Detect Current Gesture", use_container_width=True):
        gesture = app.detect_gesture_simulation()
        app.process_gesture(gesture)
        st.toast(f"Gesture Detected: {gesture}", icon="✅")
    
    # Current Mode & Feedback
    st.markdown(f'''
    <div class="demo-section">
        <h4>📱 Current Mode: {app.current_mode.upper()}</h4>
        <p>Last Gesture: {app.current_gesture if app.current_gesture else "None"}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Real-time Feedback Display
    if app.feedback_message:
        st.markdown(f'<div class="feedback-message">💡 {app.feedback_message}</div>', 
                   unsafe_allow_html=True)
    
    # Message Composition
    st.subheader("💬 Compose Message")
    st.text_area("Your Message:", value=app.typed_text, height=100, key="message_display")
    
    # Virtual Keyboard
    st.subheader("⌨️ Virtual Keyboard")
    for row in app.mobile_keyboard:
        cols = st.columns(len(row))
        for i, key in enumerate(row):
            with cols[i]:
                if st.button(key, key=f"key_{key}_{i}", use_container_width=True):
                    if key == 'DEL':
                        app.process_gesture('DELETE')
                    elif key == 'VOICE':
                        app.process_gesture('VOICE')
                    elif key == 'HELP':
                        app.process_gesture('HELP')
                    else:
                        app.process_gesture(key)
    
    # Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Send Message", use_container_width=True):
            app.send_message()
    with col2:
        if st.button("🔄 Switch Mode", use_container_width=True):
            app.process_gesture('MOUSE')
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    quick_cols = st.columns(4)
    actions = [
        ("🌐 Google", "google"),
        ("📺 YouTube", "youtube"), 
        ("🌤️ Weather", "weather"),
        ("❓ Help", "help")
    ]
    
    for i, (label, command) in enumerate(actions):
        with quick_cols[i]:
            if st.button(label, use_container_width=True):
                app.typed_text = command
                app.send_message()
    
    # Chat History
    st.subheader("💬 Conversation")
    display_chat_messages(app.chat_history)
    
    # Statistics & History
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Gesture History")
        if app.gesture_history:
            for i, (gesture, timestamp) in enumerate(reversed(app.gesture_history[-5:])):
                st.write(f"{i+1}. 🎯 {gesture} - {time.strftime('%H:%M:%S', time.localtime(timestamp))}")
        else:
            st.write("No gestures yet")
    
    with col2:
        st.subheader("📈 Usage Stats")
        stats_data = {
            'Metric': ['Gestures', 'Messages', 'Mode Switches', 'Voice Commands'],
            'Count': [
                len(app.gesture_history),
                len([m for m in app.chat_history if m['type'] == 'user']),
                len([g for g in app.gesture_history if g[0] == 'MOUSE']),
                len([g for g in app.gesture_history if g[0] == 'VOICE'])
            ]
        }
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True)
    
    # Demo Instructions
    with st.expander("🎓 Demo Instructions"):
        st.markdown("""
        ### 🎯 **Demo Scenarios:**
        
        **1. 👋 Hand Gesture Typing**
        - Show ASL A, B, C gestures to camera
        - See real-time text conversion
        - Use SPACE, DELETE gestures
        
        **2. 🖱️ Mouse Control** 
        - Move cursor with hand movements
        - Click with finger taps
        - Scroll with two fingers
        
        **3. 🎤 Voice Control**
        - Activate voice commands
        - Speak natural language
        - Get instant responses
        
        ### 💡 **Feedback System:**
        - Every action provides clear feedback
        - Visual and text confirmation
        - Error prevention guidance
        - Success confirmation
        
        *All features work together for complete mobile accessibility!*
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
