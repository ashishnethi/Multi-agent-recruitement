import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go
import time
import random
from streamlit_pdf_viewer import pdf_viewer

# Import our existing modules
from ai_recruitment_agent_team import (
    init_session_state,
    create_resume_analyzer,
    create_email_agent,
    create_scheduler_agent,
    extract_text_from_pdf,
    analyze_resume,
    send_selection_email,
    send_rejection_email,
    schedule_interview,
    ROLE_REQUIREMENTS,
    sanitize_ascii,
    openrouter_chat,
)

# Page configuration
st.set_page_config(
    page_title="AI Recruitment System Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Common base */
    body, .stApp {
        font-family: 'Inter', sans-serif;
        transition: background-color 0.5s ease, color 0.5s ease;
        user-select: none;
    }

    /* Light Mode (default) */
    .light-mode {
        background: #f4f7f9;
        color: #1f2937 !important;
    }
    .light-mode h1, .light-mode h2, .light-mode h3, 
    .light-mode h4, .light-mode h5, .light-mode h6 {
        color: #1f2937 !important;
    }

    /* Dark Mode */
    .dark-mode {
        background: #121212;
        color: #f1f1f1 !important;
    }
    .dark-mode h1, .dark-mode h2, .dark-mode h3, 
    .dark-mode h4, .dark-mode h5, .dark-mode h6 {
        color: #e0e0e0 !important;
    }

    /* Containers/card backgrounds */
    .metric-card, .candidate-card, .email-preview, .sidebar-stats {
        border-radius: 18px;
        margin-bottom: 1.8rem;
        padding: 2.2rem 2rem;
        position: relative;
        transition: background-color 0.4s ease, box-shadow 0.4s ease;
        user-select: text;
    }
    .light-mode .metric-card, .light-mode .candidate-card,
    .light-mode .email-preview, .light-mode .sidebar-stats {
        background: #ffffffcc;
        box-shadow: 0 5px 18px rgba(0,0,0,0.07);
        border: 1.2px solid #90e0ef50;
        color: #1f2937;
    }
    .dark-mode .metric-card, .dark-mode .candidate-card,
    .dark-mode .email-preview, .dark-mode .sidebar-stats {
        background: #1e1e1ecc;
        box-shadow: 0 5px 18px rgba(0,0,0,0.5);
        border: 1.2px solid #0a9396cc;
        color: #e0e0e0;
    }
    .metric-card:hover, .candidate-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(10, 147, 150, 0.25);
    }

    /* Headers with gradients */
    .light-mode .main-header {
        background: linear-gradient(135deg, #005f73 0%, #0a9396 100%);
        color: #caf0f8;
        box-shadow: 0 8px 30px rgba(0, 95, 115, 0.55);
        user-select: none;
    }
    .dark-mode .main-header {
        background: linear-gradient(135deg, #0a9396 0%, #005f73 100%);
        color: #caf0f8;
        box-shadow: 0 12px 40px rgba(10, 147, 150, 0.75);
        user-select: none;
    }
    .main-header h1 {
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        text-shadow: 0 4px 16px rgba(0,0,0,0.4);
    }
    .main-header p {
        font-weight: 400;
        font-size: 1.25rem;
        letter-spacing: 0.05em;
    }

    /* Step Indicator Styles */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        border-radius: 20px;
        padding: 1.8rem 1rem;
        margin: 3rem 0 3rem 0;
        user-select: none;
    }
    .light-mode .step-indicator {
        background-color: #e0f7f9;
        box-shadow: 0 3px 15px rgba(10,147,150,0.25);
    }
    .dark-mode .step-indicator {
        background-color: #19323c;
        box-shadow: 0 3px 15px rgba(10,147,150,0.9);
    }
    .step {
        padding: 1.6rem 0;
        flex: 1;
        margin: 0 0.5rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 1.1rem;
        text-align: center;
        cursor: default;
        position: relative;
        user-select: none;
        transition: all 0.3s ease;
        white-space: nowrap;
        color: #0a555e;
    }
    .dark-mode .step {
        color: #71c9ce;
    }
    .step::before {
        content: '';
        position: absolute;
        top: 50%;
        right: -50%;
        width: 100%;
        height: 3px;
        border-radius: 10px;
        z-index: -1;
    }
    .light-mode .step::before {
        background: #ade8f4;
    }
    .dark-mode .step::before {
        background: #72d6db;
    }
    .step:last-child::before {
        display: none;
    }
    .step.active {
        background-color: #0a9396;
        color: #caf0f8;
        font-weight: 700;
        box-shadow: 0 10px 22px rgba(10,147,150,0.5);
        transform: scale(1.1);
    }
    .step.completed {
        background-color: #94d2bd;
        color: #004643;
        box-shadow: 0 7px 20px rgba(148,210,189,0.6);
    }
    .dark-mode .step.completed {
        background-color: #4ca3a6;
        color: #b6e3e1;
    }

    /* Remove problematic overlapping line in progress bar */
    .progress-bar {
        height: 12px !important;
        border-radius: 10px !important;
        background: linear-gradient(90deg, #0a9396, #94d2bd) !important;
        box-shadow: 0 4px 15px rgba(10, 147, 150, 0.4);
        margin-top: 0 !important;
        /* Removed any overlapping borders or lines */
    }

    /* Status badges with good contrast */
    .status-badge {
        padding: 1rem 2rem;
        border-radius: 30px;
        font-weight: 700;
        font-size: 0.95rem;
        text-transform: uppercase;
        user-select: none;
        border: none !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    }
    .light-mode .status-selected {
        background: #138086;
        color: #c5f1f1;
        border: 1.5px solid #1c5e5e;
    }
    .dark-mode .status-selected {
        background: #0d5557;
        color: #caf0f8;
        border: 1.5px solid #1c5e5e;
    }
    .light-mode .status-rejected {
        background: #ef233c;
        color: #f9d6d5;
        border: 1.5px solid #9e1420;
    }
    .dark-mode .status-rejected {
        background: #b11c2a;
        color: #ffc1c1;
        border: 1.5px solid #670f1a;
    }
    .light-mode .status-pending {
        background: #f4a261;
        color: #4a2e00;
        border: 1.5px solid #974a0e;
    }
    .dark-mode .status-pending {
        background: #a36a3c;
        color: #e2cbae;
        border: 1.5px solid #6b4520;
    }

    /* Text visibility for warnings/errors in dark mode */
    .light-mode .stMarkdown > div[role="alert"] {
        color: #b34142 !important;
    }
    .dark-mode .stMarkdown > div[role="alert"] {
        color: #f56565 !important;
    }
    .light-mode .warning, .light-mode .stWarning {
        color: #855a42 !important;
    }
    .dark-mode .warning, .dark-mode .stWarning {
        color: #f6ad55 !important;
    }
    .light-mode .error, .light-mode .stError {
        color: #a02f2f !important;
    }
    .dark-mode .error, .dark-mode .stError {
        color: #fc8181 !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        padding: 0.75rem 1.6rem;
        font-weight: 700;
        font-size: 1rem;
        border: none !important;
        cursor: pointer;
        user-select: none;
        transition: all 0.3s ease;
    }
    .light-mode .stButton > button {
        background-image: linear-gradient(135deg, #0a9396 0%, #94d2bd 100%);
        color: #f0fdfa !important;
        box-shadow: 0 10px 25px rgba(10, 147, 150, 0.4);
    }
    .dark-mode .stButton > button {
        background-image: linear-gradient(135deg, #0a9396ee 0%, #94d2bdcc 100%);
        color: #caf0f8 !important;
        box-shadow: 0 10px 25px rgba(10, 147, 150, 0.9);
    }
.stButton > button:hover {
    transform: scale(1.01);
    box-shadow: 0 8px 14px rgba(10, 147, 150, 0.25);
    filter: brightness(1.03);
    transition: all 0.2s ease-in-out;
}

    .stButton > button:disabled {
        background-color: #9ed8db !important;
        color: #5f797a !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
    }

    /* Sidebar */
    .sidebar-stats {
        padding: 1.8rem;
        margin: 1rem 0 2rem 0;
        border-radius: 18px;
        font-weight: 600;
        user-select: none;
        transition: background-color 0.4s ease, color 0.3s ease;
    }
    .light-mode .sidebar-stats {
        background: #ffffffcc;
        color: #024047;
        box-shadow: 0 7px 25px rgba(10, 147, 150, 0.35);
        border: 1.5px solid #90e0ef70;
    }
    .dark-mode .sidebar-stats {
        background: #1e1e1ecc;
        color: #a0e5e5;
        box-shadow: 0 7px 30px rgba(10, 147, 150, 0.85);
        border: 1.5px solid #0a9396cc;
    }
    .sidebar-stats h4 {
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    .stat-item {
        display: flex;
        justify-content: space-between;
        padding: 0.6rem 0;
        font-size: 1rem;
        border-bottom: 1px solid #e0f2f1cc;
    }
    .stat-item:last-child {
        border-bottom: none;
    }
    .light-mode .stat-item {
        border-color: #e0f2f1cc;
    }
    .dark-mode .stat-item {
        border-color: #108284aa;
    }
    .stat-value {
        font-weight: 700;
        color: inherit;
    }

    /* Email Preview and Zoom Link */
    .email-preview {
        padding: 2rem 2.2rem;
        border-radius: 18px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 18px rgba(10, 147, 150, 0.3);
        user-select: text;
        transition: background-color 0.4s ease, color 0.3s ease;
    }
    .light-mode .email-preview {
        background: #f0f9f9;
        border: 2px solid #0a9396cc;
        color: #024047;
    }
    .dark-mode .email-preview {
        background: #123335cc;
        border: 2px solid #0a9396cc;
        color: #b0f0f0;
    }
    .email-preview h4 {
        margin-bottom: 1.25rem;
        font-weight: 700;
    }
    .zoom-link {
        padding: 1.2rem;
        border-radius: 14px;
        text-align: center;
        font-weight: 700;
        margin: 1.75rem 0;
        box-shadow: 0 8px 20px rgba(10, 147, 150, 0.38);
        user-select: text;
        transition: background-color 0.4s ease, color 0.3s ease;
    }
    .light-mode .zoom-link {
        background: linear-gradient(135deg, #0a9396, #94d2bd);
        color: #e0f7f9;
    }
    .dark-mode .zoom-link {
        background: linear-gradient(135deg, #94d2bdaa, #0a9396cc);
        color: #caf0f8;
    }

    /* Notifications */
    .notification {
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        animation: slideIn 0.4s ease-out;
        user-select: none;
        color: inherit;
        transition: background-color 0.4s ease, color 0.3s ease;
    }
    .light-mode .notification-success {
        background: #b7e4c7;
        border-left: 5px solid #138086;
        color: #073b3a;
    }
    .dark-mode .notification-success {
        background: #1a4f46cc;
        border-left: 5px solid #27ae60;
        color: #caf0f8;
    }
    .light-mode .notification-error {
        background: #f8d7da;
        border-left: 5px solid #991b1e;
        color: #5e1b1f;
    }
    .dark-mode .notification-error {
        background: #621c1fcc;
        border-left: 5px solid #e74c3c;
        color: #ffb3b3;
    }
    .light-mode .notification-info {
        background: #caf0f8;
        border-left: 5px solid #0a9396;
        color: #055c60;
    }
    .dark-mode .notification-info {
        background: #0a9396cc;
        border-left: 5px solid #94d2bd;
        color: #d7f2fb;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-120%); }
        to { opacity: 1; transform: translateX(0); }
    }

    /* Misc fixes for inputs, selects, textareas - ensure text visible */
    .stMarkdown, .stTextArea, .stTextInput, .stSelectbox, .stText {
        color: inherit !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        color: inherit !important;
        font-weight: 600;
        border-radius: 12px;
        transition: color 0.4s ease;
    }

</style>
""", unsafe_allow_html=True)

def init_data_storage():
    """Initialize data storage for candidates and interviews"""
    if 'candidates_data' not in st.session_state:
        st.session_state.candidates_data = []
    if 'interviews_data' not in st.session_state:
        st.session_state.interviews_data = []
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'email_templates' not in st.session_state:
        st.session_state.email_templates = {
            'interview_invitation': {
                'subject': 'Interview Invitation - {company_name}',
                'body': '''Dear {candidate_name},

Congratulations! We are pleased to invite you for an interview for the {role} position at {company_name}.

Interview Details:
- Date: {interview_date}
- Time: {interview_time}
- Duration: 60 minutes
- Meeting Link: {zoom_link}

Please join the meeting 5 minutes early to ensure everything is working properly.

We look forward to speaking with you!

Best regards,
{company_name} Recruitment Team'''
            },
            'interview_confirmation': {
                'subject': 'Interview Confirmation - {company_name}',
                'body': '''Dear {candidate_name},

This is a confirmation of your upcoming interview for the {role} position.

Interview Details:
- Date: {interview_date}
- Time: {interview_time}
- Duration: 60 minutes
- Meeting Link: {zoom_link}

Please prepare:
1. Your resume
2. Examples of your work
3. Questions about the role and company

If you need to reschedule, please contact us at least 24 hours in advance.

Best regards,
{company_name} Recruitment Team'''
            },
            'interview_reminder': {
                'subject': 'Interview Reminder - Tomorrow at {interview_time}',
                'body': '''Dear {candidate_name},

This is a friendly reminder about your interview tomorrow for the {role} position at {company_name}.

Interview Details:
- Date: {interview_date}
- Time: {interview_time}
- Duration: 60 minutes
- Meeting Link: {zoom_link}

We look forward to meeting you!

Best regards,
{company_name} Recruitment Team'''
            }
        }
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []

def add_notification(message, type='info'):
    """Add a notification to the session state"""
    notification = {
        'id': len(st.session_state.notifications) + 1,
        'message': message,
        'type': type,
        'timestamp': datetime.now().isoformat()
    }
    st.session_state.notifications.append(notification)

def show_notifications():
    """Display notifications"""
    if st.session_state.notifications:
        for notification in st.session_state.notifications[-3:]:  # Show last 3
            st.markdown(f'''
            <div class="notification notification-{notification['type']}">
                {notification['message']}
            </div>
            ''', unsafe_allow_html=True)

def save_candidate_data(candidate_data):
    """Save candidate data to session state"""
    st.session_state.candidates_data.append(candidate_data)
    add_notification(f"Candidate {candidate_data['name']} added successfully!", 'success')
    
def save_interview_data(interview_data):
    """Save interview data to session state"""
    st.session_state.interviews_data.append(interview_data)
    add_notification(f"Interview scheduled for {interview_data['candidate_name']}!", 'success')

def get_candidates_by_status(status=None):
    """Get candidates filtered by status"""
    candidates = st.session_state.candidates_data
    if status:
        return [c for c in candidates if c.get('status') == status]
    return candidates

def render_step_indicator(current_step, total_steps=4):
    """Render enhanced step indicator"""
    steps = ['Configuration', 'Candidate Analysis', 'Interview Scheduling', 'Dashboard']
    icons = ['🔧', '👤', '📅', '📊']
    
    step_html = '<div class="step-indicator">'
    for i, (step, icon) in enumerate(zip(steps, icons), 1):
        step_class = 'step'
        if i == current_step:
            step_class += ' active'
        elif i < current_step:
            step_class += ' completed'
        
        step_html += f'<div class="{step_class}">{icon} {step}</div>'
    
    step_html += '</div>'
    st.markdown(step_html, unsafe_allow_html=True)

def configuration_page():
    """Enhanced configuration page"""
    st.markdown('''
    <div class="main-header">
        <h1>🔧 System Configuration</h1>
        <p>Configure your AI recruitment system settings</p>
    </div>
    ''', unsafe_allow_html=True)
    
    render_step_indicator(1)
    
    # Progress bar
    progress = 0.25
    st.markdown(f'<div class="progress-bar" style="width: {progress*100}%"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("🔑 API Configuration")
        
        with st.expander("OpenRouter Settings", expanded=True):
            api_key = st.text_input(
                "OpenRouter API Key", 
                type="password", 
                value=st.session_state.openai_api_key,
                help="Get your API key from https://openrouter.ai"
            )
            if api_key:
                st.session_state.openai_api_key = api_key
                st.success("✅ API Key configured")
        
        with st.expander("Zoom Settings"):
            st.session_state.zoom_account_id = st.text_input(
                "Zoom Account ID", 
                type="password", 
                value=st.session_state.zoom_account_id
            )
            st.session_state.zoom_client_id = st.text_input(
                "Zoom Client ID", 
                type="password", 
                value=st.session_state.zoom_client_id
            )
            st.session_state.zoom_client_secret = st.text_input(
                "Zoom Client Secret", 
                type="password", 
                value=st.session_state.zoom_client_secret
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("📧 Email Configuration")
        
        with st.expander("Email Settings", expanded=True):
            st.session_state.email_sender = st.text_input(
                "Sender Email", 
                value=st.session_state.email_sender,
                help="Gmail address for sending emails"
            )
            st.session_state.email_passkey = st.text_input(
                "Email App Password", 
                type="password", 
                value=st.session_state.email_passkey,
                help="Gmail app password (not regular password)"
            )
            st.session_state.company_name = st.text_input(
                "Company Name", 
                value=st.session_state.company_name,
                help="Your company name for email templates"
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Configuration validation with enhanced UI
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.subheader("✅ Configuration Status")
    
    required_configs = {
        'OpenRouter API Key': st.session_state.openai_api_key,
        'Email Sender': st.session_state.email_sender,
        'Email Password': st.session_state.email_passkey,
        'Company Name': st.session_state.company_name
    }
    
    optional_configs = {
        'Zoom Account ID': st.session_state.zoom_account_id,
        'Zoom Client ID': st.session_state.zoom_client_id,
        'Zoom Client Secret': st.session_state.zoom_client_secret
    }
    
    config_status = {}
    
    for name, value in required_configs.items():
        if value:
            st.success(f"✅ {name}")
            config_status[name] = True
        else:
            st.error(f"❌ {name} - Required")
            config_status[name] = False
    
    for name, value in optional_configs.items():
        if value:
            st.info(f"ℹ️ {name} - Optional")
            config_status[name] = True
        else:
            st.warning(f"⚠️ {name} - Optional (needed for interview scheduling)")
            config_status[name] = False
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation with enhanced buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if all(config_status[name] for name in required_configs.keys()):
            if st.button("🚀 Proceed to Candidate Analysis", type="primary", use_container_width=True):
                st.session_state.current_step = 2
                add_notification("Configuration completed successfully!", 'success')
                st.rerun()
        else:
            st.button("🚀 Proceed to Candidate Analysis", disabled=True, use_container_width=True)
            st.caption("Please complete required configurations")

def candidate_analysis_page():
    """Enhanced candidate analysis page"""
    st.markdown('''
    <div class="main-header">
        <h1>👤 Candidate Analysis</h1>
        <p>Upload resumes and analyze candidates with AI</p>
    </div>
    ''', unsafe_allow_html=True)
    
    render_step_indicator(2)
    
    # Progress bar
    progress = 0.5
    st.markdown(f'<div class="progress-bar" style="width: {progress*100}%"></div>', unsafe_allow_html=True)
    
    # Role selection with enhanced UI
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.subheader("🎯 Job Position")
    role = st.selectbox(
        "Select Role to Recruit For", 
        ["ai_ml_engineer", "frontend_engineer", "backend_engineer"],
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    # Display role requirements with better formatting
    with st.expander("📋 Role Requirements", expanded=True):
        st.markdown(ROLE_REQUIREMENTS[role])
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Resume upload and analysis with enhanced layout
    col1, col2 = st.columns([1, 1])


    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("📄 Resume Upload")
        resume_file = st.file_uploader(
            "Upload Resume (PDF)", 
            type=["pdf"],
            help="Upload candidate's resume in PDF format"
        )
        
        if resume_file:
            st.success("✅ Resume uploaded successfully!")
            
            # Display the uploaded resume
            st.markdown("### 📄 Resume Preview")
            try:
                # ✅ Convert UploadedFile to bytes before passing to pdf_viewer
                pdf_viewer(resume_file.read(), width=700, height=500)
            except Exception as e:
                st.warning(f"Could not display PDF preview: {e}")
                st.info("PDF uploaded but preview not available")
   
            
            # Extract text with progress
            with st.spinner("Extracting text from PDF..."):
                resume_text = extract_text_from_pdf(resume_file)
                if resume_text:
                    st.session_state.current_resume_text = resume_text
                    st.session_state.current_resume_file = resume_file
                    st.info(f"📊 Extracted {len(resume_text)} characters from resume")
                    
                    # Show extracted text in expander
                    with st.expander("📝 View Extracted Text", expanded=False):
                        st.text_area("Resume Text", value=resume_text, height=200, disabled=True)
                else:
                    st.error("❌ Failed to extract text from PDF")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("📧 Candidate Information")
        candidate_email = st.text_input(
            "Candidate Email", 
            value=st.session_state.get('candidate_email', ''),
            help="Email address for communication"
        )
        st.session_state.candidate_email = candidate_email
        
        candidate_name = st.text_input(
            "Candidate Name", 
            value=st.session_state.get('candidate_name', ''),
            help="Full name of the candidate"
        )
        st.session_state.candidate_name = candidate_name
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis section with enhanced UI
    st.markdown("---")
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.subheader("🔍 Resume Analysis")
    
    # Add clear form button
    if st.session_state.get('current_resume_text') or st.session_state.get('candidate_email'):
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🗑️ Clear Form", use_container_width=True):
                st.session_state.current_resume_text = ""
                st.session_state.candidate_email = ""
                st.session_state.candidate_name = ""
                st.session_state.current_resume_file = None
                st.session_state.show_email_preview = False
                st.rerun()
        with col2:
            st.info("💡 Form has data. Click 'Clear Form' to start fresh or continue with current data.")
    
    if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
        if not st.session_state.get('current_resume_text'):
            st.warning("⚠️ Please upload a resume first")
        elif not candidate_email:
            st.warning("⚠️ Please enter candidate email")
        elif not candidate_name:
            st.warning("⚠️ Please enter candidate name")
        else:
            with st.spinner("🤖 AI is analyzing the resume..."):
                try:
                    analyzer = create_resume_analyzer()
                    email_agent = create_email_agent()
                    
                    is_selected, feedback = analyze_resume(
                        st.session_state.current_resume_text, 
                        role, 
                        analyzer
                    )
                    
                    # Create candidate data with enhanced fields
                    candidate_data = {
                        'id': len(st.session_state.candidates_data) + 1,
                        'name': candidate_name,
                        'email': candidate_email,
                        'role': role,
                        'resume_text': st.session_state.current_resume_text,
                        'status': 'selected' if is_selected else 'rejected',
                        'feedback': feedback,
                        'analysis_date': datetime.now().isoformat(),
                        'matching_skills': [],  # Could be extracted from analysis
                        'missing_skills': [],   # Could be extracted from analysis
                        'score': random.randint(60, 95) if is_selected else random.randint(20, 60)
                    }
                    
                    # Save candidate data
                    save_candidate_data(candidate_data)
                    
                    # Display results with enhanced UI
                    st.markdown("### 📊 Analysis Results")
                    
                    status_class = "status-selected" if is_selected else "status-rejected"
                    status_text = "SELECTED" if is_selected else "REJECTED"
                    st.markdown(f'<div class="status-badge {status_class}">{status_text}</div>', unsafe_allow_html=True)
                    
                    # Show score
                    st.metric("AI Score", f"{candidate_data['score']}/100")
                    
                    st.markdown("### 💬 Feedback")
                    st.info(feedback)
                    
                    # Email Action Section
                    st.markdown("### 📧 Email Actions")
                    
                    if is_selected:
                        st.success("🎉 Candidate Selected!")
                        st.info("💡 This candidate has been selected. You can proceed and schedule the Ai interview.")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("📧 Send Selection Email", type="primary", use_container_width=True):
                                with st.spinner("Sending email..."):
                                    try:
                                        send_selection_email(email_agent, candidate_email, role)
                                        st.success(f"✅ Selection email sent to {candidate_email}")
                                        st.balloons()
                                        add_notification(f"Selection email sent to {candidate_email}!", 'success')
                                    except Exception as e:
                                        st.error(f"❌ Failed to send email: {str(e)}")
                                        add_notification(f"Failed to send email: {str(e)}", 'error')
                        
                        with col2:
                            if st.button("👁️ Preview Email", use_container_width=True):
                                st.session_state.show_email_preview = True
                                st.session_state.email_type = 'selection'
                                st.rerun()
                        
                        with col3:
                            if st.button("📅 Go to Interview Scheduling", use_container_width=True):
                                st.session_state.current_step = 3
                                st.rerun()
                        
                        # Email Preview Section
                        if st.session_state.get('show_email_preview') and st.session_state.get('email_type') == 'selection':
                            st.markdown("---")
                            st.markdown("### 📧 Email Preview")
                            
                            # Generate email preview (no send)
                            try:
                                email_prompt = (
                                    f"Send an email to {candidate_email} about selection for the {role} "
                                    f"position. Congratulate them and mention next steps. Include company name: "
                                    f"{st.session_state.company_name}."
                                )
                                email_content = openrouter_chat(
                                    messages=[{"role": "user", "content": email_prompt}],
                                    api_key=st.session_state.openai_api_key,
                                )
                                
                                # Display the preview
                                st.markdown('<div class="email-preview">', unsafe_allow_html=True)
                                st.text_input("Subject", value="Update on your job application", disabled=True)
                                st.text_area("Email Body", value=email_content, height=200, disabled=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("✅ Send This Email", type="primary", use_container_width=True):
                                        with st.spinner("Sending email..."):
                                            try:
                                                send_selection_email(email_agent, candidate_email, role)
                                                st.success(f"✅ Selection email sent to {candidate_email}")
                                                st.balloons()
                                                add_notification(f"Selection email sent to {candidate_email}!", 'success')
                                                st.session_state.show_email_preview = False
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"❌ Failed to send email: {str(e)}")
                                                add_notification(f"Failed to send email: {str(e)}", 'error')
                                
                                with col2:
                                    if st.button("❌ Cancel", use_container_width=True):
                                        st.session_state.show_email_preview = False
                                        st.rerun()
                                        
                            except Exception as e:
                                st.error(f"❌ Failed to generate email preview: {str(e)}")
                                st.info("Please try again or send email directly")
                    
                    else:
                        st.warning("❌ Candidate Not Selected")
                        st.info("💡 This candidate was not selected. You can send a polite rejection email with feedback.")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("📧 Send Rejection Email", type="secondary", use_container_width=True):
                                with st.spinner("Sending email..."):
                                    try:
                                        send_rejection_email(email_agent, candidate_email, role, feedback)
                                        st.success(f"✅ Rejection email sent to {candidate_email}")
                                        add_notification(f"Rejection email sent to {candidate_email}!", 'success')
                                    except Exception as e:
                                        st.error(f"❌ Failed to send email: {str(e)}")
                                        add_notification(f"Failed to send email: {str(e)}", 'error')
                        
                        with col2:
                            if st.button("👁️ Preview Email", use_container_width=True):
                                st.session_state.show_email_preview = True
                                st.session_state.email_type = 'rejection'
                                st.rerun()
                        
                        # Email Preview Section for Rejection
                        if st.session_state.get('show_email_preview') and st.session_state.get('email_type') == 'rejection':
                            st.markdown("---")
                            st.markdown("### 📧 Email Preview")
                            
                            # Generate rejection email preview (no send)
                            try:
                                email_prompt = (
                                    f"send an email to {candidate_email} regarding the {role} application. "
                                    f"Use all lowercase, be empathetic and human. Mention feedback: {feedback}. "
                                    f"Encourage upskilling and retry. Suggest learning resources based on missing "
                                    f"skills. End with exactly:\nbest,\nthe ai recruiting team"
                                )
                                email_content = openrouter_chat(
                                    messages=[{"role": "user", "content": email_prompt}],
                                    api_key=st.session_state.openai_api_key,
                                )
                                
                                # Display the preview
                                st.markdown('<div class="email-preview">', unsafe_allow_html=True)
                                st.text_input("Subject", value="Update on your job application", disabled=True)
                                st.text_area("Email Body", value=email_content, height=200, disabled=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("✅ Send This Email", type="secondary", use_container_width=True):
                                        with st.spinner("Sending email..."):
                                            try:
                                                send_rejection_email(email_agent, candidate_email, role, feedback)
                                                st.success(f"✅ Rejection email sent to {candidate_email}")
                                                add_notification(f"Rejection email sent to {candidate_email}!", 'success')
                                                st.session_state.show_email_preview = False
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"❌ Failed to send email: {str(e)}")
                                                add_notification(f"Failed to send email: {str(e)}", 'error')
                                
                                with col2:
                                    if st.button("❌ Cancel", use_container_width=True):
                                        st.session_state.show_email_preview = False
                                        st.rerun()
                                        
                            except Exception as e:
                                st.error(f"❌ Failed to generate email preview: {str(e)}")
                                st.info("Please try again or send email directly")
                        
                        # Add analyze another button
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("🔄 Analyze Another Resume", use_container_width=True):
                                # Clear form
                                st.session_state.current_resume_text = ""
                                st.session_state.candidate_email = ""
                                st.session_state.candidate_name = ""
                                st.session_state.current_resume_file = None
                                st.session_state.show_email_preview = False
                                st.rerun()
                        
                        with col2:
                            if st.button("📅 Go to Interview Scheduling", use_container_width=True):
                                st.session_state.current_step = 3
                                st.rerun()
                    
                    # Don't clear form automatically - let user decide
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    add_notification(f"Analysis failed: {str(e)}", 'error')
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent candidates with enhanced cards
    if st.session_state.candidates_data:
        st.markdown("---")
        st.subheader("📋 Recent Candidates")
        
        for candidate in st.session_state.candidates_data[-3:]:  # Show last 3
            with st.container():
                status_icon = "✅" if candidate['status'] == 'selected' else "❌"
                st.markdown(f'''
                <div class="candidate-card">
                    <h4>{status_icon} {candidate['name']}</h4>
                    <p><strong>Email:</strong> {candidate['email']}</p>
                    <p><strong>Role:</strong> {candidate['role'].replace('_', ' ').title()}</p>
                    <p><strong>Status:</strong> {candidate['status'].title()}</p>
                    <p><strong>Score:</strong> {candidate.get('score', 'N/A')}/100</p>
                    <p><strong>Date:</strong> {candidate['analysis_date'][:10]}</p>
                </div>
                ''', unsafe_allow_html=True)
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Back to Configuration", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    
    with col3:
        if st.button("➡️ Go to Interview Scheduling", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()

def interview_scheduling_page():
    """Enhanced interview scheduling page with mail preview"""
    st.markdown('''
    <div class="main-header">
        <h1>📅 Interview Scheduling</h1>
        <p>Schedule interviews with email preview and editing</p>
    </div>
    ''', unsafe_allow_html=True)
    
    render_step_indicator(3)
    
    # Progress bar
    progress = 0.75
    st.markdown(f'<div class="progress-bar" style="width: {progress*100}%"></div>', unsafe_allow_html=True)
    
    # Get selected candidates
    selected_candidates = get_candidates_by_status('selected')
    
    if not selected_candidates:
        st.markdown('<div class="notification notification-info">', unsafe_allow_html=True)
        st.warning("⚠️ No selected candidates found. Please analyze candidates first.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("⬅️ Back to Candidate Analysis", use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()
        return
    
    st.subheader("👥 Selected Candidates")
    
    # Display selected candidates with enhanced UI
    for candidate in selected_candidates:
        with st.expander(f"👤 {candidate['name']} - {candidate['role'].replace('_', ' ').title()}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f'''
                <div class="candidate-card">
                    <h4>📧 {candidate['email']}</h4>
                    <p><strong>Analysis Date:</strong> {candidate['analysis_date'][:10]}</p>
                    <p><strong>Score:</strong> {candidate.get('score', 'N/A')}/100</p>
                    <p><strong>Feedback:</strong> {candidate['feedback'][:100]}...</p>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                if st.button(f"📅 Schedule Interview", key=f"schedule_{candidate['id']}"):
                    st.session_state.selected_candidate = candidate
                    st.session_state.scheduling_step = 'email_template'
                    st.rerun()
    
    # Email template selection and preview
    if 'selected_candidate' in st.session_state and 'scheduling_step' in st.session_state:
        candidate = st.session_state.selected_candidate
        
        if st.session_state.scheduling_step == 'email_template':
            st.markdown("---")
            st.subheader("📧 Email Template Selection")
            
            # Template selection
            template_options = list(st.session_state.email_templates.keys())
            selected_template = st.selectbox(
                "Choose Email Template",
                template_options,
                format_func=lambda x: x.replace('_', ' ').title()
            )
            
            # Preview email
            template = st.session_state.email_templates[selected_template]
            
            # Generate preview data
            ist_tz = pytz.timezone('Asia/Kolkata')
            tomorrow = datetime.now(ist_tz) + timedelta(days=1)
            interview_time = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0)
            
            preview_data = {
                'candidate_name': candidate['name'],
                'company_name': st.session_state.company_name,
                'role': candidate['role'].replace('_', ' ').title(),
                'interview_date': interview_time.strftime('%B %d, %Y'),
                'interview_time': interview_time.strftime('%I:%M %p IST'),
                'zoom_link': 'https://zoom.us/j/123456789'  # Placeholder
            }
            
            # Email preview
            st.markdown('<div class="email-preview">', unsafe_allow_html=True)
            st.markdown("### 📧 Email Preview")
            
            # Subject preview
            subject = template['subject'].format(**preview_data)
            st.text_input("Subject", value=subject, disabled=True)
            
            # Body preview
            body = template['body'].format(**preview_data)
            st.text_area("Email Body", value=body, height=200, disabled=True)
            
            # Zoom link preview
            st.markdown(f'''
            <div class="zoom-link">
                🔗 Zoom Meeting Link: {preview_data['zoom_link']}
            </div>
            ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Edit options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✏️ Edit Email", use_container_width=True):
                    st.session_state.scheduling_step = 'edit_email'
                    st.session_state.editing_template = selected_template
                    st.rerun()
            
            with col2:
                if st.button("📅 Schedule & Send", type="primary", use_container_width=True):
                    st.session_state.scheduling_step = 'confirm_schedule'
                    st.session_state.final_template = selected_template
                    st.rerun()
            
            with col3:
                if st.button("❌ Cancel", use_container_width=True):
                    del st.session_state.selected_candidate
                    del st.session_state.scheduling_step
                    st.rerun()
        
        elif st.session_state.scheduling_step == 'edit_email':
            st.markdown("---")
            st.subheader("✏️ Edit Email Template")
            
            template_key = st.session_state.editing_template
            template = st.session_state.email_templates[template_key]
            
            # Editable fields
            new_subject = st.text_input("Subject", value=template['subject'])
            new_body = st.text_area("Email Body", value=template['body'], height=300)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 Save Template", use_container_width=True):
                    st.session_state.email_templates[template_key]['subject'] = new_subject
                    st.session_state.email_templates[template_key]['body'] = new_body
                    st.session_state.scheduling_step = 'email_template'
                    add_notification("Email template updated successfully!", 'success')
                    st.rerun()
            
            with col2:
                if st.button("📅 Schedule & Send", type="primary", use_container_width=True):
                    # Update template temporarily
                    st.session_state.email_templates[template_key]['subject'] = new_subject
                    st.session_state.email_templates[template_key]['body'] = new_body
                    st.session_state.scheduling_step = 'confirm_schedule'
                    st.session_state.final_template = template_key
                    st.rerun()
            
            with col3:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.scheduling_step = 'email_template'
                    st.rerun()
        
        elif st.session_state.scheduling_step == 'confirm_schedule':
            st.markdown("---")
            st.subheader("✅ Confirm Interview Scheduling")
            
            candidate = st.session_state.selected_candidate
            template_key = st.session_state.final_template
            template = st.session_state.email_templates[template_key]
            
            # Final confirmation
            st.markdown(f'''
            <div class="notification notification-info">
                <h4>📅 Interview Details</h4>
                <p><strong>Candidate:</strong> {candidate['name']}</p>
                <p><strong>Email:</strong> {candidate['email']}</p>
                <p><strong>Role:</strong> {candidate['role'].replace('_', ' ').title()}</p>
                <p><strong>Template:</strong> {template_key.replace('_', ' ').title()}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col2:
                if st.button("🚀 Confirm & Schedule", type="primary", use_container_width=True):
                    with st.spinner("Scheduling interview and sending email..."):
                        try:
                            scheduler = create_scheduler_agent()
                            email_agent = create_email_agent()
                            
                            # Schedule interview
                            schedule_interview(
                                scheduler, 
                                candidate['email'], 
                                email_agent, 
                                candidate['role']
                            )
                            
                            # Save interview data
                            interview_data = {
                                'candidate_id': candidate['id'],
                                'candidate_name': candidate['name'],
                                'candidate_email': candidate['email'],
                                'role': candidate['role'],
                                'scheduled_date': datetime.now().isoformat(),
                                'status': 'scheduled',
                                'template_used': template_key
                            }
                            
                            save_interview_data(interview_data)
                            
                            st.success(f"✅ Interview scheduled for {candidate['name']}")
                            add_notification(f"Interview scheduled and email sent to {candidate['name']}!", 'success')
                            
                            # Clear scheduling state
                            del st.session_state.selected_candidate
                            del st.session_state.scheduling_step
                            del st.session_state.final_template
                            
                        except Exception as e:
                            st.error(f"❌ Failed to schedule interview: {str(e)}")
                            add_notification(f"Failed to schedule interview: {str(e)}", 'error')
            
            with col3:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.scheduling_step = 'email_template'
                    st.rerun()
    
    # Scheduled interviews with enhanced display
    if st.session_state.interviews_data:
        st.markdown("---")
        st.subheader("📋 Scheduled Interviews")
        
        interviews_df = pd.DataFrame(st.session_state.interviews_data)
        
        if not interviews_df.empty:
            # Enhanced dataframe display
            st.dataframe(
                interviews_df[['candidate_name', 'candidate_email', 'role', 'scheduled_date', 'status']],
                use_container_width=True
            )
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Back to Candidate Analysis", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()
    
    with col3:
        if st.button("➡️ Go to Dashboard", use_container_width=True):
            st.session_state.current_step = 4
            st.rerun()

def dashboard_page():
    """Enhanced dashboard page with advanced analytics"""
    st.markdown('''
    <div class="main-header">
        <h1>📊 Recruitment Dashboard</h1>
        <p>Advanced analytics and insights for your recruitment process</p>
    </div>
    ''', unsafe_allow_html=True)
    
    render_step_indicator(4)
    
    # Progress bar
    progress = 1.0
    st.markdown(f'<div class="progress-bar" style="width: {progress*100}%"></div>', unsafe_allow_html=True)
    
    # Statistics with enhanced metrics
    total_candidates = len(st.session_state.candidates_data)
    selected_candidates = len(get_candidates_by_status('selected'))
    rejected_candidates = len(get_candidates_by_status('rejected'))
    scheduled_interviews = len(st.session_state.interviews_data)
    
    # Enhanced metrics display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Total Candidates",
            value=total_candidates,
            delta=None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Selected",
            value=selected_candidates,
            delta=f"{selected_candidates/total_candidates*100:.1f}%" if total_candidates > 0 else "0%"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Rejected",
            value=rejected_candidates,
            delta=f"{rejected_candidates/total_candidates*100:.1f}%" if total_candidates > 0 else "0%"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Scheduled Interviews",
            value=scheduled_interviews,
            delta=None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced charts
    if total_candidates > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution pie chart with enhanced styling
            status_data = {
                'Selected': selected_candidates,
                'Rejected': rejected_candidates
            }
            
            fig_pie = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                title="Candidate Status Distribution",
                color_discrete_map={'Selected': '#28a745', 'Rejected': '#dc3545'},
                hole=0.3
            )
            fig_pie.update_layout(
                font=dict(family="Inter", size=12),
                title_font=dict(size=16, family="Inter")
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Role distribution with enhanced styling
            role_data = {}
            for candidate in st.session_state.candidates_data:
                role = candidate['role'].replace('_', ' ').title()
                role_data[role] = role_data.get(role, 0) + 1
            
            if role_data:
                fig_bar = px.bar(
                    x=list(role_data.keys()),
                    y=list(role_data.values()),
                    title="Candidates by Role",
                    labels={'x': 'Role', 'y': 'Count'},
                    color=list(role_data.values()),
                    color_continuous_scale='viridis'
                )
                fig_bar.update_layout(
                    font=dict(family="Inter", size=12),
                    title_font=dict(size=16, family="Inter")
                )
                st.plotly_chart(fig_bar, use_container_width=True)
    
    # Recent activity with enhanced display
    st.markdown("---")
    st.subheader("📈 Recent Activity")
    
    if st.session_state.candidates_data:
        # Create a timeline of recent candidates
        recent_candidates = sorted(
            st.session_state.candidates_data, 
            key=lambda x: x['analysis_date'], 
            reverse=True
        )[:5]
        
        for candidate in recent_candidates:
            status_icon = "✅" if candidate['status'] == 'selected' else "❌"
            score = candidate.get('score', 'N/A')
            st.markdown(f'''
            <div class="candidate-card">
                <h4>{status_icon} {candidate['name']}</h4>
                <p><strong>Role:</strong> {candidate['role'].replace('_', ' ').title()}</p>
                <p><strong>Score:</strong> {score}/100</p>
                <p><strong>Date:</strong> {candidate['analysis_date'][:10]}</p>
            </div>
            ''', unsafe_allow_html=True)
    
    # Export functionality
    st.markdown("---")
    st.subheader("📤 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Candidates", use_container_width=True):
            if st.session_state.candidates_data:
                df = pd.DataFrame(st.session_state.candidates_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"candidates_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No candidate data to export")
    
    with col2:
        if st.button("📅 Export Interviews", use_container_width=True):
            if st.session_state.interviews_data:
                df = pd.DataFrame(st.session_state.interviews_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"interviews_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No interview data to export")
    
    with col3:
        if st.button("📋 Generate Report", use_container_width=True):
            # Generate a simple text report
            report = f"""
AI Recruitment System Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
- Total Candidates: {total_candidates}
- Selected: {selected_candidates}
- Rejected: {rejected_candidates}
- Scheduled Interviews: {scheduled_interviews}

Success Rate: {(selected_candidates/total_candidates*100):.1f}% if total_candidates > 0 else 0%

Recent Candidates:
"""
            for candidate in recent_candidates:
                report += f"- {candidate['name']} ({candidate['role']}) - {candidate['status']}\n"
            
            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"recruitment_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Back to Interview Scheduling", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()
    
    with col2:
        if st.button("🔄 Start New Recruitment", type="primary", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()
    
    with col3:
        if st.button("⚙️ Configuration", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()

def main():
    """Main application with enhanced features"""
    # Initialize session state
    init_session_state()
    init_data_storage()
    
    # Sidebar navigation with enhanced stats
    with st.sidebar:
        st.markdown("### 🎯 AI Recruitment System Pro")
        st.markdown("---")
        
        # Quick stats in sidebar
        if st.session_state.candidates_data:
            st.markdown('<div class="sidebar-stats">', unsafe_allow_html=True)
            st.markdown('<h4>📊 Quick Stats</h4>', unsafe_allow_html=True)
            
            total = len(st.session_state.candidates_data)
            selected = len(get_candidates_by_status('selected'))
            interviews = len(st.session_state.interviews_data)
            
            st.markdown(f'''
            <div class="stat-item">
                <span>Total Candidates</span>
                <span class="stat-value">{total}</span>
            </div>
            <div class="stat-item">
                <span>Selected</span>
                <span class="stat-value">{selected}</span>
            </div>
            <div class="stat-item">
                <span>Interviews</span>
                <span class="stat-value">{interviews}</span>
            </div>
            ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation buttons
        pages = {
            1: "🔧 Configuration",
            2: "👤 Candidate Analysis", 
            3: "📅 Interview Scheduling",
            4: "📊 Dashboard"
        }
        
        for step_num, page_name in pages.items():
            if st.button(page_name, key=f"nav_{step_num}", use_container_width=True):
                st.session_state.current_step = step_num
                st.rerun()
        
        st.markdown("---")
        
        # Notifications
        if st.session_state.notifications:
            st.markdown("### 🔔 Recent Notifications")
            for notification in st.session_state.notifications[-3:]:
                icon = "✅" if notification['type'] == 'success' else "❌" if notification['type'] == 'error' else "ℹ️"
                st.markdown(f"{icon} {notification['message']}")
    
    # Show notifications
    show_notifications()
    
    # Main content area
    current_step = st.session_state.current_step
    
    if current_step == 1:
        configuration_page()
    elif current_step == 2:
        candidate_analysis_page()
    elif current_step == 3:
        interview_scheduling_page()
    elif current_step == 4:
        dashboard_page()
    else:
        st.error("Invalid step. Redirecting to configuration...")
        st.session_state.current_step = 1
        st.rerun()

if __name__ == "__main__":
    main()
