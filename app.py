# app.py (Optimized for Streamlit Cloud, no OpenCV required)
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import time
import pandas as pd
import random

# -----------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------
st.set_page_config(
    page_title="ASL AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------
# CUSTOM STYLES
# -----------------------------------------------
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; text-align:center; margin-bottom:1rem; background: linear-gradient(45deg,#1f77b4,#ff6b6b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .chat-container { background-color:#f8f9fa; border-radius:15px; padding:20px; margin:10px 0; max-height:400px; overflow-y:auto; border:2px solid #e9ecef;}
    .user-message { background:linear-gradient(135deg,#667eea 0%,#764ba2 100%); color:white; padding:12px 16px; border-radius:18px 18px 5px 18px; margin:8px 0; max-width:80%; margin-left:auto; box-shadow:0 2px 5px rgba(0,0,0,0.1);}
    .bot-message { background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%); color:white; padding:12px 16px; border-radius:18px 18px 18px 5px; margin:8px 0; max-width:80%; margin-right:auto; box-shadow:0 2px 5px rgba(0,0,0,0.1);}
    .keyboard-key { display:inline-block; width:45px; height:45px; background:linear-gradient(135deg,#667eea 0%,#764ba2 100%); color:white; border:none; border-radius:8px; text-align:center; line-height:45px; margin:3px; font-weight:bold; cursor:pointer; transition:all 0.3s ease;}
    .keyboard-key:hover { transform:translateY(-2px); box-shadow:0 4px 8px rgba(0,0,0,0.2);}
    .keyboard-key.space { width:200px; background:linear-gradient(135deg,#4facfe 0%,#00f2fe 100%);}
    .keyboard-key.special { background:linear-gradient(135deg,#ff6b6b 0%,#ee5a24 100%);}
    .mode-indicator { background:linear-gradient(135deg,#a8edea 0%,#fed6e3 100%); padding:10px; border-radius:10px; text-align:center; font-weight:bold; margin:10px 0;}
    .gesture-card { background:white; padding:1rem; border-radius:10px; margin:0.5rem 0; border-left:5px solid #1f77b4; box-shadow:0 2px 4px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------
# CACHED FUNCTIONS
# -----------------------------------------------
@st.cache_data
def generate_webcam_placeholder():
    """Simulated webcam feed placeholder using PIL"""
    width, height = 400, 300
    img = Image.new('RGB', (width, height), color=(50, 50, 50))
    draw = ImageDraw.Draw(img)
    # Gradient background
    for y in range(height):
        color = int(100 + (y / height) * 100)
        draw.line([(0, y), (width, y)], fill=(color, color, color))
    # Text
    draw.text((80, 50), "ASL CAMERA FEED", fill=(255, 255, 255))
    draw.text((60, 100), "Show hand gestures here", fill=(200, 200, 255))
    # Hand simulation
    cx, cy, r = width//2, height//2, 40
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=(0,255,0), width=3)
    draw.ellipse((cx-5, cy-5, cx+5, cy+5), fill=(0,255,0))
    return img

@st.cache_resource
def get_ai_response_cached(user_message):
    """Simulated AI responses"""
    responses = {
        "hello": "👋 Hello! I'm your ASL AI assistant. How can I help you today?",
        "help": "🤖 I can help you with:\n• Typing via gestures\n• Voice commands\n• Quick actions\nJust ask me anything!",
        "weather": "🌤️ It's sunny in AI world!",
        "time": f"⏰ Current time is {time.strftime('%H:%M:%S')}",
        "name": "I'm ASL AI Chatbot - your gesture-controlled assistant!",
        "default": "🤔 Interesting! In real deployment, I'd use GPT or similar AI for answers."
    }
    msg = user_message.lower()
    for key in responses:
        if key in msg and key != "default":
            return responses[key]
    return responses["default"]

# -----------------------------------------------
# CHATBOT CLASS
# -----------------------------------------------
class AIChatbotASL:
    def __init__(self):
        self.typed_text = ""
        self.current_mode = "typing"
        self.gesture_history = []
        self.feedback_message = ""
        self.chat_history = []
        self.gestures = [*map(chr, range(65,91))] + ['SPACE','DELETE','SEND','CLEAR','HELP','VOICE','MOUSE']

    def simulate_gesture_prediction(self):
        return random.choice(self.gestures)

    def process_gesture(self, gesture):
        now = time.time()
        if gesture in [chr(i) for i in range(65,91)]:
            self.typed_text += gesture
            self.feedback_message = f"Typed: {gesture}"
        elif gesture == 'SPACE':
            self.typed_text += ' '
            self.feedback_message = "Space added"
        elif gesture == 'DELETE':
            self.typed_text = self.typed_text[:-1]
            self.feedback_message = "Deleted character"
        elif gesture == 'SEND':
            if self.typed_text.strip():
                self.chat_history.append({'type':'user','message':self.typed_text,'time':now})
                response = get_ai_response_cached(self.typed_text)
                self.chat_history.append({'type':'bot','message':response,'time':now})
                self.feedback_message = "Message sent!"
                self.typed_text = ""
            else:
                self.feedback_message = "Please type a message first"
        elif gesture == 'CLEAR':
            self.typed_text = ""
            self.feedback_message = "Input cleared"
        elif gesture == 'HELP':
            self.typed_text = "help"
            self.process_gesture('SEND')
        elif gesture == 'VOICE':
            self.typed_text = "What's the weather?"
            self.process_gesture('SEND')
        elif gesture == 'MOUSE':
            self.current_mode = 'mouse' if self.current_mode == 'typing' else 'typing'
            self.feedback_message = f"Switched to {self.current_mode} mode"

        self.gesture_history.append((gesture, now))
        if len(self.gesture_history)>10:
            self.gesture_history = self.gesture_history[-10:]

# -----------------------------------------------
# DISPLAY FUNCTIONS
# -----------------------------------------------
def display_chat(chat_history):
    if not chat_history:
        st.markdown("""
        <div class='chat-container'>
            <div style='text-align:center;color:#666;padding:20px;'>
                <h3>🤖 Welcome to ASL AI Chatbot!</h3>
                <p>Start chatting using gestures or virtual keyboard</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    html = "<div class='chat-container'>"
    for msg in chat_history[-10:]:
        if msg['type']=='user':
            html += f"<div class='user-message'><b>You:</b> {msg['message']}<div style='font-size:0.8em;opacity:0.7;text-align:right'>{time.strftime('%H:%M',time.localtime(msg['time']))}</div></div>"
        else:
            html += f"<div class='bot-message'><b>AI Assistant:</b> {msg['message']}<div style='font-size:0.8em;opacity:0.7'>{time.strftime('%H:%M',time.localtime(msg['time']))}</div></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# -----------------------------------------------
# MAIN APP
# -----------------------------------------------
def main():
    st.markdown('<h1 class="main-header">🤖 ASL AI Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#666;">Gesture + Voice + Keyboard Control</p>', unsafe_allow_html=True)

    if 'asl_app' not in st.session_state:
        st.session_state.asl_app = AIChatbotASL()
    asl_app = st.session_state.asl_app

    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader("💬 Chat Interface")
        display_chat(asl_app.chat_history)
        st.text_input("Your Message:", value=asl_app.typed_text, disabled=True)

        # Quick actions in a form
        with st.form("actions"):
            c1,c2,c3,c4 = st.columns(4)
            ask_help = c1.form_submit_button("❓ Help")
            ask_weather = c2.form_submit_button("🌤️ Weather")
            voice = c3.form_submit_button("🗣️ Voice")
            clear = c4.form_submit_button("🗑️ Clear Chat")

            if ask_help:
                asl_app.typed_text = "help"
                asl_app.process_gesture("SEND")
            elif ask_weather:
                asl_app.typed_text = "What's the weather like?"
                asl_app.process_gesture("SEND")
            elif voice:
                asl_app.process_gesture("VOICE")
            elif clear:
                asl_app.chat_history.clear()

    with col2:
        st.subheader("👋 Gesture Panel")
        webcam_image = generate_webcam_placeholder()
        st.image(webcam_image, use_column_width=True, caption="Simulated Camera Feed")

        cols = st.columns(2)
        if cols[0].button("🎯 Detect Gesture", use_container_width=True):
            g = asl_app.simulate_gesture_prediction()
            asl_app.process_gesture(g)
            st.success(f"Detected: {g}")

        if cols[1].button("🔄 Switch Mode", use_container_width=True):
            asl_app.process_gesture("MOUSE")

        mode_icon = "🟢" if asl_app.current_mode=="typing" else "🔵"
        st.markdown(f"<div class='mode-indicator'>{mode_icon} Mode: {asl_app.current_mode.upper()}</div>", unsafe_allow_html=True)

        if asl_app.feedback_message:
            st.info(f"💡 {asl_app.feedback_message}")

        st.subheader("📊 Recent Gestures")
        for g, ts in reversed(asl_app.gesture_history[-5:]):
            st.markdown(f"<div class='gesture-card'>🎯 {g} <small>({time.strftime('%H:%M:%S',time.localtime(ts))})</small></div>", unsafe_allow_html=True)

        st.subheader("📈 Chat Stats")
        stats = {
            "Metric":["Messages","Gestures","AI Responses","Session Time"],
            "Value":[
                len([m for m in asl_app.chat_history if m['type']=="user"]),
                len(asl_app.gesture_history),
                len([m for m in asl_app.chat_history if m['type']=="bot"]),
                f"{int(time.time()-(asl_app.gesture_history[0][1] if asl_app.gesture_history else time.time()))}s"
            ]
        }
        st.dataframe(pd.DataFrame(stats), use_container_width=True)

    with st.expander("📖 How to Use"):
        st.markdown("""
        **Gestures:** A-Z letters, SPACE, DELETE, SEND, CLEAR, HELP, VOICE  
        **Modes:** Typing & Mouse (switch with MOUSE gesture)  
        **Chat:** Quick actions or gestures to interact with AI  
        *Note: Real deployment would use MediaPipe for live hand gestures.*
        """)

if __name__=="__main__":
    main()

