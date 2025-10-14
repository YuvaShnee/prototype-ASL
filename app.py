# app.py
import streamlit as st
import numpy as np
import time
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import random

# Page configuration for mobile-like interface
st.set_page_config(
    page_title="ASL Mobile App",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for realistic mobile app
st.markdown("""
<style>
    /* Hide all Streamlit default elements */
    .main-header {
        font-size: 0px;
        color: transparent;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile app container */
    .mobile-app {
        width: 375px;
        height: 812px;
        background: #000;
        border-radius: 40px;
        margin: 20px auto;
        padding: 20px;
        position: relative;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        border: 10px solid #333;
        overflow: hidden;
    }
    
    /* Phone screen */
    .phone-screen {
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border-radius: 30px;
        overflow: hidden;
        position: relative;
    }
    
    /* Status bar */
    .status-bar {
        height: 44px;
        background: rgba(0,0,0,0.9);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 20px;
        color: white;
        font-size: 14px;
        font-weight: bold;
    }
    
    /* App content */
    .app-content {
        height: calc(100% - 44px);
        padding: 20px;
        color: white;
        overflow-y: auto;
    }
    
    /* Demo scenarios panel */
    .demo-panel {
        position: fixed;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        background: rgba(0,0,0,0.9);
        border-radius: 15px;
        padding: 20px;
        width: 280px;
        color: white;
        z-index: 1000;
        border: 2px solid #00ff00;
        backdrop-filter: blur(10px);
    }
    
    .scenario-btn {
        width: 100%;
        padding: 15px;
        margin: 10px 0;
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
        border: none;
        border-radius: 12px;
        color: white;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .scenario-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,122,255,0.4);
    }
    
    .scenario-btn.active {
        background: linear-gradient(135deg, #00ff00 0%, #00cc00 100%);
        box-shadow: 0 0 20px rgba(0,255,0,0.5);
    }
    
    /* Mobile app elements */
    .app-section {
        background: rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .camera-view {
        width: 100%;
        height: 200px;
        background: linear-gradient(45deg, #000, #333);
        border-radius: 12px;
        margin: 10px 0;
        position: relative;
        overflow: hidden;
        border: 2px solid #00ff00;
    }
    
    .hand-animation {
        position: absolute;
        width: 80px;
        height: 80px;
        background: rgba(0,255,0,0.3);
        border-radius: 50%;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        animation: pulse 2s infinite;
        border: 3px solid #00ff00;
    }
    
    @keyframes pulse {
        0% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
        50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.7; }
        100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
    }
    
    .keyboard {
        display: grid;
        grid-template-columns: repeat(10, 1fr);
        gap: 5px;
        margin: 10px 0;
    }
    
    .key {
        background: rgba(255,255,255,0.2);
        border: none;
        border-radius: 8px;
        color: white;
        padding: 12px 5px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: center;
    }
    
    .key:hover {
        background: rgba(0,122,255,0.6);
        transform: scale(1.05);
    }
    
    .key.special {
        background: rgba(255,59,48,0.6);
    }
    
    .key.action {
        background: rgba(52,199,89,0.6);
    }
    
    .message-bubble {
        max-width: 80%;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 18px;
        font-size: 14px;
        line-height: 1.4;
    }
    
    .message-user {
        background: #007AFF;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    
    .message-bot {
        background: rgba(255,255,255,0.2);
        margin-right: auto;
        border-bottom-left-radius: 4px;
    }
    
    .typing-area {
        width: 100%;
        height: 60px;
        background: rgba(255,255,255,0.1);
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 12px;
        color: white;
        padding: 15px;
        font-size: 16px;
        margin: 10px 0;
    }
    
    .control-button {
        width: 100%;
        padding: 15px;
        margin: 5px 0;
        background: rgba(0,122,255,0.8);
        border: none;
        border-radius: 12px;
        color: white;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .control-button:hover {
        background: rgba(0,122,255,1);
        transform: translateY(-2px);
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
        self.mouse_position = [50, 50]
        self.voice_command_active = False
        self.active_scenario = None
        self.animation_frame = 0
        
        # Demo scenarios
        self.scenarios = {
            "asl_typing": {
                "title": "👆 ASL Typing",
                "description": "Type with hand gestures",
                "icon": "👆",
                "color": "#007AFF"
            },
            "mouse_control": {
                "title": "🖐️ Mouse Control", 
                "description": "Navigate with gestures",
                "icon": "🖐️",
                "color": "#FF2D55"
            },
            "voice_commands": {
                "title": "🎤 Voice Control",
                "description": "Hands-free commands", 
                "icon": "🎤",
                "color": "#34C759"
            }
        }

    def create_camera_animation(self):
        """Create animated camera view with hand detection"""
        # Create a realistic camera view
        img = Image.new('RGB', (300, 200), color='#000000')
        draw = ImageDraw.Draw(img)
        
        # Camera frame
        draw.rectangle([10, 10, 290, 190], outline='#00ff00', width=2)
        
        # Animated hand circle
        pulse_size = 5 * abs(np.sin(self.animation_frame * 0.5))
        center_x, center_y = 150, 100
        
        # Hand detection area
        draw.ellipse([
            center_x-40-pulse_size, center_y-40-pulse_size,
            center_x+40+pulse_size, center_y+40+pulse_size
        ], outline='#00ff00', width=3)
        
        # Hand dots (fingers)
        for i, angle in enumerate([0, 72, 144, 216, 288]):
            rad = np.radians(angle + self.animation_frame * 10)
            dot_x = center_x + int(30 * np.cos(rad))
            dot_y = center_y + int(30 * np.sin(rad))
            draw.ellipse([dot_x-4, dot_y-4, dot_x+4, dot_y+4], fill='#00ff00')
        
        # Status text
        draw.text((150, 30), "📱 Mobile Camera Active", fill='#00ff00', anchor='mm')
        draw.text((150, 170), "Hand Detected ✓", fill='#00ff00', anchor='mm')
        
        self.animation_frame += 1
        return img

    def create_phone_interface(self):
        """Create the main phone interface"""
        # This will be handled by HTML/CSS in Streamlit components
        pass

    def process_gesture(self, gesture):
        """Process detected gesture"""
        if gesture in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 
                      'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 
                      'W', 'X', 'Y', 'Z']:
            self.typed_text += gesture
            self.feedback_message = f"📱 Gesture '{gesture}' detected"
            
        elif gesture == 'SPACE':
            self.typed_text += ' '
            self.feedback_message = "␣ Space added"
            
        elif gesture == 'DELETE':
            self.typed_text = self.typed_text[:-1] if self.typed_text else ""
            self.feedback_message = "🗑️ Character deleted"
            
        elif gesture == 'ENTER':
            self.send_message()
            
        elif gesture == 'MOUSE':
            self.current_mode = 'mouse' if self.current_mode == 'typing' else 'typing'
            self.feedback_message = f"🔄 {self.current_mode.upper()} mode"
            
        self.current_gesture = gesture
        self.gesture_history.append((gesture, time.time()))

    def control_mouse(self, action):
        """Control mouse movement"""
        if action == "left":
            self.mouse_position[0] = max(0, self.mouse_position[0] - 10)
            self.feedback_message = "🖐️ Cursor moved left"
        elif action == "right":
            self.mouse_position[0] = min(100, self.mouse_position[0] + 10)
            self.feedback_message = "🖐️ Cursor moved right"
        elif action == "click":
            self.feedback_message = "👇 Mouse clicked"
        elif action == "scroll":
            self.feedback_message = "🔄 Page scrolled"

    def activate_voice(self):
        """Activate voice command"""
        commands = [
            "Hello mobile assistant",
            "Open camera application", 
            "Send message to contact",
            "What's the weather today?",
            "Set alarm for morning"
        ]
        self.typed_text = random.choice(commands)
        self.feedback_message = "🎤 Voice command activated"

    def send_message(self):
        """Send message in chat"""
        if self.typed_text.strip():
            self.chat_history.append({
                'type': 'user',
                'message': self.typed_text,
                'time': time.time()
            })
            
            # AI response
            responses = {
                "hello": "👋 Hello! I'm your mobile ASL assistant",
                "camera": "📷 Opening camera for gesture detection",
                "weather": "🌤️ Beautiful day for mobile gestures!",
                "default": "📱 Command received via mobile interface"
            }
            
            response = responses.get(self.typed_text.lower(), responses["default"])
            
            self.chat_history.append({
                'type': 'bot',
                'message': response,
                'time': time.time()
            })
            
            self.feedback_message = "📤 Message sent"
            self.typed_text = ""

    def start_scenario(self, scenario_name):
        """Start a demo scenario"""
        self.active_scenario = scenario_name
        self.feedback_message = f"🚀 Starting {self.scenarios[scenario_name]['title']}"

def main():
    # Initialize app
    if 'mobile_app' not in st.session_state:
        st.session_state.mobile_app = MobileASLApp()
    
    app = st.session_state.mobile_app
    
    # Demo Scenarios Panel (Left Side)
    st.markdown("""
    <div class="demo-panel">
        <h3 style="text-align: center; margin-bottom: 20px; color: #00ff00;">🎯 Demo Scenarios</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create scenario buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("👆\nASL Typing", use_container_width=True, key="btn_asl"):
            app.start_scenario("asl_typing")
    with col2:
        if st.button("🖐️\nMouse Control", use_container_width=True, key="btn_mouse"):
            app.start_scenario("mouse_control")
    with col3:
        if st.button("🎤\nVoice Control", use_container_width=True, key="btn_voice"):
            app.start_scenario("voice_commands")
    
    # Mobile App Interface
    st.markdown("""
    <div class="mobile-app">
        <div class="phone-screen">
            <div class="status-bar">
                <span>9:41</span>
                <span>📶 100% 🔋</span>
            </div>
            <div class="app-content">
    """, unsafe_allow_html=True)
    
    # App Title
    st.markdown("<h2 style='text-align: center; color: white; margin: 20px 0;'>ASL Mobile</h2>", unsafe_allow_html=True)
    
    # Camera View
    st.markdown("<div class='camera-view'>", unsafe_allow_html=True)
    camera_img = app.create_camera_animation()
    st.image(camera_img, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Feedback Message
    if app.feedback_message:
        st.markdown(f"""
        <div style='background: rgba(0,255,0,0.2); padding: 10px; border-radius: 10px; 
                    border: 1px solid #00ff00; margin: 10px 0; text-align: center; color: #00ff00;'>
            🔥 {app.feedback_message}
        </div>
        """, unsafe_allow_html=True)
    
    # Typing Area
    st.markdown("<div class='app-section'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: white;'>💬 Your Message</h4>", unsafe_allow_html=True)
    
    # Text display
    st.markdown(f"""
    <div class='typing-area'>
        {app.typed_text or "Type with gestures..."}
    </div>
    """, unsafe_allow_html=True)
    
    # Virtual Keyboard
    st.markdown("<h4 style='color: white; margin-top: 20px;'>⌨️ Quick Type</h4>", unsafe_allow_html=True)
    
    # Keyboard rows
    keyboard_rows = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'DEL'],
        ['SPACE', 'ENTER', 'VOICE', 'MOUSE']
    ]
    
    for row in keyboard_rows:
        cols = st.columns(len(row))
        for i, key in enumerate(row):
            with cols[i]:
                if st.button(key, use_container_width=True, key=f"key_{key}_{i}"):
                    if key == 'DEL':
                        app.process_gesture('DELETE')
                    elif key == 'SPACE':
                        app.process_gesture('SPACE')
                    elif key == 'ENTER':
                        app.send_message()
                    elif key == 'VOICE':
                        app.activate_voice()
                    elif key == 'MOUSE':
                        app.process_gesture('MOUSE')
                    else:
                        app.process_gesture(key)
    
    st.markdown("</div>", unsafe_allow_html=True)  # End app-section
    
    # Mouse Control Section
    if app.current_mode == "mouse":
        st.markdown("<div class='app-section'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: white;'>🖐️ Mouse Control</h4>", unsafe_allow_html=True)
        
        mouse_cols = st.columns(4)
        with mouse_cols[0]:
            if st.button("⬅️", use_container_width=True, key="mouse_left"):
                app.control_mouse("left")
        with mouse_cols[1]:
            if st.button("➡️", use_container_width=True, key="mouse_right"):
                app.control_mouse("right")
        with mouse_cols[2]:
            if st.button("👆", use_container_width=True, key="mouse_click"):
                app.control_mouse("click")
        with mouse_cols[3]:
            if st.button("🔄", use_container_width=True, key="mouse_scroll"):
                app.control_mouse("scroll")
        
        # Mouse position indicator
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; margin: 10px 0;'>
            <div style='color: white; text-align: center;'>
                Cursor Position: ({app.mouse_position[0]}, {app.mouse_position[1]})
            </div>
            <div style='width: 100%; height: 20px; background: rgba(255,255,255,0.2); border-radius: 10px; margin: 10px 0;'>
                <div style='width: {app.mouse_position[0]}%; height: 100%; background: #007AFF; border-radius: 10px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Chat History
    st.markdown("<div class='app-section'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: white;'>📱 Conversation</h4>", unsafe_allow_html=True)
    
    if app.chat_history:
        for msg in app.chat_history[-3:]:
            bubble_class = "message-user" if msg['type'] == 'user' else "message-bot"
            st.markdown(f"""
            <div class='message-bubble {bubble_class}'>
                {msg['message']}
                <div style='font-size: 10px; opacity: 0.7; text-align: right;'>
                    {time.strftime('%H:%M', time.localtime(msg['time']))}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center; color: rgba(255,255,255,0.5); padding: 20px;'>
            Start typing with gestures to begin conversation...
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Gesture History
    st.markdown("<div class='app-section'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: white;'>📊 Recent Gestures</h4>", unsafe_allow_html=True)
    
    if app.gesture_history:
        for gesture, timestamp in app.gesture_history[-5:]:
            st.markdown(f"""
            <div style='background: rgba(0,255,0,0.1); padding: 8px 12px; margin: 5px 0; 
                        border-radius: 8px; border-left: 3px solid #00ff00; color: white;'>
                🎯 {gesture} - {time.strftime('%H:%M:%S', time.localtime(timestamp))}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center; color: rgba(255,255,255,0.5); padding: 10px;'>
            No gestures yet...
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Close mobile app HTML
    st.markdown("""
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh for animations
    time.sleep(0.1)
    st.rerun()

if __name__ == "__main__":
    main()
