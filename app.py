
import streamlit as st
import time
import webbrowser
import json
import random
from datetime import datetime

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
def simulate_gesture_detection():
    """Simulate gesture detection for demo purposes"""
    gestures = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                'SPACE', 'ENTER', 'BACKSPACE']
    
    current_time = time.time()
    
    # Only simulate if enough time has passed since last gesture
    if current_time - st.session_state.last_gesture_time > 2.0:
        if random.random() < 0.4:  # 40% chance of detecting a gesture
            gesture = random.choice(gestures)
            stability = min(st.session_state.gesture_stability + random.uniform(0.2, 0.4), 1.0)
            st.session_state.gesture_stability = stability
            
            if stability >= 0.8:
                st.session_state.asl_prediction = gesture
                if gesture in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    st.session_state.typed_text += gesture
                    st.session_state.feedback_message = f"✍️ Typed: {gesture}"
                elif gesture == 'SPACE':
                    st.session_state.typed_text += ' '
                    st.session_state.feedback_message = "␣ Space added"
                elif gesture == 'BACKSPACE' and st.session_state.typed_text:
                    st.session_state.typed_text = st.session_state.typed_text[:-1]
                    st.session_state.feedback_message = "⌫ Character deleted"
                elif gesture == 'ENTER':
                    st.session_state.feedback_message = "↵ Execute command"
                
                st.session_state.gesture_stability = 0.0  # Reset after action
                st.session_state.last_gesture_time = current_time
        else:
            # Gradually decrease stability when no gesture detected
            st.session_state.gesture_stability = max(st.session_state.gesture_stability - 0.1, 0.0)

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
             "SPACE", "BACKSPACE", "ENTER"]
        )
        
        if st.button("👆 Simulate This Gesture", use_container_width=True):
            st.session_state.asl_prediction = manual_gesture
            if manual_gesture in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                st.session_state.typed_text += manual_gesture
                st.session_state.feedback_message = f"✍️ Manually typed: {manual_gesture}"
            elif manual_gesture == 'SPACE':
                st.session_state.typed_text += ' '
                st.session_state.feedback_message = "␣ Space added"
            elif manual_gesture == 'BACKSPACE' and st.session_state.typed_text:
                st.session_state.typed_text = st.session_state.typed_text[:-1]
                st.session_state.feedback_message = "⌫ Character deleted"
        
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
                <div style="font-size: 4rem;">👋</div>
                <h3>Gesture Detection Active</h3>
                <p>Simulating ASL gesture recognition...</p>
                <div style="background: linear-gradient(90deg, #00FF00, #FFFF00, #FF0000); 
                            height: 4px; border-radius: 2px; margin: 1rem 0;"></div>
                <p>Show hand gestures to detect letters</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Inactive view
            st.markdown("""
            <div class="camera-feed" style="border-color: #666;">
                <div style="font-size: 4rem;">📷</div>
                <h3>Gesture Feed Inactive</h3>
                <p>Start simulation to begin gesture recognition</p>
                <div style="background: #666; height: 4px; border-radius: 2px; margin: 1rem 0;"></div>
                <p>Click 'Start Simulation' to begin</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Gesture stability indicator
        st.markdown("### Gesture Stability")
        stability = st.session_state.gesture_stability
        st.progress(stability)
        
        col_stab1, col_stab2, col_stab3 = st.columns([2, 1, 1])
        with col_stab1:
            st.write(f"Current stability: **{int(stability * 100)}%**")
        with col_stab2:
            if stability < 0.5:
                st.write("🔴 Low")
            elif stability < 0.8:
                st.write("🟡 Medium")
            else:
                st.write("🟢 High")
        with col_stab3:
            if stability >= 0.8:
                st.success("Ready!")
    
    with col2:
        # ASL Prediction Display
        st.markdown("### 🔍 ASL Prediction")
        if st.session_state.asl_prediction:
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem; background: #1e2a38; 
                        border-radius: 15px; border: 3px solid #FF64FF; margin-bottom: 1rem;">
                <div style="font-size: 4rem; font-weight: bold;">{st.session_state.asl_prediction}</div>
                <p>Detected Gesture</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: #1e2a38; 
                        border-radius: 15px; border: 2px dashed #666; margin-bottom: 1rem;">
                <div style="font-size: 2rem;">👋</div>
                <p>No gesture detected</p>
                <p style="font-size: 0.8rem; color: #999;">Show ASL gesture to detect letters</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Typed text display
        st.markdown("### 📝 Communication Output")
        st.text_area(
            "Current typed text:",
            st.session_state.typed_text,
            height=120,
            key="typed_display_area",
            label_visibility="collapsed"
        )
        
        # Text management buttons
        col_clear1, col_clear2 = st.columns(2)
        with col_clear1:
            if st.button("🗑️ Clear Text", use_container_width=True):
                st.session_state.typed_text = ""
                st.session_state.feedback_message = "📝 Text cleared"
        with col_clear2:
            if st.button("📋 Copy Text", use_container_width=True) and st.session_state.typed_text:
                st.session_state.feedback_message = "📋 Text copied to clipboard"

def render_ai_chat():
    """Render AI chat interface"""
    st.markdown("## 🤖 AI Assistant")
    
    # Chat container
    chat_container = st.container(height=400)
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages[-10:]:  # Show last 10 messages
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>🤖 Assistant:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    col_input1, col_input2 = st.columns([4, 1])
    with col_input1:
        user_input = st.text_input(
            "Type your message...", 
            key="chat_input",
            placeholder="Ask about gesture controls, sector features, or accessibility..."
        )
    with col_input2:
        send_button = st.button("Send", use_container_width=True)
    
    if send_button and user_input:
        # Add user message
        add_message("user", user_input)
        
        # Get AI response
        ai_response = get_ai_response(user_input, st.session_state.current_sector)
        add_message("assistant", ai_response)
        
        # Clear input by rerunning
        st.rerun()
    
    # Quick chat buttons
    st.markdown("### Quick Questions")
    quick_cols = st.columns(4)
    quick_questions = [
        ("Hello 👋", "Hello! How does this work?"),
        ("Help ❓", "What can I do with this system?"),
        ("Gestures ✋", "How do gesture controls work?"),
        ("Features 🚀", f"What are the key features for {st.session_state.current_sector}?")
    ]
    
    for idx, (label, question) in enumerate(quick_questions):
        with quick_cols[idx]:
            if st.button(label, use_container_width=True):
                add_message("user", question)
                ai_response = get_ai_response(question, st.session_state.current_sector)
                add_message("assistant", ai_response)
                st.rerun()

def render_footer():
    """Render footer with feedback"""
    # Feedback message
    if st.session_state.feedback_message:
        st.success(st.session_state.feedback_message)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p><strong>SignLink Pro</strong> - Multi-Sector Accessibility System</p>
        <p>Enterprise • Healthcare • Education • Powered by Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== MAIN APP ====================
def main():
    # Header
    render_header()
    
    # Main layout
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
    
    # Continuous gesture simulation (if active)
    if st.session_state.simulation_active:
        simulate_gesture_detection()
        time.sleep(0.5)  # Small delay for simulation
        st.rerun()

if __name__ == "__main__":
    main()
