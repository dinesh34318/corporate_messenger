import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.styles import inject_css
from backend.auth import register_user, DEPARTMENTS, ROLES
from backend.database import get_all_users, get_users_by_department, get_tasks_assigned_by


def show_admin_dashboard():
    inject_css()
    user = st.session_state.get("user", {})
    if not user or user.get("role") not in ("Admin", "Manager"):
        st.session_state["page"] = "login"
        st.rerun()

    # ── Sidebar navigation ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:1rem 0 1.5rem;">
            <div style="font-size:1.1rem;font-weight:700;color:#e6edf3;">{user.get('name','Admin')}</div>
            <div style="font-size:0.78rem;color:#8b949e;">{user.get('role')} · {user.get('department')}</div>
            <div style="font-size:0.72rem;color:#484f58;font-family:'JetBrains Mono',monospace;margin-top:2px;">{user.get('login_id')}</div>
        </div>
        <hr style="border-color:#30363d;margin-bottom:1rem;">
        """, unsafe_allow_html=True)

        nav_options = ["🏠 Overview", "👤 Register User", "📋 Manage Users",
                       "💬 Messages", "📅 Calendar", "🔑 Change Password"]
        nav = st.radio("Navigation", nav_options, label_visibility="collapsed")

        st.markdown("<hr style='border-color:#30363d;'>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.session_state["page"] = "home"
            st.rerun()

    # ── Overview ────────────────────────────────────────────────────────
    if nav == "🏠 Overview":
        st.markdown("## 🏠 Admin Overview")

        try:
            all_users = get_all_users()
            total = len(all_users)
            admins = sum(1 for u in all_users if u.get("role") == "Admin")
            managers = sum(1 for u in all_users if u.get("role") == "Manager")
            regular = total - admins - managers
            my_tasks = get_tasks_assigned_by(user["login_id"])
        except Exception as e:
            st.error(f"Database error: {e}")
            return

        c1, c2, c3, c4 = st.columns(4)
        for col, label, val, color in [
            (c1, "Total Users", total, "#2d96ff"),
            (c2, "Admins", admins, "#f85149"),
            (c3, "Managers", managers, "#d29922"),
            (c4, "Tasks Created", len(my_tasks), "#3fb950"),
        ]:
            with col:
                st.markdown(f"""
                <div class="corp-card" style="text-align:center;">
                    <div style="font-size:2rem;font-weight:700;color:{color};">{val}</div>
                    <div style="color:#8b949e;font-size:0.85rem;margin-top:4px;">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 👥 All Users")

        dept_filter = st.selectbox("Filter by Department", ["All"] + list(DEPARTMENTS.values()))
        filtered = [u for u in all_users if dept_filter == "All" or u.get("department") == dept_filter]

        for u in filtered:
            role_color = {"Admin": "#f85149", "Manager": "#d29922", "User": "#3fb950"}.get(u.get("role","User"), "#8b949e")
            pw_status = "✅ Changed" if u.get("password_changed") else "⚠️ Default"
            st.markdown(f"""
            <div class="corp-card" style="display:flex;align-items:center;justify-content:space-between;padding:0.9rem 1.2rem;">
                <div>
                    <span style="font-weight:600;color:#e6edf3;">{u.get('name','')}</span>
                    <span style="font-family:monospace;color:#8b949e;font-size:0.8rem;margin-left:8px;">
                        {u.get('login_id','')}
                    </span>
                </div>
                <div style="display:flex;gap:12px;align-items:center;">
                    <span style="background:rgba(0,0,0,0.3);border-radius:20px;padding:2px 10px;
                                 color:{role_color};font-size:0.78rem;font-weight:600;">
                        {u.get('role','')}
                    </span>
                    <span style="color:#8b949e;font-size:0.78rem;">{u.get('department','')}</span>
                    <span style="color:#8b949e;font-size:0.75rem;">{pw_status}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Register User ────────────────────────────────────────────────────
    elif nav == "👤 Register User":
        st.markdown("## 👤 Register New User")
        st.markdown("""
        <div class="alert-info">
            ℹ️ Fill in the details below. A Login ID and default password will be auto-generated.
            Share these credentials securely with the new employee.
        </div>
        """, unsafe_allow_html=True)

        with st.form("register_form"):
            name = st.text_input("Full Name", placeholder="e.g. Dinesh Kumar")
            dept = st.selectbox("Department", list(DEPARTMENTS.values()))
            role = st.selectbox("Role", ["User", "Manager", "Admin"])
            submitted = st.form_submit_button("➕ Create Account", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("Name is required.")
            else:
                login_id, plain_pw, err = register_user(
                    name=name.strip(),
                    department=dept,
                    role=role,
                    created_by=user["login_id"]
                )
                if err:
                    st.error(f"Error: {err}")
                else:
                    st.success(f"✅ Account created successfully!")
                    st.markdown(f"""
                    <div style="background:#0d1117;border:1px solid #3fb950;border-radius:12px;
                                padding:1.5rem;margin-top:1rem;">
                        <div style="color:#3fb950;font-weight:700;font-size:1rem;margin-bottom:1rem;">
                            🔐 Credentials to share with {name}
                        </div>
                        <div style="margin-bottom:0.6rem;">
                            <span style="color:#8b949e;font-size:0.82rem;">LOGIN ID</span><br>
                            <span style="font-family:monospace;font-size:1.1rem;color:#e6edf3;
                                         background:#161b22;padding:4px 10px;border-radius:6px;">
                                {login_id}
                            </span>
                        </div>
                        <div>
                            <span style="color:#8b949e;font-size:0.82rem;">DEFAULT PASSWORD</span><br>
                            <span style="font-family:monospace;font-size:1.1rem;color:#e6edf3;
                                         background:#161b22;padding:4px 10px;border-radius:6px;">
                                {plain_pw}
                            </span>
                        </div>
                        <div style="margin-top:1rem;color:#d29922;font-size:0.8rem;">
                            ⚠️ The user will be forced to change this password on first login.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── Manage Users ─────────────────────────────────────────────────────
    elif nav == "📋 Manage Users":
        st.markdown("## 📋 Manage Users")
        try:
            all_users = get_all_users(exclude_login=user["login_id"])
        except Exception as e:
            st.error(str(e))
            return

        search = st.text_input("🔍 Search by name or login ID", placeholder="Type to filter...")
        filtered = [
            u for u in all_users
            if not search or search.lower() in u.get("name","").lower()
            or search.lower() in u.get("login_id","").lower()
        ]

        if not filtered:
            st.info("No users found.")
        for u in filtered:
            with st.expander(f"{u.get('name','')}  ·  {u.get('login_id','')}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Department:** {u.get('department','')}")
                    st.markdown(f"**Role:** {u.get('role','')}")
                with c2:
                    st.markdown(f"**Password Changed:** {'Yes ✅' if u.get('password_changed') else 'No ⚠️'}")
                    st.markdown(f"**Active:** {'Yes' if u.get('is_active', True) else 'No ❌'}")

                tasks = get_tasks_assigned_by(user["login_id"])
                user_tasks = [t for t in tasks if t.get("assigned_to") == u.get("login_id")]
                if user_tasks:
                    st.markdown(f"**Tasks assigned to this user:** {len(user_tasks)}")

    # ── Messages ─────────────────────────────────────────────────────────
    elif nav == "💬 Messages":
        from frontend.pages.messages import show_messages
        show_messages()

    # ── Calendar ─────────────────────────────────────────────────────────
    elif nav == "📅 Calendar":
        from frontend.pages.calendar import show_calendar
        show_calendar()

    # ── Change Password ──────────────────────────────────────────────────
    elif nav == "🔑 Change Password":
        from frontend.pages.change_password import show_change_password
        show_change_password()
