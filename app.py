import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import time
import plotly.express as px
from datetime import datetime

# ------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------
st.set_page_config(
    page_title="ASL Mobile Guardian",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------
# CUSTOM CSS FOR PROFESSIONAL UI
# ------------------------------------------------
def local_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .scenario-low {
        background-color: #d4edda;
        border: 2px solid #c3e6cb;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .scenario-medium {
        background-color: #fff3cd;
        border: 2px solid #ffeaa7;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .scenario-high {
        background-color: #f8d7da;
        border: 2px solid #f5c6cb;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
    .demo-scenario {
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .demo-scenario:hover {
        border-color: #1f77b4;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .mobile-interface {
        border: 3px solid #e0e0e0;
        border-radius: 15px;
        padding: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: 10px 0;
    }
    .phone-mockup {
        border: 2px solid #333;
        border-radius: 25px;
        padding: 20px;
        background-color: #000;
        width: 300px;
        margin: 0 auto;
    }
    .mobile-screen {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border-radius: 20px;
        padding: 20px;
        color: white;
        min-height: 500px;
    }
    .gesture-feedback {
        background: rgba(0,255,0,0.1);
        border: 2px solid #00ff00;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: #00ff00;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ------------------------------------------------
# MOBILE INTERFACE DISPLAY FUNCTIONS
# ------------------------------------------------
def display_mobile_interface(scenario_type):
    """Display the appropriate mobile interface based on scenario"""
    if scenario_type == "typing":
        st.markdown("""
        <div class="mobile-screen">
            <div style="text-align: center; padding: 20px;">
                <h3 style="color: white;">📱 ASL Mobile App</h3>
                <div style="background: rgba(0,255,0,0.2); padding: 20px; border-radius: 15px; margin: 20px 0;">
                    <h4 style="color: #00ff00;">👆 Gesture Typing Active</h4>
                    <p>Camera detecting hand gestures...</p>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <p style="color: white; font-size: 18px;">HELLO WORLD</p>
                </div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0;">
                    <button style="padding: 15px; background: #007AFF; border: none; border-radius: 10px; color: white;">A</button>
                    <button style="padding: 15px; background: #007AFF; border: none; border-radius: 10px; color: white;">B</button>
                    <button style="padding: 15px; background: #007AFF; border: none; border-radius: 10px; color: white;">C</button>
                    <button style="padding: 15px; background: #FF2D55; border: none; border-radius: 10px; color: white;">DEL</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif scenario_type == "mouse":
        st.markdown("""
        <div class="mobile-screen">
            <div style="text-align: center; padding: 20px;">
                <h3 style="color: white;">📱 ASL Mobile App</h3>
                <div style="background: rgba(255,59,48,0.2); padding: 20px; border-radius: 15px; margin: 20px 0;">
                    <h4 style="color: #FF3B30;">🖐️ Mouse Control Active</h4>
                    <p>Hand gestures controlling cursor...</p>
                </div>
                <div style="position: relative; height: 200px; background: rgba(255,255,255,0.1); border-radius: 10px; margin: 20px 0;">
                    <div style="position: absolute; top: 50%; left: 50%; width: 20px; height: 20px; background: #00ff00; border-radius: 50%; transform: translate(-50%, -50%);"></div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0;">
                    <button style="padding: 15px; background: #5856D6; border: none; border-radius: 10px; color: white;">⬅️</button>
                    <button style="padding: 15px; background: #5856D6; border: none; border-radius: 10px; color: white;">➡️</button>
                    <button style="padding: 15px; background: #34C759; border: none; border-radius: 10px; color: white;">👆</button>
                    <button style="padding: 15px; background: #FF9500; border: none; border-radius: 10px; color: white;">🔄</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:  # voice scenario
        st.markdown("""
        <div class="mobile-screen">
            <div style="text-align: center; padding: 20px;">
                <h3 style="color: white;">📱 ASL Mobile App</h3>
                <div style="background: rgba(52,199,89,0.2); padding: 20px; border-radius: 15px; margin: 20px 0;">
                    <h4 style="color: #34C759;">🎤 Voice Control Active</h4>
                    <p>Listening for voice commands...</p>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 50%; width: 100px; height: 100px; margin: 30px auto; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 40px;">🎤</span>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 20px 0;">
                    <p style="color: white; font-style: italic;">"Hello, open Google search"</p>
                </div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin: 20px 0;">
                    <button style="padding: 15px; background: #34C759; border: none; border-radius: 10px; color: white;">🎤 Speak</button>
                    <button style="padding: 15px; background: #007AFF; border: none; border-radius: 10px; color: white;">📝 Type</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_sms_alert():
    """Display the SMS alert for critical scenarios"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="phone-mockup">', unsafe_allow_html=True)
        st.markdown("""
        <div style="background: white; color: black; padding: 15px; border-radius: 10px; font-family: Arial;">
            <div style="background: #007AFF; color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <strong>ASL Mobile Alert</strong>
            </div>
            <p><strong>Voice Command Executed:</strong></p>
            <p>"Emergency: Call doctor immediately"</p>
            <p style="font-size: 12px; color: gray;">Sent to Medical Staff</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------
# SIDEBAR
# ------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/iphone.png", width=80)
    st.title("Control Panel")

    selected_tab = st.radio("Navigation",
                            ["Live Demo", "Usage Dashboard", "System Analytics", "About"])

    st.markdown("---")
    st.markdown("### Demo Scenarios")
    scenario = st.selectbox("Choose Scenario",
                            ["ASL Typing with Mobile App",
                             "Mouse Control with Mobile App", 
                             "Voice Control with Mobile App"])

    st.markdown("---")
    st.markdown("### System Status")
    st.success("🟢 All Systems Operational")
    st.info("📡 Connected to Mobile Network")
    st.metric("Active Users", "156", "12")

# ------------------------------------------------
# AI ANALYSIS MOCK FUNCTION FOR ASL APP
# ------------------------------------------------
def analyze_asl_scenario(scenario):
    if scenario == "ASL Typing with Mobile App":
        return {
            "scenario_level": "BASIC",
            "accuracy_score": 94,
            "speed_wpm": 25,
            "confidence": 92,
            "features": {"gesture_recognition": 95, "camera_stability": 90,
                         "typing_accuracy": 96, "response_time": 88},
            "recommendation": "Excellent gesture recognition. Continue using ASL typing for communication.",
            "alert_status": "NORMAL",
            "interface_type": "typing",
            "user_image": "https://raw.githubusercontent.com/YuvaShnee/Agentic-AI-predictive-maintain/main/normal_baby.png"
        }
    elif scenario == "Mouse Control with Mobile App":
        return {
            "scenario_level": "INTERMEDIATE", 
            "accuracy_score": 78,
            "speed_wpm": 18,
            "confidence": 85,
            "features": {"cursor_control": 82, "click_accuracy": 75,
                         "scroll_precision": 80, "gesture_stability": 70},
            "recommendation": "Good mouse control. Practice improves precision. Consider calibration.",
            "alert_status": "WARNING",
            "interface_type": "mouse",
            "user_image": "https://raw.githubusercontent.com/YuvaShnee/Agentic-AI-predictive-maintain/main/medium_risk_baby.png"
        }
    else:  # Voice Control
        return {
            "scenario_level": "ADVANCED",
            "accuracy_score": 65,
            "speed_wpm": 32,
            "confidence": 88,
            "features": {"speech_recognition": 85, "command_accuracy": 70,
                         "noise_reduction": 75, "response_latency": 60},
            "recommendation": "Voice control active. Background noise detected. Improve microphone positioning.",
            "alert_status": "CRITICAL",
            "interface_type": "voice",
            "user_image": "https://raw.githubusercontent.com/YuvaShnee/Agentic-AI-predictive-maintain/main/high5.png"
        }

# ------------------------------------------------
# GENERATE MOCK PERFORMANCE DATA
# ------------------------------------------------
def generate_performance_data():
    timestamps = pd.date_range(start='2024-01-01 08:00', periods=24, freq='H')
    accuracy = np.random.normal(85, 8, 24)
    return pd.DataFrame({'timestamp': timestamps, 'accuracy': accuracy})

# ------------------------------------------------
# MAIN TABS
# ------------------------------------------------
if selected_tab == "Live Demo":
    st.markdown('<h1 class="main-header">📱 ASL Mobile Guardian</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Accessibility Interface System")

    st.markdown("## 🎥 Live Mobile Demo")
    with st.spinner('🔄 AI Analysis in Progress...'):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)
        analysis_result = analyze_asl_scenario(scenario)

    col1, col2 = st.columns([2, 1])

    # Left Column: Mobile Interface + User View
    with col1:
        st.markdown('<div class="mobile-interface">', unsafe_allow_html=True)
        st.markdown("### 📱 Mobile App Interface")
        display_mobile_interface(analysis_result["interface_type"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("### 👤 User Interaction View")
        st.image(analysis_result["user_image"], caption="User Interaction Analysis", width=600)

    # Right Column: Performance Metrics
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📈 Real-time Performance Metrics")
        performance_data = generate_performance_data()
        fig_perf = px.line(performance_data, x='timestamp', y='accuracy', 
                          title='Gesture Recognition Accuracy Trend')
        fig_perf.add_hline(y=90, line_dash="dash", line_color="green", annotation_text="Excellent")
        fig_perf.add_hline(y=70, line_dash="dash", line_color="orange", annotation_text="Good")
        fig_perf.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="Needs Improvement")
        st.plotly_chart(fig_perf, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("#### Current Performance Parameters")
        col_met1, col_met2 = st.columns(2)
        with col_met1:
            st.metric("Accuracy Score", f"{analysis_result['accuracy_score']}%", "2%")
            st.metric("Speed", f"{analysis_result['speed_wpm']} WPM", "3 WPM")
        with col_met2:
            st.metric("AI Confidence", f"{analysis_result['confidence']}%", "1%")
            st.metric("Response Time", "120ms", "5ms")

    # Scenario Summary
    st.markdown("### 🎯 AI Performance Assessment")
    scenario_level = analysis_result["scenario_level"]
    if scenario_level == "BASIC":
        st.markdown('<div class="scenario-low">', unsafe_allow_html=True)
        st.success("🟢 **BASIC SCENARIO - EXCELLENT PERFORMANCE**")
    elif scenario_level == "INTERMEDIATE":
        st.markdown('<div class="scenario-medium">', unsafe_allow_html=True)
        st.warning("🟡 **INTERMEDIATE SCENARIO - GOOD PERFORMANCE**")
    else:
        st.markdown('<div class="scenario-high">', unsafe_allow_html=True)
        st.error("🔴 **ADVANCED SCENARIO - NEEDS ATTENTION**")

    st.write(f"**Typing Speed:** {analysis_result['speed_wpm']} Words Per Minute")
    st.write(f"**AI Confidence Score:** {analysis_result['confidence']}%")
    st.write(f"**System Recommendation:** {analysis_result['recommendation']}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Real-time Feedback Messages
    st.markdown("### 💬 Real-time Feedback Messages")
    if analysis_result["interface_type"] == "typing":
        st.markdown("""
        <div class="gesture-feedback">
            ✅ Gesture 'H' detected and typed | 📱 Mobile camera tracking active | 
            ⏱️ Response time: 120ms | 🎯 Accuracy: 96%
        </div>
        """, unsafe_allow_html=True)
    elif analysis_result["interface_type"] == "mouse":
        st.markdown("""
        <div class="gesture-feedback">
            🖐️ Hand gesture moved cursor RIGHT | 👆 Tap gesture detected - CLICK performed |
            🔄 Scroll gesture recognized | 📱 Mobile sensors active
        </div>
        """, unsafe_allow_html=True)
    else:  # voice
        st.markdown("""
        <div class="gesture-feedback">
            🎤 Voice command: "Open Google search" | 🔊 Audio processing complete |
            📱 Command executed successfully | ⚡ Response: 850ms
        </div>
        """, unsafe_allow_html=True)

    # Detailed Features
    st.markdown("### 🔬 Detailed AI Feature Analysis")
    features = analysis_result["features"]
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1: 
        st.metric("Gesture Recognition", f"{features['gesture_recognition']}%")
    with col_f2: 
        st.metric("Command Accuracy", f"{features.get('command_accuracy', features.get('click_accuracy', 0))}%")
    with col_f3: 
        st.metric("System Stability", f"{features.get('camera_stability', features.get('gesture_stability', features.get('noise_reduction', 0)))}%")
    with col_f4: 
        st.metric("Response Quality", f"{features['response_time']}%")

    # Alerts and Notifications
    if analysis_result["alert_status"] == "CRITICAL":
        st.error("🚨 **ATTENTION REQUIRED: Voice Control Optimization Needed**")
        st.markdown("### 📱 System Notification Sent")
        display_sms_alert()
        st.warning("🔄 **Optimization Protocols Activated:**")
        st.write("- 🎤 Microphone calibration initiated")
        st.write("- 🔊 Noise reduction algorithms enhanced")
        st.write("- 📱 Audio processing optimized")
        st.write("- 🔧 System tuning in progress")
        st.balloons()
    elif analysis_result["alert_status"] == "WARNING":
        st.warning("⚠️ **PERFORMANCE NOTICE**: Mouse control precision can be improved")
        st.info("📋 **Recommended Actions:** Practice sessions & calibration check")

# -----------------------------
# Usage Dashboard Tab
# -----------------------------
elif selected_tab == "Usage Dashboard":
    st.markdown('<h1 class="main-header">📱 Usage Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Overview of ASL Mobile App Usage")
    
    usage_data = pd.DataFrame({
        "User ID": ["USER001", "USER002", "USER003", "USER004"],
        "Primary Mode": ["Gesture Typing", "Mouse Control", "Voice Control", "Gesture Typing"],
        "Accuracy (%)": [94, 78, 65, 89],
        "Session Duration": ["45 min", "32 min", "28 min", "51 min"],
        "Last Active": ["08:15", "09:30", "07:45", "08:50"]
    })
    st.table(usage_data)

# -----------------------------
# System Analytics Tab
# -----------------------------
elif selected_tab == "System Analytics":
    st.markdown('<h1 class="main-header">📊 System Analytics</h1>', unsafe_allow_html=True)
    st.markdown("### Aggregated Usage Patterns")
    
    # Create sample analytics data
    analytics_data = pd.DataFrame({
        "Gesture Typing": [65, 68, 72, 70, 75],
        "Mouse Control": [25, 22, 20, 23, 18],
        "Voice Control": [10, 10, 8, 7, 7]
    }, index=['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])
    
    st.bar_chart(analytics_data)
    
    st.markdown("### Feature Usage Distribution")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Sessions", "1,234", "12%")
        st.metric("Average Accuracy", "82%", "3%")
    with col2:
        st.metric("Active Users", "156", "8%")
        st.metric("Response Time", "145ms", "-5ms")

# -----------------------------
# About Tab
# -----------------------------
elif selected_tab == "About":
    st.markdown('<h1 class="main-header">ℹ️ About ASL Mobile Guardian</h1>', unsafe_allow_html=True)
    st.markdown("""
    **ASL Mobile Guardian** is an AI-powered accessibility interface system.
    - Enables communication through ASL gestures, mouse control, and voice commands
    - Developed for enhanced mobile accessibility
    - Provides Live Demo, Usage Dashboard, and System Analytics
    - Supports multiple interaction modes for diverse user needs
    """)
    
    st.markdown("### 🎯 Supported Scenarios")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**👆 ASL Typing**\n\nGesture-based text input using mobile camera")
    with col2:
        st.warning("**🖐️ Mouse Control**\n\nHand gesture-based cursor control")
    with col3:
        st.success("**🎤 Voice Control**\n\nVoice command interface for hands-free operation")

# ------------------------------------------------
# FOOTER
# ------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "ASL Mobile Guardian 📱 - Enhancing Mobile Accessibility | Tech4Good 2024 | Accessibility AI Solutions"
    "</div>",
    unsafe_allow_html=True
)
   
