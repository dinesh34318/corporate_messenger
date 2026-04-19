import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from frontend.styles import inject_css


def show_home():
    inject_css()

    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem 2rem;">
        <div style="font-size:3.5rem; font-weight:800; 
                    background: linear-gradient(135deg, #2d96ff, #58aeff, #a8d5ff);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                    letter-spacing:-0.03em; margin-bottom:0.5rem;">
            Corporate<br>Smart Messenger
        </div>
        <div style="font-size:1.1rem; color:#8b949e; max-width:520px; margin:0 auto 2.5rem; line-height:1.7;">
            AI-powered workplace communication with intelligent task scheduling, 
            RAG-based chat analysis, and role-based access control.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    cols = st.columns(3)
    features = [
        ("🔐", "Role-Based Access", "Admins create and manage user credentials. Full separation between admin and user roles."),
        ("🤖", "AI Task Detection", "Messages about meetings and deadlines are automatically converted into scheduled tasks using RAG."),
        ("💬", "Smart Messaging", "Direct and group chat with real-time refresh, read receipts, and chat history analysis."),
        ("📅", "Auto Scheduling", "AI detects action items in every message and assigns tasks to the right team members."),
        ("🔍", "RAG Assistant", "Ask natural language questions about your team's chat history and get intelligent answers."),
        ("📊", "Admin Dashboard", "Full visibility of all users, departments, and team activities from one control panel."),
    ]
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="nav-card">
                <div class="nav-card-icon">{icon}</div>
                <div class="nav-card-title">{title}</div>
                <div class="nav-card-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🚀  Sign In", use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()

    st.markdown("""
    <div style="text-align:center; margin-top:3rem; color:#484f58; font-size:0.8rem;">
        Corporate Smart Messenger &nbsp;|&nbsp; Powered by Claude AI &amp; RAG
    </div>
    """, unsafe_allow_html=True)
