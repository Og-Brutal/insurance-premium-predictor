import time
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="InsurePredict | Premium Estimator",
    page_icon="IP",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DEFAULT_API_URL = "http://127.0.0.1:8000"

TIER_1_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune",
]
TIER_2_CITIES = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi",
    "Visakhapatnam", "Coimbatore", "Bhopal", "Nagpur", "Vadodara", "Surat",
    "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi", "Agra", "Dehradun",
    "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem",
    "Vijayawada", "Tiruchirappalli", "Bhavnagar", "Gwalior", "Dhanbad",
    "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal", "Kolhapur",
    "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri",
]
ALL_CITIES = sorted(TIER_1_CITIES + TIER_2_CITIES)

OCCUPATIONS = [
    "retired",
    "freelancer",
    "student",
    "government_job",
    "business_owner",
    "unemployed",
    "private_job",
]

OCCUPATION_LABELS = {
    "retired": "Retired",
    "freelancer": "Freelancer",
    "student": "Student",
    "government_job": "Government",
    "business_owner": "Business Owner",
    "unemployed": "Unemployed",
    "private_job": "Private Job",
}

PRESETS = {
    "Young Professional": {
        "age": 26, "weight": 68.0, "height": 1.75, "income": 12.0,
        "smoker": False, "city": "Bangalore", "occupation": "private_job",
    },
    "Senior Retiree": {
        "age": 67, "weight": 78.0, "height": 1.68, "income": 4.5,
        "smoker": True, "city": "Jaipur", "occupation": "retired",
    },
    "Business Owner": {
        "age": 44, "weight": 92.0, "height": 1.72, "income": 45.0,
        "smoker": False, "city": "Mumbai", "occupation": "business_owner",
    },
    "Student": {
        "age": 21, "weight": 58.0, "height": 1.66, "income": 1.5,
        "smoker": False, "city": "Indore", "occupation": "student",
    },
}

CATEGORY_COPY = {
    "low": (
        "Low Premium",
        "Favourable risk factors across the board — you land in the most affordable band.",
    ),
    "medium": (
        "Medium Premium",
        "A balanced profile. Some factors push your premium into the middle band.",
    ),
    "high": (
        "High Premium",
        "Several risk factors stack up here, placing you in the highest premium band.",
    ),
}

CATEGORY_ORDER = ["low", "medium", "high"]
NAV_PAGES = ["Estimate", "How it works", "History"]

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@500;600;700;800&display=swap');

    :root {
        --bg-0: #070B14;
        --bg-1: #0B1220;
        --surface: rgba(20, 28, 46, 0.72);
        --surface-solid: #141C2E;
        --surface-2: #0F1626;
        --border: rgba(148, 163, 184, 0.14);
        --border-strong: rgba(148, 163, 184, 0.26);
        --text: #E8EEF6;
        --muted: #9FB0C6;
        --muted-2: #6B7C93;
        --accent: #2DD4BF;
        --accent-2: #38BDF8;
        --accent-soft: rgba(45, 212, 191, 0.16);
        --accent-glow: rgba(45, 212, 191, 0.16);
        --low: #34D399;
        --medium: #FBBF24;
        --high: #F87171;
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.25);
        --shadow-md: 0 10px 30px rgba(0, 0, 0, 0.32);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(1200px 700px at 82% -12%, rgba(56, 189, 248, 0.05), transparent 60%),
            linear-gradient(180deg, #080D18 0%, #0A0F1B 100%);
        background-attachment: fixed;
        color: var(--text);
    }

    #MainMenu, footer, header { visibility: hidden; }

    .block-container {
        padding-top: 0.75rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1120px;
    }

    /* ---- Top navigation ---- */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        padding: 1rem 1.4rem;
        margin: 0 0 1.5rem;
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid var(--border);
        border-radius: 14px;
        box-shadow: var(--shadow-md);
        backdrop-filter: blur(12px);
        position: relative;
        overflow: hidden;
    }
    .brand {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        min-width: 200px;
    }
    .brand-mark {
        width: 38px; height: 38px;
        border-radius: 10px;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
        color: #06121A;
        font-family: 'Sora', sans-serif;
        font-weight: 800;
        font-size: 0.8rem;
        letter-spacing: 0.04em;
        display: flex; align-items: center; justify-content: center;
    }
    .brand-text {
        display: flex;
        flex-direction: column;
        line-height: 1.15;
    }
    .brand-name {
        font-family: 'Sora', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #F7FAFC;
        letter-spacing: -0.01em;
    }
    .brand-tag {
        font-size: 0.72rem;
        color: var(--muted);
        font-weight: 500;
    }
    .nav-status {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.85rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        white-space: nowrap;
    }
    .nav-status.online {
        background: rgba(45, 212, 191, 0.12);
        color: #5EEAD4;
        border: 1px solid rgba(45, 212, 191, 0.35);
    }
    .nav-status.offline {
        background: rgba(248, 113, 113, 0.12);
        color: #FCA5A5;
        border: 1px solid rgba(248, 113, 113, 0.35);
    }
    .status-dot {
        width: 7px; height: 7px; border-radius: 50%;
        background: currentColor;
    }

    .page-intro {
        margin: 0 0 1.25rem;
    }
    .page-intro h1 {
        font-family: 'Sora', sans-serif;
        font-size: 1.7rem;
        font-weight: 700;
        color: #F1F5F9;
        margin: 0 0 0.4rem;
        letter-spacing: -0.02em;
    }
    .page-intro p {
        margin: 0;
        color: var(--muted);
        font-size: 0.98rem;
        line-height: 1.55;
        max-width: 640px;
    }

    /* ---- Panels ---- */
    .panel {
        background: rgba(17, 24, 39, 0.6);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.35rem 1.45rem 1.45rem;
        box-shadow: var(--shadow-sm);
        margin-bottom: 1rem;
        transition: border-color 0.2s ease;
    }
    .panel:hover {
        border-color: var(--border-strong);
    }
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        color: var(--muted);
        margin: 0 0 0.95rem;
        padding-bottom: 0.65rem;
        border-bottom: 1px solid var(--border);
    }

    /* ---- Form field readability ---- */
    label[data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] p {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: var(--text) !important;
        letter-spacing: 0.01em;
    }
    [data-testid="stCaption"] {
        color: var(--muted-2) !important;
        font-size: 0.82rem !important;
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="select"] > div,
    .stNumberInput input,
    .stTextInput input {
        font-size: 0.95rem !important;
        color: var(--text) !important;
    }
    div[data-baseweb="input"],
    div[data-baseweb="select"] > div,
    .stNumberInput div[data-baseweb="input"] {
        background: var(--surface-2) !important;
        border-color: var(--border) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stSlider"] label p {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: var(--text) !important;
    }
    div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
        background-color: var(--accent) !important;
        box-shadow: 0 0 0 4px rgba(45, 212, 191, 0.22), 0 2px 8px rgba(0, 0, 0, 0.4);
    }
    div[data-baseweb="select"] span {
        color: var(--text) !important;
        font-size: 0.95rem !important;
    }
    /* Popover menus (selectbox dropdown) */
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li {
        background: var(--surface-solid) !important;
        color: var(--text) !important;
    }

    /* Nav page switcher */
    div[data-testid="stRadio"] {
        background: rgba(17, 24, 39, 0.6);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.4rem 0.5rem;
        margin-bottom: 1.2rem;
        box-shadow: var(--shadow-sm);
        display: inline-block;
    }
    div[data-testid="stRadio"] > label {
        display: none !important;
    }
    div[data-testid="stRadio"] [role="radiogroup"] {
        gap: 0.3rem !important;
        justify-content: flex-start !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background: transparent;
        border: 1px solid transparent;
        border-radius: 10px;
        padding: 0.45rem 1.05rem !important;
        margin: 0 !important;
        transition: background 0.2s ease, color 0.2s ease;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
        background: rgba(148, 163, 184, 0.08);
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {
        background: rgba(45, 212, 191, 0.12) !important;
        border-color: rgba(45, 212, 191, 0.3) !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] p,
    div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] span {
        color: #5EEAD4 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] p,
    div[data-testid="stRadio"] label[data-baseweb="radio"] span {
        color: var(--muted) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    /* Hide the default radio circle */
    div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
        display: none !important;
    }

    /* ---- Stat cards ---- */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.7rem;
        margin-top: 0.35rem;
    }
    .stat-card {
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.9rem 1rem;
        transition: border-color 0.2s ease;
    }
    .stat-card:hover {
        border-color: var(--border-strong);
    }
    .stat-card .k {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        color: var(--muted-2);
        margin: 0 0 0.3rem;
    }
    .stat-card .v {
        font-family: 'Sora', sans-serif;
        font-size: 1.35rem;
        font-weight: 700;
        color: #F4F8FC;
        line-height: 1.15;
    }
    .stat-card .sub {
        font-size: 0.78rem;
        color: var(--muted);
        margin-top: 0.25rem;
    }

    .gauge-wrap { margin: 0.5rem 0 0.15rem; }
    .gauge-bar {
        position: relative; height: 10px; border-radius: 999px; overflow: visible;
        background: linear-gradient(90deg,
            #38BDF8 0%, #38BDF8 14%,
            #34D399 14%, #34D399 40%,
            #FBBF24 40%, #FBBF24 60%,
            #F87171 60%, #F87171 100%);
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.4);
    }
    .gauge-marker {
        position: absolute; top: -5px; width: 2px; height: 20px;
        background: #F1F5F9; border-radius: 2px;
        transform: translateX(-1px);
    }
    .gauge-scale {
        display: flex; justify-content: space-between;
        font-size: 0.68rem; color: var(--muted-2); margin-top: 0.45rem;
    }

    .risk-track { display: flex; gap: 5px; margin-top: 0.4rem; }
    .risk-seg {
        flex: 1; height: 7px; border-radius: 999px;
        background: rgba(148, 163, 184, 0.16);
    }
    .risk-seg.on-low { background: var(--low); }
    .risk-seg.on-medium { background: var(--medium); }
    .risk-seg.on-high { background: var(--high); }

    /* ---- Buttons ---- */
    div[data-testid="stButton"] > button {
        border-radius: 11px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.2s ease !important;
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        width: 100%;
        background: linear-gradient(135deg, var(--accent) 0%, #14B8A6 100%) !important;
        color: #06121A !important;
        border: none !important;
        padding: 0.85rem 1.4rem !important;
        box-shadow: var(--shadow-sm) !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px var(--accent-glow) !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: var(--surface-2) !important;
        border: 1px solid var(--border-strong) !important;
        color: var(--text) !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }

    /* ---- Result ---- */
    .result-card {
        border-radius: 14px;
        padding: 1.8rem 1.9rem;
        color: #fff;
        text-align: left;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: var(--shadow-md);
        animation: resultIn 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .result-card::after {
        content: "";
        position: absolute; top: -40%; right: -8%;
        width: 240px; height: 240px; border-radius: 50%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.07), transparent 70%);
        pointer-events: none;
    }
    .result-card.low { background: linear-gradient(150deg, #0B3B2E 0%, #10744F 100%); }
    .result-card.medium { background: linear-gradient(150deg, #5C2C0A 0%, #A5620E 100%); }
    .result-card.high { background: linear-gradient(150deg, #5E1A1A 0%, #B22222 100%); }
    .result-card.default { background: linear-gradient(150deg, #10263C 0%, #115E6E 100%); }
    .result-card .label {
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.14em;
        text-transform: uppercase; opacity: 0.85; margin-bottom: 0.45rem;
    }
    .result-card .amount {
        font-family: 'Sora', sans-serif;
        font-size: 2.4rem; font-weight: 800; line-height: 1.1;
        margin: 0 0 0.45rem;
    }
    .result-card .hint {
        font-size: 0.95rem; opacity: 0.94; max-width: 520px; line-height: 1.5;
    }
    .insight-row {
        display: flex; gap: 0.5rem; flex-wrap: wrap;
        margin-top: 1.1rem;
    }
    .insight-pill {
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.24);
        border-radius: 999px;
        padding: 0.38rem 0.8rem;
        font-size: 0.8rem;
        font-weight: 500;
        backdrop-filter: blur(4px);
    }

    .scale-row { display: flex; gap: 0.5rem; margin-top: 0.9rem; }
    .scale-item {
        flex: 1; text-align: center; padding: 0.65rem 0.35rem;
        border-radius: 11px; font-size: 0.82rem; font-weight: 600;
        background: var(--surface);
        border: 1px solid var(--border);
        color: var(--muted);
        backdrop-filter: blur(10px);
    }
    .scale-item.active {
        background: rgba(45, 212, 191, 0.14);
        border-color: rgba(45, 212, 191, 0.35);
        color: #5EEAD4;
    }

    .confidence-badge {
        display: inline-flex; align-items: center; gap: 0.4rem;
        margin-top: 0.85rem; padding: 0.4rem 0.85rem;
        background: rgba(255,255,255,0.18);
        border: 1px solid rgba(255,255,255,0.28);
        border-radius: 999px; font-size: 0.82rem; font-weight: 600;
    }
    .confidence-badge .conf-pct {
        font-family: 'Sora', sans-serif;
        font-size: 1rem; font-weight: 700;
    }

    .prob-panel {
        margin-top: 0.9rem; padding: 1.1rem 1.2rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        backdrop-filter: blur(12px);
    }
    .prob-panel .prob-title {
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em;
        text-transform: uppercase; color: var(--muted-2); margin-bottom: 0.85rem;
    }
    .prob-row {
        display: grid; grid-template-columns: 78px 1fr 48px;
        align-items: center; gap: 0.65rem; margin-bottom: 0.6rem;
    }
    .prob-row:last-child { margin-bottom: 0; }
    .prob-row .prob-label {
        font-size: 0.85rem; font-weight: 600; color: var(--muted);
        text-transform: capitalize;
    }
    .prob-row.active .prob-label { color: var(--text); font-weight: 700; }
    .prob-track {
        height: 8px; border-radius: 999px;
        background: rgba(148, 163, 184, 0.14); overflow: hidden;
    }
    .prob-fill {
        height: 100%; border-radius: 999px;
        background: #64748B;
        animation: growWidth 0.6s ease;
    }
    .prob-row.low .prob-fill { background: linear-gradient(90deg, #059669, #34D399); }
    .prob-row.medium .prob-fill { background: linear-gradient(90deg, #D97706, #FBBF24); }
    .prob-row.high .prob-fill { background: linear-gradient(90deg, #DC2626, #F87171); }
    .prob-row .prob-pct {
        font-size: 0.82rem; font-weight: 600; color: var(--muted); text-align: right;
    }
    .prob-row.active .prob-pct { color: var(--text); }

    .loader-wrap {
        display: flex; flex-direction: column; align-items: center;
        padding: 2.4rem 1.4rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(14px);
    }
    .loader-ring {
        width: 50px; height: 50px; border-radius: 50%;
        border: 3px solid rgba(148, 163, 184, 0.18);
        border-top-color: var(--accent);
        animation: spin 0.85s linear infinite;
        margin-bottom: 1rem;
    }
    .loader-title {
        font-family: 'Sora', sans-serif;
        font-size: 1.15rem; font-weight: 600; color: #F4F8FC; margin-bottom: 0.3rem;
    }
    .loader-sub { color: var(--muted); font-size: 0.92rem; margin-bottom: 1rem; }
    .loader-track {
        width: min(320px, 80%); height: 6px; border-radius: 999px;
        background: rgba(148, 163, 184, 0.14); overflow: hidden;
    }
    .loader-fill {
        height: 100%; border-radius: 999px;
        background: linear-gradient(90deg, var(--accent), var(--accent-2));
        transition: width 0.35s ease;
    }

    .error-card {
        background: rgba(248, 113, 113, 0.1);
        border: 1px solid rgba(248, 113, 113, 0.35);
        border-radius: 14px; padding: 1.2rem 1.35rem;
        color: #FCA5A5;
    }

    .stale-note {
        display: inline-block; margin-bottom: 0.55rem;
        background: rgba(251, 191, 36, 0.12);
        border: 1px solid rgba(251, 191, 36, 0.35);
        color: #FCD34D; font-size: 0.78rem; font-weight: 600;
        padding: 0.32rem 0.75rem; border-radius: 999px;
    }

    .empty-state {
        text-align: left; padding: 1.5rem 1.4rem;
        border: 1px dashed var(--border-strong);
        border-radius: 14px; color: var(--muted);
        background: var(--surface);
        backdrop-filter: blur(10px);
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .empty-state strong { color: var(--accent); }

    .footer-note {
        text-align: center; color: var(--muted-2);
        font-size: 0.8rem; margin-top: 1.75rem;
    }

    .ref-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    .ref-table th {
        text-align: left; color: var(--accent); font-weight: 700;
        font-size: 0.72rem; letter-spacing: 0.09em; text-transform: uppercase;
        padding: 0.55rem 0.7rem; border-bottom: 1px solid var(--border-strong);
    }
    .ref-table td {
        padding: 0.6rem 0.7rem; color: var(--text);
        border-bottom: 1px solid var(--border);
    }
    .ref-table code {
        background: rgba(45, 212, 191, 0.12);
        color: #7DE9DA;
        padding: 0.1rem 0.4rem; border-radius: 6px;
        font-size: 0.85rem;
    }
    .ref-table tr:hover td { background: rgba(148, 163, 184, 0.06); }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(11, 18, 32, 0.92) !important;
        border-right: 1px solid var(--border);
        backdrop-filter: blur(14px);
    }
    section[data-testid="stSidebar"] h3 {
        font-family: 'Sora', sans-serif;
        color: #F4F8FC !important;
        font-size: 1rem !important;
    }

    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes resultIn {
        from { opacity: 0; transform: translateY(12px) scale(0.98); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes growWidth {
        from { width: 0 !important; }
    }

    @media (max-width: 768px) {
        .top-nav { flex-wrap: wrap; }
        .page-intro h1 { font-size: 1.5rem; }
        .result-card .amount { font-size: 1.95rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Derived-feature helpers (mirror the backend's computed fields)
# ---------------------------------------------------------------------------
def compute_bmi(weight: float, height: float) -> float:
    return weight / (height ** 2)


def compute_age_group(age: int) -> str:
    if age < 25:
        return "Young"
    if age < 45:
        return "Adult"
    if age < 60:
        return "Middle-aged"
    return "Senior"


def compute_lifestyle_risk(smoker: bool, bmi: float) -> str:
    if smoker and bmi > 30:
        return "High"
    if smoker or bmi > 27:
        return "Medium"
    return "Low"


def compute_city_tier(city: str) -> int:
    if city in TIER_1_CITIES:
        return 1
    if city in TIER_2_CITIES:
        return 2
    return 3


def bmi_band(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def format_occupation(value: str) -> str:
    return OCCUPATION_LABELS.get(value, value.replace("_", " ").title())


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
st.session_state.setdefault("history", [])
st.session_state.setdefault("last_result", None)
st.session_state.setdefault("api_base", DEFAULT_API_URL)
st.session_state.setdefault("nav_page", "Estimate")

for field, default in [
    ("age", 30), ("weight", 65.0), ("height", 1.70), ("income", 10.0),
    ("smoker", False), ("city", "Mumbai"), ("occupation", "private_job"),
]:
    st.session_state.setdefault(f"in_{field}", default)


def apply_preset(name: str):
    preset = PRESETS[name]
    for field, value in preset.items():
        st.session_state[f"in_{field}"] = value
    st.session_state["last_result"] = None


@st.cache_data(ttl=10, show_spinner=False)
def check_api(base_url: str) -> bool:
    try:
        requests.get(f"{base_url.rstrip('/')}/docs", timeout=3)
        return True
    except requests.exceptions.RequestException:
        return False


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------
def render_loader(slot, title: str, message: str, progress: int):
    slot.markdown(
        f"""
        <div class="loader-wrap">
            <div class="loader-ring"></div>
            <div class="loader-title">{title}</div>
            <div class="loader-sub">{message}</div>
            <div class="loader-track">
                <div class="loader-fill" style="width: {progress}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def parse_prediction(raw) -> dict:
    """Normalize API Prediction into Predicted_class / Confidence_Score / Class_Probabilities."""
    if isinstance(raw, dict):
        predicted = raw.get("Predicted_class", raw.get("predicted_class", ""))
        confidence = raw.get("Confidence_Score", raw.get("confidence_score"))
        probs = raw.get("Class_Probabilities", raw.get("class_probabilities")) or {}
        return {
            "Predicted_class": str(predicted).strip() if predicted is not None else "",
            "Confidence_Score": float(confidence) if confidence is not None else None,
            "Class_Probabilities": {str(k): float(v) for k, v in probs.items()},
        }
    if isinstance(raw, (int, float)):
        return {
            "Predicted_class": "",
            "Confidence_Score": None,
            "Class_Probabilities": {},
            "numeric": float(raw),
        }
    return {
        "Predicted_class": str(raw).strip() if raw is not None else "",
        "Confidence_Score": None,
        "Class_Probabilities": {},
    }


def render_result(prediction, payload: dict, stale: bool = False):
    bmi = compute_bmi(payload["weight"], payload["height"])
    age_group = compute_age_group(payload["age"])
    risk = compute_lifestyle_risk(payload["smoker"], bmi)
    tier = compute_city_tier(payload["city"])

    detail = parse_prediction(prediction)
    numeric = detail.get("numeric")
    confidence = detail.get("Confidence_Score")
    probs = detail.get("Class_Probabilities") or {}

    if numeric is not None:
        card_class = "default"
        title = f"₹{numeric:,.0f}"
        hint = "Estimated annual insurance premium based on your profile."
        key = None
    else:
        key = detail["Predicted_class"].strip().lower()
        card_class = key if key in CATEGORY_COPY else "default"
        title, hint = CATEGORY_COPY.get(
            key,
            (
                detail["Predicted_class"] or "Unknown",
                "Predicted premium category based on your profile.",
            ),
        )

    confidence_html = ""
    if confidence is not None:
        pct = max(0.0, min(1.0, float(confidence))) * 100
        confidence_html = (
            f'<div class="confidence-badge">'
            f'Confidence <span class="conf-pct">{pct:.0f}%</span>'
            f"</div>"
        )

    if stale:
        st.markdown(
            '<div class="stale-note">Inputs changed since this prediction — run it again to refresh</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="result-card {card_class}">
            <div class="label">Prediction result</div>
            <div class="amount">{title}</div>
            <div class="hint">{hint}</div>
            {confidence_html}
            <div class="insight-row">
                <div class="insight-pill">BMI {bmi:.1f} · {bmi_band(bmi)}</div>
                <div class="insight-pill">{age_group} ({payload['age']} yrs)</div>
                <div class="insight-pill">{risk} lifestyle risk</div>
                <div class="insight-pill">{payload['city']} · Tier {tier}</div>
                <div class="insight-pill">{format_occupation(payload['occupation'])}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if key in CATEGORY_ORDER:
        items = "".join(
            f'<div class="scale-item {"active" if c == key else ""}">{c.title()}</div>'
            for c in CATEGORY_ORDER
        )
        st.markdown(f'<div class="scale-row">{items}</div>', unsafe_allow_html=True)

    if probs:
        ordered = []
        for cat in CATEGORY_ORDER:
            match = next((k for k in probs if str(k).lower() == cat), None)
            if match is not None:
                ordered.append((cat, probs[match]))
        for label, value in probs.items():
            if str(label).lower() not in CATEGORY_ORDER:
                ordered.append((str(label), value))

        rows = "".join(
            f"""
            <div class="prob-row {label.lower()}{" active" if label.lower() == key else ""}">
                <div class="prob-label">{str(label).title()}</div>
                <div class="prob-track">
                    <div class="prob-fill" style="width: {max(0.0, min(1.0, float(value))) * 100:.1f}%;"></div>
                </div>
                <div class="prob-pct">{max(0.0, min(1.0, float(value))) * 100:.0f}%</div>
            </div>
            """
            for label, value in ordered
        )
        st.markdown(
            f"""
            <div class="prob-panel">
                <div class="prob-title">Class probabilities</div>
                {rows}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_error(message: str):
    st.markdown(
        f"""
        <div class="error-card">
            <strong>Unable to get a prediction</strong><br/>{message}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar (settings only)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Settings")

    api_base = st.text_input("API base URL", value=st.session_state["api_base"])
    st.session_state["api_base"] = api_base

    online = check_api(api_base)
    if online:
        st.success("Backend reachable")
    else:
        st.error("Backend offline")
    st.button("Re-check connection", on_click=check_api.clear, use_container_width=True)

    st.divider()
    st.markdown("**Sample profiles**")
    st.caption("Load a ready-made profile into the form.")
    for name in PRESETS:
        st.button(name, key=f"preset_{name}", on_click=apply_preset, args=(name,), use_container_width=True)

    st.divider()
    precise_mode = st.toggle("Precise number entry", value=False, help="Swap sliders for number inputs.")
    celebrate = st.toggle("Celebration effects", value=False, help="Balloons on a low-premium result.")

    if st.session_state["history"]:
        st.divider()
        st.caption(f"{len(st.session_state['history'])} prediction(s) this session")
        if st.button("Clear history", use_container_width=True):
            st.session_state["history"] = []
            st.rerun()

API_URL = f"{st.session_state['api_base'].rstrip('/')}/predict"

# ---------------------------------------------------------------------------
# Top navigation
# ---------------------------------------------------------------------------
status_class = "online" if online else "offline"
status_label = "API online" if online else "API offline"
st.markdown(
    f"""
    <div class="top-nav">
        <div class="brand">
            <div class="brand-mark">IP</div>
            <div class="brand-text">
                <span class="brand-name">InsurePredict</span>
                <span class="brand-tag">Insurance premium estimator</span>
            </div>
        </div>
        <div class="nav-status {status_class}">
            <span class="status-dot"></span>{status_label}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.radio(
    "Navigation",
    options=NAV_PAGES,
    horizontal=True,
    key="nav_page",
    label_visibility="collapsed",
)

# ---------------------------------------------------------------------------
# Estimate page
# ---------------------------------------------------------------------------
if page == "Estimate":
    st.markdown(
        """
        <div class="page-intro">
            <h1>Estimate your premium band</h1>
            <p>Enter your profile details. The model returns Low, Medium, or High with a confidence score and class probabilities.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    form_col, side_col = st.columns([1.4, 1], gap="large")

    with form_col:
        st.markdown('<div class="section-title">Personal details</div>', unsafe_allow_html=True)
        if precise_mode:
            c1, c2, c3 = st.columns(3)
            age = c1.number_input("Age (years)", min_value=1, max_value=119, step=1, key="in_age")
            weight = c2.number_input("Weight (kg)", min_value=1.0, max_value=200.0, step=0.5, format="%.1f", key="in_weight")
            height = c3.number_input("Height (m)", min_value=0.5, max_value=2.5, step=0.01, format="%.2f", key="in_height")
        else:
            age = st.slider("Age (years)", min_value=1, max_value=119, step=1, key="in_age")
            c1, c2 = st.columns(2)
            weight = c1.slider("Weight (kg)", min_value=1.0, max_value=200.0, step=0.5, format="%.1f", key="in_weight")
            height = c2.slider("Height (m)", min_value=0.5, max_value=2.5, step=0.01, format="%.2f", key="in_height")

        st.markdown('<div class="section-title">Income and lifestyle</div>', unsafe_allow_html=True)
        c4, c5 = st.columns([2, 1])
        with c4:
            if precise_mode:
                income_lpa = st.number_input(
                    "Annual income (LPA)", min_value=0.1, max_value=100.0, step=0.5, format="%.1f",
                    key="in_income", help="Income in lakhs per annum",
                )
            else:
                income_lpa = st.slider(
                    "Annual income (LPA)", min_value=0.1, max_value=100.0, step=0.1, format="%.1f",
                    key="in_income", help="Income in lakhs per annum",
                )
            st.caption("LPA = lakhs per annum")
        with c5:
            smoker = st.toggle("Smoker", key="in_smoker", help="Smoking raises the lifestyle-risk factor.")
            st.caption("Currently: Yes" if smoker else "Currently: No")

        st.markdown('<div class="section-title">Location and work</div>', unsafe_allow_html=True)
        city = st.selectbox(
            "City", options=ALL_CITIES, key="in_city",
            help="City tier is derived automatically and sent to the model.",
        )
        selected_occupation = st.segmented_control(
            "Occupation", options=OCCUPATIONS, format_func=format_occupation,
            key="in_occupation", selection_mode="single",
        )
        occupation = selected_occupation or "private_job"
        if selected_occupation is None:
            st.caption(f"No occupation selected — defaulting to {format_occupation(occupation)}.")

        st.write("")
        predict_clicked = st.button("Predict my premium", type="primary", use_container_width=True)
        if not online:
            st.caption("Backend looks offline. Start the FastAPI server, then re-check the connection in Settings.")

    bmi_preview = compute_bmi(weight, height)
    risk_preview = compute_lifestyle_risk(smoker, bmi_preview)
    tier_preview = compute_city_tier(city)
    age_group_preview = compute_age_group(age)
    marker_pos = min(max((bmi_preview - 15) / 25 * 100, 0), 100)
    risk_idx = {"Low": 1, "Medium": 2, "High": 3}[risk_preview]
    risk_segs = "".join(
        f'<div class="risk-seg {"on-" + risk_preview.lower() if i < risk_idx else ""}"></div>'
        for i in range(3)
    )

    with side_col:
        st.markdown(
            f"""
            <div class="panel">
                <div class="section-title">Live risk profile</div>
                <div class="stat-card" style="margin-bottom:0.7rem;">
                    <div class="k">Body mass index</div>
                    <div class="v">{bmi_preview:.1f} <span style="font-size:0.88rem;color:var(--muted);font-weight:600;">{bmi_band(bmi_preview)}</span></div>
                    <div class="gauge-wrap">
                        <div class="gauge-bar"><div class="gauge-marker" style="left:{marker_pos:.1f}%;"></div></div>
                        <div class="gauge-scale"><span>15</span><span>18.5</span><span>25</span><span>30</span><span>40</span></div>
                    </div>
                </div>
                <div class="stat-card" style="margin-bottom:0.7rem;">
                    <div class="k">Lifestyle risk</div>
                    <div class="v">{risk_preview}</div>
                    <div class="risk-track">{risk_segs}</div>
                    <div class="sub">{'Smoker' if smoker else 'Non-smoker'} · BMI {bmi_preview:.1f}</div>
                </div>
                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="k">Age group</div>
                        <div class="v" style="font-size:1.1rem;">{age_group_preview}</div>
                        <div class="sub">{age} years</div>
                    </div>
                    <div class="stat-card">
                        <div class="k">City tier</div>
                        <div class="v" style="font-size:1.1rem;">Tier {tier_preview}</div>
                        <div class="sub">{city}</div>
                    </div>
                    <div class="stat-card">
                        <div class="k">Occupation</div>
                        <div class="v" style="font-size:1rem;">{format_occupation(occupation)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="k">Income</div>
                        <div class="v" style="font-size:1rem;">₹{income_lpa:.1f} LPA</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    result_slot = st.empty()

    current_payload = {
        "age": int(age),
        "weight": float(weight),
        "height": float(height),
        "income_lpa": float(income_lpa),
        "smoker": bool(smoker),
        "city": city,
        "occupation": occupation,
    }

    if predict_clicked:
        stages = [
            ("Validating your profile", 22),
            ("Deriving BMI, age group and city tier", 48),
            ("Running the model", 74),
        ]
        for message, progress in stages:
            render_loader(result_slot, "Estimating your premium", message, progress)
            time.sleep(0.35)

        try:
            response = requests.post(API_URL, json=current_payload, timeout=30)

            if response.status_code == 200:
                prediction = parse_prediction(response.json().get("Prediction"))
                predicted_class = prediction["Predicted_class"]
                confidence = prediction.get("Confidence_Score")
                render_loader(result_slot, "Estimating your premium", "Preparing your result", 100)
                time.sleep(0.25)
                result_slot.empty()

                st.session_state["last_result"] = {
                    "prediction": prediction,
                    "payload": current_payload,
                }
                history_row = {
                    "Time": datetime.now().strftime("%H:%M:%S"),
                    "Prediction": predicted_class.title() if predicted_class else "—",
                    "Age": current_payload["age"],
                    "BMI": round(compute_bmi(current_payload["weight"], current_payload["height"]), 1),
                    "Smoker": "Yes" if current_payload["smoker"] else "No",
                    "City": current_payload["city"],
                    "Tier": compute_city_tier(current_payload["city"]),
                    "Occupation": format_occupation(current_payload["occupation"]),
                    "Income (LPA)": current_payload["income_lpa"],
                }
                if confidence is not None:
                    history_row["Confidence"] = f"{max(0.0, min(1.0, float(confidence))) * 100:.0f}%"
                st.session_state["history"].append(history_row)

                if celebrate and predicted_class.strip().lower() == "low":
                    st.balloons()
            else:
                detail = response.text
                try:
                    detail = response.json().get("detail", detail)
                except ValueError:
                    pass
                result_slot.empty()
                st.session_state["last_result"] = None
                render_error(f"Server returned {response.status_code}. {detail}")
        except requests.exceptions.ConnectionError:
            result_slot.empty()
            st.session_state["last_result"] = None
            render_error(
                f"Cannot reach the prediction API at <code>{API_URL}</code>. "
                "Make sure the FastAPI backend is running."
            )
        except requests.exceptions.Timeout:
            result_slot.empty()
            st.session_state["last_result"] = None
            render_error("The request timed out. Please try again.")
        except requests.exceptions.RequestException as exc:
            result_slot.empty()
            st.session_state["last_result"] = None
            render_error(str(exc))

    last = st.session_state["last_result"]
    if last:
        render_result(last["prediction"], last["payload"], stale=last["payload"] != current_payload)
    elif not predict_clicked:
        st.markdown(
            """
            <div class="empty-state">
                Fill in your details and select <strong>Predict my premium</strong> to see your estimated band,
                confidence score, and class probabilities.
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# How it works
# ---------------------------------------------------------------------------
elif page == "How it works":
    st.markdown(
        """
        <div class="page-intro">
            <h1>How the estimate is built</h1>
            <p>Your raw inputs are converted into six engineered features before they reach the model.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    age = st.session_state["in_age"]
    weight = st.session_state["in_weight"]
    height = st.session_state["in_height"]
    income_lpa = st.session_state["in_income"]
    smoker = st.session_state["in_smoker"]
    city = st.session_state["in_city"]
    occupation = st.session_state["in_occupation"] or "private_job"

    feature_rows = [
        ("bmi", f"{compute_bmi(weight, height):.2f}", "weight ÷ height²"),
        ("age_group", compute_age_group(age).lower().replace("-", "_"), "young &lt; 25 · adult &lt; 45 · middle_aged &lt; 60 · senior"),
        ("lifestyle_risk", compute_lifestyle_risk(smoker, compute_bmi(weight, height)).lower(), "smoker and BMI together"),
        ("city_tier", str(compute_city_tier(city)), "metro list lookup, default tier 3"),
        ("income_lpa", f"{income_lpa:.1f}", "passed through as-is"),
        ("occupation", occupation, "passed through as-is"),
    ]
    rows_html = "".join(
        f"<tr><td><code>{name}</code></td><td><strong>{value}</strong></td><td>{rule}</td></tr>"
        for name, value, rule in feature_rows
    )
    st.markdown(
        f"""
        <div class="panel">
            <div class="section-title">Features sent to the model</div>
            <table class="ref-table">
                <tr><th>Feature</th><th>Your value</th><th>Derived from</th></tr>
                {rows_html}
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ins1, ins2 = st.columns(2)
    with ins1:
        st.markdown(
            """
            <div class="panel">
                <div class="section-title">BMI reference</div>
                <table class="ref-table">
                    <tr><th>Band</th><th>Range</th></tr>
                    <tr><td>Underweight</td><td>below 18.5</td></tr>
                    <tr><td>Normal</td><td>18.5 – 24.9</td></tr>
                    <tr><td>Overweight</td><td>25 – 29.9</td></tr>
                    <tr><td>Obese</td><td>30 and above</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ins2:
        st.markdown(
            """
            <div class="panel">
                <div class="section-title">Lifestyle risk rules</div>
                <table class="ref-table">
                    <tr><th>Risk</th><th>Condition</th></tr>
                    <tr><td>High</td><td>smoker and BMI above 30</td></tr>
                    <tr><td>Medium</td><td>smoker, or BMI above 27</td></tr>
                    <tr><td>Low</td><td>neither of the above</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("City tier reference"):
        tcol1, tcol2 = st.columns(2)
        tcol1.markdown("**Tier 1**\n\n" + " · ".join(TIER_1_CITIES))
        tcol2.markdown(f"**Tier 2** ({len(TIER_2_CITIES)} cities)\n\n" + " · ".join(TIER_2_CITIES))
        st.caption("Any city outside these lists is treated as tier 3.")

# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------
else:
    st.markdown(
        """
        <div class="page-intro">
            <h1>Session history</h1>
            <p>Predictions from this browser session. Download as CSV if you need a record.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history = st.session_state["history"]
    if not history:
        st.markdown(
            """
            <div class="empty-state">
                No predictions yet. Run an estimate on the Estimate page to build session history.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        df = pd.DataFrame(history)
        counts = df["Prediction"].value_counts()
        mcols = st.columns(4)
        mcols[0].metric("Total runs", len(df))
        for i, cat in enumerate(["Low", "Medium", "High"]):
            mcols[i + 1].metric(f"{cat} premium", int(counts.get(cat, 0)))

        st.dataframe(df.iloc[::-1], width="stretch", hide_index=True)

        chart_df = pd.DataFrame(
            {"Predictions": [int(counts.get(c, 0)) for c in ["Low", "Medium", "High"]]},
            index=["Low", "Medium", "High"],
        )
        st.bar_chart(chart_df, color="#2DD4BF", height=240)

        st.download_button(
            "Download history as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="insurepredict_history.csv",
            mime="text/csv",
            use_container_width=True,
        )

st.markdown(
    """
    <div class="footer-note">
        Estimates are indicative and for guidance only · Not a formal insurance quotation
    </div>
    """,
    unsafe_allow_html=True,
)
