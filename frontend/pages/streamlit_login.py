import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.styles import inject_css
from backend.auth import login_user


def show_login():
    inject_css()

    # Centre the login card
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div style="text-align:center; padding: 2rem 0 1.5rem;">
            <div style="font-size:2rem; font-weight:700; color:#ff6b35;">
                💬 Sign In
            </div>
            <div style="color:#e6edf3; font-size:0.9rem; margin-top:0.4rem;">
                Enter your credentials provided by your administrator
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Add custom CSS for login form
        st.markdown("""
        <style>
            .stForm {
                background: rgba(45, 150, 255, 0.05);
                border: 1px solid rgba(45, 150, 255, 0.2);
                border-radius: 12px;
                padding: 1.5rem;
                margin-top: 1rem;
            }
            .stForm input {
                background: #1c2128 !important;
                border: 1px solid #30363d !important;
                color: #e6edf3 !important;
                border-radius: 8px;
                padding: 0.75rem;
            }
            .stForm button {
                background: linear-gradient(135deg, #ff6b35, #e55100) !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                padding: 0.75rem 1.5rem !important;
                transition: all 0.2s ease !important;
            }
            .stForm button:hover {
                background: linear-gradient(135deg, #e55100, #ff6b35) !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 6px 20px rgba(255, 107, 53, 0.3) !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            login_id = st.text_input("Login ID", placeholder="e.g. devusr000001")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if not login_id or not password:
                st.error("Please enter both Login ID and password.")
            else:
                user, err = login_user(login_id.strip(), password)
                if err:
                    st.error(err)
                else:
                    # Store session
                    st.session_state["user"] = {
                        "login_id": user["login_id"],
                        "name": user.get("name", ""),
                        "role": user.get("role", "User"),
                        "department": user.get("department", ""),
                        "password_changed": user.get("password_changed", False),
                    }
                    # Force password change on first login
                    if not user.get("password_changed", False):
                        st.session_state["page"] = "change_password"
                        st.warning("🔑 Please change your default password before continuing.")
                        st.rerun()
                    elif user.get("role") == "Admin":
                        st.session_state["page"] = "admin_dashboard"
                        st.rerun()
                    else:
                        st.session_state["page"] = "user_dashboard"
                        st.rerun()

        st.markdown("""
        <div style="margin-top:1.5rem; padding:1rem; background:rgba(45,150,255,0.08); 
                    border:1px solid rgba(45,150,255,0.2); border-radius:10px;">
            <div style="color:#e6edf3; font-size:0.8rem; line-height:1.7;">
                <b style="color:#58aeff;">Login ID format:</b><br>
                &nbsp;• Users: <code style="color:#ffffff;">devusr000001</code> &nbsp;(dept + role + sequence)<br>
                &nbsp;• Admins: <code style="color:#ffffff;">devadm000000</code><br>
                &nbsp;• Default password = your Login ID (change on first login)
            </div>
        </div>
        """, unsafe_allow_html=True)

    _, c2, _ = st.columns([2, 1, 2])
    with c2:
        if st.button("← Back to Home", use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()
