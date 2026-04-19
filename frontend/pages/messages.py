import streamlit as st
import sys, os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.styles import inject_css
from backend.database import (
    get_user_conversations, get_or_create_direct_conversation,
    create_group_conversation, get_messages, send_message,
    get_all_users, get_conversation, create_task
)
from backend.rag_extractor import extract_task_from_message
from backend.rag_indexer import index_messages


def _process_message_for_tasks(msg_id, content, sender, sender_name, conv_id, participants):
    """Index message and create tasks if actionable."""
    fake_msg = {
        "_id": msg_id,
        "content": content,
        "sender": sender,
        "sender_name": sender_name,
        "conversation_id": conv_id,
        "timestamp": datetime.utcnow(),
        "indexed": False,
    }
    try:
        index_messages([fake_msg])
    except Exception:
        pass

    tasks = extract_task_from_message(
        text=content,
        sender=sender,
        sender_name=sender_name,
        conversation_id=conv_id,
        message_id=msg_id,
        participants=participants,
    )
    for t in tasks:
        try:
            create_task(**t)
        except Exception:
            pass
    return len(tasks)


def show_messages():
    inject_css()
    user = st.session_state.get("user", {})
    if not user:
        return

    st.markdown("## 💬 Messages")

    # ── New conversation panel ───────────────────────────────────────────
    with st.expander("➕ New Conversation"):
        tab_direct, tab_group = st.tabs(["Direct Chat", "Group Chat"])

        with tab_direct:
            try:
                all_users = get_all_users(exclude_login=user["login_id"])
            except Exception as e:
                st.error(str(e))
                all_users = []
            user_options = {f"{u['name']} ({u['login_id']})": u["login_id"] for u in all_users}
            selected_label = st.selectbox("Select user", list(user_options.keys()), key="dm_select")
            if st.button("Start Direct Chat"):
                target_login = user_options[selected_label]
                try:
                    conv_id = get_or_create_direct_conversation(user["login_id"], target_login)
                    st.session_state["active_conv"] = conv_id
                    st.success("Chat opened!")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        with tab_group:
            group_name = st.text_input("Group Name", key="grp_name")
            try:
                all_users2 = get_all_users(exclude_login=user["login_id"])
            except Exception:
                all_users2 = []
            user_opts2 = {f"{u['name']} ({u['login_id']})": u["login_id"] for u in all_users2}
            selected_members = st.multiselect("Add members", list(user_opts2.keys()), key="grp_members")
            if st.button("Create Group"):
                if not group_name.strip():
                    st.error("Enter a group name.")
                elif not selected_members:
                    st.error("Select at least one member.")
                else:
                    members = [user_opts2[m] for m in selected_members] + [user["login_id"]]
                    try:
                        conv_id = create_group_conversation(group_name.strip(), members, user["login_id"])
                        st.session_state["active_conv"] = conv_id
                        st.success(f"Group '{group_name}' created!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    # ── Layout: conversation list + chat window ──────────────────────────
    col_list, col_chat = st.columns([1, 2.5])

    with col_list:
        st.markdown("### 🗂️ Conversations")
        try:
            conversations = get_user_conversations(user["login_id"])
        except Exception as e:
            st.error(str(e))
            conversations = []

        if not conversations:
            st.markdown("<div style='color:#8b949e;font-size:0.85rem;'>No conversations yet.</div>",
                        unsafe_allow_html=True)

        for conv in conversations:
            conv_id = str(conv["_id"])
            is_active = st.session_state.get("active_conv") == conv_id

            if conv.get("type") == "group":
                name = conv.get("name", "Group")
                icon = "👥"
            else:
                other = [p for p in conv.get("participants", []) if p != user["login_id"]]
                name = other[0] if other else "Unknown"
                icon = "👤"

            last_msg = conv.get("last_message")
            preview = last_msg["content"][:28] + "…" if last_msg and len(last_msg.get("content","")) > 28 else (last_msg["content"] if last_msg else "No messages yet")

            border = "border-color:#2d96ff;" if is_active else ""
            if st.button(f"{icon} {name}", key=f"conv_{conv_id}", use_container_width=True):
                st.session_state["active_conv"] = conv_id
                st.rerun()

            st.markdown(f"""
            <div style="color:#8b949e;font-size:0.72rem;margin:-8px 0 6px 4px;
                        padding-bottom:6px;border-bottom:1px solid #21262d;">
                {preview}
            </div>
            """, unsafe_allow_html=True)

    # ── Chat window ───────────────────────────────────────────────────────
    with col_chat:
        active_conv = st.session_state.get("active_conv")

        if not active_conv:
            st.markdown("""
            <div style="display:flex;align-items:center;justify-content:center;
                        height:400px;color:#484f58;font-size:1rem;">
                ← Select a conversation to start chatting
            </div>
            """, unsafe_allow_html=True)
            return

        # Load conversation info
        try:
            conv = get_conversation(active_conv)
        except Exception as e:
            st.error(str(e))
            return

        if not conv:
            st.warning("Conversation not found.")
            return

        participants = conv.get("participants", [])
        if conv.get("type") == "group":
            header = f"👥 {conv.get('name','Group')}"
        else:
            other = [p for p in participants if p != user["login_id"]]
            header = f"👤 {other[0] if other else 'Unknown'}"

        st.markdown(f"""
        <div style="padding:0.8rem 1rem;background:#1c2128;border:1px solid #30363d;
                    border-radius:10px 10px 0 0;margin-bottom:0;font-weight:600;
                    color:#e6edf3;display:flex;align-items:center;gap:8px;">
            {header}
            <span style="font-size:0.72rem;color:#8b949e;margin-left:auto;">
                {len(participants)} participant{'s' if len(participants)!=1 else ''}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Add refresh button
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("🔄", key="refresh_messages", help="Refresh messages"):
                st.session_state["refresh_chat"] = True
                st.rerun()

        # Message history
        try:
            messages = get_messages(active_conv, limit=80)
        except Exception as e:
            st.error(str(e))
            messages = []

        chat_html = """
        <div style="background:#0d1117;border:1px solid #30363d;border-top:none;
                    height:450px;overflow-y:auto;padding:1rem;display:flex;
                    flex-direction:column;gap:6px;" id="chat-scroll">
        """
        last_date_str = None
        now_date = datetime.utcnow().date()
        for msg in messages:
            ts = msg.get("timestamp")
            time_str = ts.strftime("%I:%M %p") if ts else ""
            if ts:
                msg_date = ts.date()
                if msg_date == now_date:
                    display_date = "TODAY"
                elif msg_date == now_date - timedelta(days=1):
                    display_date = "YESTERDAY"
                else:
                    display_date = msg_date.strftime("%d %B %Y").upper()
                
                if display_date != last_date_str:
                    chat_html += f"""
                    <div style="display:flex;justify-content:center;margin:10px 0;">
                        <div style="background:#1c2128;color:#8b949e;font-size:0.7rem;padding:4px 10px;border-radius:10px;font-weight:600;">
                            {display_date}
                        </div>
                    </div>"""
                    last_date_str = display_date

            is_me = msg.get("sender") == user["login_id"]
            content = msg.get("content", "").replace("&", "&amp;").replace('"', "&quot;").replace("'", "&#x27;")
            sender_name = msg.get("sender_name", msg.get("sender", ""))

            if is_me:
                chat_html += f"""
                <div style="display:flex;justify-content:flex-end;margin-bottom:6px;">
                    <div style="max-width:75%;">
                        <div style="background: linear-gradient(135deg, #1a4a7a, #1e5c99); color: #ffffff; border-radius: 16px 16px 4px 16px; padding: 0.6rem 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
                            <div>{content}</div>
                            <div style="font-size:0.65rem; color:rgba(255,255,255,0.7); text-align:right; margin-top:4px; display:flex; justify-content:flex-end; align-items:center; gap:4px;">
                                {time_str}
                                <span style="color:#58aeff; font-weight:bold;">✓✓</span>
                            </div>
                        </div>
                    </div>
                </div>"""
            else:
                chat_html += f"""
                <div style="display:flex;justify-content:flex-start;margin-bottom:6px;">
                    <div style="max-width:75%;">
                        <div style="color: #58aeff; font-size: 0.75rem; font-weight: 600; margin-bottom: 2px;">{sender_name}</div>
                        <div style="background: #1c2128; color: #ffffff; border: 1px solid #30363d; border-radius: 16px 16px 16px 4px; padding: 0.6rem 1rem;">
                            <div>{content}</div>
                            <div style="font-size:0.65rem; color:rgba(255,255,255,0.7); text-align:right; margin-top:4px;">
                                {time_str}
                            </div>
                        </div>
                    </div>
                </div>"""

        chat_html += "</div>"
        chat_html += """
        <script>
            const el = document.getElementById('chat-scroll');
            if(el) el.scrollTop = el.scrollHeight;
        </script>"""
        
        # Use components.html for proper rendering
        import streamlit.components.v1 as components
        components.html(chat_html, height=450, scrolling=False)

        # Message input
        # Add custom CSS for button styling
        st.markdown("""
        <style>
            div[data-testid="stForm"] button[data-testid="baseButton-secondary"] {
                background: linear-gradient(135deg, #ff6b35, #e55100) !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                padding: 0.75rem 1.5rem !important;
                transition: all 0.2s ease !important;
            }
            div[data-testid="stForm"] button[data-testid="baseButton-primary"] {
                background: linear-gradient(135deg, #2d96ff, #58aeff) !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                padding: 0.75rem 1.5rem !important;
                transition: all 0.2s ease !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        with st.form("send_msg_form", clear_on_submit=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                msg_content = st.text_input(
                    "Message", placeholder="Type a message… (meetings/tasks are auto-detected by AI)",
                    label_visibility="collapsed"
                )
            with c2:
                submitted = st.form_submit_button("📤", key="send_msg_btn", use_container_width=True)

        if submitted and msg_content.strip():
            try:
                msg_id = send_message(
                    conversation_id=active_conv,
                    sender_login=user["login_id"],
                    content=msg_content.strip(),
                    sender_name=user.get("name", user["login_id"])
                )
                # Auto-extract tasks in real time
                n_tasks = _process_message_for_tasks(
                    msg_id=msg_id,
                    content=msg_content.strip(),
                    sender=user["login_id"],
                    sender_name=user.get("name", user["login_id"]),
                    conv_id=active_conv,
                    participants=participants,
                )
                if n_tasks > 0:
                    st.markdown(f"""
                    <div class="alert-info" style="margin-top:4px;">
                        🤖 AI detected an actionable message {n_tasks} task(s) auto-scheduled for participants.
                    </div>
                    """, unsafe_allow_html=True)
                # Force a complete refresh to show the new message
                st.session_state["refresh_chat"] = True
                st.rerun()
            except Exception as e:
                st.error(f"Failed to send: {e}")
        
        # Auto-refresh messages periodically
        if st.session_state.get("refresh_chat", False):
            st.session_state["refresh_chat"] = False
            st.rerun()
