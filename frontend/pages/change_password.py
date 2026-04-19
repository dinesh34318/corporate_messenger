import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.styles import inject_css
from backend.auth import change_password


def show_change_password():
    inject_css()
    user = st.session_state.get("user", {})
    if not user:
        st.session_state["page"] = "login"
        st.rerun()

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div style="text-align:center; padding:2rem 0 1.5rem;">
            <div style="font-size:1.8rem; font-weight:700; color:#e6edf3;">🔑 Change Password</div>
            <div style="color:#8b949e; font-size:0.85rem; margin-top:0.4rem;">
                Keep your account secure with a strong password
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not user.get("password_changed"):
            st.markdown("""
            <div class="alert-warn">
                ⚠️ You must change your default password before using the app.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("change_pw_form"):
            current = st.text_input("Current Password", type="password")
            new_pw  = st.text_input("New Password", type="password",
                                     help="Min 8 chars, 1 uppercase, 1 digit, 1 special character")
            confirm = st.text_input("Confirm New Password", type="password")
            submitted = st.form_submit_button("Update Password", use_container_width=True)

        if submitted:
            if not current or not new_pw or not confirm:
                st.error("All fields are required.")
            elif new_pw != confirm:
                st.error("New passwords do not match.")
            else:
                ok, msg = change_password(user["login_id"], current, new_pw)
                if ok:
                    st.success("✅ " + msg)
                    st.session_state["user"]["password_changed"] = True
                    role = user.get("role", "User")
                    target = "admin_dashboard" if role == "Admin" else "user_dashboard"
                    import time; time.sleep(1)
                    st.session_state["page"] = target
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("""
        <div style="margin-top:1rem; padding:0.8rem 1rem; background:rgba(45,150,255,0.06);
                    border:1px solid rgba(45,150,255,0.15); border-radius:10px;
                    color:#8b949e; font-size:0.8rem;">
            Password requirements: at least 8 characters, 1 uppercase letter, 1 number, 1 special character.
        </div>
        """, unsafe_allow_html=True)

        # Theme Settings
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### <div style='color:#e6edf3;'>Theme Settings</div>", unsafe_allow_html=True)
        
        current_theme = st.session_state.get("theme", "dark")
        theme_options = ["dark", "light", "blue"]
        selected_theme = st.selectbox("Choose Theme", theme_options, index=theme_options.index(current_theme))
        
        if st.button("Apply Theme", use_container_width=True):
            st.session_state["theme"] = selected_theme
            st.success(f"Theme changed to {selected_theme}!")
            st.rerun()

        if user.get("password_changed"):
            st.markdown("<br>", unsafe_allow_html=True)
            role = user.get("role", "User")
            target = "admin_dashboard" if role == "Admin" else "user_dashboard"
            if st.button("<- Back to Dashboard", use_container_width=True):
                st.session_state["page"] = target
                st.rerun()
