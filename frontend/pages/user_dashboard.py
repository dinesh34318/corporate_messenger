import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.styles import inject_css
from backend.database import get_user_tasks, update_task_status, mark_task_seen, get_unseen_task_count


def show_user_dashboard():
    inject_css()
    user = st.session_state.get("user", {})
    if not user:
        st.session_state["page"] = "login"
        st.rerun()

    # ── Sidebar navigation ──────────────────────────────────────────────
    with st.sidebar:
        try:
            unseen = get_unseen_task_count(user["login_id"])
        except Exception:
            unseen = 0

        task_badge = f" 🔴 {unseen}" if unseen > 0 else ""
        st.markdown(f"""
        <div style="padding:1rem 0 1.5rem;">
            <div style="font-size:1.1rem;font-weight:700;color:#e6edf3;">{user.get('name','User')}</div>
            <div style="font-size:0.78rem;color:#8b949e;">{user.get('role')} · {user.get('department')}</div>
            <div style="font-size:0.72rem;color:#484f58;font-family:'JetBrains Mono',monospace;margin-top:2px;">{user.get('login_id')}</div>
        </div>
        <hr style="border-color:#30363d;margin-bottom:1rem;">
        """, unsafe_allow_html=True)

        nav_options = [
            "🏠 Dashboard",
            f"📋 My Tasks{task_badge}",
            "💬 Messages",
            "🤖 AI Assistant",
            "📅 Calendar",
            "🔑 Change Password",
        ]
        nav = st.radio("Navigation", nav_options, label_visibility="collapsed")

        st.markdown("<hr style='border-color:#30363d;'>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.session_state["page"] = "home"
            st.rerun()

    # ── Dashboard Home ───────────────────────────────────────────────────
    if nav == "🏠 Dashboard":
        st.markdown(f"## 👋 Welcome, {user.get('name', 'User')}!")

        try:
            tasks = get_user_tasks(user["login_id"])
            pending = [t for t in tasks if t.get("status") == "pending"]
            done = [t for t in tasks if t.get("status") == "done"]
            meetings = [t for t in pending if t.get("task_type") == "meeting"]
        except Exception as e:
            st.error(str(e))
            tasks, pending, done, meetings = [], [], [], []

        c1, c2, c3, c4 = st.columns(4)
        for col, label, val, color in [
            (c1, "Total Tasks", len(tasks), "#2d96ff"),
            (c2, "Pending", len(pending), "#d29922"),
            (c3, "Meetings", len(meetings), "#3fb950"),
            (c4, "Completed", len(done), "#8b949e"),
        ]:
            with col:
                st.markdown(f"""
                <div class="corp-card" style="text-align:center;">
                    <div style="font-size:2rem;font-weight:700;color:{color};">{val}</div>
                    <div style="color:#8b949e;font-size:0.85rem;margin-top:4px;">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        if pending:
            st.markdown("### 🔥 Pending Tasks")
            for t in pending[:5]:
                due = t.get("due_date")
                due_str = due.strftime("%b %d, %H:%M") if due else "No deadline"
                badge_cls = "badge-meeting" if t.get("task_type") == "meeting" else "badge-action"
                st.markdown(f"""
                <div class="corp-card" style="padding:0.9rem 1.2rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span class="task-badge {badge_cls}">{t.get('task_type','task').upper()}</span>
                            <span style="font-weight:600;color:#e6edf3;margin-left:8px;">{t['title']}</span>
                        </div>
                        <div style="color:#8b949e;font-size:0.78rem;">📅 {due_str}</div>
                    </div>
                    <div style="color:#8b949e;font-size:0.82rem;margin-top:6px;">
                        From: {t.get('assigned_by','')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # AI summary
        st.markdown("### 🤖 AI Task Summary")
        if st.button("Generate AI Summary of My Tasks"):
            with st.spinner("Analysing your workload..."):
                try:
                    from backend.rag_assistant import summarise_tasks_for_user
                    summary = summarise_tasks_for_user(user["login_id"], pending)
                    st.markdown(f"""
                    <div class="corp-card" style="border-color:#2d96ff;">
                        <div style="color:#58aeff;font-size:0.8rem;font-weight:600;margin-bottom:0.5rem;">
                            🤖 AI SUMMARY
                        </div>
                        <div style="color:#e6edf3;line-height:1.7;">{summary}</div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"AI summary unavailable: {e}")

    # ── My Tasks ─────────────────────────────────────────────────────────
    elif "My Tasks" in nav:
        st.markdown("## 📋 My Tasks")
        try:
            tasks = get_user_tasks(user["login_id"])
            # Mark all as seen
            for t in tasks:
                if not t.get("seen"):
                    try:
                        mark_task_seen(t["_id"])
                    except Exception:
                        pass
        except Exception as e:
            st.error(str(e))
            tasks = []

        tab_pending, tab_done, tab_all = st.tabs(["⏳ Pending", "✅ Done", "📂 All"])

        def render_tasks(task_list, show_complete_btn=True, tab_prefix=""):
            if not task_list:
                st.info("No tasks here.")
                return
            for t in task_list:
                due = t.get("due_date")
                due_str = due.strftime("%b %d, %Y %H:%M") if due else "No deadline"
                badge_cls = "badge-meeting" if t.get("task_type") == "meeting" else "badge-action"
                status_cls = "badge-done" if t.get("status") == "done" else "badge-pending"

                expander_label = f"{t['title']}   ·   {due_str}"
                with st.expander(expander_label):
                    # Apply dark color to the expander content
                    st.markdown(f"""
                    <style>
                        div[data-testid="stExpander"] > div > div > div > div:first-child {{
                            color: #000000 !important;
                            font-weight: 600 !important;
                        }}
                    </style>
                    """, unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style="margin-bottom:0.8rem;">
                        <span class="task-badge {badge_cls}">{t.get('task_type','task').upper()}</span>
                        &nbsp;
                        <span class="task-badge {status_cls}">{t.get('status','pending').upper()}</span>
                    </div>
                    <div style="color:#8b949e;font-size:0.82rem;line-height:1.6;
                                white-space:pre-line;">{t.get('description','')}</div>
                    <div style="margin-top:0.8rem;color:#484f58;font-size:0.75rem;">
                        Assigned by: {t.get('assigned_by','')} &nbsp;|&nbsp; Created: {str(t.get('created_at',''))[:16]}
                    </div>
                    """, unsafe_allow_html=True)

                    if show_complete_btn and t.get("status") == "pending":
                        if st.button(" Mark as Done", key=f"{tab_prefix}_done_{t['_id']}"):
                            update_task_status(t["_id"], "done")
                            st.success("Marked as done!")
                            st.rerun()
                    elif t.get("status") == "done":
                        if st.button(" Re-open", key=f"{tab_prefix}_reopen_{t['_id']}"):
                            update_task_status(t["_id"], "pending")
                            st.rerun()

        with tab_pending:
            render_tasks([t for t in tasks if t.get("status") == "pending"], tab_prefix="pending")
        with tab_done:
            render_tasks([t for t in tasks if t.get("status") == "done"], show_complete_btn=False, tab_prefix="done")
        with tab_all:
            render_tasks(tasks, tab_prefix="all")

    # ── Messages ─────────────────────────────────────────────────────────
    elif nav == "💬 Messages":
        from frontend.pages.messages import show_messages
        show_messages()

    # ── AI Assistant ─────────────────────────────────────────────────────
    elif nav == "🤖 AI Assistant":
        from frontend.pages.ai_assistant import show_ai_assistant
        show_ai_assistant()

    # ── Calendar ─────────────────────────────────────────────────────────
    elif nav == "📅 Calendar":
        from frontend.pages.calendar import show_calendar
        show_calendar()

    # ── Change Password ──────────────────────────────────────────────────
    elif nav == "🔑 Change Password":
        from frontend.pages.change_password import show_change_password
        show_change_password()
