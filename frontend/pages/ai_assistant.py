import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.styles import inject_css


def show_ai_assistant():
    inject_css()
    user = st.session_state.get("user", {})
    if not user:
        return

    st.markdown("## 🤖 AI Assistant")
    st.markdown("""
    <div class="alert-info">
        Ask me anything about your team's conversations, schedules, project status, or pending tasks.
        I search through your chat history using semantic AI to find relevant answers.
    </div>
    """, unsafe_allow_html=True)

    # Suggested queries
    st.markdown("#### 💡 Suggested Questions")
    suggestions = [
        "What meetings are scheduled this week?",
        "What are my pending tasks?",
        "What is the status of the current project?",
        "Who mentioned the deployment deadline?",
        "Summarise what was discussed in the team chat today.",
    ]
    cols = st.columns(3)
    for i, s in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(s, key=f"sug_{i}", use_container_width=True):
                st.session_state["ai_query"] = s

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat history
    if "ai_history" not in st.session_state:
        st.session_state["ai_history"] = []

    # Display history
    for turn in st.session_state["ai_history"]:
        role = turn["role"]
        content = turn["content"]
        if role == "user":
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-end;margin:6px 0;">
                <div class="msg-bubble-me" style="max-width:80%;">{content}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-start;margin:6px 0;">
                <div style="max-width:85%;">
                    <div style="font-size:0.75rem;color:#2d96ff;font-weight:600;margin-bottom:3px;">🤖 AI ASSISTANT</div>
                    <div class="msg-bubble-other" style="line-height:1.7;">{content}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Query input
    with st.form("ai_form", clear_on_submit=True):
        if "ai_query" in st.session_state:
            query = st.text_input(
                "Ask AI",
                value=st.session_state.pop("ai_query"),
                placeholder="e.g. What meetings are scheduled this week?",
                label_visibility="collapsed"
            )
        else:
            query = st.text_input(
                "Ask AI",
                placeholder="e.g. What meetings are scheduled this week?",
                label_visibility="collapsed"
            )
        c1, c2 = st.columns([5, 1])
        with c2:
            submitted = st.form_submit_button("Ask 🚀", use_container_width=True)
        with c1:
            clear = st.form_submit_button("Clear History", use_container_width=True)

    if clear:
        st.session_state["ai_history"] = []
        st.rerun()

    if submitted and query.strip():
        st.session_state["ai_history"].append({"role": "user", "content": query.strip()})

        with st.spinner("🔍 Searching chat history and generating answer…"):
            try:
                from backend.rag_assistant import ask_assistant
                answer = ask_assistant(
                    question=query.strip(),
                    user_login=user["login_id"],
                    user_name=user.get("name", "")
                )
            except Exception as e:
                answer = f"⚠️ AI assistant error: {str(e)}\n\nMake sure ANTHROPIC_API_KEY is set and the RAG index has been seeded."

        st.session_state["ai_history"].append({"role": "assistant", "content": answer})
        st.rerun()

    st.markdown("""
    <div style="margin-top:2rem;padding:0.8rem 1rem;background:rgba(45,150,255,0.05);
                border:1px solid rgba(45,150,255,0.1);border-radius:10px;
                color:#484f58;font-size:0.75rem;">
        💡 Tip: Run <code>python backend/seed_index.py</code> once to index existing messages into the AI knowledge base.
        New messages are indexed automatically when sent.
    </div>
    """, unsafe_allow_html=True)
