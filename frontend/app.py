import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

import streamlit as st

st.set_page_config(
    page_title="CompanyGPT",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── session state ────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── constants ────────────────────────────────────────────────────
ROLE_COLORS = {
    "hr": "#10b981", "finance": "#3b82f6",
    "marketing": "#f59e0b", "engineering": "#8b5cf6", "c_level": "#ef4444"
}
ROLE_ICONS = {
    "hr": "👥", "finance": "💰",
    "marketing": "📣", "engineering": "⚙️", "c_level": "👑"
}
SUGGESTED = {
    "hr":          ["What is the leave policy?", "How many employees do we have?", "What are payroll details?"],
    "finance":     ["What is our Q4 revenue?", "Show financial summary", "What are quarterly expenses?"],
    "marketing":   ["What was Q4 marketing spend?", "Summarize 2024 marketing report", "What campaigns ran in 2024?"],
    "engineering": ["What is in the engineering master doc?", "What are our technical standards?", "Show engineering overview"],
    "c_level":     ["Give me a company overview", "What are Q4 financials?", "Show HR summary"]
}

# ── global styles ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"], p, span, div, label {
    font-family: 'Space Grotesk', sans-serif !important;
}

.stApp {
    background: #030712;
}

section[data-testid="stSidebar"] {
    background: #0b1120 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}

section[data-testid="stSidebar"] * {
    font-family: 'Space Grotesk', sans-serif !important;
}

/* buttons */
div[data-testid="stButton"] > button {
    background: rgba(255,255,255,0.06) !important;
    color: rgba(255,255,255,0.8) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.2) !important;
}

/* sign in button override */
div[data-testid="stButton"] > button[kind="primary"],
.signin-btn > div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.3) !important;
}

/* text inputs */
div[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: white !important;
    font-size: 14px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    padding: 12px 16px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}
div[data-testid="stTextInput"] label {
    color: rgba(255,255,255,0.5) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}

/* chat input */
div[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    color: white !important;
    font-size: 14px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
div[data-testid="stChatInput"] textarea:focus {
    border-color: #6366f1 !important;
}

/* spinner */
div[data-testid="stSpinner"] p {
    color: rgba(255,255,255,0.5) !important;
    font-size: 13px !important;
}

/* scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }

/* hide streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════
def verify_user(username, password):
    import bcrypt
    from auth.models import SessionLocal, User
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return user
        return None
    finally:
        db.close()


# ══════════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════════════
def show_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        # logo
        st.markdown("""
        <div style="text-align:center;padding:48px 0 36px;">
            <div style="width:68px;height:68px;
                 background:linear-gradient(135deg,#6366f1,#8b5cf6);
                 border-radius:18px;margin:0 auto 18px;
                 display:flex;align-items:center;justify-content:center;
                 font-size:28px;box-shadow:0 0 48px rgba(99,102,241,0.45);">🏢</div>
            <h1 style="color:white;font-size:28px;font-weight:700;
                margin:0;letter-spacing:-0.3px;
                font-family:'Space Grotesk',sans-serif;">CompanyGPT</h1>
            <p style="color:rgba(255,255,255,0.3);font-size:12px;
               text-transform:uppercase;letter-spacing:2.5px;margin-top:8px;">
               AtliQ Internal Intelligence</p>
        </div>
        """, unsafe_allow_html=True)

        # demo accounts
        st.markdown("""
        <p style="color:rgba(255,255,255,0.25);font-size:11px;
           text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">
           Demo accounts</p>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:28px;">
            <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
                 border-radius:10px;padding:10px 14px;">
                <div style="color:#10b981;font-size:11px;font-weight:600;
                     text-transform:uppercase;letter-spacing:0.5px;">👥 HR</div>
                <div style="color:rgba(255,255,255,0.35);font-size:12px;
                     margin-top:3px;font-family:'Space Grotesk',sans-serif;">alice / alice123</div>
            </div>
            <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);
                 border-radius:10px;padding:10px 14px;">
                <div style="color:#3b82f6;font-size:11px;font-weight:600;
                     text-transform:uppercase;letter-spacing:0.5px;">💰 Finance</div>
                <div style="color:rgba(255,255,255,0.35);font-size:12px;
                     margin-top:3px;font-family:'Space Grotesk',sans-serif;">bob / bob123</div>
            </div>
            <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);
                 border-radius:10px;padding:10px 14px;">
                <div style="color:#f59e0b;font-size:11px;font-weight:600;
                     text-transform:uppercase;letter-spacing:0.5px;">📣 Marketing</div>
                <div style="color:rgba(255,255,255,0.35);font-size:12px;
                     margin-top:3px;font-family:'Space Grotesk',sans-serif;">carol / carol123</div>
            </div>
            <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
                 border-radius:10px;padding:10px 14px;">
                <div style="color:#ef4444;font-size:11px;font-weight:600;
                     text-transform:uppercase;letter-spacing:0.5px;">👑 C-Level</div>
                <div style="color:rgba(255,255,255,0.35);font-size:12px;
                     margin-top:3px;font-family:'Space Grotesk',sans-serif;">eve / eve123</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # form
        username = st.text_input("Username", placeholder="Enter your username", key="login_user")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        if st.button("Sign in →", use_container_width=True, type="primary"):
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                user = verify_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = user.username
                    st.session_state.role = user.role
                    st.session_state.messages = []
                    st.rerun()
                else:
                    st.error("Invalid username or password.")


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════
def show_sidebar():
    role = st.session_state.role
    username = st.session_state.username
    color = ROLE_COLORS.get(role, "#6366f1")
    icon = ROLE_ICONS.get(role, "🔵")

    with st.sidebar:
        st.markdown(f"""
        <div style="padding:20px 0 16px;">
            <div style="background:rgba(255,255,255,0.04);
                 border:1px solid rgba(255,255,255,0.08);
                 border-radius:14px;padding:20px;text-align:center;">
                <div style="width:54px;height:54px;border-radius:50%;
                     background:{color}18;border:2px solid {color}66;
                     display:flex;align-items:center;justify-content:center;
                     font-size:22px;margin:0 auto 12px;">{icon}</div>
                <p style="color:white;font-size:16px;font-weight:600;margin:0;
                   font-family:'Space Grotesk',sans-serif;">{username.capitalize()}</p>
                <div style="display:inline-block;background:{color}18;color:{color};
                     border:1px solid {color}44;border-radius:20px;
                     padding:3px 14px;font-size:11px;font-weight:600;
                     text-transform:uppercase;letter-spacing:0.8px;margin-top:8px;
                     font-family:'Space Grotesk',sans-serif;">{role.replace('_', ' ')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <p style="color:rgba(255,255,255,0.25);font-size:10px;text-transform:uppercase;
           letter-spacing:1.2px;margin:4px 0 10px;
           font-family:'Space Grotesk',sans-serif;">Data access</p>
        """, unsafe_allow_html=True)

        from auth.rbac import ROLE_DEPARTMENT_ACCESS
        depts = ROLE_DEPARTMENT_ACCESS.get(role, [])
        for d in depts:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;
                 padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                <div style="width:6px;height:6px;border-radius:50%;
                     background:{color};flex-shrink:0;"></div>
                <span style="color:rgba(255,255,255,0.65);font-size:13px;
                      font-family:'Space Grotesk',sans-serif;">{d.capitalize()}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.divider()

        if st.button("🗑️  Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("🚪  Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.messages = []
            st.rerun()

        st.markdown("""
        <div style="position:fixed;bottom:20px;left:0;width:264px;text-align:center;">
            <span style="color:rgba(255,255,255,0.12);font-size:11px;
                  font-family:'Space Grotesk',sans-serif;">
                CompanyGPT · AtliQ Internal
            </span>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  CHAT PAGE
# ══════════════════════════════════════════════════════════════════
def show_chat():
    show_sidebar()

    role = st.session_state.role
    color = ROLE_COLORS.get(role, "#6366f1")

    # header
    st.markdown(f"""
    <div style="padding:28px 0 20px;
         border-bottom:1px solid rgba(255,255,255,0.05);
         margin-bottom:28px;">
        <div style="display:flex;align-items:center;gap:14px;">
            <div style="width:40px;height:40px;border-radius:12px;
                 background:linear-gradient(135deg,#6366f1,#8b5cf6);
                 display:flex;align-items:center;justify-content:center;font-size:18px;">🏢</div>
            <div>
                <h1 style="color:white;font-size:22px;font-weight:700;margin:0;
                    font-family:'Space Grotesk',sans-serif;letter-spacing:-0.3px;">CompanyGPT</h1>
                <p style="color:rgba(255,255,255,0.3);font-size:12px;margin:2px 0 0;
                   font-family:'Space Grotesk',sans-serif;">
                   Logged in as <span style="color:{color};">{st.session_state.username}</span>
                   · {role.replace('_',' ').title()} access
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # suggested questions — only when chat is empty
    if len(st.session_state.messages) == 0:
        questions = SUGGESTED.get(role, [])
        st.markdown("""
        <p style="color:rgba(255,255,255,0.2);font-size:11px;text-transform:uppercase;
           letter-spacing:1.2px;margin-bottom:12px;
           font-family:'Space Grotesk',sans-serif;">Try asking</p>
        """, unsafe_allow_html=True)
        cols = st.columns(3)
        for i, q in enumerate(questions[:3]):
            with cols[i]:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.03);
                     border:1px solid rgba(255,255,255,0.07);
                     border-radius:12px;padding:12px 14px;margin-bottom:4px;
                     font-size:13px;color:rgba(255,255,255,0.55);
                     font-family:'Space Grotesk',sans-serif;line-height:1.4;">
                     {q}</div>
                """, unsafe_allow_html=True)
                if st.button("Ask →", key=f"sq_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": q})
                    st.rerun()

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-end;margin:16px 0;">
                <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);
                     color:white;border-radius:18px 18px 4px 18px;
                     padding:12px 18px;max-width:68%;font-size:14px;
                     line-height:1.6;font-family:'Space Grotesk',sans-serif;
                     box-shadow:0 4px 20px rgba(99,102,241,0.25);">
                    {msg["content"]}
                </div>
            </div>""", unsafe_allow_html=True)

        else:
            sources_html = ""
            if msg.get("sources"):
                chips = "".join([
                    f'<span style="background:rgba(255,255,255,0.06);'
                    f'border:1px solid rgba(255,255,255,0.1);'
                    f'border-radius:20px;padding:3px 10px;font-size:11px;'
                    f'color:rgba(255,255,255,0.4);margin-right:4px;'
                    f'font-family:Space Grotesk,sans-serif;">📄 {s}</span>'
                    for s in msg["sources"]
                ])
                sources_html = f'<div style="margin-top:12px;display:flex;flex-wrap:wrap;gap:4px;">{chips}</div>'

            guardrail_html = ""
            if msg.get("guardrail"):
                guardrail_html = f"""
                <div style="background:rgba(239,68,68,0.08);
                     border:1px solid rgba(239,68,68,0.2);
                     color:#ef4444;border-radius:8px;
                     padding:8px 12px;font-size:12px;margin-top:10px;
                     font-family:'Space Grotesk',sans-serif;">
                     ⚠️ {msg['guardrail']}
                </div>"""

            st.markdown(f"""
            <div style="display:flex;justify-content:flex-start;
                 margin:16px 0;gap:12px;align-items:flex-start;">
                <div style="width:34px;height:34px;border-radius:10px;
                     background:rgba(99,102,241,0.15);
                     border:1px solid rgba(99,102,241,0.3);
                     display:flex;align-items:center;
                     justify-content:center;font-size:16px;
                     flex-shrink:0;margin-top:2px;">🏢</div>
                <div style="background:rgba(255,255,255,0.04);
                     border:1px solid rgba(255,255,255,0.07);
                     color:rgba(255,255,255,0.85);
                     border-radius:4px 18px 18px 18px;
                     padding:14px 18px;max-width:74%;
                     font-size:14px;line-height:1.75;
                     font-family:'Space Grotesk',sans-serif;">
                    {msg["content"]}
                    {sources_html}
                    {guardrail_html}
                </div>
            </div>""", unsafe_allow_html=True)

    # chat input
    if prompt := st.chat_input("Ask about company data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Searching documents..."):
            from rag.chain import run_rag_chain
            result = run_rag_chain(query=prompt, role=role)

        import re
        clean = result["answer"]
        clean = re.sub(r'</?\w+[^>]*>', '', clean)  # strip any HTML tags
        clean = clean.strip()

        st.session_state.messages.append({
            "role": "assistant",
            "content": clean,
            "sources": result.get("sources", []),
            "guardrail": result.get("guardrail_triggered")
        })
        st.rerun()


# ══════════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════════
if not st.session_state.authenticated:
    show_login()
else:
    show_chat()
