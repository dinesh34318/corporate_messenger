import streamlit as st
import sys, os
from datetime import date, timedelta
import calendar
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.styles import inject_css
from backend.database import save_event, get_events_for_date, get_all_events_for_user, get_user_tasks


def show_calendar():
    inject_css()
    user = st.session_state.get("user", {})
    if not user:
        return

    st.markdown("## 📅 Calendar")

    # Month navigation
    today = date.today()
    if "cal_year" not in st.session_state:
        st.session_state["cal_year"] = today.year
    if "cal_month" not in st.session_state:
        st.session_state["cal_month"] = today.month
    if "cal_selected" not in st.session_state:
        st.session_state["cal_selected"] = today.isoformat()

    cy = st.session_state["cal_year"]
    cm = st.session_state["cal_month"]

    # Get all events and tasks for dot indicators
    try:
        all_events = get_all_events_for_user(user["login_id"])
        all_tasks = get_user_tasks(user["login_id"])
    except Exception:
        all_events, all_tasks = [], []

    event_dates = {e["date"] for e in all_events}
    task_dates = set()
    for t in all_tasks:
        due = t.get("due_date")
        if due:
            task_dates.add(due.date().isoformat())

    # Header
    col_prev, col_title, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("◀ Prev", use_container_width=True):
            if cm == 1:
                st.session_state["cal_year"] -= 1
                st.session_state["cal_month"] = 12
            else:
                st.session_state["cal_month"] -= 1
            st.rerun()
    with col_title:
        month_name = calendar.month_name[cm]
        st.markdown(f"""
        <div style="text-align:center;font-size:1.3rem;font-weight:700;
                    color:#e6edf3;padding:0.4rem;">{month_name} {cy}</div>
        """, unsafe_allow_html=True)
    with col_next:
        if st.button("Next ▶", use_container_width=True):
            if cm == 12:
                st.session_state["cal_year"] += 1
                st.session_state["cal_month"] = 1
            else:
                st.session_state["cal_month"] += 1
            st.rerun()

    # Calendar grid
    cal = calendar.monthcalendar(cy, cm)
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Day headers
    day_cols = st.columns(7)
    for i, d in enumerate(day_names):
        with day_cols[i]:
            color = "#f85149" if d in ("Sat", "Sun") else "#8b949e"
            st.markdown(f"""
            <div style="text-align:center;font-size:0.75rem;font-weight:600;
                        color:{color};padding:4px 0;border-bottom:1px solid #30363d;">
                {d}
            </div>
            """, unsafe_allow_html=True)

    # Day cells
    selected = st.session_state.get("cal_selected", today.isoformat())
    for week in cal:
        week_cols = st.columns(7)
        for i, day in enumerate(week):
            with week_cols[i]:
                if day == 0:
                    st.markdown("<div style='height:44px;'></div>", unsafe_allow_html=True)
                    continue
                d_str = f"{cy}-{cm:02d}-{day:02d}"
                is_today = (d_str == today.isoformat())
                is_selected = (d_str == selected)
                has_event = d_str in event_dates
                has_task = d_str in task_dates
                is_weekend = (i >= 5)

                label = str(day)
                if has_event or has_task or is_today:
                    indicators = []
                    if has_event: indicators.append(" ")
                    if has_task: indicators.append(" ")
                    if is_today: indicators.append(" ")
                    label = f"{day}{''.join(indicators)}"
                if is_selected: label = f"[{label}]"

                if st.button(label, key=f"day_{d_str}", use_container_width=True):
                    st.session_state["cal_selected"] = d_str
                    st.rerun()

    st.markdown("<hr style='border-color:#30363d;margin:1.5rem 0;'>", unsafe_allow_html=True)

    # Selected day detail
    sel_date = st.session_state.get("cal_selected", today.isoformat())
    st.markdown(f"### 📆 {sel_date}")

    col_events, col_add = st.columns([1.5, 1])

    with col_events:
        # Tasks due on this day
        day_tasks = [t for t in all_tasks if t.get("due_date") and t["due_date"].date().isoformat() == sel_date]
        if day_tasks:
            st.markdown("**📋 Tasks due today:**")
            for t in day_tasks:
                badge = "badge-meeting" if t.get("task_type") == "meeting" else "badge-action"
                st.markdown(f"""
                <div class="corp-card" style="padding:0.6rem 1rem;margin-bottom:6px;">
                    <span class="task-badge {badge}">{t.get('task_type','task').upper()}</span>
                    <span style="color:#e6edf3;margin-left:8px;font-size:0.88rem;">{t['title']}</span>
                    <div style="color:#484f58;font-size:0.75rem;margin-top:3px;">
                        From: {t.get('assigned_by','')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Manual events
        try:
            day_events = get_events_for_date(user["login_id"], sel_date)
        except Exception:
            day_events = []

        if day_events:
            st.markdown("**📌 My Events:**")
            for e in day_events:
                st.markdown(f"""
                <div class="corp-card" style="padding:0.6rem 1rem;margin-bottom:6px;">
                    <div style="font-weight:600;color:#e6edf3;">{e.get('title','')}</div>
                    <div style="color:#8b949e;font-size:0.82rem;margin-top:4px;">{e.get('note','')}</div>
                </div>
                """, unsafe_allow_html=True)

        if not day_tasks and not day_events:
            st.markdown("<div style='color:#484f58;font-size:0.85rem;'>No tasks or events for this day.</div>",
                        unsafe_allow_html=True)

    with col_add:
        st.markdown("**➕ Add Event**")
        with st.form("add_event_form"):
            ev_title = st.text_input("Event Title", placeholder="e.g. Team standup")
            ev_note = st.text_area("Note (optional)", placeholder="Additional details…", height=80)
            if st.form_submit_button("Save Event", use_container_width=True):
                if ev_title.strip():
                    try:
                        save_event(user["login_id"], sel_date, ev_title.strip(), ev_note.strip())
                        st.success("✅ Event saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.error("Event title is required.")

    st.markdown("""
    <div style="margin-top:1rem;font-size:0.75rem;color:#484f58;">
        🟢 Green dot = saved event &nbsp;|&nbsp; 🔴 Red dot = task due
    </div>
    """, unsafe_allow_html=True)
