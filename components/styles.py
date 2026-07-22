import streamlit as st


def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
        :root { --bg:#090b12; --panel:rgba(20,24,37,.74); --line:rgba(255,255,255,.09); --text:#f5f7ff; --muted:#99a2b7; --violet:#8b5cf6; --blue:#38bdf8; --green:#5eead4; }
        .stApp { background: radial-gradient(circle at 80% -10%,#251a4c 0,transparent 28%), radial-gradient(circle at 15% 0,#102947 0,transparent 25%), var(--bg); color:var(--text); font-family:'DM Sans',sans-serif; }
        #MainMenu, footer, header { visibility:hidden; } .block-container { padding:1.5rem 2rem 3rem; max-width:1500px; }
        [data-testid="stSidebar"] { background:rgba(10,13,23,.93); border-right:1px solid var(--line); } [data-testid="stSidebar"] > div:first-child { padding:1.35rem .85rem; }
        h1,h2,h3 { font-family:'Manrope',sans-serif; letter-spacing:-.04em; } h1 { font-size:2rem!important; } h2 { font-size:1.25rem!important; }
        p,span,label { color:var(--text); } [data-testid="stCaptionContainer"] p { color:var(--muted)!important; }
        .brand { display:flex; align-items:center; gap:10px; padding:8px 10px 25px; font-family:'Manrope'; font-weight:800; font-size:18px; } .brand-mark { width:31px; height:31px; border-radius:10px; display:grid; place-items:center; background:linear-gradient(135deg,#a78bfa,#38bdf8); box-shadow:0 8px 24px #6d5dfc55; }
        .eyebrow { color:#a5b4fc; font-size:.72rem; text-transform:uppercase; letter-spacing:.13em; font-weight:700; margin-bottom:.35rem; } .muted { color:var(--muted); }
        .topbar { display:flex; justify-content:space-between; align-items:center; padding:10px 0 24px; } .date-chip,.profile-chip { border:1px solid var(--line); background:rgba(255,255,255,.04); border-radius:12px; padding:9px 12px; font-size:.82rem; color:#c8cfde; } .profile-chip { color:white; }
        .hero { position:relative; overflow:hidden; padding:30px; min-height:210px; border:1px solid rgba(167,139,250,.35); border-radius:22px; background:linear-gradient(110deg,rgba(79,70,229,.35),rgba(14,165,233,.16)); box-shadow:0 20px 55px rgba(0,0,0,.25); animation:fadeUp .5s ease both; } .hero:after { content:''; position:absolute; width:260px; height:260px; right:-80px; top:-150px; background:#8b5cf6; opacity:.22; filter:blur(60px); border-radius:100%; } .hero h1 { margin:.1rem 0 .45rem!important; max-width:600px; } .hero p { color:#d9def0; max-width:550px; }
        .metric-card,.glass-card { background:var(--panel); backdrop-filter:blur(18px); border:1px solid var(--line); border-radius:18px; box-shadow:0 10px 30px rgba(0,0,0,.18); } .metric-card { padding:17px; min-height:105px; transition:transform .2s ease,border-color .2s ease; animation:fadeUp .5s ease both; } .metric-card:hover,.glass-card:hover { transform:translateY(-3px); border-color:rgba(167,139,250,.38); } .metric-label { color:var(--muted); font-size:.78rem; } .metric-value { font:700 1.7rem 'Manrope'; margin-top:8px; } .metric-note { color:#7dd3fc; font-size:.75rem; margin-top:5px; }
        .glass-card { padding:21px; margin-bottom:16px; } .section-title { display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; } .section-title h3 { margin:0; font-size:1rem; }
        .event-row { display:flex; gap:13px; padding:13px 0; border-bottom:1px solid var(--line); } .event-row:last-child { border:0; } .event-dot { width:9px; height:9px; border-radius:10px; margin-top:6px; background:linear-gradient(#a78bfa,#38bdf8); box-shadow:0 0 12px #8b5cf6; } .event-title { font-weight:600; font-size:.9rem; } .event-time { color:var(--muted); font-size:.78rem; margin-top:3px; }
        .agent-shell { border:1px solid transparent; border-radius:22px; background:linear-gradient(var(--panel),var(--panel)) padding-box,linear-gradient(130deg,#8b5cf6,#38bdf8,#5eead4) border-box; box-shadow:0 0 35px rgba(99,102,241,.13); padding:22px; } .agent-head { display:flex; gap:11px; align-items:center; } .agent-orb { width:36px; height:36px; display:grid; place-items:center; border-radius:12px; background:linear-gradient(135deg,#8b5cf6,#38bdf8); animation:pulse 2.2s infinite; } .suggestion { border:1px solid var(--line); color:#c9d1e5; background:#ffffff08; border-radius:11px; padding:8px 11px; font-size:.8rem; }
        .progress-ring { width:126px; height:126px; display:grid; place-items:center; border-radius:50%; background:conic-gradient(#8b5cf6 var(--progress),#252a3b 0); margin:8px auto; } .progress-ring:before { content:attr(data-value); display:grid; place-items:center; width:98px; height:98px; border-radius:50%; background:#121624; color:white; font-weight:700; }
        .bar { height:8px; border-radius:10px; background:#262b3d; overflow:hidden; margin:9px 0 17px; } .bar > span { display:block; height:100%; border-radius:inherit; background:linear-gradient(90deg,#8b5cf6,#38bdf8); }
        .stButton>button,[data-testid="stFormSubmitButton"]>button { border:0!important; color:white!important; border-radius:11px!important; background:linear-gradient(110deg,#7c3aed,#2563eb)!important; font-weight:600!important; box-shadow:0 8px 20px #4f46e544; transition:transform .2s ease,box-shadow .2s ease!important; } .stButton>button:hover,[data-testid="stFormSubmitButton"]>button:hover { transform:translateY(-2px); box-shadow:0 11px 26px #4f46e577!important; }
        .stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div { background:rgba(255,255,255,.055)!important; border-color:var(--line)!important; border-radius:11px!important; color:white!important; } [data-testid="stChatInput"] { border:1px solid rgba(167,139,250,.36); border-radius:16px; background:#101522; }
        [data-testid="stMetric"] { background:transparent; } [data-testid="stMetricValue"] { color:white; } [data-testid="stRadio"] label { border-radius:10px; padding:5px; } [data-testid="stRadio"] label:hover { background:#ffffff0b; }
        @keyframes fadeUp { from {opacity:0;transform:translateY(10px)} to {opacity:1;transform:none} } @keyframes pulse { 50% { box-shadow:0 0 0 8px #8b5cf622; } }
        </style>
        """,
        unsafe_allow_html=True,
    )
