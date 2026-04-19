GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-card: #1c2128;
    --bg-hover: #22272e;
    --accent: #2d96ff;
    --accent-light: #58aeff;
    --accent-dim: rgba(45, 150, 255, 0.15);
    --success: #3fb950;
    --warning: #d29922;
    --danger: #f85149;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --text-muted: #484f58;
    --border: #30363d;
    --border-light: #21262d;
    --radius: 10px;
    --radius-lg: 16px;
    --shadow: 0 4px 20px rgba(0,0,0,0.4);
    --shadow-lg: 0 8px 40px rgba(0,0,0,0.6);
}

html, body, .stApp {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* Hide default Streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }

/* Headings */
h1, h2, h3, h4 {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background-color: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-dim) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #1a7fd4) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.01em;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(45,150,255,0.3) !important;
    background: linear-gradient(135deg, #4daeff, var(--accent)) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--bg-hover) !important;
    border: 1px solid var(--border) !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--accent) !important;
    background: var(--accent-dim) !important;
    box-shadow: none !important;
}

/* Labels */
.stTextInput label, .stTextArea label, .stSelectbox label,
.stMultiSelect label, .stDateInput label {
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Cards */
.corp-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.corp-card:hover { border-color: var(--accent); }

/* Message bubbles */
.msg-bubble-me {
    background: linear-gradient(135deg, #1a4a7a, #1e5c99);
    color: #ffffff !important;
    border-radius: 16px 16px 4px 16px;
    padding: 0.6rem 1rem;
    margin: 0.2rem 0;
    max-width: 75%;
    margin-left: auto;
    font-size: 0.9rem;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.msg-bubble-other {
    background: var(--bg-card);
    color: #ffffff !important;
    border: 1px solid var(--border);
    border-radius: 16px 16px 16px 4px;
    padding: 0.6rem 1rem;
    margin: 0.2rem 0;
    max-width: 75%;
    font-size: 0.9rem;
    line-height: 1.5;
}
.msg-sender { color: #58aeff !important; font-size: 0.75rem; font-weight: 600; margin-bottom: 2px; }
.msg-time { color: var(--text-muted); font-size: 0.7rem; margin-top: 3px; text-align: right; }

/* Task badges */
.task-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-meeting { background: rgba(45,150,255,0.2); color: var(--accent-light); }
.badge-action  { background: rgba(210,153,34,0.2); color: #e3a527; }
.badge-pending { background: rgba(63,185,80,0.15); color: var(--success); }
.badge-done    { background: rgba(72,79,88,0.4); color: var(--text-secondary); }

/* Dashboard nav cards */
.nav-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.8rem 1.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.25s ease;
    margin-bottom: 1rem;
}
.nav-card:hover {
    border-color: var(--accent);
    background: var(--bg-hover);
    transform: translateY(-2px);
    box-shadow: var(--shadow);
}
.nav-card-icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
.nav-card-title { font-size: 1rem; font-weight: 600; color: var(--text-primary); }
.nav-card-desc { font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px; }

/* Alert boxes */
.alert-info  { background:rgba(45,150,255,0.1); border:1px solid rgba(45,150,255,0.3); border-radius:var(--radius); padding:0.8rem 1rem; color:var(--accent-light); margin:0.5rem 0; }
.alert-success{background:rgba(63,185,80,0.1); border:1px solid rgba(63,185,80,0.3); border-radius:var(--radius); padding:0.8rem 1rem; color:var(--success); margin:0.5rem 0; }
.alert-warn { background:rgba(210,153,34,0.1); border:1px solid rgba(210,153,34,0.3); border-radius:var(--radius); padding:0.8rem 1rem; color:#e3a527; margin:0.5rem 0; }
.alert-danger{ background:rgba(248,81,73,0.1); border:1px solid rgba(248,81,73,0.3); border-radius:var(--radius); padding:0.8rem 1rem; color:var(--danger); margin:0.5rem 0; }

/* Divider */
.section-divider { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* Streamlit multiselect */
.stMultiSelect > div { background: var(--bg-secondary) !important; border-color: var(--border) !important; }

/* Expander */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
}

/* Radio */
.stRadio > div { gap: 0.5rem; }
.stRadio label { color: var(--text-secondary) !important; }

/* Success / error messages */
.stSuccess { background: rgba(63,185,80,0.1) !important; border-color: var(--success) !important; color: var(--success) !important; }
.stError   { background: rgba(248,81,73,0.1) !important; border-color: var(--danger) !important; }
.stWarning { background: rgba(210,153,34,0.1) !important; border-color: var(--warning) !important; }
.stInfo    { background: rgba(45,150,255,0.1) !important; border-color: var(--accent) !important; }
</style>
"""


def inject_css():
    import streamlit as st
    
    # Get current theme from session state
    theme = st.session_state.get("theme", "dark")
    
    # Theme-specific CSS overrides
    theme_css = ""
    if theme == "light":
        theme_css = """<style>
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --bg-card: #e9ecef;
    --bg-hover: #dee2e6;
    --accent: #0066cc;
    --accent-light: #3399ff;
    --accent-dim: rgba(0, 102, 204, 0.1);
    --text-primary: #212529;
    --text-secondary: #6c757d;
    --text-muted: #adb5bd;
    --border: #dee2e6;
    --border-light: #e9ecef;
}
</style>"""
    elif theme == "blue":
        theme_css = """<style>
:root {
    --bg-primary: #0a1929;
    --bg-secondary: #132f4c;
    --bg-card: #1e3a5f;
    --bg-hover: #2a4d7a;
    --accent: #00b4d8;
    --accent-light: #48cae4;
    --accent-dim: rgba(0, 180, 216, 0.15);
    --text-primary: #ffffff;
    --text-secondary: #90e0ef;
    --text-muted: #caf0f8;
    --border: #2a4d7a;
    --border-light: #1e3a5f;
}
</style>"""
    
    full_css = GLOBAL_CSS + theme_css
    st.markdown(full_css, unsafe_allow_html=True)
