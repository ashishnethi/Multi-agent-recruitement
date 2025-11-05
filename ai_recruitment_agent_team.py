from typing import Literal, Tuple, Dict, Optional
import os
import time
import json
import requests
import PyPDF2
from datetime import datetime, timedelta
import pytz

import streamlit as st
import openai
from openai import OpenAI
from agno.agent import Agent
from agno.tools.email import EmailTools
from phi.tools.zoom import ZoomTool
from phi.utils.log import logger
from streamlit_pdf_viewer import pdf_viewer

# ======================================================================
# --- OPENROUTER CONFIGURATION ---
# ======================================================================

def setup_openrouter(api_key: str):
    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"

OR_MODEL = "nousresearch/hermes-4-405b"

# ======================================================================
# --- ROLE REQUIREMENTS ---
# ======================================================================

ROLE_REQUIREMENTS: Dict[str, str] = {
    "ai_ml_engineer": """
        Required Skills:
        - Python, PyTorch/TensorFlow
        - Machine Learning algorithms and frameworks
        - Deep Learning and Neural Networks
        - Data preprocessing and analysis
        - MLOps and model deployment
        - RAG, LLM, Finetuning and Prompt Engineering
    """,
    "frontend_engineer": """
        Required Skills:
        - React/Vue.js/Angular
        - HTML5, CSS3, JavaScript/TypeScript
        - Responsive design
        - State management
        - Frontend testing
    """,
    "backend_engineer": """
        Required Skills:
        - Python/Java/Node.js
        - REST APIs
        - Database design and management
        - System architecture
        - Cloud services (AWS/GCP/Azure)
        - Kubernetes, Docker, CI/CD
    """
}

# ======================================================================
# --- CUSTOM ZOOM TOOL ---
# ======================================================================

class CustomZoomTool(ZoomTool):
    def __init__(self, *, account_id: Optional[str] = None, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None, name: str = "zoom_tool"):
        super().__init__(account_id=account_id, client_id=client_id, client_secret=client_secret, name=name)
        self.token_url = "https://zoom.us/oauth/token"
        self.access_token = None
        self.token_expires_at = 0

    def get_access_token(self) -> str:
        if self.access_token and time.time() < self.token_expires_at:
            return str(self.access_token)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "account_credentials", "account_id": self.account_id}
        try:
            response = requests.post(self.token_url, headers=headers, data=data,
                                     auth=(self.client_id, self.client_secret))
            response.raise_for_status()
            token_info = response.json()
            self.access_token = token_info["access_token"]
            expires_in = token_info["expires_in"]
            self.token_expires_at = time.time() + expires_in - 60
            self._set_parent_token(str(self.access_token))
            return str(self.access_token)
        except requests.RequestException as e:
            logger.error(f"Error fetching access token: {e}")
            return ""

    def _set_parent_token(self, token: str) -> None:
        if token:
            self._ZoomTool__access_token = token

# ======================================================================
# --- SESSION INITIALIZATION ---
# ======================================================================

def init_session_state() -> None:
    defaults = {
        'candidate_email': "", 'openai_api_key': "", 'resume_text': "",
        'analysis_complete': False, 'is_selected': False,
        'zoom_account_id': "", 'zoom_client_id': "", 'zoom_client_secret': "",
        'email_sender': "", 'email_passkey': "", 'company_name': "", 'current_pdf': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ======================================================================
# --- SANITIZATION FIX ---
# ======================================================================

def sanitize_ascii(text: str) -> str:
    """Remove emojis and non-ASCII characters to prevent UnicodeEncodeError."""
    if not text:
        return ""
    return text.encode("ascii", errors="ignore").decode("ascii")

# ======================================================================
# --- OPENROUTER CHAT HELPER ---
# ======================================================================

# ======================================================================
# --- OPENROUTER CHAT HELPER (safe, ASCII-clean version) ---
# ======================================================================

def sanitize_ascii(text: str) -> str:
    """Remove or replace any non-ASCII character to prevent encoding errors."""
    if not isinstance(text, str):
        return text
    return text.encode("ascii", errors="ignore").decode("ascii")

def openrouter_chat(messages: list, api_key: str) -> str:
    """Send chat messages to OpenRouter and return model response."""
    from openai import OpenAI

    # 1️⃣ sanitize all message contents
    safe_messages = []
    for msg in messages:
        safe_msg = {}
        for k, v in msg.items():
            safe_msg[k] = sanitize_ascii(v) if isinstance(v, str) else v
        safe_messages.append(safe_msg)

    # 2️⃣ sanitize headers & strip anything unsafe
    safe_headers = {
        "HTTP-Referer": "http://localhost",
        "X-Title": "AI Recruitment System",
    }

    # 3️⃣ create client and send safe request
    client = OpenAI(api_key=sanitize_ascii(api_key), base_url="https://openrouter.ai/api/v1")

    try:
        resp = client.chat.completions.create(
            model=OR_MODEL,
            messages=safe_messages,
            extra_headers=safe_headers
        )
        # 4️⃣ sanitize response text too, just in case
        return sanitize_ascii(resp.choices[0].message.content)
    except Exception as e:
        raise RuntimeError(f"OpenRouter chat request failed: {e}")


# ======================================================================
# --- RESUME ANALYZER ---
# ======================================================================

def create_resume_analyzer():
    api_key = st.session_state.openai_api_key
    if not api_key:
        st.error("Please enter your OpenRouter API key first.")
        return None

    class ResumeAnalyzer:
        def run(self, prompt):
            messages = [{"role": "user", "content": sanitize_ascii(prompt)}]
            result = openrouter_chat(messages, api_key)
            class Msg:
                def __init__(self, content): self.content = content
            class Resp:
                def __init__(self, content): self.messages = [Msg(content)]
            return Resp(result)
    return ResumeAnalyzer()

# ======================================================================
# --- EMAIL AGENT ---
# ======================================================================

# def create_email_agent():
#     api_key = st.session_state.openai_api_key
#     class EmailAgent:
#         def run(self, prompt):
#             messages = [{"role": "user", "content": sanitize_ascii(prompt)}]
#             return openrouter_chat(messages, api_key)
#     return EmailAgent()
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def create_email_agent():
    api_key = st.session_state.openai_api_key
    sender = st.session_state.email_sender
    app_password = st.session_state.email_passkey

    class EmailAgent:
        def run(self, prompt):
            # Step 1: Let the AI draft the email text
            messages = [{"role": "user", "content": prompt}]
            email_content = openrouter_chat(messages, api_key)

            # Step 2: Send the email via SMTP (Gmail)
            try:
                msg = MIMEMultipart()
                msg["From"] = sender
                msg["To"] = extract_email(prompt)
                msg["Subject"] = "Update on your job application"

                msg.attach(MIMEText(email_content, "plain", "utf-8"))

                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender, app_password)
                    server.send_message(msg)

                st.success(f"✅ Email sent to {msg['To']}")
                print(f"✅ Email sent successfully to {msg['To']}")
            except Exception as e:
                st.error(f"❌ Failed to send email: {e}")
                print(f"❌ Email send error: {e}")

            return email_content

    # helper to extract email address from the prompt text
    def extract_email(prompt_text):
        import re
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', prompt_text)
        return match.group(0) if match else sender

    return EmailAgent()

# ======================================================================
# --- SCHEDULER AGENT ---
# ======================================================================

def create_scheduler_agent():
    api_key = st.session_state.openai_api_key
    zoom_tools = CustomZoomTool(
        account_id=st.session_state.zoom_account_id,
        client_id=st.session_state.zoom_client_id,
        client_secret=st.session_state.zoom_client_secret
    )
    class SchedulerAgent:
        def run(self, prompt):
            messages = [{"role": "user", "content": sanitize_ascii(prompt)}]
            return openrouter_chat(messages, api_key)
    return SchedulerAgent()

# ======================================================================
# --- PDF TEXT EXTRACTION ---
# ======================================================================

def extract_text_from_pdf(pdf_file) -> str:
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting PDF text: {str(e)}")
        return ""

# ======================================================================
# --- RESUME ANALYSIS ---
# ======================================================================

def analyze_resume(resume_text: str,
                   role: Literal["ai_ml_engineer", "frontend_engineer", "backend_engineer"],
                   analyzer) -> Tuple[bool, str]:
    try:
        response = analyzer.run(
            f"""Please analyze this resume against the following requirements and provide your response in valid JSON:
            Role Requirements:
            {ROLE_REQUIREMENTS[role]}
            Resume Text:
            {resume_text}
            Your response must be JSON like:
            {{
                "selected": true/false,
                "feedback": "...",
                "matching_skills": ["skill1", "skill2"],
                "missing_skills": ["skill3"],
                "experience_level": "junior/mid/senior"
            }}
            Criteria:
            - Match ≥70% of skills
            - Consider theory + practice
            - Value projects & adaptability
            Return ONLY JSON without markdown or backticks.
            """
        )
        assistant_message = response.messages[0].content
        result = json.loads(assistant_message.strip())
        if not isinstance(result, dict) or not all(k in result for k in ["selected", "feedback"]):
            raise ValueError("Invalid response format")
        return result["selected"], result["feedback"]
    except (json.JSONDecodeError, ValueError) as e:
        st.error(f"Error processing response: {str(e)}")
        return False, f"Error analyzing resume: {str(e)}"

# ======================================================================
# --- EMAIL FUNCTIONS ---
# ======================================================================

def send_selection_email(email_agent, to_email: str, role: str) -> None:
    email_agent.run(
        f"""
        Send an email to {to_email} about selection for the {role} position.
        Congratulate them and mention next steps.
        Include company name: {st.session_state.company_name}.
        """
    )

def send_rejection_email(email_agent, to_email: str, role: str, feedback: str) -> None:
    safe_feedback = sanitize_ascii(feedback)
    email_agent.run(
        f"""
        send an email to {to_email} regarding the {role} application.
        Use all lowercase, be empathetic and human.
        Mention feedback: {safe_feedback}
        Encourage upskilling and retry.
        Suggest learning resources based on missing skills.
        End with exactly:
        best,
        the ai recruiting team
        """
    )

# ======================================================================
# --- INTERVIEW SCHEDULING ---
# ======================================================================

def schedule_interview(scheduler, candidate_email: str, email_agent, role: str) -> None:
    try:
        ist_tz = pytz.timezone('Asia/Kolkata')
        current_time_ist = datetime.now(ist_tz)
        tomorrow_ist = current_time_ist + timedelta(days=1)
        interview_time = tomorrow_ist.replace(hour=11, minute=0, second=0, microsecond=0)
        formatted_time = interview_time.strftime('%Y-%m-%dT%H:%M:%S')

        meeting_response = scheduler.run(
            f"""Schedule a 60-minute technical interview:
            - Title: '{role} Technical Interview'
            - Date: {formatted_time}
            - Timezone: IST (India Standard Time)
            - Attendee: {candidate_email}
            """
        )

        email_agent.run(
            f"""Send interview confirmation email:
            - Role: {role}
            - Meeting Details: {meeting_response}
            - Timezone: IST
            - Ask candidate to join 5 minutes early
            """
        )
        st.success("Interview scheduled successfully! Check your email for details.")
    except Exception as e:
        logger.error(f"Error scheduling interview: {str(e)}")
        st.error("Unable to schedule interview. Please try again.")

# ======================================================================
# --- MAIN APP ---
# ======================================================================

def main() -> None:
    st.title("AI Recruitment System")
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        st.subheader("OpenRouter Settings")
        api_key = st.text_input("OpenRouter API Key", type="password", value=st.session_state.openai_api_key)
        if api_key:
            st.session_state.openai_api_key = api_key

        st.subheader("Zoom Settings")
        st.session_state.zoom_account_id = st.text_input("Zoom Account ID", type="password", value=st.session_state.zoom_account_id)
        st.session_state.zoom_client_id = st.text_input("Zoom Client ID", type="password", value=st.session_state.zoom_client_id)
        st.session_state.zoom_client_secret = st.text_input("Zoom Client Secret", type="password", value=st.session_state.zoom_client_secret)

        st.subheader("Email Settings")
        st.session_state.email_sender = st.text_input("Sender Email", value=st.session_state.email_sender)
        st.session_state.email_passkey = st.text_input("Email App Password", type="password", value=st.session_state.email_passkey)
        st.session_state.company_name = st.text_input("Company Name", value=st.session_state.company_name)

    # Check configuration
    required = {
        'OpenRouter API Key': st.session_state.openai_api_key,
        'Zoom Account ID': st.session_state.zoom_account_id,
        'Zoom Client ID': st.session_state.zoom_client_id,
        'Zoom Client Secret': st.session_state.zoom_client_secret,
        'Email Sender': st.session_state.email_sender,
        'Email Password': st.session_state.email_passkey,
        'Company Name': st.session_state.company_name
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        st.warning(f"Please configure the following: {', '.join(missing)}")
        return

    # Role
    role = st.selectbox("Select Role", ["ai_ml_engineer", "frontend_engineer", "backend_engineer"])
    with st.expander("View Required Skills", expanded=True):
        st.markdown(ROLE_REQUIREMENTS[role])

    # Resume
    resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    if resume_file:
        st.subheader("Uploaded Resume")
        text = extract_text_from_pdf(resume_file)
        if text:
            st.session_state.resume_text = text
            st.success("Resume processed successfully!")

    email = st.text_input("Candidate Email", value=st.session_state.candidate_email)
    st.session_state.candidate_email = email

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Analyze Resume"):
            if not st.session_state.resume_text:
                st.warning("Please upload and process a resume before analysis.")
            elif not email:
                st.warning("Please enter candidate email before analysis.")
            else:
                with st.spinner("Analyzing resume..."):
                    analyzer = create_resume_analyzer()
                    email_agent = create_email_agent()
                    is_selected, feedback = analyze_resume(st.session_state.resume_text, role, analyzer)
                    st.session_state.analysis_complete = True
                    st.session_state.is_selected = is_selected
                    st.session_state.analysis_feedback = feedback

                    if is_selected:
                        st.success("🎉 Selected for next round!")
                        send_selection_email(email_agent, email, role)
                    else:
                        st.warning("❌ Not selected.")
                        st.info(f"Feedback: {feedback}")
                        send_rejection_email(email_agent, email, role, feedback)

                    st.info(f"Feedback:\n\n{st.session_state.analysis_feedback}")

    with col2:
        if st.session_state.analysis_complete and st.session_state.is_selected:
            if st.button("Schedule Interview"):
                if not email:
                    st.warning("Please enter candidate email before scheduling.")
                else:
                    scheduler = create_scheduler_agent()
                    email_agent = create_email_agent()
                    schedule_interview(scheduler, email, email_agent, role)
        else:
            st.button("Schedule Interview", disabled=True)
            if not st.session_state.analysis_complete:
                st.caption("Analyze resume first to enable scheduling.")
            elif not st.session_state.is_selected:
                st.caption("Candidate not selected, cannot schedule interview.")

    if st.session_state.analysis_complete:
        if st.session_state.is_selected:
            st.success(f"Candidate {email} selected for role {role}.")
        else:
            st.warning(f"Candidate {email} not selected.")

if __name__ == "__main__":
    main()
