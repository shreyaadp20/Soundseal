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

from integrate import apply_watermark, add_to_fingerprint_db, match_fingerprint, extract_watermark

# --- Page Configuration ---
st.set_page_config(
    page_title="Soundseal — Audio Protection",
    layout="wide",
    page_icon="🔒",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL STYLES ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&family=Space+Grotesk:wght@300;400;600;700&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:      #0a0a0a;
    --surface: #111111;
    --panel:   #161616;
    --border:  #2a2a2a;
    --accent:  #e8ff00;
    --accent2: #ff4d4d;
    --text:    #f0f0f0;
    --muted:   #ffffff;
    --font-display: 'Bebas Neue', sans-serif;
    --font-body:    'Space Grotesk', sans-serif;
    --font-mono:    'DM Mono', monospace;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* ── BODY ── */
body, .stApp {
    background-color: var(--bg) !important;
    font-family: var(--font-body);
    color: var(--text);
}

/* ── MARQUEE BANNER ── */
.marquee-wrap {
    background: var(--accent);
    overflow: hidden;
    padding: 10px 0;
    border-top: 2px solid #000;
    border-bottom: 2px solid #000;
}
.marquee-inner {
    display: flex;
    white-space: nowrap;
    animation: marquee 22s linear infinite;
}
.marquee-item {
    font-family: var(--font-display);
    font-size: 1.1rem;
    color: #000;
    padding: 0 2.5rem;
    letter-spacing: 0.08em;
}
.marquee-dot { color: #000; opacity: 0.4; font-size: 0.7rem; }
@keyframes marquee {
    from { transform: translateX(0); }
    to   { transform: translateX(-50%); }
}

/* ── HERO HEADER ── */
.hero {
    background: var(--bg);
    padding: 60px 64px 40px;
    border-bottom: 1px solid var(--border);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 380px; height: 380px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(232,255,0,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--accent);
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.hero-title {
    font-family: var(--font-display);
    font-size: clamp(3.5rem, 8vw, 7rem);
    line-height: 0.95;
    letter-spacing: -0.01em;
    color: var(--text);
    text-transform: uppercase;
    margin-bottom: 20px;
}
.hero-title span { color: var(--accent); }
.hero-sub {
    font-size: 1rem;
    color: var(--muted);
    max-width: 560px;
    line-height: 1.65;
    font-weight: 300;
}
.hero-badges {
    display: flex;
    gap: 10px;
    margin-top: 28px;
    flex-wrap: wrap;
}
.badge {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    border: 1px solid var(--border);
    padding: 5px 14px;
    border-radius: 2px;
    color: var(--muted);
}
.badge.active { border-color: var(--accent); color: var(--accent); }

/* ── TABS ── */
div[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 64px !important;
}
div[data-baseweb="tab"] {
    font-family: var(--font-display) !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.08em !important;
    color: var(--muted) !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    padding: 18px 28px !important;
    margin-right: 4px !important;
    transition: all 0.2s ease !important;
}
div[data-baseweb="tab"]:hover {
    color: var(--text) !important;
}
div[aria-selected="true"][data-baseweb="tab"] {
    color: var(--accent) !important;
    border-bottom: 3px solid var(--accent) !important;
}
div[data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 0 !important;
}

/* ── MAIN CONTENT AREA ── */
.content-area {
    padding: 48px 64px;
}

/* ── SECTION TITLE ── */
.section-title {
    font-family: var(--font-display);
    font-size: 2.6rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 6px;
}
.section-sub {
    font-size: 0.88rem;
    color: var(--muted);
    margin-bottom: 40px;
    font-weight: 300;
    line-height: 1.6;
}

/* ── 3D UPLOAD CARD ── */
.upload-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 36px 32px;
    position: relative;
    transform-style: preserve-3d;
    transform: perspective(900px) rotateX(1.5deg) rotateY(-0.8deg);
    box-shadow:
        0 2px 0 var(--border),
        0 4px 0 #0e0e0e,
        0 6px 0 #0c0c0c,
        0 8px 0 #0a0a0a,
        0 12px 30px rgba(0,0,0,0.6);
    transition: transform 0.35s ease, box-shadow 0.35s ease;
}
.upload-card:hover {
    transform: perspective(900px) rotateX(0deg) rotateY(0deg) translateY(-4px);
    box-shadow:
        0 2px 0 var(--border),
        0 4px 0 #0e0e0e,
        0 18px 50px rgba(232,255,0,0.08),
        0 24px 40px rgba(0,0,0,0.7);
}

/* ── STEP INDICATORS ── */
.steps-row {
    display: flex;
    gap: 20px;
    margin-bottom: 40px;
}
.step-card {
    flex: 1;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 22px 20px;
    position: relative;
    transform-style: preserve-3d;
    transform: perspective(600px) rotateX(2deg);
    box-shadow:
        0 3px 0 #0c0c0c,
        0 6px 0 #080808,
        0 10px 20px rgba(0,0,0,0.4);
    transition: transform 0.3s, box-shadow 0.3s;
}
.step-card:hover {
    transform: perspective(600px) rotateX(0deg) translateY(-3px);
    box-shadow: 0 12px 30px rgba(232,255,0,0.07), 0 12px 20px rgba(0,0,0,0.5);
}
.step-num {
    font-family: var(--font-display);
    font-size: 2.8rem;
    color: var(--border);
    line-height: 1;
    margin-bottom: 8px;
}
.step-label {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 6px;
}
.step-desc {
    font-size: 0.82rem;
    color: var(--muted);
    line-height: 1.5;
}

/* ── RESULT CARD ── */
.result-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 28px 26px;
    margin-top: 20px;
    transform-style: preserve-3d;
    transform: perspective(800px) rotateX(1deg);
    box-shadow:
        0 2px 0 #0d0d0d,
        0 5px 0 #090909,
        0 8px 20px rgba(0,0,0,0.4);
}
.result-card.success { border-left: 3px solid var(--accent); }
.result-card.error   { border-left: 3px solid var(--accent2); }
.result-label {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 10px;
}
.result-value {
    font-family: var(--font-mono);
    font-size: 0.85rem;
    color: var(--text);
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-all;
}
.payload-highlight {
    font-family: var(--font-mono);
    background: rgba(232,255,0,0.06);
    border: 1px solid rgba(232,255,0,0.2);
    border-radius: 2px;
    padding: 14px 16px;
    color: var(--accent);
    font-size: 0.9rem;
    word-break: break-all;
    margin-top: 8px;
}

/* ── OVERRIDE STREAMLIT WIDGETS ── */
div[data-testid="stFileUploader"] {
    background: transparent !important;
}
div[data-testid="stFileUploader"] > label {
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
div[data-testid="stFileUploader"] > div {
    background: var(--surface) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 3px !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stFileUploader"] > div:hover {
    border-color: var(--accent) !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    font-family: var(--font-display) !important;
    font-size: 1rem !important;
    letter-spacing: 0.1em !important;
    padding: 12px 32px !important;
    border-radius: 2px !important;
    cursor: pointer !important;
    position: relative !important;
    transform-style: preserve-3d !important;
    box-shadow: 0 5px 0 #9aaa00, 0 8px 15px rgba(0,0,0,0.4) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 7px 0 #9aaa00, 0 12px 20px rgba(0,0,0,0.4) !important;
}
.stButton > button:active {
    transform: translateY(4px) !important;
    box-shadow: 0 1px 0 #9aaa00 !important;
}

/* Download button */
.stDownloadButton > button {
    background: transparent !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    font-family: var(--font-display) !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.1em !important;
    padding: 10px 28px !important;
    border-radius: 2px !important;
    box-shadow: 3px 3px 0 rgba(232,255,0,0.3) !important;
    transition: box-shadow 0.2s, transform 0.2s !important;
}
.stDownloadButton > button:hover {
    transform: translate(-2px, -2px) !important;
    box-shadow: 5px 5px 0 rgba(232,255,0,0.4) !important;
}

/* ── SPINNER / STATUS ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── EXPANDER ── */
details {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    padding: 4px 0 !important;
}
details summary {
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.14em !important;
    color: var(--muted) !important;
    padding: 10px 16px !important;
    cursor: pointer !important;
}
details[open] summary { color: var(--text) !important; }

/* ── TEXT AREA ── */
.stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.78rem !important;
    border-radius: 2px !important;
}

/* ── SUCCESS / WARNING / ERROR ── */
div[data-testid="stAlert"] {
    border-radius: 2px !important;
    border-left-width: 3px !important;
}

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; }

/* ── COLUMNS ── */
div[data-testid="column"] { padding: 0 12px !important; }

/* ── FOOTER ── */
.app-footer {
    border-top: 1px solid var(--border);
    padding: 24px 64px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.footer-brand {
    font-family: var(--font-display);
    font-size: 1.3rem;
    color: var(--border);
    letter-spacing: 0.08em;
}
.footer-note {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 0.12em;
}
</style>
""", unsafe_allow_html=True)

# ── MARQUEE ──────────────────────────────────────────────────────────────────
marquee_items = (
    "WATERMARK" + " ◆ " +
    "FINGERPRINT" + " ◆ " +
    "PROTECT" + " ◆ " +
    "VERIFY" + " ◆ " +
    "AUTHENTICATE" + " ◆ " +
    "PERTH ENGINE" + " ◆ " +
    "AUDFPRINT" + " ◆ "
) * 8

st.markdown(f"""
<div class="marquee-wrap">
  <div class="marquee-inner">
    <span class="marquee-item">{marquee_items}</span>
    <span class="marquee-item">{marquee_items}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">◈ Integrated Audio Protection System</div>
  <div class="hero-title">Sound<span>seal</span></div>
  <div class="hero-sub">
    Embed invisible ownership cues with <strong>Perth</strong> and extract acoustic landmarks 
    with <strong>audfprint</strong> — a unified pipeline for audio provenance and rights management.
  </div>
  <div class="hero-badges">
    <span class="badge active">Perth Watermarking</span>
    <span class="badge active">Audfprint Fingerprinting</span>
    <span class="badge">WAV Input</span>
    <span class="badge">Local DB Storage</span>
  </div>
</div>
""", unsafe_allow_html=True)

DB_PATH = os.path.join("c:\\design_Projects", "integrated_fpdb.pklz")

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs([" INGEST ", " VERIFY "])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: INGEST
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("""<div class="content-area">""", unsafe_allow_html=True)

    st.markdown("""
    <div class="section-title">Ingest Audio</div>
    <div class="section-sub">
        Upload a WAV file to embed an invisible watermark and register its acoustic fingerprint 
        to the protection database.
    </div>
    """, unsafe_allow_html=True)

    # Step cards
    st.markdown("""
    <div class="steps-row">
      <div class="step-card">
        <div class="step-num">01</div>
        <div class="step-label">Upload</div>
        <div class="step-desc">Drop a WAV audio file you want to protect and register.</div>
      </div>
      <div class="step-card">
        <div class="step-num">02</div>
        <div class="step-label">Watermark</div>
        <div class="step-desc">Perth embeds an imperceptible ownership payload into the signal.</div>
      </div>
      <div class="step-card">
        <div class="step-num">03</div>
        <div class="step-label">Fingerprint</div>
        <div class="step-desc">Acoustic landmarks are extracted and logged to the fingerprint DB.</div>
      </div>
      <div class="step-card">
        <div class="step-num">04</div>
        <div class="step-label">Download</div>
        <div class="step-desc">Retrieve the protected file — ready for distribution.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Upload zone
    st.markdown("""<div class="upload-card">""", unsafe_allow_html=True)
    upload_ingest = st.file_uploader(
        "Drop target audio here — WAV only",
        type=["wav"],
        key="upload_ingest"
    )
    st.markdown("""</div>""", unsafe_allow_html=True)

    if upload_ingest is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬡  PROCESS & INGEST", key="btn_ingest"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_in:
                tmp_in.write(upload_ingest.read())
                tmp_in_path = tmp_in.name

            tmp_out_path = tmp_in_path.replace(".wav", "_watermarked.wav")

            with st.spinner("Applying Perth implicit watermark…"):
                apply_watermark(tmp_in_path, tmp_out_path)

            f = io.StringIO()
            with st.spinner("Registering fingerprints to DB…"):
                with contextlib.redirect_stdout(f):
                    add_to_fingerprint_db(DB_PATH, tmp_out_path)
            fingerprint_logs = f.getvalue()

            st.markdown("""
            <div class="result-card success">
              <div class="result-label">✓ Status</div>
              <div class="result-value">Ingestion complete — watermark embedded, fingerprint registered.</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("FINGERPRINTING LOGS"):
                st.code(fingerprint_logs, language="text")

            with open(tmp_out_path, "rb") as out_file:
                st.download_button(
                    label="⬇  DOWNLOAD PROTECTED FILE",
                    data=out_file,
                    file_name=f"watermarked_{upload_ingest.name}",
                    mime="audio/wav"
                )

            os.remove(tmp_in_path)

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: VERIFY
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""<div class="content-area">""", unsafe_allow_html=True)

    st.markdown("""
    <div class="section-title">Verify Audio</div>
    <div class="section-sub">
        Upload an unknown or suspicious WAV file. The system will cross-reference the 
        fingerprint database and attempt watermark extraction to determine provenance.
    </div>
    """, unsafe_allow_html=True)

    # Step cards
    st.markdown("""
    <div class="steps-row">
      <div class="step-card">
        <div class="step-num">01</div>
        <div class="step-label">Upload Query</div>
        <div class="step-desc">Drop the unknown audio you want to investigate.</div>
      </div>
      <div class="step-card">
        <div class="step-num">02</div>
        <div class="step-label">Fingerprint Match</div>
        <div class="step-desc">Audfprint queries the DB for acoustic landmark matches.</div>
      </div>
      <div class="step-card">
        <div class="step-num">03</div>
        <div class="step-label">Watermark Extract</div>
        <div class="step-desc">Perth decodes any embedded ownership payload from the signal.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div class="upload-card">""", unsafe_allow_html=True)
    upload_verify = st.file_uploader(
        "Drop query audio here — WAV only",
        type=["wav"],
        key="upload_verify"
    )
    st.markdown("""</div>""", unsafe_allow_html=True)

    if upload_verify is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬡  VERIFY AUDIO", key="btn_verify"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_query:
                tmp_query.write(upload_verify.read())
                tmp_query_path = tmp_query.name

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                <div style="font-family:'DM Mono',monospace;font-size:0.68rem;letter-spacing:0.2em;
                            text-transform:uppercase;color:#ffffff;margin-bottom:14px;">
                    ◈ Audfprint Match Results
                </div>
                """, unsafe_allow_html=True)

                with st.spinner("Querying fingerprint database…"):
                    f = io.StringIO()
                    with contextlib.redirect_stdout(f):
                        try:
                            match_fingerprint(DB_PATH, tmp_query_path)
                        except Exception as e:
                            print(f"Error during match: {e}")
                    match_logs = f.getvalue()

                if "Matched" in match_logs:
                    st.markdown("""
                    <div class="result-card success">
                      <div class="result-label">✓ Match Status</div>
                      <div class="result-value">Match found in fingerprint database.</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="result-card error">
                      <div class="result-label">⚠ Match Status</div>
                      <div class="result-value">No definitive match — file requires further investigation.</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.text_area("Raw Match Output", match_logs, height=140, key="match_out")

            with col2:
                st.markdown("""
                <div style="font-family:'DM Mono',monospace;font-size:0.68rem;letter-spacing:0.2em;
                            text-transform:uppercase;color:#ffffff;margin-bottom:14px;">
                    ◈ Perth Watermark Payload
                </div>
                """, unsafe_allow_html=True)

                with st.spinner("Extracting embedded watermark…"):
                    watermark = extract_watermark(tmp_query_path)

                if watermark is not None:
                    st.markdown(f"""
                    <div class="result-card success">
                      <div class="result-label">✓ Payload Extracted</div>
                      <div class="payload-highlight">{watermark}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="result-card error">
                      <div class="result-label">✗ Watermark Status</div>
                      <div class="result-value">No valid watermark payload recovered from this file.</div>
                    </div>
                    """, unsafe_allow_html=True)

            os.remove(tmp_query_path)

    st.markdown("</div>", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
  <div class="footer-brand">SOUNDSEAL</div>
  <div class="footer-note">PERTH ENGINE ◆ AUDFPRINT ◆ INTEGRATED PROTECTION PIPELINE</div>
</div>
""", unsafe_allow_html=True)