import streamlit as st


def inject_global_css() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap');
            html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
                font-family: 'Kanit', sans-serif !important;
                background-color: #0B0F19;
            }

            .block-container { padding-top: 2rem; max-width: 1100px; }

            /* Header Section */
            .hero-header {
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.5) 100%);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 16px;
                padding: 24px 30px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            }
            .hero-title { font-size: 2rem; font-weight: 700; color: #FFFFFF; margin: 0; letter-spacing: 0.5px; }
            .hero-sub { color: #94A3B8; font-size: 1rem; margin-top: 6px; font-weight: 300; }

            /* Metric Cards */
            .metric-card {
                background: rgba(30, 41, 59, 0.45);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px; 
                padding: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .metric-card:hover {
                transform: translateY(-4px);
                border-color: rgba(99, 102, 241, 0.3);
                box-shadow: 0 12px 40px rgba(99, 102, 241, 0.1);
            }
            .metric-label {
                font-size: 11px; color: #64748B; text-transform: uppercase;
                letter-spacing: 1.5px; margin-bottom: 8px; font-weight: 500;
            }
            .metric-value { font-size: 1.35rem; font-weight: 600; color: #F8FAFC; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
            .metric-value--live { color: #F87171; font-weight: 700; text-shadow: 0 0 10px rgba(248, 113, 113, 0.3); }
            .metric-value--next { color: #818CF8; font-weight: 700; text-shadow: 0 0 10px rgba(129, 140, 248, 0.3); }
            .metric-value--free { color: #34D399; font-weight: 700; }

            /* Status Banners */
            .status-banner {
                padding: 20px 24px; border-radius: 16px; color: white;
                margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.08);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
                backdrop-filter: blur(10px);
                transition: transform 0.2s;
            }
            .status-banner:hover {
                transform: scale(1.005);
            }
            .status-now  { background: linear-gradient(135deg, rgba(239, 68, 68, 0.85), rgba(185, 28, 28, 0.85)); border-color: rgba(239, 68, 68, 0.3); }
            .status-next { background: linear-gradient(135deg, rgba(99, 102, 241, 0.85), rgba(67, 56, 202, 0.85)); border-color: rgba(99, 102, 241, 0.3); }
            .status-free { background: linear-gradient(135deg, rgba(16, 185, 129, 0.85), rgba(4, 120, 87, 0.85)); border-color: rgba(16, 185, 129, 0.3); }

            /* Class Cards */
            .class-card {
                background: rgba(30, 41, 59, 0.35); 
                backdrop-filter: blur(8px);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 14px; padding: 18px 20px; margin-bottom: 12px;
                border-left: 5px solid #6366F1; 
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            .class-card:hover { 
                transform: translateX(4px); 
                background: rgba(30, 41, 59, 0.6);
                border-color: rgba(255,255,255,0.1);
                box-shadow: 0 6px 24px rgba(0,0,0,0.15);
            }
            .class-card--live { border-left-color: #EF4444; background: rgba(239, 68, 68, 0.05); border-color: rgba(239, 68, 68, 0.15); }
            .class-card--done { border-left-color: #475569; opacity: 0.55; }
            .class-card__time { color: #94A3B8; font-size: 0.85rem; font-weight: 500; display: flex; align-items: center; gap: 6px; }
            .class-card__subject { font-size: 1.15rem; font-weight: 600; color: #F8FAFC; margin: 6px 0; }
            .class-card__room { color: #CBD5E1; font-size: 0.9rem; display: flex; align-items: center; gap: 4px; }

            /* Badges */
            .badge {
                display: inline-block; padding: 4px 12px; border-radius: 999px;
                font-size: 11px; font-weight: 600; margin-top: 10px;
                letter-spacing: 0.5px;
            }
            .badge--live { background: rgba(239,68,68,0.15); color: #FCA5A5; border: 1px solid rgba(239,68,68,0.25); }
            .badge--upcoming { background: rgba(99,102,241,0.15); color: #A5B4FC; border: 1px solid rgba(99,102,241,0.25); }
            .badge--done { background: rgba(100,116,139,0.15); color: #94A3B8; border: 1px solid rgba(100,116,139,0.2); }

            /* Live Countdown Card */
            .live-countdown-card {
                background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.12) 100%);
                border: 1px solid rgba(99, 102, 241, 0.25);
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(99, 102, 241, 0.08);
                margin-bottom: 24px;
                backdrop-filter: blur(12px);
                animation: pulseBorder 3s infinite alternate;
            }
            @keyframes pulseBorder {
                0% { border-color: rgba(99, 102, 241, 0.25); }
                100% { border-color: rgba(139, 92, 246, 0.5); }
            }
            .live-countdown-title {
                font-size: 0.8rem;
                color: #A5B4FC;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                margin-bottom: 8px;
                font-weight: 600;
            }
            .live-countdown-subject {
                font-size: 1.4rem;
                font-weight: 700;
                color: #F8FAFC;
                margin-bottom: 12px;
            }
            .live-timer-value {
                font-size: 2.5rem;
                font-weight: 700;
                font-family: monospace;
                color: #FCA5A5;
                text-shadow: 0 0 15px rgba(252, 165, 165, 0.4);
                letter-spacing: 1px;
            }

            /* Empty States */
            .empty-state {
                text-align: center; padding: 50px 30px;
                background: rgba(30, 41, 59, 0.35); border-radius: 16px;
                border: 1px dashed rgba(255,255,255,0.08);
                backdrop-filter: blur(10px);
            }
            .empty-state h3 { color: #F8FAFC; margin-bottom: 10px; font-weight: 600; }
            .empty-state p { color: #64748B; margin-bottom: 20px; }

            /* Streamlit overrides */
            div[data-testid="stSidebar"] {
                background-color: #0F172A !important;
                border-right: 1px solid rgba(255,255,255,0.04);
            }
            div[data-testid="stSidebar"] .stMetric label { color: #64748B !important; }

            .stButton > button[kind="primary"] {
                background: linear-gradient(90deg, #6366F1, #8B5CF6);
                border: none; border-radius: 12px; font-weight: 600;
                color: white !important;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.25);
                transition: all 0.2s;
            }
            .stButton > button[kind="primary"]:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35);
            }
            .stButton > button {
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.08) !important;
                background-color: rgba(30, 41, 59, 0.4) !important;
                color: #CBD5E1 !important;
                transition: all 0.2s;
            }
            .stButton > button:hover {
                border-color: rgba(255,255,255,0.15) !important;
                background-color: rgba(30, 41, 59, 0.6) !important;
                color: #FFFFFF !important;
            }

            /* Custom scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            ::-webkit-scrollbar-track {
                background: #0B0F19;
            }
            ::-webkit-scrollbar-thumb {
                background: #1E293B;
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #334155;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, css_class: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value {css_class}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_banner(kind: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="status-banner status-{kind}">
            <div style="font-size:0.8rem;opacity:0.85;text-transform:uppercase;letter-spacing:1px;">{title}</div>
            <div style="font-size:1.2rem;font-weight:600;margin-top:4px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_class_card(c: dict, state: str) -> None:
    badge_map = {
        "live": ("กำลังเรียน", "badge--live"),
        "upcoming": ("ถัดไป", "badge--upcoming"),
        "done": ("เรียนจบแล้ว", "badge--done"),
    }
    badge_text, badge_cls = badge_map[state]
    st.markdown(
        f"""
        <div class="class-card class-card--{state}">
            <div class="class-card__time">{c['start_time']} – {c['end_time']}</div>
            <div class="class-card__subject">{c['subject']}</div>
            <div class="class-card__room">📍 {c.get('room') or 'ไม่ระบุห้อง'}</div>
            <span class="badge {badge_cls}">{badge_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )