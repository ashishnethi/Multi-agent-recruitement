# 🎯 AI Recruitment System Pro

A premium, multi-page AI-powered recruitment system built with Streamlit that automates resume analysis, candidate communication, and interview scheduling with advanced UI/UX features.

## ✨ Features

### 🔧 Configuration Page
- **API Key Management**: Secure configuration of OpenRouter API keys
- **Email Settings**: Gmail integration for automated candidate communication
- **Zoom Integration**: Optional Zoom API setup for interview scheduling
- **Company Branding**: Customize company name for email templates

### 👤 Candidate Analysis Page
- **Resume Upload**: PDF resume processing with text extraction
- **AI-Powered Analysis**: Intelligent resume screening against job requirements
- **Role-Specific Evaluation**: Predefined requirements for AI/ML, Frontend, and Backend roles
- **Automated Communication**: Instant email notifications to candidates
- **Real-time Feedback**: Detailed analysis results and recommendations

### 📅 Interview Scheduling Page
- **Selected Candidates**: View all candidates who passed the initial screening
- **Email Template Selection**: Choose from pre-built email templates
- **Mail Preview & Editing**: Preview and edit emails before sending
- **One-Click Scheduling**: Automated interview scheduling with Zoom integration
- **Calendar Management**: Track scheduled interviews and candidate status
- **Email Confirmations**: Automatic interview confirmation emails

### 📊 Dashboard Page
- **Recruitment Analytics**: Visual statistics and metrics
- **Status Tracking**: Real-time overview of candidate pipeline
- **Performance Insights**: Success rates and role distribution
- **Recent Activity**: Timeline of recruitment activities

## 🚀 Pro Features

### 📧 Email Template System
- **Pre-built Templates**: Interview invitation, confirmation, and reminder templates
- **Template Selection**: Choose appropriate template for each candidate
- **Live Preview**: Real-time email preview with candidate data
- **Template Editing**: Edit templates on-the-fly before sending
- **Custom Variables**: Dynamic placeholders for candidate and company data

### 🔔 Notification System
- **Real-time Notifications**: Toast notifications for all actions
- **Success/Error Alerts**: Visual feedback for user actions
- **Notification History**: Track recent system notifications
- **Animated Alerts**: Smooth slide-in animations

### 📊 Advanced Analytics
- **Enhanced Charts**: Interactive pie charts and bar graphs
- **Score Tracking**: AI analysis scores for each candidate
- **Performance Metrics**: Success rates and conversion tracking
- **Role Distribution**: Visual breakdown by job positions
- **Timeline View**: Recent activity with detailed information

### 📤 Export & Reporting
- **CSV Export**: Export candidates and interviews data
- **Report Generation**: Automated recruitment reports
- **Data Download**: Download data in multiple formats
- **Report Templates**: Pre-formatted report structures

### 🎨 Premium UI Elements
- **Gradient Backgrounds**: Multi-color gradients with texture overlays
- **Hover Effects**: Interactive card animations
- **Progress Bars**: Visual progress tracking
- **Status Indicators**: Enhanced status badges with gradients
- **Custom Typography**: Inter font family for modern look
- **Responsive Design**: Optimized for all screen sizes

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- OpenRouter API key (get from https://openrouter.ai)
- Gmail account with app password
- Zoom account (optional, for interview scheduling)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_recruitment_agents_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   # Option 1: Use the launcher script
   python run_recruitment_system.py
   
   # Option 2: Run directly
   streamlit run ai_recruitment_system_pro.py
   ```

### Configuration

1. **OpenRouter Setup**
   - Visit https://openrouter.ai
   - Create an account and get your API key
   - Enter the API key in the Configuration page

2. **Gmail Setup**
   - Enable 2-factor authentication on your Gmail account
   - Generate an app password (not your regular password)
   - Use your Gmail address and app password in the Email Settings

3. **Zoom Setup (Optional)**
   - Create a Zoom app in the Zoom Marketplace
   - Get your Account ID, Client ID, and Client Secret
   - Enter these credentials for interview scheduling

## 🎨 UI/UX Improvements

### Premium Design
- **Advanced Gradients**: Multi-color gradient backgrounds with texture overlays
- **Enhanced Cards**: Hover effects and shadow animations
- **Status Badges**: Gradient status indicators with animations
- **Step Indicators**: Interactive progress tracking with icons
- **Responsive Design**: Optimized for desktop, tablet, and mobile
- **Custom Fonts**: Inter font family for modern typography
- **Smooth Animations**: CSS transitions and hover effects

### Enhanced User Experience
- **Multi-Page Flow**: Logical progression through recruitment steps
- **Real-time Feedback**: Instant status updates and notifications
- **Data Persistence**: Session-based data storage
- **Visual Analytics**: Charts and graphs for recruitment insights
- **Intuitive Navigation**: Sidebar navigation with quick stats

### Improved Functionality
- **Batch Processing**: Handle multiple candidates efficiently
- **Data Visualization**: Interactive charts and metrics
- **Error Handling**: Graceful error management with user-friendly messages
- **Progress Tracking**: Visual indicators for each step
- **Quick Actions**: One-click operations for common tasks

## 📋 Usage Flow

1. **Configuration** → Set up API keys and email settings
2. **Candidate Analysis** → Upload resumes and analyze candidates
3. **Interview Scheduling** → Schedule interviews for selected candidates
4. **Dashboard** → Monitor recruitment progress and analytics

## 🔧 Technical Architecture

### Core Components
- **Resume Analyzer**: AI-powered resume screening using OpenRouter
- **Email Agent**: Automated candidate communication via SMTP
- **Scheduler Agent**: Interview scheduling with Zoom integration
- **Data Management**: Session-based storage for candidates and interviews

### Technologies Used
- **Streamlit**: Web application framework
- **OpenRouter**: AI model access
- **PyPDF2**: PDF text extraction
- **Plotly**: Data visualization
- **Pandas**: Data manipulation
- **SMTP**: Email communication
- **Zoom API**: Interview scheduling

## 🎯 Role Requirements

The system includes predefined requirements for three key roles:

### AI/ML Engineer
- Python, PyTorch/TensorFlow
- Machine Learning algorithms and frameworks
- Deep Learning and Neural Networks
- Data preprocessing and analysis
- MLOps and model deployment
- RAG, LLM, Finetuning and Prompt Engineering

### Frontend Engineer
- React/Vue.js/Angular
- HTML5, CSS3, JavaScript/TypeScript
- Responsive design
- State management
- Frontend testing

### Backend Engineer
- Python/Java/Node.js
- REST APIs
- Database design and management
- System architecture
- Cloud services (AWS/GCP/Azure)
- Kubernetes, Docker, CI/CD

## 🔒 Security Features

- **Password Fields**: Sensitive data input with password masking
- **Session Management**: Secure session state handling
- **Error Sanitization**: ASCII-only text processing to prevent encoding issues
- **API Key Protection**: Secure storage of API credentials

## 📈 Analytics & Reporting

- **Candidate Statistics**: Total, selected, and rejected counts
- **Success Rates**: Percentage-based metrics
- **Role Distribution**: Visual breakdown by job positions
- **Timeline Tracking**: Recent activity monitoring
- **Performance Insights**: Recruitment efficiency metrics

## 🚀 Future Enhancements

- **Database Integration**: Persistent data storage
- **Advanced Analytics**: Machine learning insights
- **Multi-language Support**: Internationalization
- **API Integration**: REST API for external systems
- **Mobile App**: Native mobile application
- **Advanced Scheduling**: Calendar integration and conflict resolution
