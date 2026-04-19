import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="Corporate Smart Messenger",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="auto",
)

# Import pages
from frontend.home import show_home
from frontend.pages.streamlit_login import show_login
from frontend.pages.change_password import show_change_password
from frontend.pages.user_dashboard import show_user_dashboard
from frontend.pages.admin_dashboard import show_admin_dashboard

@st.cache_resource
def init_rag_store():
    import os
    from backend.rag_indexer import CHROMA_PATH, seed_index
    if not os.path.exists(CHROMA_PATH) or not os.listdir(CHROMA_PATH):
        print("[INIT] Chroma store missing or empty. Rebuilding from MongoDB...")
        try:
            seed_index()
        except Exception as e:
            print(f"[INIT] Error seeding index: {e}")
    return True

def main():
    init_rag_store()
    # Initialise session state
    if "page" not in st.session_state:
        st.session_state["page"] = "home"

    page = st.session_state.get("page", "home")
    user = st.session_state.get("user", {})

    # Guard: logged-in admin trying to access user page or vice-versa
    if page == "user_dashboard" and user.get("role") in ("Admin",):
        st.session_state["page"] = "admin_dashboard"
        page = "admin_dashboard"

    # Route
    if page == "home":
        show_home()
    elif page == "login":
        show_login()
    elif page == "change_password":
        show_change_password()
    elif page == "user_dashboard":
        if not user:
            st.session_state["page"] = "login"
            st.rerun()
        show_user_dashboard()
    elif page == "admin_dashboard":
        if not user:
            st.session_state["page"] = "login"
            st.rerun()
        show_admin_dashboard()
    else:
        show_home()


if __name__ == "__main__":
    main()
