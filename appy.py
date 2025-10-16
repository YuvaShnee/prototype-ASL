import streamlit as st
import time
import webbrowser
import json
import random
from datetime import datetime
import cv2
import numpy as np
import base64
from PIL import Image
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    .action-button {
        background: linear-gradient(45deg, #FF64FF, #64B5FF);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 0.2rem;
        cursor: pointer;
    }
    .camera-feed {
        background: #1e2a38;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        border: 2px solid #FF64FF;
    }
    .keyboard-key {
        background: #2d3746;
        border: 1px solid #555;
        border-radius: 5px;
        padding: 0.5rem;
        margin: 0.2rem;
        text-align: center;
        cursor: pointer;
        min-width: 40px;
        display: inline-block;
    }
    .keyboard-key:hover {
        background: #3d4756;
    }
    .keyboard-key.active {
        background: #FF64FF;
        color: white;
    }
    .presentation-slide {
        background: #1e2a38;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        border: 2px solid #64B5FF;
        height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .healthcare-alert {
        background: #ff4444;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
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
if 'last_gesture_time' not in st.session_state:
    st.session_state.last_gesture_time = 0
if 'simulation_active' not in st.session_state:
    st.session_state.simulation_active = False
if 'visual_keyboard_active' not in st.session_state:
    st.session_state.visual_keyboard_active = False
if 'visual_mouse_active' not in st.session_state:
    st.session_state.visual_mouse_active = False
if 'current_slide' not in st.session_state:
    st.session_state.current_slide = 1
if 'total_slides' not in st.session_state:
    st.session_state.total_slides = 10
if 'healthcare_gestures' not in st.session_state:
    st.session_state.healthcare_gestures = {}
if 'emergency_gestures' not in st.session_state:
    st.session_state.emergency_gestures = {}
if 'email_notifications' not in st.session_state:
    st.session_state.email_notifications = []
if 'gesture_hold_start' not in st.session_state:
    st.session_state.gesture_hold_start = None

# ==================== SECTOR CONFIGURATION ====================
SECTORS = {
    "healthcare": {
        "name": "🏥 Healthcare",
        "color": "#00FFFF",
        "scenario": "Patient Accessibility & Rehabilitation",
        "description": "Medical chart access, patient communication, and rehabilitation support",
        "icon": "🏥"
    },
    "enterprise": {
        "name": "💼 Enterprise", 
        "color": "#FF64FF",
        "scenario": "Manufacturing Control & Productivity",
        "description": "CAD control, presentations, and multi-monitor management",
        "icon": "💼"
    },
    "education": {
        "name": "🎓 Education",
        "color": "#FFA500", 
        "scenario": "Inclusive Learning & Disability Support",
        "description": "Interactive learning, whiteboard control, and accessibility tools",
        "icon": "🎓"
    }
}

QUICK_ACTIONS = {
    "healthcare": [
        {"name": "Patient Info", "gesture": "P", "icon": "👤", "color": "#00FFFF", "url": "https://www.epic.com"},
        {"name": "Medical Chart", "gesture": "M", "icon": "📋", "color": "#FFFF00", "url": ""},
        {"name": "Emergency", "gesture": "E", "icon": "🚨", "color": "#FF0000", "url": ""},
        {"name": "Communicate", "gesture": "C", "icon": "💬", "color": "#00FF00", "url": ""},
        {"name": "Voice CMD", "gesture": "V", "icon": "🎤", "color": "#FF69B4", "url": ""}
    ],
    "enterprise": [
        {"name": "Dashboard", "gesture": "D", "icon": "📊", "color": "#FF64FF", "url": "https://www.tableau.com"},
        {"name": "CAD Control", "gesture": "C", "icon": "🖥️", "color": "#64FFFF", "url": ""},
        {"name": "Presentation", "gesture": "P", "icon": "📽️", "color": "#FFFF64", "url": ""},
        {"name": "Monitors", "gesture": "M", "icon": "🖥️🖥️", "color": "#FF6464", "url": ""},
        {"name": "Voice CMD", "gesture": "V", "icon": "🎤", "color": "#64FF64", "url": ""}
    ],
    "education": [
        {"name": "Lesson Control", "gesture": "L", "icon": "📚", "color": "#FFA500", "url": "https://classroom.google.com"},
        {"name": "Whiteboard", "gesture": "W", "icon": "🖊️", "color": "#90EE90", "url": "https://whiteboard.microsoft.com"},
        {"name": "Assessment", "gesture": "A", "icon": "📝", "color": "#FFFF64", "url": ""},
        {"name": "Accessibility", "gesture": "X", "icon": "♿", "color": "#00FFFF", "url": "https://accessibility.google"},
        {"name": "Voice CMD", "gesture": "V", "icon": "🎤", "color": "#FF69B4", "url": ""}
    ]
}

# ==================== HEALTHCARE GESTURE CONFIGURATION ====================
HEALTHCARE_GESTURES = {
    "B": {"name": "Breakfast", "description": "Request breakfast", "emergency": False},
    "L": {"name": "Lunch", "description": "Request lunch", "emergency": False},
    "D": {"name": "Dinner", "description": "Request dinner", "emergency": False},
    "T": {"name": "Tablets", "description": "Request medication", "emergency": False},
    "W": {"name": "Water", "description": "Request water", "emergency": False},
    "P": {"name": "Pain", "description": "Report pain", "emergency": True},
    "H": {"name": "Help", "description": "Request assistance", "emergency": True},
    "E": {"name": "Emergency", "description": "Critical emergency", "emergency": True}
}

# ==================== EMAIL CONFIGURATION ====================
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "healthcare.alerts@hospital.com",
    "sender_password": "password_placeholder",  # In production, use environment variables
    "admin_email": "admin@hospital.com"
}

# ==================== GESTURE RECOGNITION SIMULATION ====================
class GestureRecognitionSimulator:
    def __init__(self):
        self.gestures = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                        'SPACE', 'ENTER', 'BACKSPACE', 'SWIPE_LEFT', 'SWIPE_RIGHT']
        self.current_gesture = None
        self.hold_timer = 0
        
    def detect_gesture(self):
        """Simulate gesture detection with realistic timing"""
        current_time = time.time()
        
        # Only simulate if enough time has passed since last gesture
        if current_time - st.session_state.last_gesture_time > 2.0:
            if random.random() < 0.4:  # 40% chance of detecting a gesture
                gesture = random.choice(self.gestures)
                stability = min(st.session_state.gesture_stability + random.uniform(0.2, 0.4), 1.0)
                st.session_state.gesture_stability = stability
                
                if stability >= 0.8:
                    self.current_gesture = gesture
                    self.process_gesture(gesture)
                    st.session_state.gesture_stability = 0.0  # Reset after action
                    st.session_state.last_gesture_time = current_time
            else:
                # Gradually decrease stability when no gesture detected
                st.session_state.gesture_stability = max(st.session_state.gesture_stability - 0.1, 0.0)
                
        return self.current_gesture
    
    def process_gesture(self, gesture):
        """Process detected gesture based on current sector"""
        sector = st.session_state.current_sector
        
        if gesture in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if sector == "healthcare":
                self.process_healthcare_gesture(gesture)
            else:
                st.session_state.typed_text += gesture
                st.session_state.feedback_message = f"✍️ Typed: {gesture}"
                
                # Special case for education: typing "google" opens Google
                if sector == "education" and "google" in st.session_state.typed_text.lower():
                    webbrowser.open("https://www.google.com")
                    st.session_state.feedback_message = "🌐 Opening Google..."
                    st.session_state.typed_text = ""
                    
        elif gesture == 'SPACE':
            st.session_state.typed_text += ' '
            st.session_state.feedback_message = "␣ Space added"
        elif gesture == 'BACKSPACE' and st.session_state.typed_text:
            st.session_state.typed_text = st.session_state.typed_text[:-1]
            st.session_state.feedback_message = "⌫ Character deleted"
        elif gesture == 'ENTER':
            st.session_state.feedback_message = "↵ Execute command"
        elif gesture == 'SWIPE_LEFT' and sector == "enterprise":
            self.previous_slide()
        elif gesture == 'SWIPE_RIGHT' and sector == "enterprise":
            self.next_slide()
            
        st.session_state.asl_prediction = gesture
        
    def process_healthcare_gesture(self, gesture):
        """Process healthcare-specific gestures"""
        if gesture in HEALTHCARE_GESTURES:
            gesture_info = HEALTHCARE_GESTURES[gesture]
            current_time = datetime.now()
            
            # Track gesture hold time for emergency tagging
            if st.session_state.gesture_hold_start is None:
                st.session_state.gesture_hold_start = current_time
                
            hold_duration = (current_time - st.session_state.gesture_hold_start).total_seconds()
            
            # Create notification
            notification = {
                "gesture": gesture,
                "name": gesture_info["name"],
                "description": gesture_info["description"],
                "timestamp": current_time,
                "emergency": gesture_info["emergency"] or hold_duration > 3.0,
                "hold_duration": hold_duration
            }
            
            st.session_state.email_notifications.append(notification)
            
            # Send email notification for emergency or held gestures
            if notification["emergency"]:
                self.send_healthcare_notification(notification)
                st.session_state.feedback_message = f"🚨 EMERGENCY: {gesture_info['name']} - Notification sent!"
            else:
                st.session_state.feedback_message = f"🏥 {gesture_info['name']} requested"
                
            # Reset hold timer
            st.session_state.gesture_hold_start = None
            
    def send_healthcare_notification(self, notification):
        """Send email notification for healthcare gestures"""
        try:
            # In a real implementation, this would connect to an SMTP server
            # For demo purposes, we'll simulate this
            subject = "URGENT" if notification["emergency"] else "Patient Request"
            message = f"""
            Patient Gesture Notification:
            
            Gesture: {notification['gesture']} - {notification['name']}
            Description: {notification['description']}
            Time: {notification['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
            Emergency: {'YES' if notification['emergency'] else 'No'}
            Hold Duration: {notification['hold_duration']:.1f} seconds
            
            Please respond accordingly.
            """
            
            # Simulate sending email (in production, use smtplib)
            print(f"EMAIL SENT: {subject}\n{message}")
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            
    def next_slide(self):
        """Navigate to next presentation slide"""
        if st.session_state.current_slide < st.session_state.total_slides:
            st.session_state.current_slide += 1
            st.session_state.feedback_message = "➡️ Next slide"
            
    def previous_slide(self):
        """Navigate to previous presentation slide"""
        if st.session_state.current_slide > 1:
            st.session_state.current_slide -= 1
            st.session_state.feedback_message = "⬅️ Previous slide"

# Initialize gesture simulator
gesture_simulator = GestureRecognitionSimulator()

# ==================== VISUAL KEYBOARD COMPONENT ====================
def render_visual_keyboard():
    """Render visual keyboard for gesture-based typing"""
    st.markdown("### ⌨️ Visual Keyboard")
    
    # Keyboard layout
    keyboard_rows = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
        ['SPACE', 'BACKSPACE', 'ENTER']
    ]
    
    for row in keyboard_rows:
        cols = st.columns(len(row))
        for idx, key in enumerate(row):
            with cols[idx]:
                if st.button(key, key=f"key_{key}", use_container_width=True):
                    if key == 'SPACE':
                        st.session_state.typed_text += ' '
                    elif key == 'BACKSPACE' and st.session_state.typed_text:
                        st.session_state.typed_text = st.session_state.typed_text[:-1]
                    elif key == 'ENTER':
                        st.session_state.feedback_message = "↵ Command executed"
                    else:
                        st.session_state.typed_text += key
                        
                    # Special case for education: typing "google" opens Google
                    if st.session_state.current_sector == "education" and "google" in st.session_state.typed_text.lower():
                        webbrowser.open("https://www.google.com")
                        st.session_state.feedback_message = "🌐 Opening Google..."
                        st.session_state.typed_text = ""

# ==================== VISUAL MOUSE COMPONENT ====================
def render_visual_mouse():
    """Render visual mouse interface for gesture-based navigation"""
    st.markdown("### 🖱️ Visual Mouse Control")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Mouse pad simulation
        st.markdown("""
        <div style="background: #1e2a38; border-radius: 10px; padding: 2rem; text-align: center; 
                    border: 2px solid #64B5FF; height: 200px; display: flex; flex-direction: column; 
                    justify-content: center; align-items: center;">
            <div style="font-size: 3rem;">🖱️</div>
            <h3>Gesture Mouse Pad</h3>
            <p>Move hand to control cursor position</p>
            <div style="background: #2d3746; width: 80%; height: 4px; border-radius: 2px; margin: 1rem 0;"></div>
            <p>Pinch to click • Swipe to scroll</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # Mouse actions
        st.markdown("#### Mouse Actions")
        
        if st.button("👆 Left Click", use_container_width=True):
            st.session_state.feedback_message = "🖱️ Left click performed"
            
        if st.button("👆 Right Click", use_container_width=True):
            st.session_state.feedback_message = "🖱️ Right click performed"
            
        if st.button("🔄 Scroll", use_container_width=True):
            st.session_state.feedback_message = "🖱️ Scrolling..."
            
        if st.button("🧭 Navigate", use_container_width=True):
            st.session_state.feedback_message = "🖱️ Navigation mode activated"

# ==================== PRESENTATION CONTROL COMPONENT ====================
def render_presentation_control():
    """Render presentation control interface for enterprise sector"""
    st.markdown("### 📊 Presentation Control")
    
    # Current slide display
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div class="presentation-slide">
            <h2>Slide {st.session_state.current_slide}</h2>
            <p>Presentation Content</p>
            <div style="margin-top: 2rem;">
                <small>Use swipe gestures to navigate</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation controls
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1, 1, 1, 1])
    
    with nav_col1:
        if st.button("⬅️ Previous", use_container_width=True):
            gesture_simulator.previous_slide()
            
    with nav_col2:
        if st.button("➡️ Next", use_container_width=True):
            gesture_simulator.next_slide()
            
    with nav_col3:
        if st.button("🎬 Start Slideshow", use_container_width=True):
            st.session_state.feedback_message = "🎬 Starting presentation..."
            
    with nav_col4:
        if st.button("⏹️ End Show", use_container_width=True):
            st.session_state.feedback_message = "⏹️ Presentation ended"
    
    # Gesture instructions
    st.markdown("""
    <div style="background: #1e2a38; padding: 1rem; border-radius: 10px; margin-top: 1rem;">
        <h4>👋 Gesture Controls:</h4>
        <ul>
            <li><strong>Swipe Right</strong> → Next Slide</li>
            <li><strong>Swipe Left</strong> → Previous Slide</li>
            <li><strong>Point</strong> → Laser Pointer</li>
            <li><strong>Pinch</strong> → Click/Select</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==================== HEALTHCARE COMMUNICATION COMPONENT ====================
def render_healthcare_communication():
    """Render healthcare communication interface"""
    st.markdown("### 🏥 Patient Communication System")
    
    # Healthcare gesture buttons
    st.markdown("#### Patient Needs & Requests")
    
    # Create buttons for healthcare gestures
    cols = st.columns(4)
    gesture_list = list(HEALTHCARE_GESTURES.items())
    
    for idx, (gesture, info) in enumerate(gesture_list):
        with cols[idx % 4]:
            button_style = "background: #ff4444; color: white;" if info["emergency"] else ""
            if st.button(
                f"{gesture}: {info['name']}", 
                use_container_width=True,
                key=f"health_{gesture}"
            ):
                # Simulate gesture detection
                gesture_simulator.process_healthcare_gesture(gesture)
    
    # Emergency notifications
    emergency_notifications = [n for n in st.session_state.email_notifications if n["emergency"]]
    if emergency_notifications:
        st.markdown("#### 🚨 Emergency Notifications")
        for notification in emergency_notifications[-3:]:  # Show last 3 emergencies
            st.markdown(f"""
            <div class="healthcare-alert">
                <strong>{notification['name']}</strong> - {notification['description']}
                <br><small>{notification['timestamp'].strftime('%H:%M:%S')} | Held for {notification['hold_duration']:.1f}s</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Recent notifications
    if st.session_state.email_notifications:
        st.markdown("#### 📋 Recent Notifications")
        for notification in st.session_state.email_notifications[-5:]:  # Show last 5 notifications
            emoji = "🚨" if notification["emergency"] else "📨"
            st.info(f"{emoji} {notification['name']}: {notification['description']} ({notification['timestamp'].strftime('%H:%M')})")

# ==================== AI CHAT FUNCTIONALITY ====================
def get_ai_response(user_input, sector):
    """Generate AI response based on sector context"""
    sector_context = {
        "healthcare": {
            "keywords": ["patient", "medical", "health", "doctor", "hospital", "emergency", "chart", "record"],
            "responses": [
                "I can help you with patient information systems and medical chart access.",
                "For healthcare settings, SignLink Pro enables hands-free medical record access.",
                "The emergency gesture can quickly alert medical staff when needed.",
                "Patient communication features help with rehabilitation and therapy sessions."
            ]
        },
        "enterprise": {
            "keywords": ["cad", "dashboard", "presentation", "monitor", "control", "manufacturing", "design"],
            "responses": [
                "In enterprise mode, you can control CAD systems and manufacturing dashboards.",
                "Use gesture controls for presentations and multi-monitor management.",
                "SignLink Pro enhances productivity in control room environments.",
                "Quick access gestures streamline professional workflow tasks."
            ]
        },
        "education": {
            "keywords": ["lesson", "teach", "student", "whiteboard", "assessment", "learning", "classroom"],
            "responses": [
                "For education, SignLink Pro supports interactive learning and whiteboard control.",
                "Accessibility features help students with special needs participate fully.",
                "Teachers can control lessons and assessments using gesture commands.",
                "The system enables inclusive classroom technology for all learners."
            ]
        }
    }
    
    context = sector_context.get(sector, sector_context["enterprise"])
    user_input_lower = user_input.lower()
    
    # Check for sector-specific keywords
    for keyword in context["keywords"]:
        if keyword in user_input_lower:
            return random.choice(context["responses"])
    
    # Default responses
    default_responses = [
        f"I'm your SignLink Pro assistant for {SECTORS[sector]['name']}. How can I help you today?",
        f"In {sector} mode, you can use gesture controls for quick access to specialized tools.",
        f"Try using the quick action buttons or ask me about {sector}-specific features!",
        f"SignLink Pro makes {SECTORS[sector]['description'].lower()} more accessible through gesture control."
    ]
    
    return random.choice(default_responses)

def add_message(role, content):
    """Add message to chat history"""
    st.session_state.messages.append({"role": role, "content": content, "timestamp": datetime.now()})

# ==================== SECTOR FUNCTIONS ====================
def switch_sector(new_sector):
    """Switch between sectors"""
    st.session_state.current_sector = new_sector
    st.session_state.feedback_message = f"✅ Switched to {SECTORS[new_sector]['name']} - {SECTORS[new_sector]['scenario']}"
    st.session_state.typed_text = ""  # Clear typed text when switching sectors

def execute_sector_action(action_name):
    """Execute sector-specific actions"""
    sector = st.session_state.current_sector
    actions = QUICK_ACTIONS[sector]
    
    for action in actions:
        if action["name"] == action_name:
            if action["url"]:
                webbrowser.open(action["url"])
                st.session_state.feedback_message = f"🌐 Opening {action_name}..."
            else:
                st.session_state.feedback_message = f"✅ {action_name} activated in {SECTORS[sector]['name']} mode"
            break

# ==================== GESTURE SIMULATION ====================
def start_gesture_simulation():
    """Start continuous gesture simulation"""
    st.session_state.simulation_active = True
    st.session_state.feedback_message = "🎭 Gesture simulation started"

def stop_gesture_simulation():
    """Stop continuous gesture simulation"""
    st.session_state.simulation_active = False
    st.session_state.feedback_message = "⏹️ Gesture simulation stopped"

# ==================== STREAMLIT UI COMPONENTS ====================
def render_header():
    """Render the main header"""
    sector = st.session_state.current_sector
    sector_info = SECTORS[sector]
    
    st.markdown(f"""
    <div class="main-header">
        {sector_info['icon']} SignLink Pro - {sector_info['name']}
    </div>
    """, unsafe_allow_html=True)
    
    # Sector description
    st.markdown(f"""
    <div style="text-align: center; color: #CCCCCC; margin-bottom: 2rem;">
        <h3>{sector_info['scenario']}</h3>
        <p>{sector_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
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
            <h3>👁️ Gesture</h3>
            <h2>{st.session_state.asl_prediction or 'None'}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        chars_typed = len(st.session_state.typed_text)
        st.markdown(f"""
        <div class="metric-card">
            <h3>📝 Typed</h3>
            <h2>{chars_typed}</h2>
        </div>
        """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with controls"""
    with st.sidebar:
        st.markdown("## 🎮 Control Panel")
        
        # Sector selection
        st.markdown("### Select Sector")
        selected_sector = st.radio(
            "Choose your sector:",
            options=list(SECTORS.keys()),
            format_func=lambda x: SECTORS[x]["name"],
            index=list(SECTORS.keys()).index(st.session_state.current_sector)
        )
        
        if selected_sector != st.session_state.current_sector:
            switch_sector(selected_sector)
        
        st.markdown("---")
        
        # Feature toggles
        st.markdown("### 🔧 Feature Toggles")
        
        if st.session_state.current_sector == "education":
            col1, col2 = st.columns(2)
            with col1:
                visual_kb = st.toggle("Visual Keyboard", value=st.session_state.visual_keyboard_active)
                if visual_kb != st.session_state.visual_keyboard_active:
                    st.session_state.visual_keyboard_active = visual_kb
                    st.session_state.feedback_message = "⌨️ Visual keyboard " + ("activated" if visual_kb else "deactivated")
            
            with col2:
                visual_mouse = st.toggle("Visual Mouse", value=st.session_state.visual_mouse_active)
                if visual_mouse != st.session_state.visual_mouse_active:
                    st.session_state.visual_mouse_active = visual_mouse
                    st.session_state.feedback_message = "🖱️ Visual mouse " + ("activated" if visual_mouse else "deactivated")
        
        # Gesture simulation control
        st.markdown("### Gesture Simulation")
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            if st.button("🎭 Start Simulation", use_container_width=True):
                start_gesture_simulation()
        with sim_col2:
            if st.button("⏹️ Stop Simulation", use_container_width=True):
                stop_gesture_simulation()
        
        # Manual gesture input
        st.markdown("### Manual Gesture Input")
        manual_gesture = st.selectbox(
            "Select a gesture to simulate:",
            ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", 
             "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
             "SPACE", "BACKSPACE", "ENTER", "SWIPE_LEFT", "SWIPE_RIGHT"]
        )
        
        if st.button("👆 Simulate This Gesture", use_container_width=True):
            gesture_simulator.process_gesture(manual_gesture)
        
        st.markdown("---")
        
        # Quick actions for current sector
        st.markdown(f"### {SECTORS[st.session_state.current_sector]['icon']} Quick Actions")
        sector_actions = QUICK_ACTIONS[st.session_state.current_sector]
        
        for action in sector_actions:
            if st.button(
                f"{action['icon']} {action['name']} ({action['gesture']})", 
                use_container_width=True,
                key=f"sidebar_{action['name']}"
            ):
                execute_sector_action(action['name'])
        
        st.markdown("---")
        
        # System info
        st.markdown("### System Status")
        st.info(f"**Sector**: {SECTORS[st.session_state.current_sector]['name']}")
        st.info(f"**Simulation**: {'Active' if st.session_state.simulation_active else 'Inactive'}")
        st.info(f"**Gestures**: {len(st.session_state.typed_text)} characters")
        
        # API Recommendations
        st.markdown("### 🔌 Recommended APIs")
        if st.session_state.current_sector == "education":
            st.info("**Google Cloud Vision** - Gesture recognition")
            st.info("**Web Speech API** - Voice feedback")
        elif st.session_state.current_sector == "healthcare":
            st.info("**Azure Cognitive Services** - Gesture recognition")
            st.info("**Twilio** - Email/SMS alerts")
        elif st.session_state.current_sector == "enterprise":
            st.info("**Leap Motion SDK** - Gesture tracking")
            st.info("**PowerPoint API** - Presentation control")

def render_quick_access():
    """Render quick access buttons"""
    st.markdown("## 🚀 Quick Access Controls")
    sector = st.session_state.current_sector
    actions = QUICK_ACTIONS[sector]
    
    cols = st.columns(len(actions))
    for idx, action in enumerate(actions):
        with cols[idx]:
            if st.button(
                f"{action['icon']}\n\n**{action['name']}**\n\nGesture: **{action['gesture']}**",
                use_container_width=True,
                key=f"quick_{action['name']}",
                help=f"Execute {action['name']} action"
            ):
                execute_sector_action(action['name'])
            
            # Visual indicator
            st.markdown(f"""
            <div style="height: 4px; background: {action['color']}; border-radius: 2px; margin-top: 0.5rem;"></div>
            """, unsafe_allow_html=True)

def render_gesture_interface():
    """Render gesture detection interface"""
    st.markdown("## ✋ Gesture Control Interface")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Camera feed simulation
        st.markdown("### 🎥 Gesture Recognition Feed")
        
        if st.session_state.simulation_active:
            # Active simulation view
            st.markdown("""
            <div class="camera-feed">
                <div style="font-size: 5rem; margin-bottom: 1rem;">👋</div>
                <h3>Gesture Detection Active</h3>
                <div style="background: linear-gradient(90deg, #00FF00, #FFFF00, #FF0000); 
                            width: 80%; height: 20px; border-radius: 10px; margin: 1rem auto;">
                    <div style="width: {}%; height: 100%; background: rgba(255,255,255,0.3); border-radius: 10px;"></div>
                </div>
                <p>Stability: {:.1f}%</p>
                <p>Detected Gesture: <strong>{}</strong></p>
            </div>
            """.format(
                st.session_state.gesture_stability * 100,
                st.session_state.gesture_stability * 100,
                st.session_state.asl_prediction or "None"
            ), unsafe_allow_html=True)
            
            # Simulate gesture detection
            gesture_simulator.detect_gesture()
        else:
            # Inactive simulation view
            st.markdown("""
            <div class="camera-feed" style="border-color: #666;">
                <div style="font-size: 5rem; margin-bottom: 1rem;">📷</div>
                <h3>Camera Feed</h3>
                <p>Gesture simulation is inactive</p>
                <p>Click "Start Simulation" to begin</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Gesture feedback and status
        st.markdown("### 📊 Gesture Status")
        
        # Feedback message
        if st.session_state.feedback_message:
            st.success(st.session_state.feedback_message)
        
        # Current gesture
        if st.session_state.asl_prediction:
            st.markdown(f"""
            <div class="gesture-card">
                <h4>Current Gesture</h4>
                <div style="font-size: 3rem; text-align: center;">{st.session_state.asl_prediction}</div>
                <p style="text-align: center;">ASL Letter</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Typed text display
        st.markdown("### 📝 Typed Text")
        st.text_area("Output", st.session_state.typed_text, height=100, key="typed_output", label_visibility="collapsed")
        
        # Clear text button
        if st.button("🗑️ Clear Text", use_container_width=True):
            st.session_state.typed_text = ""
            st.session_state.feedback_message = "📝 Text cleared"

def render_sector_specific_interface():
    """Render sector-specific interface components"""
    sector = st.session_state.current_sector
    
    if sector == "education":
        if st.session_state.visual_keyboard_active:
            render_visual_keyboard()
        if st.session_state.visual_mouse_active:
            render_visual_mouse()
            
    elif sector == "healthcare":
        render_healthcare_communication()
        
    elif sector == "enterprise":
        render_presentation_control()

def render_chat_interface():
    """Render AI chat interface"""
    st.markdown("## 💬 SignLink Assistant")
    
    # Display chat messages
    for message in st.session_state.messages[-10:]:  # Show last 10 messages
        with st.chat_message(message["role"]):
            st.write(message["content"])
            st.caption(message["timestamp"].strftime("%H:%M:%S"))
    
    # Chat input
    if prompt := st.chat_input("Ask about SignLink Pro features..."):
        # Add user message
        add_message("user", prompt)
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        response = get_ai_response(prompt, st.session_state.current_sector)
        
        # Add AI response
        add_message("assistant", response)
        with st.chat_message("assistant"):
            st.write(response)

# ==================== MAIN APPLICATION ====================
def main():
    """Main application function"""
    
    # Render UI components
    render_header()
    render_sidebar()
    render_quick_access()
    
    st.markdown("---")
    
    # Main content area
    render_gesture_interface()
    render_sector_specific_interface()
    
    st.markdown("---")
    
    # Chat interface
    render_chat_interface()
    
    # Auto-refresh for simulation
    if st.session_state.simulation_active:
        time.sleep(0.5)
        st.rerun()

if __name__ == "__main__":
    main()
