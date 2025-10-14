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
    page_title="ASL Mobile App - Interactive Demo",
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
    
    .demo-scenario {
        position: fixed;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 15px;
        width: 300px;
        color: white;
        z-index: 1000;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .scenario-point {
        background: rgba(255,255,255,0.2);
        border-radius: 10px;
        padding: 10px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .scenario-point:hover {
        background: rgba(255,255,255,0.3);
        transform: translateX(5px);
        border-color: #4ECDC4;
    }
    
    .scenario-point.active {
        background: rgba(255,255,255,0.4);
        border-color: #00ff00;
    }
    
    .mobile-phone {
        background: #2c3e50;
        border-radius: 25px;
        padding: 20px;
        margin: 10px auto;
        width: 250px;
        height: 500px;
        position: relative;
        border: 3px solid #34495e;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    
    .phone-screen {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        border-radius: 15px;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .gesture-animation {
        position: absolute;
        width: 80px;
        height: 80px;
        background: rgba(255,255,255,0.9);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
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
        self.active_scenario = None
        self.phone_gesture_position = {"A": [60, 150], "B": [150, 150], "C": [120, 250]}
        
        # Demo scenarios
        self.scenarios = {
            "asl_typing": {
                "title": "👋 ASL Gesture Typing",
                "description": "Type using hand gestures on mobile",
                "steps": [
                    "Show 'A' gesture to camera",
                    "Show 'B' gesture to camera", 
                    "Show 'C' gesture to camera",
                    "Add space between words",
                    "Send message"
                ]
            },
            "mouse_control": {
                "title": "🖱️ Mouse Control",
                "description": "Control cursor with finger gestures",
                "steps": [
                    "Move hand to control cursor",
                    "Tap index finger to click",
                    "Two-finger scroll",
                    "Right-click with three fingers"
                ]
            },
            "voice_commands": {
                "title": "🎤 Voice Control",
                "description": "Hands-free voice commands",
                "steps": [
                    "Tap microphone button",
                    "Speak your command",
                    "Wait for processing",
                    "See instant response"
                ]
            }
        }

    def create_mobile_phone_display(self, scenario=None):
        """Create an animated mobile phone display showing current scenario"""
        phone_bg = Image.new('RGB', (250, 500), color='#2c3e50')
        screen_bg = Image.new('RGB', (210, 460), color='#74b9ff')
        draw = ImageDraw.Draw(screen_bg)
        
        # Phone frame
        draw.rectangle([0, 0, 209, 459], outline='#34495e', width=3)
        
        # Status bar
        draw.rectangle([0, 0, 209, 30], fill='#2c3e50')
        draw.text((105, 15), "ASL Mobile", fill='white', anchor='mm')
        
        # Content area based on scenario
        if scenario == "asl_typing":
            # Show gesture animation positions
            for gesture, pos in self.phone_gesture_position.items():
                x, y = pos
                draw.ellipse([x-20, y-20, x+20, y+20], fill='rgba(255,255,255,0.8)')
                draw.text((x, y), gesture, fill='#2c3e50', anchor='mm', font_size=20)
            
            draw.text((105, 80), "👋 Gesture Typing", fill='white', anchor='mm')
            draw.text((105, 400), "Make ASL gestures", fill='white', anchor='mm')
            
        elif scenario == "mouse_control":
            # Show cursor control
            cursor_x, cursor_y = self.mouse_position
            draw.rectangle([cursor_x-5, cursor_y-5, cursor_x+5, cursor_y+5], fill='#00ff00')
            draw.text((105, 80), "🖱️ Mouse Control", fill='white', anchor='mm')
            draw.text((105, 400), "Move hand to navigate", fill='white', anchor='mm')
            
        elif scenario == "voice_commands":
            # Show voice interface
            draw.ellipse([80, 150, 130, 200], fill='#fd79a8')
            draw.text((105, 175), "🎤", fill='white', anchor='mm', font_size=20)
            draw.text((105, 80), "🎤 Voice Control", fill='white', anchor='mm')
            draw.text((105, 400), "Speak your command", fill='white', anchor='mm')
            
        else:
            # Default home screen
            draw.text((105, 150), "📱 ASL Mobile", fill='white', anchor='mm', font_size=24)
            draw.text((105, 200), "Tap scenario to start", fill='white', anchor='mm')
            draw.text((105, 400), "Accessibility First", fill='white', anchor='mm')
        
        # Paste screen onto phone
        phone_bg.paste(screen_bg, (20, 20))
        return phone_bg

    def start_scenario(self, scenario_name):
        """Start a demo scenario"""
        self.active_scenario = scenario_name
        self.feedback_message = f"🎬 Starting {self.scenarios[scenario_name]['title']} demo!"
        
        if scenario_name == "asl_typing":
            self.typed_text = ""
            self.current_mode = "typing"
        elif scenario_name == "mouse_control":
            self.current_mode = "mouse"
            self.mouse_position = [100, 100]
        elif scenario_name == "voice_commands":
            self.voice_command_active = True

    def process_gesture(self, gesture):
        """Process detected gesture with scenario-aware feedback"""
        current_time = time.time()
        
        if gesture in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 
                      'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 
                      'W', 'X', 'Y', 'Z']:
            self.typed_text += gesture
            self.feedback_message = f"✅ Mobile camera detected ASL '{gesture}' gesture!"
            
        elif gesture == 'SPACE':
            self.typed_text += ' '
            self.feedback_message = "␣ Space gesture recognized on mobile"
            
        elif gesture == 'DELETE':
            self.typed_text = self.typed_text[:-1] if self.typed_text else ""
            self.feedback_message = "🗑️ Delete gesture performed on phone"
            
        elif gesture == 'ENTER':
            self.send_message()
            
        elif gesture == 'MOUSE':
            self.current_mode = 'mouse' if self.current_mode == 'typing' else 'typing'
            self.feedback_message = f"🔄 Switched to {self.current_mode.upper()} mode on mobile"
            
        elif gesture == 'VOICE':
            self.activate_voice_command()
            
        self.current_gesture = gesture
        self.gesture_history.append((gesture, current_time))

    def control_mouse(self, action):
        """Control mouse with mobile-specific feedback"""
        if action == "move_left":
            self.mouse_position[0] = max(20, self.mouse_position[0] - 20)
            self.feedback_message = "🖐️ Hand gesture moved mobile cursor LEFT"
            
        elif action == "move_right":
            self.mouse_position[0] = min(180, self.mouse_position[0] + 20)
            self.feedback_message = "🖐️ Hand gesture moved mobile cursor RIGHT"
            
        elif action == "move_up":
            self.mouse_position[1] = max(40, self.mouse_position[1] - 20)
            self.feedback_message = "🖐️ Hand gesture moved mobile cursor UP"
            
        elif action == "move_down":
            self.mouse_position[1] = min(420, self.mouse_position[1] + 20)
            self.feedback_message = "🖐️ Hand gesture moved mobile cursor DOWN"
            
        elif action == "click":
            self.feedback_message = "👇 Finger tap detected - MOBILE CLICK performed!"
            
        elif action == "scroll":
            self.feedback_message = "🔄 Two-finger scroll on mobile screen"

    def activate_voice_command(self):
        """Activate voice command on mobile"""
        self.voice_command_active = True
        voice_commands = [
            "Hello mobile assistant",
            "Open camera on my phone",
            "Send text message to contact",
            "What's the weather today?",
            "Set reminder for meeting"
        ]
        
        selected_command = random.choice(voice_commands)
        self.typed_text = selected_command
        self.feedback_message = f"🎤 Mobile voice command: '{selected_command}'"

    def send_message(self):
        """Send message from mobile"""
        if self.typed_text.strip():
            self.chat_history.append({
                'type': 'user',
                'message': self.typed_text,
                'time': time.time()
            })
            
            ai_response = self.get_ai_response(self.typed_text)
            
            self.chat_history.append({
                'type': 'bot', 
                'message': ai_response,
                'time': time.time()
            })
            
            self.feedback_message = "📤 Message sent from mobile!"
            self.typed_text = ""

    def get_ai_response(self, user_message):
        """Get mobile-appropriate AI response"""
        responses = {
            "hello": "👋 Hello! Mobile ASL assistant here. Great gesture control!",
            "help": "🤖 Mobile help: Use gestures, voice, or touch to control your phone",
            "weather": "🌤️ Perfect weather for mobile ASL testing!",
            "google": "🌐 Opening Google on your mobile...",
            "youtube": "📺 Launching YouTube mobile app...",
            "camera": "📷 Mobile camera activated for gesture recognition!",
            "default": "📱 Mobile command received! ASL gestures working perfectly."
        }
        
        user_lower = user_message.lower()
        for key in responses:
            if key in user_lower:
                return responses[key]
        return responses["default"]

def main():
    st.markdown('<h1 class="main-header">📱 ASL Mobile App - Interactive Demo</h1>', 
                unsafe_allow_html=True)
    
    # Initialize session state
    if 'mobile_app' not in st.session_state:
        st.session_state.mobile_app = MobileASLApp()
    
    app = st.session_state.mobile_app
    
    # Left Side Demo Scenario Panel
    st.markdown(f'''
    <div class="demo-scenario">
        <h3>🎯 Demo Scenarios</h3>
        <p>Click to start mobile demo:</p>
        
        <div class="scenario-point {'active' if app.active_scenario == 'asl_typing' else ''}" 
             onclick="alert('Starting ASL Gesture Demo on Mobile')">
            <strong>👋 ASL Gesture Typing</strong>
            <br><small>Type with hand gestures on phone</small>
        </div>
        
        <div class="scenario-point {'active' if app.active_scenario == 'mouse_control' else ''}" 
             onclick="alert('Starting Mouse Control Demo on Mobile')">
            <strong>🖱️ Mouse Control</strong>
            <br><small>Navigate with finger gestures</small>
        </div>
        
        <div class="scenario-point {'active' if app.active_scenario == 'voice_commands' else ''}" 
             onclick="alert('Starting Voice Control Demo on Mobile')">
            <strong>🎤 Voice Commands</strong>
            <br><small>Hands-free mobile control</small>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Mobile container
    st.markdown('<div class="mobile-container">', unsafe_allow_html=True)
    
    # Mobile Phone Display
    st.subheader("📱 Mobile Phone Demo")
    
    # Create and display mobile phone
    phone_display = app.create_mobile_phone_display(app.active_scenario)
    st.image(phone_display, use_column_width=False, caption="ASL Mobile Phone Interface")
    
    # Scenario Control Buttons
    st.subheader("🎬 Control Demo Scenarios")
    
    scenario_cols = st.columns(3)
    with scenario_cols[0]:
        if st.button("👋 Start ASL Typing", use_container_width=True):
            app.start_scenario("asl_typing")
    with scenario_cols[1]:
        if st.button("🖱️ Start Mouse Control", use_container_width=True):
            app.start_scenario("mouse_control")
    with scenario_cols[2]:
        if st.button("🎤 Start Voice Control", use_container_width=True):
            app.start_scenario("voice_commands")
    
    # Active Scenario Display
    if app.active_scenario:
        scenario = app.scenarios[app.active_scenario]
        st.markdown(f'''
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                    border-radius: 10px; padding: 15px; margin: 10px 0;">
            <h4>🎯 Active: {scenario['title']}</h4>
            <p><strong>Description:</strong> {scenario['description']}</p>
            <p><strong>Steps:</strong></p>
            <ul>
                {"".join([f"<li>{step}</li>" for step in scenario['steps']])}
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    # Real-time Feedback
    if app.feedback_message:
        st.markdown(f'<div class="feedback-message">📱 {app.feedback_message}</div>', 
                   unsafe_allow_html=True)
    
    # Demo Interaction Area
    st.subheader("🔄 Demo Interactions")
    
    if app.active_scenario == "asl_typing":
        st.markdown("**👋 ASL Gesture Typing Demo**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("A Gesture", use_container_width=True):
                app.process_gesture('A')
        with col2:
            if st.button("B Gesture", use_container_width=True):
                app.process_gesture('B')
        with col3:
            if st.button("C Gesture", use_container_width=True):
                app.process_gesture('C')
                
    elif app.active_scenario == "mouse_control":
        st.markdown("**🖱️ Mouse Control Demo**")
        mouse_cols = st.columns(4)
        with mouse_cols[0]:
            if st.button("⬅️ Left", use_container_width=True):
                app.control_mouse("move_left")
        with mouse_cols[1]:
            if st.button("➡️ Right", use_container_width=True):
                app.control_mouse("move_right")
        with mouse_cols[2]:
            if st.button("🖱️ Click", use_container_width=True):
                app.control_mouse("click")
        with mouse_cols[3]:
            if st.button("🔄 Scroll", use_container_width=True):
                app.control_mouse("scroll")
                
    elif app.active_scenario == "voice_commands":
        st.markdown("**🎤 Voice Control Demo**")
        voice_cols = st.columns(2)
        with voice_cols[0]:
            if st.button("🎤 Activate Voice", use_container_width=True):
                app.activate_voice_command()
        with voice_cols[1]:
            if st.button("🗣️ Random Command", use_container_width=True):
                app.process_gesture('VOICE')
    
    # Message Composition
    st.subheader("💬 Mobile Message")
    st.text_area("Typing Area:", value=app.typed_text, height=80, key="mobile_message")
    
    # Virtual Keyboard for Mobile
    st.subheader("⌨️ Mobile Keyboard")
    mobile_keys = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['SPACE', 'DEL', 'ENTER', 'VOICE']
    ]
    
    for row in mobile_keys:
        cols = st.columns(len(row))
        for i, key in enumerate(row):
            with cols[i]:
                if st.button(key, use_container_width=True):
                    if key == 'DEL':
                        app.process_gesture('DELETE')
                    elif key == 'SPACE':
                        app.process_gesture('SPACE')
                    elif key == 'ENTER':
                        app.send_message()
                    elif key == 'VOICE':
                        app.process_gesture('VOICE')
                    else:
                        app.process_gesture(key)
    
    # Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Send from Mobile", use_container_width=True):
            app.send_message()
    with col2:
        if st.button("🔄 Switch Mobile Mode", use_container_width=True):
            app.process_gesture('MOUSE')
    
    # Quick Mobile Actions
    st.subheader("⚡ Mobile Quick Actions")
    quick_cols = st.columns(4)
    actions = [
        ("🌐 Mobile Google", "google"),
        ("📱 Open Camera", "camera"), 
        ("📞 Call Contact", "call"),
        ("📍 Get Location", "location")
    ]
    
    for i, (label, command) in enumerate(actions):
        with quick_cols[i]:
            if st.button(label, use_container_width=True):
                app.typed_text = command
                app.send_message()
    
    # Conversation History
    st.subheader("💬 Mobile Conversation")
    if app.chat_history:
        for msg in app.chat_history[-4:]:
            if msg['type'] == 'user':
                st.markdown(f"**📱 You:** {msg['message']}")
            else:
                st.markdown(f"**🤖 Assistant:** {msg['message']}")
            st.caption(f"Mobile - {time.strftime('%H:%M', time.localtime(msg['time']))}")
    else:
        st.info("Start a demo scenario to see mobile conversation")
    
    # Demo Statistics
    st.subheader("📊 Mobile Demo Stats")
    stats_data = {
        'Mobile Metric': ['Gestures Used', 'Messages Sent', 'Mode Changes', 'Voice Commands'],
        'Count': [
            len(app.gesture_history),
            len([m for m in app.chat_history if m['type'] == 'user']),
            len([g for g in app.gesture_history if g[0] == 'MOUSE']),
            len([g for g in app.gesture_history if g[0] == 'VOICE'])
        ]
    }
    st.dataframe(pd.DataFrame(stats_data), use_container_width=True)
    
    # Demo Instructions
    with st.expander("📱 Mobile Demo Guide"):
        st.markdown("""
        ### 🎯 **Mobile Demo Scenarios:**
        
        **👋 ASL Gesture Typing on Mobile**
        - Use hand gestures instead of keyboard
        - Mobile camera detects ASL signs
        - Real-time text conversion
        
        **🖱️ Mouse Control on Mobile** 
        - Control cursor with finger gestures
        - Tap to click, scroll with two fingers
        - Full navigation without touch
        
        **🎤 Voice Commands on Mobile**
        - Hands-free operation
        - Natural language processing
        - Instant mobile responses
        
        ### 💡 **How to Demo:**
        1. Click scenario in left panel
        2. Watch mobile phone display
        3. Use interaction buttons
        4. See real-time feedback
        
        *Perfect for mobile accessibility demonstrations!*
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
