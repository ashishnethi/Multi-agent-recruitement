#!/usr/bin/env python3
"""
AI Recruitment System Pro Launcher
Run this script to start the enhanced AI recruitment system
"""

import subprocess
import sys
import os


def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    try:
        import streamlit  # noqa: F401
        import pandas  # noqa: F401
        import plotly  # noqa: F401
        import PyPDF2  # noqa: F401
        from streamlit_pdf_viewer import pdf_viewer  # noqa: F401
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False


def main() -> None:
    """Main launcher function."""
    print("🎯 AI Recruitment System Pro Launcher")
    print("=" * 50)
    print("✨ Enhanced UI/UX with Mail Preview & Editing")
    print("📊 Advanced Analytics & Export Features")
    print("🔔 Notifications & Improved Flow")
    print("=" * 50)

    app_file = "ai_recruitment_system_pro.py"
    if not os.path.exists(app_file):
        print(f"❌ {app_file} not found in current directory")
        print("Please run this script from the project root directory")
        return

    if not check_dependencies():
        return

    print("🚀 Starting AI Recruitment System Pro...")
    print("📱 The application will open in your default web browser")
    print("🔗 If it doesn't open automatically, go to: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    print("=" * 50)

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                app_file,
                "--server.port",
                "8501",
                "--server.address",
                "localhost",
            ],
            check=False,
        )
    except KeyboardInterrupt:
        print("\n👋 AI Recruitment System Pro stopped")
    except Exception as e:
        print(f"❌ Error starting application: {e}")


if __name__ == "__main__":
    main()



