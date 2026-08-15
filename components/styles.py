import streamlit as st


def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        :root {
            --bg:#F8FAFC; --panel:#FFFFFF; --line:#E8ECF0; --text:#0F172A; --muted:#64748B;
            --primary:#6C63FF; --primary-light:#EEF0FF; --secondary:#4F8EF7; --accent:#8B5CF6;
            --radius:16px;
        }
        .stApp { background: var(--bg); color: var(--text); font-family:'Inter',sans-serif; }
        footer { visibility:hidden; }
        .block-container { padding:4.5rem 2rem 3rem; max-width:1500px; }

        [data-testid="stSidebar"] { background:#FFFFFF; border-right:1px solid var(--line); }
        [data-testid="stSidebar"] > div:first-child { padding:1.35rem .85rem; }

        h1,h2,h3 { font-family:'Inter',sans-serif; font-weight:700; letter-spacing:-.02em; color:var(--text); }
        h1 { font-size:2rem!important; } h2 { font-size:1.25rem!important; }
        p,span,label { color:var(--text); }
        [data-testid="stCaptionContainer"] p { color:var(--muted)!important; }
        .muted { color:var(--muted); }

        .brand { display:flex; align-items:center; gap:10px; padding:8px 10px 25px; font-weight:800; font-size:18px; color:var(--text); }
        .brand-mark { width:31px; height:31px; border-radius:10px; display:grid; place-items:center; color:white;
            background:linear-gradient(135deg,var(--primary),var(--secondary)); box-shadow:0 8px 20px rgba(108,99,255,.28); }

        .eyebrow { color:var(--primary); font-size:.72rem; text-transform:uppercase; letter-spacing:.13em; font-weight:700; margin-bottom:.35rem; }

        .topbar { display:flex; justify-content:space-between; align-items:center; padding:10px 0 24px; }
        .date-chip,.profile-chip { border:1px solid var(--line); background:#F8FAFC; border-radius:12px; padding:9px 12px; font-size:.82rem; color:var(--muted); }
        .profile-chip { color:var(--text); font-weight:500; }

        .hero { position:relative; overflow:hidden; padding:30px; border:1px solid var(--line); border-radius:22px;
            background:linear-gradient(110deg,var(--primary-light),#EAF2FF); box-shadow:0 10px 30px rgba(108,99,255,.08); }
        .hero h1 { margin:.1rem 0 .45rem!important; max-width:600px; color:var(--text); }
        .hero p { color:var(--muted); max-width:550px; }

        .metric-card,.glass-card { background:var(--panel); border:1px solid var(--line); border-radius:var(--radius); box-shadow:0 4px 16px rgba(15,23,42,.04); }
        .metric-card { padding:17px; min-height:105px; transition:transform .18s ease,border-color .18s ease; }
        .metric-card:hover,.glass-card:hover { transform:translateY(-2px); border-color:var(--primary); }
        .metric-label { color:var(--muted); font-size:.78rem; }
        .metric-value { font:700 1.7rem 'Inter'; margin-top:8px; color:var(--text); }
        .metric-note { color:var(--secondary); font-size:.75rem; margin-top:5px; }

        .glass-card { padding:21px; margin-bottom:16px; }
        .section-title { display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; }
        .section-title h3 { margin:0; font-size:1rem; }

        .event-row { display:flex; gap:13px; padding:13px 0; border-bottom:1px solid var(--line); }
        .event-row:last-child { border:0; }
        .event-dot { width:9px; height:9px; border-radius:10px; margin-top:6px; background:linear-gradient(var(--primary),var(--secondary)); }
        .event-title { font-weight:600; font-size:.9rem; color:var(--text); }
        .event-time { color:var(--muted); font-size:.78rem; margin-top:3px; }

        .agent-shell { border-radius:22px; background:var(--panel); border:1px solid var(--line); box-shadow:0 10px 30px rgba(108,99,255,.06); padding:22px; }
        .agent-head { display:flex; gap:11px; align-items:center; }
        .agent-orb { width:36px; height:36px; display:grid; place-items:center; border-radius:12px; color:white;
            background:linear-gradient(135deg,var(--primary),var(--accent)); }
        .suggestion { border:1px solid var(--line); color:var(--text); background:var(--primary-light); border-radius:11px; padding:8px 11px; font-size:.8rem; }

        .progress-ring { width:126px; height:126px; display:grid; place-items:center; border-radius:50%;
            background:conic-gradient(var(--primary) var(--progress),#EEF0F5 0); margin:8px auto; }
        .progress-ring:before { content:attr(data-value); display:grid; place-items:center; width:98px; height:98px; border-radius:50%; background:white; color:var(--text); font-weight:700; }

        .bar { height:8px; border-radius:10px; background:#EEF0F5; overflow:hidden; margin:9px 0 17px; }
        .bar > span { display:block; height:100%; border-radius:inherit; background:linear-gradient(90deg,var(--primary),var(--secondary)); }

        .stButton>button,[data-testid="stFormSubmitButton"]>button {
            border:0!important; color:white!important; border-radius:11px!important;
            background:linear-gradient(110deg,var(--primary),var(--secondary))!important; font-weight:600!important;
            box-shadow:0 8px 20px rgba(108,99,255,.25); transition:transform .18s ease,box-shadow .18s ease!important; }
        .stButton>button:hover,[data-testid="stFormSubmitButton"]>button:hover { transform:translateY(-2px); box-shadow:0 11px 26px rgba(108,99,255,.35)!important; }

        .stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div {
            background:#FFFFFF!important; border:1px solid var(--line)!important; border-radius:11px!important; color:var(--text)!important; }
        [data-testid="stChatInput"] { border:1px solid var(--line); border-radius:16px; background:#FFFFFF; }

        [data-testid="stMetric"] { background:transparent; }
        [data-testid="stMetricValue"] { color:var(--text); }
        [data-testid="stRadio"] label { border-radius:10px; padding:5px; }
        [data-testid="stRadio"] label:hover { background:var(--primary-light); }
 
        .exam-actions .stButton > button {background: transparent !important;color: var(--muted) !important;border: 1px solid var(--line) !important;box-shadow: none !important;border-radius: 9px !important;font-size: 0.75rem !important;font-weight: 500 !important;padding: 7px 8px !important;min-height: 34px !important;}
        .exam-actions .stButton > button:hover {background: var(--primary-light) !important;color: var(--primary) !important;border-color: var(--primary) !important;box-shadow: none !important;transform: none !important;}
        </style>
        """,
        unsafe_allow_html=True,
    )