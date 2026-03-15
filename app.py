import streamlit as st
import os
import tempfile
import sys
import io
import contextlib

# Add dependencies explicitly so that integrate.py can find them
WATERMARK_DIR = r"c:\design_Projects\Audio-Watermarking\src"
FINGERPRINT_DIR = r"c:\design_Projects\fingerprinting"

if WATERMARK_DIR not in sys.path:
    sys.path.append(WATERMARK_DIR)
if FINGERPRINT_DIR not in sys.path:
    sys.path.append(FINGERPRINT_DIR)

from integrate import apply_watermark, add_to_fingerprint_db, match_fingerprint, extract_watermark, check_database

st.set_page_config(
    page_title="SoundSeal — Audio Protection",
    layout="wide",
    page_icon="🔒",
    initial_sidebar_state="collapsed"
)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"

# ── GLOBAL STYLES ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Share+Tech+Mono&family=Barlow:wght@300;400;500;600;700&family=Barlow+Condensed:wght@400;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:        #040404;
    --surface:   #0c0c0c;
    --panel:     #101010;
    --border:    #1e1e1e;
    --border2:   #2d2d2d;
    --accent:    #c9b8ff;
    --accent-dim: rgba(201,184,255,0.12);
    --accent-glow: rgba(201,184,255,0.4);
    --red:       #ff3333;
    --text:      #ffb3d9;
    --muted:     #c084a0;
    --font-display: 'Bebas Neue', sans-serif;
    --font-body:    'Barlow', sans-serif;
    --font-cond:    'Barlow Condensed', sans-serif;
    --font-mono:    'Share Tech Mono', monospace;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #3a2540; border-radius: 2px; }

body, .stApp {
    background-color: var(--bg) !important;
    font-family: var(--font-body);
    color: var(--text);
    overflow-x: hidden;
}

/* ── MARQUEE ── */
.marquee-wrap {
    background: var(--accent);
    overflow: hidden;
    padding: 9px 0;
    position: relative;
    z-index: 100;
}
.marquee-track {
    display: flex;
    white-space: nowrap;
    animation: ticker 30s linear infinite;
    width: max-content;
}
.marquee-item {
    font-family: var(--font-display);
    font-size: 0.85rem;
    color: #000;
    padding: 0 2rem;
    letter-spacing: 0.1em;
}
@keyframes ticker {
    from { transform: translateX(0); }
    to   { transform: translateX(-50%); }
}

/* ── NAV BAR VISUAL ── */
.nav-bar-visual {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 56px;
    height: 64px;
    border-bottom: 1px solid var(--border);
    background: rgba(4,4,4,0.98);
    position: relative;
    z-index: 99;
}
.nav-logo {
    font-family: var(--font-display);
    font-size: 1.6rem;
    letter-spacing: 0.05em;
    color: var(--text);
}
.nav-logo span { color: var(--accent); }
.nav-placeholder {
    display: flex;
    gap: 4px;
    align-items: center;
}
.nav-pill {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 7px 18px;
    border-radius: 2px;
    border: 1px solid transparent;
    color: var(--muted);
    background: transparent;
}
.nav-pill.active-pill {
    color: #000;
    background: var(--accent);
    border-color: var(--accent);
    font-weight: 600;
}

/* ── NAV BUTTONS CONTAINER ── */
.nav-buttons-row {
    position: absolute;
    top: 0;
    right: 56px;
    height: 64px;
    display: flex;
    align-items: center;
    gap: 4px;
    z-index: 100;
}

/* Make nav buttons look like nav pills */
.nav-buttons-row .stButton > button {
    background: transparent !important;
    color: var(--muted) !important;
    border: 1px solid transparent !important;
    font-family: var(--font-mono) !important;
    font-size: 0.7rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    padding: 7px 18px !important;
    border-radius: 2px !important;
    box-shadow: none !important;
    transform: none !important;
    transition: all 0.2s !important;
    height: 36px !important;
    line-height: 1 !important;
    min-height: unset !important;
}
.nav-buttons-row .stButton > button:hover {
    color: var(--text) !important;
    border-color: var(--border2) !important;
    box-shadow: none !important;
    transform: none !important;
    background: transparent !important;
}

/* Active nav button override */
.nav-active .stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border-color: var(--accent) !important;
    font-weight: 600 !important;
}
.nav-active .stButton > button:hover {
    background: var(--accent) !important;
    color: #000 !important;
    box-shadow: 0 0 20px rgba(201,184,255,0.3) !important;
    transform: none !important;
}

/* ── HERO CTA BUTTONS ── */
.hero-cta-row {
    display: flex;
    gap: 20px;
    justify-content: center;
    padding: 20px 0 48px;
}

/* Large CTA Ingest button */
.cta-ingest-wrap .stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    font-family: var(--font-cond) !important;
    font-size: 1.15rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    padding: 20px 52px !important;
    border-radius: 2px !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 0 0px rgba(201,184,255,0) !important;
    position: relative !important;
    width: 280px !important;
    height: 64px !important;
}
.cta-ingest-wrap .stButton > button:hover {
    box-shadow: 0 0 40px rgba(201,184,255,0.45), 0 0 80px rgba(201,184,255,0.15) !important;
    transform: translateY(-3px) !important;
    filter: brightness(1.08) !important;
}
.cta-ingest-wrap .stButton > button:active {
    transform: translateY(0px) !important;
    box-shadow: 0 0 20px rgba(201,184,255,0.3) !important;
}

/* Large CTA Verify button */
.cta-verify-wrap .stButton > button {
    background: transparent !important;
    color: var(--accent) !important;
    border: 1px solid rgba(201,184,255,0.5) !important;
    font-family: var(--font-cond) !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    padding: 20px 52px !important;
    border-radius: 2px !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
    width: 280px !important;
    height: 64px !important;
    box-shadow: inset 0 0 0px rgba(201,184,255,0) !important;
}
.cta-verify-wrap .stButton > button:hover {
    background: rgba(201,184,255,0.07) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 30px rgba(201,184,255,0.2), inset 0 0 20px rgba(201,184,255,0.05) !important;
    transform: translateY(-3px) !important;
}
.cta-verify-wrap .stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── ACTION BUTTON (Process / Verify inside pages) ── */
.action-btn-wrap {
    display: flex;
    justify-content: flex-start;
    padding: 0 0 24px;
}
.action-btn-wrap .stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    font-family: var(--font-cond) !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    padding: 16px 44px !important;
    border-radius: 2px !important;
    height: 54px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 0px rgba(201,184,255,0) !important;
}
.action-btn-wrap .stButton > button:hover {
    box-shadow: 0 0 35px rgba(201,184,255,0.4) !important;
    transform: translateY(-2px) !important;
    filter: brightness(1.05) !important;
}
.action-btn-wrap .stButton > button:active {
    transform: translateY(0) !important;
}

/* ── HERO ── */
.hero-wrap {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 0px 64px 0px;
    overflow: hidden;
}
.hero-content {
    position: relative;
    z-index: 2;
    text-align: center;
    max-width: 900px;
    margin: 0 auto;
}
.hero-tag {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--accent);
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}
.hero-title {
    font-family: var(--font-display);
    font-size: clamp(5rem, 10vw, 9.5rem);
    line-height: 0.9;
    letter-spacing: 0.01em;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 24px;
}
.hero-title em {
    font-style: normal;
    color: var(--accent);
}
.hero-desc {
    font-family: var(--font-body);
    font-size: 1.05rem;
    color: var(--muted);
    line-height: 1.7;
    max-width: 540px;
    margin: 0 auto 36px;
    font-weight: 300;
}
.hero-desc strong { color: var(--text); font-weight: 600; }

/* CTA label above buttons */
.cta-label {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: #333;
    text-transform: uppercase;
    text-align: center;
    margin-bottom: 6px;
}

/* ── FEATURE ROW ── */
.feature-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    border-top: 1px solid var(--border);
}
.feature-cell {
    padding: 36px 32px;
    border-right: 1px solid var(--border);
    position: relative;
    overflow: hidden;
    transition: background 0.3s;
}
.feature-cell:last-child { border-right: none; }
.feature-cell:hover { background: var(--surface); }
.feature-cell::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.3s;
}
.feature-cell:hover::before { transform: scaleX(1); }
.feature-icon {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--accent);
    letter-spacing: 0.2em;
    margin-bottom: 14px;
}
.feature-name {
    font-family: var(--font-cond);
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 8px;
}
.feature-desc {
    font-size: 0.82rem;
    color: var(--muted);
    line-height: 1.6;
}

/* ── PAGE LAYOUT ── */
.page-wrap { min-height: 100vh; background: var(--bg); }
.page-header {
    padding: 64px 64px 0;
    border-bottom: 1px solid var(--border);
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 500px; height: 300px;
    background: radial-gradient(ellipse at top right, rgba(201,184,255,0.04) 0%, transparent 70%);
    pointer-events: none;
}
.page-eyebrow {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--accent);
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.page-eyebrow::before {
    content: '';
    width: 20px;
    height: 1px;
    background: var(--accent);
}
.page-title {
    font-family: var(--font-display);
    font-size: clamp(3.5rem, 7vw, 6rem);
    line-height: 0.9;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 16px;
}
.page-title span { color: var(--accent); }
.page-sub {
    font-size: 0.95rem;
    color: var(--muted);
    max-width: 520px;
    line-height: 1.7;
    font-weight: 300;
    padding-bottom: 40px;
}
.page-num {
    position: absolute;
    top: 64px;
    right: 64px;
    font-family: var(--font-display);
    font-size: 8rem;
    color: rgba(255,179,217,0.04);
    line-height: 1;
    pointer-events: none;
}

/* ── STEPS ── */
.steps-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
    padding: 48px 64px;
    border-bottom: 1px solid var(--border);
}
.step-item {
    padding: 0 28px 0 0;
    border-right: 1px solid var(--border);
    margin-right: 28px;
}
.step-item:last-child { border-right: none; padding-right: 0; margin-right: 0; }
.step-n {
    font-family: var(--font-display);
    font-size: 3.5rem;
    color: #2d1f35;
    line-height: 1;
    margin-bottom: 10px;
}
.step-l {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 7px;
}
.step-d { font-size: 0.82rem; color: var(--muted); line-height: 1.6; }

/* ── UPLOAD ZONE ── */
.upload-section { padding: 48px 64px 32px; }
.upload-zone-wrapper { position: relative; }
.upload-zone-deco {
    position: absolute;
    inset: -1px;
    border: 1px solid var(--border2);
    border-radius: 4px;
    pointer-events: none;
    z-index: 1;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.upload-zone-wrapper:hover .upload-zone-deco {
    border-color: rgba(201,184,255,0.3);
    box-shadow: 0 0 40px rgba(201,184,255,0.05), inset 0 0 40px rgba(201,184,255,0.02);
}
.upload-corner {
    position: absolute;
    width: 14px;
    height: 14px;
    z-index: 2;
    pointer-events: none;
}
.upload-corner.tl { top: -1px; left: -1px; border-top: 2px solid var(--accent); border-left: 2px solid var(--accent); }
.upload-corner.tr { top: -1px; right: -1px; border-top: 2px solid var(--accent); border-right: 2px solid var(--accent); }
.upload-corner.bl { bottom: -1px; left: -1px; border-bottom: 2px solid var(--accent); border-left: 2px solid var(--accent); }
.upload-corner.br { bottom: -1px; right: -1px; border-bottom: 2px solid var(--accent); border-right: 2px solid var(--accent); }
.upload-label {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 10px;
}
.upload-hint {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    color: #3a3a3a;
    letter-spacing: 0.15em;
    margin-top: 10px;
}

/* ── RESULT CARDS ── */
.result-section { padding: 0 64px 64px; }
.result-panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 3px;
    overflow: hidden;
}
.result-panel-header {
    padding: 14px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--surface);
}
.result-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--border2); }
.result-dot.green { background: var(--accent); box-shadow: 0 0 8px var(--accent-glow); }
.result-dot.red { background: var(--red); box-shadow: 0 0 8px rgba(255,51,51,0.5); }
.result-panel-title {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
}
.result-panel-body { padding: 20px; }
.result-status {
    font-family: var(--font-cond);
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.result-status.ok { color: var(--accent); }
.result-status.fail { color: var(--red); }
.result-msg { font-size: 0.82rem; color: var(--muted); line-height: 1.6; }
.payload-box {
    background: rgba(201,184,255,0.04);
    border: 1px solid rgba(201,184,255,0.15);
    border-radius: 2px;
    padding: 14px 16px;
    margin-top: 12px;
    font-family: var(--font-mono);
    font-size: 0.85rem;
    color: var(--accent);
    word-break: break-all;
    line-height: 1.5;
}

/* ── STREAMLIT OVERRIDES ── */
div[data-testid="stFileUploader"] > label { display: none !important; }
div[data-testid="stFileUploader"] > div {
    background: var(--surface) !important;
    border: 1px dashed #252525 !important;
    border-radius: 3px !important;
    min-height: 160px !important;
    transition: all 0.25s !important;
}
div[data-testid="stFileUploader"] > div:hover {
    border-color: rgba(201,184,255,0.35) !important;
    background: rgba(201,184,255,0.02) !important;
}
div[data-testid="stFileUploader"] p {
    font-family: var(--font-mono) !important;
    font-size: 0.75rem !important;
    color: #444 !important;
    letter-spacing: 0.1em !important;
}
div[data-testid="stFileUploader"] small {
    font-family: var(--font-mono) !important;
    font-size: 0.6rem !important;
    color: #333 !important;
}
div[data-testid="stFileUploader"] button {
    background: transparent !important;
    border: 1px solid var(--border2) !important;
    color: var(--muted) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    border-radius: 2px !important;
    padding: 6px 16px !important;
    transition: all 0.2s !important;
}
div[data-testid="stFileUploader"] button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* Default stButton (for action buttons not in special wrappers) */
.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    font-family: var(--font-cond) !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    padding: 13px 36px !important;
    border-radius: 2px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    box-shadow: 0 0 25px rgba(201,184,255,0.25) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(1px) !important; }

.stDownloadButton > button {
    background: transparent !important;
    color: var(--accent) !important;
    border: 1px solid rgba(201,184,255,0.4) !important;
    font-family: var(--font-cond) !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    padding: 11px 28px !important;
    border-radius: 2px !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: rgba(201,184,255,0.06) !important;
    box-shadow: 0 0 20px rgba(201,184,255,0.15) !important;
}

.stSpinner > div { border-top-color: var(--accent) !important; }

.stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: #555 !important;
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important;
    border-radius: 2px !important;
}

details {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
}
details summary {
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    color: var(--muted) !important;
    padding: 10px 16px !important;
    cursor: pointer !important;
}

/* ── FOOTER ── */
.site-footer {
    border-top: 1px solid var(--border);
    padding: 24px 64px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 40px;
}
.footer-logo { font-family: var(--font-display); font-size: 1.2rem; color: #5a3050; letter-spacing: 0.08em; }
.footer-meta { font-family: var(--font-mono); font-size: 0.6rem; color: #5a3050; letter-spacing: 0.14em; text-transform: uppercase; }

/* ── ANIMATIONS ── */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
.page-animate { animation: fadeIn 0.5s ease forwards; }

/* ── DIVIDER ── */
div[data-testid="stHorizontalBlock"] { gap: 0 !important; }

/* column padding reset for nav area */
.nav-col div[data-testid="column"] { padding: 0 4px !important; }
</style>
""", unsafe_allow_html=True)

# ── MARQUEE HTML ──────────────────────────────────────────────────────────────
MARQUEE_ITEMS = "PERTH ENGINE ◆ AUDFPRINT ◆ WATERMARK ◆ FINGERPRINT ◆ PROTECT ◆ VERIFY ◆ AUTHENTICATE ◆ SOUNDSEAL ◆ RIGHTS MANAGEMENT ◆ AUDIO PROVENANCE ◆ "
st.markdown(f"""
<div class="marquee-wrap">
  <div class="marquee-track">
    <span class="marquee-item">{MARQUEE_ITEMS * 6}</span>
    <span class="marquee-item">{MARQUEE_ITEMS * 6}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── NAV ──────────────────────────────────────────────────────────────────────
# Draw logo side
page = st.session_state.page

st.markdown("""
<div class="nav-bar-visual">
  <div class="nav-logo">Sound<span>Seal</span></div>
  <div style="width:360px;"></div>
</div>
""", unsafe_allow_html=True)

# Overlay actual buttons on top of nav using negative margin trick
st.markdown("""
<style>
/* Pull the nav button row up into the nav bar */
.nav-row-container {
    position: relative;
    margin-top: -56px;
    margin-bottom: 0;
    padding-right: 56px;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    height: 48px;
    z-index: 200;
    pointer-events: none;
}
.nav-row-container > * { pointer-events: auto; }

/* Target the specific row we create for nav */
div[data-testid="stHorizontalBlock"].nav-button-row {
    position: relative;
    margin-top: -60px !important;
    padding-right: 56px !important;
    justify-content: flex-end !important;
    z-index: 200 !important;
    background: transparent !important;
    gap: 4px !important;
}
div[data-testid="stHorizontalBlock"].nav-button-row > div[data-testid="column"] {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
    padding: 0 2px !important;
}
</style>
""", unsafe_allow_html=True)

# Use a container to hold nav buttons
with st.container():
    st.markdown('<div class="nav-button-row" data-testid="stHorizontalBlock">', unsafe_allow_html=True)
    nav_cols = st.columns([6, 1, 1, 1])
    
    with nav_cols[1]:
        home_cls = "nav-active" if page == "home" else ""
        st.markdown(f'<div class="{home_cls}">', unsafe_allow_html=True)
        if st.button("HOME", key="nav_home_btn"):
            st.session_state.page = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with nav_cols[2]:
        ingest_cls = "nav-active" if page == "ingest" else ""
        st.markdown(f'<div class="{ingest_cls}">', unsafe_allow_html=True)
        if st.button("INGEST", key="nav_ingest_btn"):
            st.session_state.page = "ingest"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with nav_cols[3]:
        verify_cls = "nav-active" if page == "verify" else ""
        st.markdown(f'<div class="{verify_cls}">', unsafe_allow_html=True)
        if st.button("VERIFY", key="nav_verify_btn"):
            st.session_state.page = "verify"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Style the nav buttons (applied after render)
st.markdown("""
<style>
/* Style nav buttons — target by key pattern */
div[data-testid="stHorizontalBlock"]:has(button[kind="secondary"]) {
    margin-top: -60px;
    padding-right: 56px;
    justify-content: flex-end;
    z-index: 200;
    background: transparent;
    position: relative;
}

/* Nav button default style */
div[data-testid="stHorizontalBlock"] div[data-testid="column"]:has(button[kind="secondary"]) .stButton > button,
div[data-testid="stHorizontalBlock"] div[data-testid="column"] .nav-active + div .stButton > button {
    background: transparent !important;
    color: var(--muted) !important;
    border: 1px solid transparent !important;
    font-family: var(--font-mono) !important;
    font-size: 0.7rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    padding: 7px 18px !important;
    border-radius: 2px !important;
    box-shadow: none !important;
    height: 36px !important;
    min-height: 36px !important;
}

.nav-active .stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border-color: var(--accent) !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    transform: none !important;
}
.nav-active .stButton > button:hover {
    background: var(--accent) !important;
    color: #000 !important;
    box-shadow: 0 0 16px rgba(201,184,255,0.3) !important;
    transform: none !important;
    filter: brightness(1.05) !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ═══════════════════════════════════════════════════════════════════════════════
if page == "home":
    # 3D Waveform canvas
    st.components.v1.html("""
<!DOCTYPE html>
<html>
<head>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background: transparent; overflow: hidden; }
canvas { display: block; }
</style>
</head>
<body>
<canvas id="c"></canvas>
<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
canvas.width  = window.innerWidth  || 1400;
canvas.height = 480;

const W = canvas.width, H = canvas.height;
const BARS = 96;
const BAR_W = (W * 0.85) / BARS;
const BAR_GAP = BAR_W * 0.28;
const START_X = W * 0.075;

let t = 0;
const phases   = Array.from({length: BARS}, () => Math.random() * Math.PI * 2);
const freqs    = Array.from({length: BARS}, (_, i) => 0.6 + (i / BARS) * 1.2);
const amps     = Array.from({length: BARS}, (_, i) => {
    const x = i / BARS;
    return 0.3 + 0.7 * Math.sin(x * Math.PI) * (0.7 + Math.random() * 0.3);
});

function easeInOut(x) {
    return x < 0.5 ? 2*x*x : 1 - Math.pow(-2*x+2,2)/2;
}

function draw() {
    ctx.clearRect(0, 0, W, H);
    const cy = H * 0.5;
    const maxH = H * 0.42;

    for (let i = 0; i < BARS; i++) {
        const wave =
            Math.sin(t * freqs[i] + phases[i]) * 0.5 +
            Math.sin(t * freqs[i] * 0.5 + phases[i] * 1.3) * 0.3 +
            Math.sin(t * freqs[i] * 2 + phases[i] * 0.7) * 0.2;

        const h = Math.abs(wave) * amps[i] * maxH;
        const x = START_X + i * (BAR_W);
        const bw = BAR_W - BAR_GAP;
        const xNorm = Math.abs(i / BARS - 0.5) * 2;
        const alphaScale = 0.5 + 0.5 * easeInOut(1 - xNorm * 0.5);
        const heightNorm = h / maxH;
        const r = Math.round(180 + heightNorm * 20);
        const g = Math.round(160 + heightNorm * 24);
        const b = 255;
        const alpha = (0.25 + heightNorm * 0.55) * alphaScale;

        const grad = ctx.createLinearGradient(0, cy - h, 0, cy);
        grad.addColorStop(0, `rgba(${r},${g},${b},${alpha})`);
        grad.addColorStop(0.6, `rgba(${r},${g},${b},${alpha * 0.6})`);
        grad.addColorStop(1, `rgba(${r},${g},${b},0)`);
        ctx.fillStyle = grad;
        ctx.fillRect(x, cy - h, bw, h);

        const grad2 = ctx.createLinearGradient(0, cy, 0, cy + h);
        grad2.addColorStop(0, `rgba(${r},${g},${b},${alpha * 0.4})`);
        grad2.addColorStop(1, `rgba(${r},${g},${b},0)`);
        ctx.fillStyle = grad2;
        ctx.fillRect(x, cy, bw, h);

        if (heightNorm > 0.55) {
            ctx.shadowColor = `rgba(201,184,255,0.6)`;
            ctx.shadowBlur = 8;
            ctx.fillStyle = `rgba(201,184,255,${(heightNorm - 0.55) * 0.6 * alphaScale})`;
            ctx.fillRect(x, cy - h, bw, 2);
            ctx.shadowBlur = 0;
        }
    }

    ctx.strokeStyle = 'rgba(201,184,255,0.08)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(START_X, cy);
    ctx.lineTo(START_X + BARS * BAR_W, cy);
    ctx.stroke();

    t += 0.018;
    requestAnimationFrame(draw);
}
draw();
</script>
</body>
</html>
""", height=480, scrolling=False)

    # Hero text — centered
    st.markdown("""
<div class="hero-wrap page-animate">
  <div class="hero-content">
    <div class="hero-tag">Integrated Audio Protection System</div>
    <div class="hero-title">Sound<em>Seal</em></div>
    <div class="hero-desc">
      Embed invisible ownership cues with <strong>Perth</strong> and extract acoustic landmarks 
      with <strong>audfprint</strong> — a unified pipeline for audio provenance and rights management.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── BIG CTA BUTTONS ── centered, prominent, working
    st.markdown('<div class="cta-label">— Select an action to begin —</div>', unsafe_allow_html=True)
    
    col_l, col_ingest, col_gap, col_verify, col_r = st.columns([2, 2, 0.3, 2, 2])

    with col_ingest:
        st.markdown('<div class="cta-ingest-wrap">', unsafe_allow_html=True)
        if st.button("⬡  INGEST AUDIO", key="home_go_ingest"):
            st.session_state.page = "ingest"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_verify:
        st.markdown('<div class="cta-verify-wrap">', unsafe_allow_html=True)
        if st.button("◈  VERIFY AUDIO", key="home_go_verify"):
            st.session_state.page = "verify"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Sub-labels under buttons
    col_l2, col_il, col_g2, col_vl, col_r2 = st.columns([2, 2, 0.3, 2, 2])
    with col_il:
        st.markdown('<div style="text-align:center; font-family:\'Share Tech Mono\',monospace; font-size:0.6rem; color:#2d2d2d; letter-spacing:0.15em; margin-top:6px;">WATERMARK + FINGERPRINT</div>', unsafe_allow_html=True)
    with col_vl:
        st.markdown('<div style="text-align:center; font-family:\'Share Tech Mono\',monospace; font-size:0.6rem; color:#2d2d2d; letter-spacing:0.15em; margin-top:6px;">MATCH + EXTRACT PAYLOAD</div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("""
<div class="feature-row">
  <div class="feature-cell">
    <div class="feature-icon">01 ── ENGINE</div>
    <div class="feature-name">Perth Watermark</div>
    <div class="feature-desc">Imperceptible ownership payload embedded directly into the audio signal.</div>
  </div>
  <div class="feature-cell">
    <div class="feature-icon">02 ── ENGINE</div>
    <div class="feature-name">Audfprint</div>
    <div class="feature-desc">Acoustic landmark extraction and database registration for rapid matching.</div>
  </div>
  <div class="feature-cell">
    <div class="feature-icon">03 ── FORMAT</div>
    <div class="feature-name">WAV Input</div>
    <div class="feature-desc">High-fidelity lossless audio — optimal for watermark integrity.</div>
  </div>
  <div class="feature-cell">
    <div class="feature-icon">04 ── STORAGE</div>
    <div class="feature-name">Local DB</div>
    <div class="feature-desc">Fingerprint database stored locally — zero cloud dependency.</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# INGEST PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "ingest":
    st.markdown("""
<div class="page-header page-animate">
  <div class="page-eyebrow">Process ── Protect ── Register</div>
  <div class="page-title">Ingest <span>Audio</span></div>
  <div class="page-sub">
    Upload a WAV file to embed an invisible watermark and register its acoustic 
    fingerprint to the protection database.
  </div>
  <div class="page-num">01</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="steps-grid page-animate">
  <div class="step-item">
    <div class="step-n">01</div>
    <div class="step-l">Upload</div>
    <div class="step-d">Drop a WAV audio file you want to protect and register.</div>
  </div>
  <div class="step-item">
    <div class="step-n">02</div>
    <div class="step-l">Watermark</div>
    <div class="step-d">Perth embeds an imperceptible ownership payload into the signal.</div>
  </div>
  <div class="step-item">
    <div class="step-n">03</div>
    <div class="step-l">Fingerprint</div>
    <div class="step-d">Acoustic landmarks extracted and logged to the fingerprint DB.</div>
  </div>
  <div class="step-item">
    <div class="step-n">04</div>
    <div class="step-l">Download</div>
    <div class="step-d">Retrieve the protected file — ready for distribution.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="upload-section page-animate">', unsafe_allow_html=True)
    st.markdown("""
<div class="upload-label">◈ Target Audio — WAV Format Only</div>
<div class="upload-zone-wrapper">
  <div class="upload-zone-deco">
    <div class="upload-corner tl"></div>
    <div class="upload-corner tr"></div>
    <div class="upload-corner bl"></div>
    <div class="upload-corner br"></div>
  </div>
""", unsafe_allow_html=True)

    upload_ingest = st.file_uploader(
        "drop_ingest", type=["wav"], key="upload_ingest", label_visibility="collapsed"
    )

    st.markdown("""
  <div class="upload-hint">DRAG & DROP WAV FILE — OR CLICK TO BROWSE — MAX 200MB</div>
</div>
</div>
""", unsafe_allow_html=True)

    if upload_ingest is not None:
        st.markdown('<div class="result-section page-animate">', unsafe_allow_html=True)
        
        # Big process button — full width wrap
        st.markdown('<div class="action-btn-wrap">', unsafe_allow_html=True)
        run_ingest = st.button("⬡  PROCESS & INGEST FILE", key="btn_ingest")
        st.markdown('</div>', unsafe_allow_html=True)

        if run_ingest:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_in:
                tmp_in.write(upload_ingest.read())
                tmp_in_path = tmp_in.name
            tmp_out_path = tmp_in_path.replace(".wav", "_watermarked.wav")

            try:
                with st.spinner("Checking fingerprint database integrity…"):
                    check_database()

                with st.spinner("Applying Perth watermark…"):
                    apply_watermark(tmp_in_path, tmp_out_path)

                f = io.StringIO()
                with st.spinner("Registering fingerprint to DB…"):
                    with contextlib.redirect_stdout(f):
                        add_to_fingerprint_db(tmp_out_path)
                fingerprint_logs = f.getvalue()

                st.markdown("""
<div class="result-panel" style="margin-bottom:16px;">
  <div class="result-panel-header">
    <div class="result-dot green"></div>
    <div class="result-panel-title">Ingestion Status</div>
  </div>
  <div class="result-panel-body">
    <div class="result-status ok">Protection Complete</div>
    <div class="result-msg">Watermark embedded via Perth engine. Acoustic fingerprint registered to local DB.</div>
  </div>
</div>
""", unsafe_allow_html=True)

                with st.expander("VIEW FINGERPRINTING LOGS"):
                    st.code(fingerprint_logs, language="text")

                st.markdown("<br>", unsafe_allow_html=True)
                with open(tmp_out_path, "rb") as out_file:
                    st.download_button(
                        label="⬇  DOWNLOAD PROTECTED FILE",
                        data=out_file,
                        file_name=f"protected_{upload_ingest.name}",
                        mime="audio/wav"
                    )

            except Exception as e:
                st.markdown(f"""
<div class="result-panel" style="margin-bottom:16px;">
  <div class="result-panel-header">
    <div class="result-dot red"></div>
    <div class="result-panel-title">Ingestion Error</div>
  </div>
  <div class="result-panel-body">
    <div class="result-status fail">Processing Failed</div>
    <div class="result-msg">{str(e)}</div>
  </div>
</div>
""", unsafe_allow_html=True)

            finally:
                if os.path.exists(tmp_in_path):
                    os.remove(tmp_in_path)

        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFY PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "verify":
    st.components.v1.html("""
<!DOCTYPE html>
<html>
<head>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background: transparent; overflow: hidden; }
canvas { display: block; }
</style>
</head>
<body>
<canvas id="fp"></canvas>
<script>
const canvas = document.getElementById('fp');
const ctx = canvas.getContext('2d');
canvas.width  = window.innerWidth || 1400;
canvas.height = 220;
const W = canvas.width, H = canvas.height;

const ridges = [];
const RIDGE_COUNT = 28;
for (let r = 0; r < RIDGE_COUNT; r++) {
    const pts = [];
    const baseY = H * 0.1 + r * (H * 0.8 / RIDGE_COUNT);
    const pts_count = 80;
    for (let i = 0; i < pts_count; i++) {
        const x = (W * 0.1) + (i / pts_count) * (W * 0.8);
        const noise = (Math.random() - 0.5) * 4 + Math.sin(i * 0.3 + r) * 6;
        pts.push({ x, y: baseY + noise });
    }
    ridges.push(pts);
}

let scanY = H * 0.05;
let scanDir = 1;

function draw() {
    ctx.clearRect(0, 0, W, H);

    ridges.forEach((pts) => {
        const distToScan = Math.abs(pts[0].y - scanY) / H;
        const brightness = Math.max(0.04, 0.25 - distToScan * 0.5);
        const scanned = pts[0].y < scanY;
        const alpha = scanned ? brightness + 0.08 : brightness;

        ctx.beginPath();
        ctx.moveTo(pts[0].x, pts[0].y);
        for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i].x, pts[i].y);
        ctx.strokeStyle = scanned ? `rgba(201,184,255,${alpha})` : `rgba(160,140,220,${alpha * 0.5})`;
        ctx.lineWidth = 1.2;
        ctx.stroke();

        if (distToScan < 0.08) {
            const glow = (0.08 - distToScan) / 0.08;
            ctx.strokeStyle = `rgba(201,184,255,${glow * 0.7})`;
            ctx.lineWidth = 2.5;
            ctx.stroke();
        }
    });

    const scanGrad = ctx.createLinearGradient(W * 0.05, 0, W * 0.95, 0);
    scanGrad.addColorStop(0, 'transparent');
    scanGrad.addColorStop(0.1, 'rgba(201,184,255,0.6)');
    scanGrad.addColorStop(0.5, 'rgba(220,200,255,0.9)');
    scanGrad.addColorStop(0.9, 'rgba(201,184,255,0.6)');
    scanGrad.addColorStop(1, 'transparent');

    ctx.beginPath();
    ctx.moveTo(W * 0.05, scanY);
    ctx.lineTo(W * 0.95, scanY);
    ctx.strokeStyle = scanGrad;
    ctx.lineWidth = 1.5;
    ctx.shadowColor = 'rgba(201,184,255,0.8)';
    ctx.shadowBlur = 12;
    ctx.stroke();
    ctx.shadowBlur = 0;

    const pct = Math.round(((scanY - H * 0.05) / (H * 0.9)) * 100);
    ctx.fillStyle = 'rgba(201,184,255,0.5)';
    ctx.font = '11px "Share Tech Mono", monospace';
    ctx.fillText(`SCANNING ${pct}%`, W * 0.05, H * 0.97);

    scanY += scanDir * 1.1;
    if (scanY > H * 0.95) scanDir = -1;
    if (scanY < H * 0.05) scanDir = 1;
    requestAnimationFrame(draw);
}
draw();
</script>
</body>
</html>
""", height=220, scrolling=False)

    st.markdown("""
<div class="page-header page-animate" style="margin-top:-8px;">
  <div class="page-eyebrow">Analyse ── Match ── Authenticate</div>
  <div class="page-title">Verify <span>Audio</span></div>
  <div class="page-sub">
    Upload an unknown or suspicious WAV file. The system cross-references the 
    fingerprint database and extracts any embedded watermark payload.
  </div>
  <div class="page-num">02</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="steps-grid page-animate">
  <div class="step-item">
    <div class="step-n">01</div>
    <div class="step-l">Upload Query</div>
    <div class="step-d">Drop the unknown audio file you want to investigate.</div>
  </div>
  <div class="step-item">
    <div class="step-n">02</div>
    <div class="step-l">Fingerprint Match</div>
    <div class="step-d">Audfprint queries the DB for acoustic landmark matches.</div>
  </div>
  <div class="step-item">
    <div class="step-n">03</div>
    <div class="step-l">Payload Extract</div>
    <div class="step-d">Perth decodes any embedded ownership payload from the signal.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="upload-section page-animate">', unsafe_allow_html=True)
    st.markdown("""
<div class="upload-label">◈ Query Audio — WAV Format Only</div>
<div class="upload-zone-wrapper">
  <div class="upload-zone-deco">
    <div class="upload-corner tl"></div>
    <div class="upload-corner tr"></div>
    <div class="upload-corner bl"></div>
    <div class="upload-corner br"></div>
  </div>
""", unsafe_allow_html=True)

    upload_verify = st.file_uploader(
        "drop_verify", type=["wav"], key="upload_verify", label_visibility="collapsed"
    )

    st.markdown("""
  <div class="upload-hint">DRAG & DROP WAV FILE — OR CLICK TO BROWSE — MAX 200MB</div>
</div>
</div>
""", unsafe_allow_html=True)

    if upload_verify is not None:
        st.markdown('<div class="result-section page-animate">', unsafe_allow_html=True)
        
        # Big verify button
        st.markdown('<div class="action-btn-wrap">', unsafe_allow_html=True)
        run_verify = st.button("◈  RUN VERIFICATION ANALYSIS", key="btn_verify")
        st.markdown('</div>', unsafe_allow_html=True)

        if run_verify:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_q:
                tmp_q.write(upload_verify.read())
                tmp_q_path = tmp_q.name

            try:
                with st.spinner("Checking fingerprint database integrity…"):
                    check_database()

                col1, col2 = st.columns(2)

                with col1:
                    with st.spinner("Querying fingerprint database…"):
                        match_logs_buf = io.StringIO()
                        matched = False
                        try:
                            with contextlib.redirect_stdout(match_logs_buf):
                                matched = match_fingerprint(tmp_q_path)
                        except Exception as e:
                            match_logs_buf.write(f"Error: {e}")
                        match_logs = match_logs_buf.getvalue()

                    dot_cls = "green" if matched else "red"
                    status_cls = "ok" if matched else "fail"
                    status_txt = "Match Found" if matched else "No Match"
                    msg_txt = "File identified in fingerprint database." if matched else "No definitive match — file may be unregistered or altered."

                    st.markdown(f"""
<div class="result-panel">
  <div class="result-panel-header">
    <div class="result-dot {dot_cls}"></div>
    <div class="result-panel-title">Audfprint Match Results</div>
  </div>
  <div class="result-panel-body">
    <div class="result-status {status_cls}">{status_txt}</div>
    <div class="result-msg">{msg_txt}</div>
  </div>
</div>
""", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.text_area("Raw Match Output", match_logs, height=120, key="match_out")

                with col2:
                    with st.spinner("Extracting watermark payload…"):
                        watermark = extract_watermark(tmp_q_path)

                    if watermark is not None:
                        st.markdown(f"""
<div class="result-panel">
  <div class="result-panel-header">
    <div class="result-dot green"></div>
    <div class="result-panel-title">Perth Watermark Payload</div>
  </div>
  <div class="result-panel-body">
    <div class="result-status ok">Payload Extracted</div>
    <div class="result-msg">Ownership data successfully decoded from the audio signal.</div>
    <div class="payload-box">{watermark}</div>
  </div>
</div>
""", unsafe_allow_html=True)
                    else:
                        st.markdown("""
<div class="result-panel">
  <div class="result-panel-header">
    <div class="result-dot red"></div>
    <div class="result-panel-title">Perth Watermark Payload</div>
  </div>
  <div class="result-panel-body">
    <div class="result-status fail">No Payload</div>
    <div class="result-msg">No valid watermark payload recovered from this file.</div>
  </div>
</div>
""", unsafe_allow_html=True)

            except Exception as e:
                st.markdown(f"""
<div class="result-panel">
  <div class="result-panel-header">
    <div class="result-dot red"></div>
    <div class="result-panel-title">Verification Error</div>
  </div>
  <div class="result-panel-body">
    <div class="result-status fail">Analysis Failed</div>
    <div class="result-msg">{str(e)}</div>
  </div>
</div>
""", unsafe_allow_html=True)

            finally:
                if os.path.exists(tmp_q_path):
                    os.remove(tmp_q_path)

        st.markdown('</div>', unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="site-footer">
  <div class="footer-logo">SOUNDSEAL</div>
  <div class="footer-meta">PERTH ENGINE ◆ AUDFPRINT ◆ INTEGRATED PROTECTION PIPELINE</div>
</div>
""", unsafe_allow_html=True)
