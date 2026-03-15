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
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,500;1,600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:          #faf8f5;
    --surface:     #f4f0eb;
    --panel:       #ffffff;
    --border:      #e8ddd4;
    --border2:     #d4c5b8;
    --accent:      #FF69B4;
    --accent2:     #069494;
    --teal:        #069494;
    --pink-light:  rgba(255,105,180,0.10);
    --accent-dim:  rgba(255,105,180,0.12);
    --accent-glow: rgba(255,105,180,0.40);
    --cyan-glow:   rgba(6,148,148,0.30);
    --red:         #e03060;
    --text:        #0f0608;
    --muted:       #2d1a22;
    --font-display: 'Cormorant Garamond', serif;
    --font-body:    'Cormorant Garamond', serif;
    --font-cond:    'Cormorant Garamond', serif;
    --font-mono:    'Cormorant Garamond', serif;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #d4a0bc; border-radius: 2px; }

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
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    font-style: italic;
    color: #fff;
    padding: 0 2rem;
    letter-spacing: 0.12em;
    font-weight: 400;
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
    background: rgba(250,248,245,0.97);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    position: relative;
    z-index: 99;
}
.nav-logo {
    font-family: var(--font-display);
    font-size: 2rem;
    letter-spacing: 0.02em;
    color: #0f0608;
    font-weight: 300;
}
.nav-logo span { color: var(--accent); font-style: italic; }
.nav-placeholder {
    display: flex;
    gap: 4px;
    align-items: center;
}
.nav-pill {
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 7px 18px;
    border-radius: 2px;
    border: 1px solid transparent;
    color: #1a0a14;
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
    color: #1a0a14 !important;
    border: 1px solid transparent !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.12em !important;
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
    border-color: #d4c5b8 !important;
    box-shadow: none !important;
    transform: none !important;
    background: transparent !important;
}

/* Active nav button override */
.nav-active .stButton > button {
    background: linear-gradient(135deg, #FF69B4 0%, #069494 100%) !important;
    color: #fff !important;
    border-color: transparent !important;
    font-weight: 600 !important;
    border-radius: 20px !important;
    box-shadow: 0 2px 14px rgba(255,105,180,0.3) !important;
}
.nav-active .stButton > button:hover {
    background: linear-gradient(135deg, #FF69B4 0%, #069494 100%) !important;
    color: #fff !important;
    box-shadow: 0 4px 20px rgba(255,105,180,0.45) !important;
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
    background: linear-gradient(135deg, #FF69B4 0%, #069494 100%) !important;
    color: #fff !important;
    border: none !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.25rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    padding: 20px 52px !important;
    border-radius: 40px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 24px rgba(255,105,180,0.3) !important;
    position: relative !important;
    width: 280px !important;
    height: 64px !important;
}
.cta-ingest-wrap .stButton > button:hover {
    box-shadow: 0 8px 40px rgba(255,105,180,0.5), 0 0 60px rgba(0,240,255,0.2) !important;
    transform: translateY(-4px) !important;
    filter: brightness(1.1) !important;
}
.cta-ingest-wrap .stButton > button:active {
    transform: translateY(0px) !important;
}

/* Large CTA Verify button */
.cta-verify-wrap .stButton > button {
    background: transparent !important;
    color: var(--accent2) !important;
    border: 1.5px solid rgba(0,240,255,0.6) !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 20px 52px !important;
    border-radius: 40px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    width: 280px !important;
    height: 64px !important;
    box-shadow: 0 0 0px rgba(0,240,255,0) !important;
}
.cta-verify-wrap .stButton > button:hover {
    background: rgba(0,240,255,0.06) !important;
    border-color: var(--accent2) !important;
    box-shadow: 0 4px 30px rgba(0,240,255,0.3), inset 0 0 20px rgba(0,240,255,0.04) !important;
    transform: translateY(-4px) !important;
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
    background: linear-gradient(135deg, #FF69B4 0%, #069494 100%) !important;
    color: #fff !important;
    border: none !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    padding: 16px 44px !important;
    border-radius: 40px !important;
    height: 54px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(255,105,180,0.3) !important;
}
.action-btn-wrap .stButton > button:hover {
    box-shadow: 0 8px 35px rgba(255,105,180,0.45), 0 0 40px rgba(0,240,255,0.15) !important;
    transform: translateY(-3px) !important;
    filter: brightness(1.08) !important;
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
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 1.1rem;
    color: var(--accent2);
    text-transform: uppercase;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}
.hero-title {
    font-family: var(--font-display);
    font-size: clamp(4.5rem, 9vw, 10rem);
    line-height: 0.88;
    letter-spacing: -0.01em;
    text-transform: none;
    color: var(--text);
    margin-bottom: 28px;
    font-weight: 300;
}
.hero-title em {
    font-style: italic;
    color: var(--accent);
    font-weight: 300;
}
.hero-desc {
    font-family: var(--font-body);
    font-size: 1.3rem;
    color: #1a0a14;
    line-height: 1.7;
    max-width: 540px;
    margin: 0 auto 36px;
    font-weight: 300;
}
.hero-desc strong { color: var(--text); font-weight: 600; font-family: 'Cormorant Garamond', serif; }

/* CTA label above buttons */
.cta-label {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem;
    letter-spacing: 0.15em;
    color: #8a5070;
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
.feature-cell:hover { background: linear-gradient(135deg, rgba(255,105,180,0.05) 0%, rgba(6,148,148,0.04) 100%); }
.feature-cell::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #FF69B4, #069494, #00F0FF);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.3s;
}
.feature-cell:hover::before { transform: scaleX(1); }
.feature-icon {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem;
    font-style: italic;
    color: var(--accent);
    letter-spacing: 0.2em;
    margin-bottom: 14px;
}
.feature-name {
    font-family: var(--font-display);
    font-size: 1.8rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: none;
    color: var(--text);
    margin-bottom: 8px;
}
.feature-desc {
    font-size: 1.15rem;
    color: #1a0a14;
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
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 1.05rem;
    color: var(--accent2);
    letter-spacing: 0.22em;
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
    background: var(--accent2);
}
.page-title {
    font-family: var(--font-display);
    font-size: clamp(3.5rem, 7vw, 6.5rem);
    line-height: 0.88;
    text-transform: none;
    color: var(--text);
    margin-bottom: 16px;
    font-weight: 300;
    letter-spacing: -0.01em;
}
.page-title span { color: var(--accent2); font-style: italic; }
.page-sub {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.25rem;
    color: #1a0a14;
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
    color: rgba(255,105,180,0.08);
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
    color: #f0d0e0;
    line-height: 1;
    margin-bottom: 10px;
}
.step-l {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 1rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--teal);
    margin-bottom: 7px;
}
.step-d { font-family: 'Cormorant Garamond', serif; font-size: 1.2rem; color: #1a0a14; line-height: 1.6; }

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
    border-color: rgba(255,105,180,0.4);
    box-shadow: 0 0 40px rgba(255,105,180,0.07), inset 0 0 40px rgba(0,240,255,0.03);
}
.upload-corner {
    position: absolute;
    width: 14px;
    height: 14px;
    z-index: 2;
    pointer-events: none;
}
.upload-corner.tl { top: -1px; left: -1px; border-top: 2px solid #FF69B4; border-left: 2px solid #FF69B4; }
.upload-corner.tr { top: -1px; right: -1px; border-top: 2px solid #00F0FF; border-right: 2px solid #00F0FF; }
.upload-corner.bl { bottom: -1px; left: -1px; border-bottom: 2px solid #00F0FF; border-left: 2px solid #00F0FF; }
.upload-corner.br { bottom: -1px; right: -1px; border-bottom: 2px solid #FF69B4; border-right: 2px solid #FF69B4; }
.upload-label {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #1a0a14;
    margin-bottom: 10px;
}
.upload-hint {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem;
    color: #8a5070;
    letter-spacing: 0.12em;
    margin-top: 10px;
}

/* ── RESULT CARDS ── */
.result-section { padding: 0 64px 64px; }
.result-panel {
    background: #ffffff;
    border: 1px solid var(--border);
    box-shadow: 0 2px 20px rgba(255,105,180,0.06);
    border-radius: 3px;
    overflow: hidden;
}
.result-panel-header {
    padding: 14px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(90deg, rgba(255,105,180,0.05) 0%, #faf8f5 100%);
}
.result-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--border2); }
.result-dot.green { background: linear-gradient(135deg,#FF69B4,#00F0FF); box-shadow: 0 0 10px rgba(255,105,180,0.7); }
.result-dot.red { background: var(--red); box-shadow: 0 0 8px rgba(255,51,51,0.5); }
.result-panel-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #1a0a14;
}
.result-panel-body { padding: 20px; }
.result-status {
    font-family: var(--font-display);
    font-size: 1.8rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: none;
    font-style: italic;
    margin-bottom: 6px;
}
.result-status.ok { color: var(--accent); font-style: italic; }
.result-status.fail { color: var(--red); }
.result-msg { font-family: 'Cormorant Garamond', serif; font-size: 1.2rem; color: #1a0a14; line-height: 1.6; }
.payload-box {
    background: rgba(6,148,148,0.04);
    border: 1px solid rgba(6,148,148,0.2);
    border-radius: 2px;
    padding: 14px 16px;
    margin-top: 12px;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    color: var(--accent2);
    font-family: 'Cormorant Garamond', serif;
    word-break: break-all;
    line-height: 1.5;
}

/* ── STREAMLIT OVERRIDES ── */
div[data-testid="stFileUploader"] > label { display: none !important; }
div[data-testid="stFileUploader"] > div {
    background: #fff !important;
    border: 1px dashed #e0ccd8 !important;
    border-radius: 3px !important;
    min-height: 160px !important;
    transition: all 0.25s !important;
}
div[data-testid="stFileUploader"] > div:hover {
    border-color: rgba(255,105,180,0.4) !important;
    background: rgba(255,105,180,0.02) !important;
}
div[data-testid="stFileUploader"] p {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.1rem !important;
    color: #1a0a14 !important;
    letter-spacing: 0.1em !important;
}
div[data-testid="stFileUploader"] small {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1rem !important;
    color: #4a2030 !important;
}
div[data-testid="stFileUploader"] button {
    background: transparent !important;
    border: 1px solid #d4a0bc !important;
    color: #1a0a14 !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1rem !important;
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
    background: linear-gradient(135deg, #FF69B4 0%, #069494 100%) !important;
    color: #fff !important;
    border: none !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    padding: 13px 36px !important;
    border-radius: 40px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 16px rgba(255,105,180,0.25) !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 28px rgba(255,105,180,0.4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(1px) !important; }

.stDownloadButton > button {
    background: transparent !important;
    color: var(--accent2) !important;
    border: 1.5px solid rgba(0,240,255,0.5) !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    padding: 11px 28px !important;
    border-radius: 40px !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: rgba(0,240,255,0.06) !important;
    box-shadow: 0 0 20px rgba(0,240,255,0.2) !important;
}

.stSpinner > div { border-top-color: #FF69B4 !important; }

.stTextArea textarea {
    background: #fff !important;
    border: 1px solid var(--border) !important;
    color: #1a0a14 !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.1rem !important;
    border-radius: 2px !important;
}
pre, code { background: #faf0f5 !important; color: #1a0a14 !important; font-family: 'Cormorant Garamond', serif !important; }

details {
    background: #faf8f5 !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
}
details summary {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1rem !important;
    letter-spacing: 0.1em !important;
    color: #1a0a14 !important;
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
.footer-logo { font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 1.6rem; color: #8a5070; letter-spacing: 0.08em; }
.footer-meta { font-family: 'Cormorant Garamond', serif; font-size: 1rem; color: #8a5070; letter-spacing: 0.12em; text-transform: uppercase; }

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
    color: #1a0a14 !important;
    border: 1px solid transparent !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.12em !important;
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
    # Organic bubblegum wave canvas
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
canvas.width  = window.innerWidth || 1400;
canvas.height = 500;
const W = canvas.width, H = canvas.height;
let t = 0;

const LAYERS = [
  { freq: 0.9,  amp: 0.28, speed: 0.012, phase: 0.0,  colorA: [255,105,180], colorB: [0,240,255],  alpha: 0.55, thick: 2.5 },
  { freq: 1.3,  amp: 0.20, speed: 0.018, phase: 1.2,  colorA: [6,148,148],   colorB: [255,105,180], alpha: 0.40, thick: 2.0 },
  { freq: 0.7,  amp: 0.34, speed: 0.009, phase: 2.4,  colorA: [0,240,255],   colorB: [255,105,180], alpha: 0.30, thick: 1.5 },
  { freq: 1.8,  amp: 0.14, speed: 0.024, phase: 3.6,  colorA: [255,150,200], colorB: [0,200,200],   alpha: 0.22, thick: 1.2 },
  { freq: 0.5,  amp: 0.42, speed: 0.006, phase: 0.8,  colorA: [6,148,148],   colorB: [255,105,180], alpha: 0.15, thick: 1.0 },
];

function sineWave(x, layer, time) {
  const xn = x / W;
  return H/2
    + Math.sin(xn * Math.PI * 2 * layer.freq + time * layer.speed * 20 + layer.phase) * H * layer.amp * 0.5
    + Math.sin(xn * Math.PI * 3.7 * layer.freq + time * layer.speed * 14 + layer.phase * 1.5) * H * layer.amp * 0.25
    + Math.sin(xn * Math.PI * 1.2 * layer.freq + time * layer.speed * 8 + layer.phase * 0.7) * H * layer.amp * 0.25;
}

function drawLayer(layer, time) {
  const pts = [];
  const STEP = 4;
  for (let x = 0; x <= W; x += STEP) {
    pts.push([x, sineWave(x, layer, time)]);
  }

  const midY = H / 2;
  const fillGrad = ctx.createLinearGradient(0, midY - H * layer.amp, 0, H);
  fillGrad.addColorStop(0,   `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},${layer.alpha * 0.6})`);
  fillGrad.addColorStop(0.5, `rgba(${layer.colorB[0]},${layer.colorB[1]},${layer.colorB[2]},${layer.alpha * 0.3})`);
  fillGrad.addColorStop(1,   `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},0)`);

  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length - 1; i++) {
    const cx = (pts[i][0] + pts[Math.min(i+1, pts.length-1)][0]) / 2;
    const cy = (pts[i][1] + pts[Math.min(i+1, pts.length-1)][1]) / 2;
    ctx.quadraticCurveTo(pts[i][0], pts[i][1], cx, cy);
  }
  ctx.lineTo(W, H);
  ctx.lineTo(0, H);
  ctx.closePath();
  ctx.fillStyle = fillGrad;
  ctx.fill();

  const strokeGrad = ctx.createLinearGradient(0, 0, W, 0);
  strokeGrad.addColorStop(0,    `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},0)`);
  strokeGrad.addColorStop(0.15, `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},${layer.alpha * 1.4})`);
  strokeGrad.addColorStop(0.5,  `rgba(${layer.colorB[0]},${layer.colorB[1]},${layer.colorB[2]},${layer.alpha * 1.8})`);
  strokeGrad.addColorStop(0.85, `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},${layer.alpha * 1.4})`);
  strokeGrad.addColorStop(1,    `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},0)`);

  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length - 1; i++) {
    const cx = (pts[i][0] + pts[Math.min(i+1, pts.length-1)][0]) / 2;
    const cy = (pts[i][1] + pts[Math.min(i+1, pts.length-1)][1]) / 2;
    ctx.quadraticCurveTo(pts[i][0], pts[i][1], cx, cy);
  }
  ctx.strokeStyle = strokeGrad;
  ctx.lineWidth = layer.thick;
  ctx.shadowColor = `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},0.8)`;
  ctx.shadowBlur = 14;
  ctx.stroke();
  ctx.shadowBlur = 0;
}

const ORBS = Array.from({length: 18}, () => ({
  x: Math.random() * W,
  y: Math.random() * H,
  r: 2 + Math.random() * 5,
  vx: (Math.random() - 0.5) * 0.4,
  vy: (Math.random() - 0.5) * 0.3,
  hue: Math.random() > 0.5 ? [255,105,180] : [0,240,255],
  alpha: 0.2 + Math.random() * 0.4,
  pulse: Math.random() * Math.PI * 2,
}));

function drawOrbs() {
  ORBS.forEach(o => {
    o.x += o.vx; o.y += o.vy; o.pulse += 0.03;
    if (o.x < -20) o.x = W + 20;
    if (o.x > W + 20) o.x = -20;
    if (o.y < -20) o.y = H + 20;
    if (o.y > H + 20) o.y = -20;
    const a = o.alpha * (0.6 + 0.4 * Math.sin(o.pulse));
    const g = ctx.createRadialGradient(o.x, o.y, 0, o.x, o.y, o.r * 3);
    g.addColorStop(0, `rgba(${o.hue[0]},${o.hue[1]},${o.hue[2]},${a})`);
    g.addColorStop(1, `rgba(${o.hue[0]},${o.hue[1]},${o.hue[2]},0)`);
    ctx.beginPath();
    ctx.arc(o.x, o.y, o.r * 3, 0, Math.PI * 2);
    ctx.fillStyle = g;
    ctx.fill();
  });
}

function draw() {
  ctx.clearRect(0, 0, W, H);
  const bg = ctx.createRadialGradient(W/2, H/2, 0, W/2, H/2, W * 0.6);
  bg.addColorStop(0,   'rgba(255,105,180,0.04)');
  bg.addColorStop(0.4, 'rgba(6,148,148,0.03)');
  bg.addColorStop(1,   'rgba(0,0,0,0)');
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, W, H);
  drawOrbs();
  for (let i = LAYERS.length - 1; i >= 0; i--) drawLayer(LAYERS[i], t);
  t += 0.3;
  requestAnimationFrame(draw);
}
draw();
</script>
</body>
</html>
""", height=500, scrolling=False)

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
        st.markdown('<div style="text-align:center; font-family:Cormorant Garamond,serif; font-size:0.95rem; color:#4a2030; letter-spacing:0.1em; margin-top:6px;">Watermark + Fingerprint</div>', unsafe_allow_html=True)
    with col_vl:
        st.markdown('<div style="text-align:center; font-family:Cormorant Garamond,serif; font-size:0.95rem; color:#4a2030; letter-spacing:0.1em; margin-top:6px;">Match + Extract Payload</div>', unsafe_allow_html=True)

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
    # Same wave as home page
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
<canvas id="v"></canvas>
<script>
const canvas = document.getElementById('v');
const ctx = canvas.getContext('2d');
canvas.width  = window.innerWidth || 1400;
canvas.height = 320;
const W = canvas.width, H = canvas.height;
let t = 0;
const LAYERS = [
  { freq: 0.9,  amp: 0.28, speed: 0.012, phase: 0.0,  colorA: [255,105,180], colorB: [6,148,148],  alpha: 0.45, thick: 2.5 },
  { freq: 1.3,  amp: 0.20, speed: 0.018, phase: 1.2,  colorA: [6,148,148],   colorB: [255,105,180], alpha: 0.32, thick: 2.0 },
  { freq: 0.7,  amp: 0.34, speed: 0.009, phase: 2.4,  colorA: [255,150,200], colorB: [6,148,148],   alpha: 0.22, thick: 1.5 },
  { freq: 1.8,  amp: 0.14, speed: 0.024, phase: 3.6,  colorA: [255,105,180], colorB: [6,148,148],   alpha: 0.16, thick: 1.0 },
];
function sineWave(x, layer, time) {
  const xn = x / W;
  return H/2
    + Math.sin(xn * Math.PI * 2 * layer.freq + time * layer.speed * 20 + layer.phase) * H * layer.amp * 0.5
    + Math.sin(xn * Math.PI * 3.7 * layer.freq + time * layer.speed * 14 + layer.phase * 1.5) * H * layer.amp * 0.25
    + Math.sin(xn * Math.PI * 1.2 * layer.freq + time * layer.speed * 8 + layer.phase * 0.7) * H * layer.amp * 0.25;
}
function drawLayer(layer, time) {
  const pts = [];
  for (let x = 0; x <= W; x += 4) pts.push([x, sineWave(x, layer, time)]);
  const fillGrad = ctx.createLinearGradient(0, H/2 - H * layer.amp, 0, H);
  fillGrad.addColorStop(0,   `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},${layer.alpha * 0.5})`);
  fillGrad.addColorStop(0.5, `rgba(${layer.colorB[0]},${layer.colorB[1]},${layer.colorB[2]},${layer.alpha * 0.25})`);
  fillGrad.addColorStop(1,   `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},0)`);
  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length-1; i++) {
    const cx = (pts[i][0] + pts[i+1][0]) / 2;
    const cy = (pts[i][1] + pts[i+1][1]) / 2;
    ctx.quadraticCurveTo(pts[i][0], pts[i][1], cx, cy);
  }
  ctx.lineTo(W, H); ctx.lineTo(0, H); ctx.closePath();
  ctx.fillStyle = fillGrad; ctx.fill();
  const strokeGrad = ctx.createLinearGradient(0, 0, W, 0);
  strokeGrad.addColorStop(0,    `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},0)`);
  strokeGrad.addColorStop(0.15, `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},${layer.alpha * 1.3})`);
  strokeGrad.addColorStop(0.5,  `rgba(${layer.colorB[0]},${layer.colorB[1]},${layer.colorB[2]},${layer.alpha * 1.6})`);
  strokeGrad.addColorStop(0.85, `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},${layer.alpha * 1.3})`);
  strokeGrad.addColorStop(1,    `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},0)`);
  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length-1; i++) {
    const cx = (pts[i][0] + pts[i+1][0]) / 2;
    const cy = (pts[i][1] + pts[i+1][1]) / 2;
    ctx.quadraticCurveTo(pts[i][0], pts[i][1], cx, cy);
  }
  ctx.strokeStyle = strokeGrad;
  ctx.lineWidth = layer.thick;
  ctx.shadowColor = `rgba(${layer.colorA[0]},${layer.colorA[1]},${layer.colorA[2]},0.6)`;
  ctx.shadowBlur = 10; ctx.stroke(); ctx.shadowBlur = 0;
}
function draw() {
  ctx.clearRect(0, 0, W, H);
  for (let i = LAYERS.length - 1; i >= 0; i--) drawLayer(LAYERS[i], t);
  t += 0.3;
  requestAnimationFrame(draw);
}
draw();
</script>
</body>
</html>
""", height=320, scrolling=False)

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