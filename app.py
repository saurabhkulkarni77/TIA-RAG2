import streamlit as st
import google.generativeai as genai
from datetime import datetime
import io
import re

# ══════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SCL Agent – Siemens PLC",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════
# CUSTOM CSS
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Rajdhani:wght@400;500;600;700&display=swap');

:root {
    --bg:       #0b0e14;
    --surface:  #111620;
    --surface2: #1a2030;
    --border:   #1e2d45;
    --accent:   #00c2ff;
    --success:  #00e676;
    --danger:   #ff3b3b;
    --warn:     #ffd600;
    --rag:      #b06dff;
    --text:     #c9d6e8;
    --muted:    #5a6a80;
}

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background: var(--bg) !important;
    color: var(--text) !important;
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
.main .block-container { background: var(--bg) !important; padding-top: 2rem !important; }

h1 { font-family:'Rajdhani',sans-serif !important; font-weight:700 !important;
     letter-spacing:3px !important; color:var(--accent) !important; font-size:2rem !important; }
h2, h3 { font-family:'Rajdhani',sans-serif !important; font-weight:600 !important;
          color:var(--text) !important; letter-spacing:1px !important; }

.metric-box { background:var(--surface2); border:1px solid var(--border);
    border-radius:8px; padding:14px 18px; text-align:center; margin-bottom:8px; }
.metric-val { font-family:'JetBrains Mono',monospace; font-size:28px; font-weight:700; color:var(--accent); }
.metric-lbl { font-size:10px; letter-spacing:2px; text-transform:uppercase; color:var(--muted); margin-top:2px; }

.audit-pass { background:rgba(0,230,118,0.08); border:1px solid rgba(0,230,118,0.25);
    border-radius:6px; padding:8px 14px; margin:4px 0;
    font-family:'JetBrains Mono',monospace; font-size:13px; color:var(--success); }
.audit-fail { background:rgba(255,59,59,0.08); border:1px solid rgba(255,59,59,0.25);
    border-radius:6px; padding:8px 14px; margin:4px 0;
    font-family:'JetBrains Mono',monospace; font-size:13px; color:var(--danger); }

.status-ok   { background:linear-gradient(90deg,rgba(0,194,255,0.1),transparent);
    border:1px solid rgba(0,194,255,0.3); border-radius:8px; padding:14px 20px;
    color:var(--accent); font-weight:600; font-size:15px; letter-spacing:1px; }
.status-warn { background:linear-gradient(90deg,rgba(255,214,0,0.1),transparent);
    border:1px solid rgba(255,214,0,0.3); border-radius:8px; padding:14px 20px;
    color:var(--warn); font-weight:600; font-size:15px; }
.status-fail { background:linear-gradient(90deg,rgba(255,59,59,0.1),transparent);
    border:1px solid rgba(255,59,59,0.3); border-radius:8px; padding:14px 20px;
    color:var(--danger); font-weight:600; font-size:15px; }

/* RAG indicator box */
.rag-active { background:linear-gradient(90deg,rgba(176,109,255,0.12),transparent);
    border:1px solid rgba(176,109,255,0.35); border-radius:8px; padding:12px 18px;
    color:var(--rag); font-size:14px; font-weight:600; margin:8px 0; }
.rag-inactive { background:var(--surface2); border:1px solid var(--border);
    border-radius:8px; padding:12px 18px; color:var(--muted); font-size:13px; margin:8px 0; }

/* PDF chunk card */
.chunk-card { background:var(--surface); border:1px solid rgba(176,109,255,0.25);
    border-left:3px solid var(--rag); border-radius:0 8px 8px 0;
    padding:12px 16px; margin:6px 0; font-family:'JetBrains Mono',monospace;
    font-size:12px; line-height:1.6; color:var(--text); }
.chunk-meta { font-size:10px; color:var(--rag); letter-spacing:1px; margin-bottom:6px; }

.tag { display:inline-block; background:rgba(0,194,255,0.12);
    border:1px solid rgba(0,194,255,0.3); border-radius:4px;
    padding:2px 10px; font-size:12px; font-family:'JetBrains Mono',monospace;
    color:var(--accent); margin:2px 3px; }
.tag-warn   { background:rgba(255,214,0,0.1);   border-color:rgba(255,214,0,0.3);   color:var(--warn); }
.tag-ok     { background:rgba(0,230,118,0.1);   border-color:rgba(0,230,118,0.3);   color:var(--success); }
.tag-danger { background:rgba(255,59,59,0.1);   border-color:rgba(255,59,59,0.3);   color:var(--danger); }
.tag-rag    { background:rgba(176,109,255,0.12); border-color:rgba(176,109,255,0.35); color:var(--rag); }

.section-lbl { font-size:10px; font-weight:700; letter-spacing:3px; text-transform:uppercase;
    color:var(--muted); margin:24px 0 10px;
    border-bottom:1px solid var(--border); padding-bottom:6px; }

textarea, input[type="text"], input[type="password"] {
    background:var(--surface2) !important; border:1px solid var(--border) !important;
    border-radius:6px !important; color:var(--text) !important;
    font-family:'Rajdhani',sans-serif !important; font-size:15px !important; }

.stButton > button {
    background:linear-gradient(135deg,#0078a8,#005580) !important;
    color:white !important; border:none !important; border-radius:6px !important;
    font-family:'Rajdhani',sans-serif !important; font-weight:600 !important;
    font-size:15px !important; letter-spacing:1px !important;
    padding:10px 24px !important; transition:all 0.2s !important; }
.stButton > button:hover {
    background:linear-gradient(135deg,#00a0d8,#006a9e) !important;
    box-shadow:0 0 16px rgba(0,194,255,0.3) !important; transform:translateY(-1px) !important; }

[data-testid="stExpander"] { background:var(--surface) !important;
    border:1px solid var(--border) !important; border-radius:8px !important; }
[data-baseweb="select"] > div { background:var(--surface2) !important;
    border-color:var(--border) !important; color:var(--text) !important; }
.stCodeBlock { border:1px solid var(--border) !important; border-radius:8px !important; }

#MainMenu, footer, .stDeployButton { visibility:hidden; }
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
for k, v in {
    "scl_code": None,
    "review_text": None,
    "history": [],
    "active_template": None,
    "rag_chunks": [],        # list of {filename, page, text}
    "rag_index": {},         # filename -> [chunk texts]
    "pdf_names": [],         # uploaded file names
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════
# PDF / RAG HELPERS
# ══════════════════════════════════════════════════════════
def extract_pdf_text(file_bytes: bytes, filename: str, progress_bar=None, ocr_dpi: int = 150) -> list[dict]:
    """
    Extract text from PDF bytes.
    Strategy:
      1. Try pypdf (instant, works for text-based PDFs).
      2. If <20% of pages yield text → OCR fallback via pdf2image + pytesseract (parallel).
    Returns list of {filename, page, text} dicts.
    """
    import concurrent.futures

    # ── Step 1: pypdf fast path ──
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)
        raw_chunks = []
        for i, page in enumerate(reader.pages):
            raw = page.extract_text() or ""
            text = re.sub(r'\n{3,}', '\n\n', raw).strip()
            raw_chunks.append({"filename": filename, "page": i + 1, "text": text})

        non_empty = sum(1 for c in raw_chunks if c["text"])
        if total_pages > 0 and (non_empty / total_pages) >= 0.2:
            return [c for c in raw_chunks if c["text"]]
        total_pages_for_ocr = total_pages
    except Exception:
        total_pages_for_ocr = 0

    # ── Step 2: OCR fallback (parallel, 150 DPI for speed) ──
    try:
        from pdf2image import convert_from_bytes
        import pytesseract

        if progress_bar:
            progress_bar.progress(0.05, text=f"🔍 Scanned PDF — converting pages to images…")

        images = convert_from_bytes(file_bytes, dpi=ocr_dpi)
        total = len(images)
        chunks = []

        def ocr_page(args):
            idx, img = args
            try:
                text = pytesseract.image_to_string(img, lang="eng", config="--psm 3").strip()
                return idx, re.sub(r'\n{3,}', '\n\n', text)
            except Exception:
                return idx, ""

        # Parallel OCR — use up to 4 workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(ocr_page, (i, img)): i for i, img in enumerate(images)}
            done_count = 0
            results = {}
            for future in concurrent.futures.as_completed(futures):
                idx, text = future.result()
                results[idx] = text
                done_count += 1
                if progress_bar:
                    progress_bar.progress(
                        0.05 + 0.93 * (done_count / total),
                        text=f"🔍 OCR: {done_count}/{total} pages of {filename}…"
                    )

        for i in range(total):
            text = results.get(i, "")
            if text:
                chunks.append({"filename": filename, "page": i + 1, "text": text})

        return chunks

    except ImportError:
        st.error(
            f"**{filename}** is a scanned PDF (no embedded text). "
            "OCR libraries are missing. Add `pdf2image` and `pytesseract` to requirements.txt."
        )
        return []
    except Exception as e:
        st.error(f"OCR failed for {filename}: {e}")
        return []

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks of ~chunk_size characters."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def build_rag_index(page_chunks: list[dict]) -> list[dict]:
    """
    Build a flat list of {filename, page, chunk_idx, text} dicts for retrieval.
    Uses simple sentence-aware splitting.
    """
    index = []
    for pc in page_chunks:
        sub_chunks = chunk_text(pc["text"])
        for j, sub in enumerate(sub_chunks):
            if sub.strip():
                index.append({
                    "filename": pc["filename"],
                    "page": pc["page"],
                    "chunk_idx": j,
                    "text": sub.strip(),
                })
    return index

def retrieve_relevant_chunks(query: str, index: list[dict], top_k: int = 6) -> list[dict]:
    """
    Simple keyword-based retrieval (TF-IDF-style term matching).
    Scores each chunk by how many query terms appear in it.
    Works offline with no embeddings required.
    """
    if not index:
        return []

    # Tokenise query
    query_terms = set(re.findall(r'\b\w{3,}\b', query.lower()))
    # Domain-specific boost terms
    boost_terms = {
        "function_block", "var_input", "var_output", "scl", "tia",
        "safety", "interlock", "timer", "ton", "limit", "bool",
        "int", "real", "word", "dint", "return", "end_if", "case"
    }

    scored = []
    for chunk in index:
        chunk_lower = chunk["text"].lower()
        chunk_words = set(re.findall(r'\b\w{3,}\b', chunk_lower))
        # Base score: overlap between query terms and chunk words
        base_score = len(query_terms & chunk_words)
        # Boost if PLC-relevant terms appear
        boost = sum(1 for t in boost_terms if t in chunk_lower) * 0.5
        scored.append((base_score + boost, chunk))

    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:top_k] if _ > 0]

def format_rag_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a block to inject into the prompt."""
    if not chunks:
        return ""
    parts = ["=== RETRIEVED DOCUMENTATION FROM UPLOADED PDFs ===\n"]
    for i, c in enumerate(chunks, 1):
        parts.append(
            f"[Source {i}: {c['filename']} — Page {c['page']}]\n"
            f"{c['text']}\n"
        )
    parts.append("=== END OF DOCUMENTATION ===")
    return "\n".join(parts)


# ══════════════════════════════════════════════════════════
# CONSTANTS & HELPERS
# ══════════════════════════════════════════════════════════
AUDIT_CHECKS = {
    "FUNCTION_BLOCK Structure":     lambda c: "FUNCTION_BLOCK" in c.upper() and "END_FUNCTION_BLOCK" in c.upper(),
    "VAR / END_VAR Declaration":    lambda c: "VAR" in c.upper() and "END_VAR" in c.upper(),
    "Safety Interlock (Global DB)": lambda c: "Global_Safety_DB" in c,
    "3-Way Handshake":              lambda c: "i_HMI_Confirm" in c and "i_System_Ready" in c and "i_AI_Req" in c,
    "Input Clamping (LIMIT)":       lambda c: "LIMIT" in c.upper(),
    "RETURN on Safety Fail":        lambda c: "RETURN" in c.upper(),
    "Output Guard (q_Execute)":     lambda c: "q_Execute" in c,
    "IF / END_IF Syntax":           lambda c: c.upper().count("IF") >= 1 and "END_IF" in c.upper(),
}

TIA_VERSIONS = ["V21", "V20", "V19", "V18", "V17", "V16"]

# Version-specific notes injected into the prompt
TIA_VERSION_NOTES = {
    "V21": (
        "TIA Portal V21 notes: Supports new Motion Control V8, enhanced SIMATIC Safety V21, "
        "improved OPC UA companion spec integration, expanded AI/ML inference blocks via S7-1500 TM NPU. "
        "New: GRAPH V9 Sequencer with parallel branches, ProDiag V3 extended diagnostics, "
        "and SINAMICS G/S drive integration improvements."
    ),
    "V20": (
        "TIA Portal V20 notes: Introduced SIMATIC ODK 1500S for custom C++ user programs, "
        "Motion Control V7 (extended cam disk, interpolation), improved Energy Suite V2, "
        "enhanced Modbus TCP performance blocks, and expanded WinCC Unified V18 integration. "
        "Supports new S7-1500R/H redundancy configurations."
    ),
    "V19": (
        "TIA Portal V19 notes: Added Web server for S7-1200/1500, improved ProDiag V2, "
        "Motion Control V6 with synchronised axes, SIMATIC S7-1500T motion extensions, "
        "and enhanced HMI simulation in TIA Portal."
    ),
    "V18": (
        "TIA Portal V18 notes: Introduced SIMATIC S7-1500 OPC UA server improvements, "
        "expanded GRAPH V8 support, improved SCL editor with IntelliSense, "
        "and enhanced safety program validation."
    ),
    "V17": (
        "TIA Portal V17 notes: Standard release with full S7-1500/1200/300 support, "
        "IEC 61131-3 compliant SCL, GRAPH V7, and WinCC Advanced V17."
    ),
    "V16": (
        "TIA Portal V16 notes: Legacy support baseline. Full IEC 61131-3 SCL. "
        "Some V17+ syntax may not be compatible."
    ),
}

FB_TEMPLATES = {
    "Lead/Lag Pump":    "Lead/Lag Pump Control with pressure monitoring, flow sensors, automatic switchover, runtime hour tracking per pump, and alternating start logic.",
    "PID Temperature":  "PID Temperature Control loop for a heat exchanger. Include setpoint ramp, manual/auto mode switch, output clamping 0–100%, and high/low deviation alarms.",
    "Conveyor Safety":  "Conveyor belt safety gate interlock. Monitor E-Stop, light curtain, physical gate switch. Require operator reset after fault. Include belt speed feedback and jam detection.",
    "Valve Sequencer":  "Motorised valve sequencer with open/close feedback, travel timeout fault, and partial-stroke test capability. Support manual override from HMI.",
    "Motor Soft-Start": "Motor soft-start with ramp-up time, current monitoring, overload protection, and auto-restart on fault clearance with configurable retry limit.",
    "Batch Dosing":     "Batch liquid dosing with load cell feedback, pre-act correction, tolerance checking, batch counter, flush sequence, and CIP mode.",
}

def run_audit(code):
    return {label: fn(code) for label, fn in AUDIT_CHECKS.items()}

def audit_score(results):
    return sum(1 for v in results.values() if v)

def count_lines(code):
    return len([l for l in code.splitlines() if l.strip()])

def count_vars(code):
    return sum(1 for line in code.splitlines() if ":" in line and any(
        t in line.upper() for t in ["BOOL","INT","REAL","DINT","WORD","DWORD","TIME","STRING","TON","CTU"]
    ))

def build_prompt(requirement: str, fb_name: str, opts: dict, rag_context: str = "") -> str:
    plc        = opts.get("plc_model", "S7-1500")
    tia_ver    = opts.get("tia_version", "V19")
    comments   = opts.get("comments", True)
    alarms     = opts.get("alarms", True)
    strictness = opts.get("strictness", "production")
    ver_notes  = TIA_VERSION_NOTES.get(tia_ver, "")
    has_rag    = bool(rag_context.strip())

    prompt_parts = [
        f"Act as a Senior Siemens TIA Portal Developer with 15+ years of {plc} experience.",
        f"You are targeting TIA Portal {tia_ver} on a {plc} CPU.",
        "",
    ]

    if ver_notes:
        prompt_parts += [f"VERSION-SPECIFIC CONTEXT:\n{ver_notes}", ""]

    if has_rag:
        prompt_parts += [
            "IMPORTANT: You have been given documentation excerpts from the user's uploaded TIA Portal PDFs below.",
            "You MUST use specific details, function names, data types, and patterns from these documents",
            "wherever they are relevant to the requirement. Cite the source document inline as (* Source: filename *).",
            "Combine this documentation knowledge with your own expertise to produce the best possible code.",
            "",
            rag_context,
            "",
        ]

    prompt_parts += [
        f"Generate a complete, production-ready Siemens SCL FUNCTION_BLOCK for:",
        f'"{requirement}"',
        "",
        f"FUNCTION BLOCK NAME: {fb_name}",
        "",
        "MANDATORY STRUCTURE:",
        f'1. FUNCTION_BLOCK "{fb_name}"',
        "2. VAR_INPUT: i_AI_Req (Bool), i_HMI_Confirm (Bool), i_System_Ready (Bool), plus all process inputs",
        "3. VAR_OUTPUT: q_Execute (Bool), q_Fault (Bool), q_Status (WORD), plus process outputs",
        "4. VAR (static): state variables, TON timers, counters, handshake state",
        "5. VAR_TEMP: temporary calculation variables only",
        "6. BEGIN ... END_FUNCTION_BLOCK",
        "",
        "SAFETY RULES (non-negotiable):",
        '- FIRST line after BEGIN: IF NOT "Global_Safety_DB".All_Systems_OK THEN q_Fault := TRUE; RETURN; END_IF;',
        "- q_Execute only TRUE when: i_AI_Req AND i_HMI_Confirm AND i_System_Ready AND all local conditions",
        "- ALL analog values scaled with LIMIT(MN:=, IN:=, MX:=)",
        "- Reset all outputs on any fault",
        "",
        "COMMENTING: Use (* comment *) on every logic block. Include header block with FB name, TIA version, date, purpose." if comments else "Minimal inline comments only.",
        "ALARMS: Include bit-mapped q_Status WORD with minimum 4 defined alarm bits." if alarms else "",
        f"Strictness: Full IEC 61131-3 compliance. Every variable declared and typed." if strictness == "production" else "Functional prototype, relax commenting.",
        "",
        f"Target: TIA Portal {tia_ver} on {plc}.",
        "Output ONLY raw SCL text — no markdown, no backticks, no prose. Begin immediately with FUNCTION_BLOCK.",
    ]

    return "\n".join(p for p in prompt_parts if p is not None)


# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ SCL AGENT")
    st.markdown("---")

    # API Key
    try:
        _api_key = st.secrets["GEMINI_API_KEY"]
        st.markdown('<span style="color:#00e676;font-size:13px;font-family:JetBrains Mono,monospace">● API key from secrets</span>', unsafe_allow_html=True)
    except Exception:
        _api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza…")
        if _api_key:
            st.markdown('<span style="color:#00e676;font-size:13px;">● Connected</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span style="color:#ff3b3b;font-size:13px;">● No API Key</span>', unsafe_allow_html=True)

    st.markdown(f"<span style='color:#5a6a80;font-size:12px;font-family:JetBrains Mono,monospace'>{datetime.now().strftime('%Y-%m-%d  %H:%M')}</span>", unsafe_allow_html=True)
    st.markdown("---")

    # ── PDF / RAG Uploader ──
    st.markdown('<div class="section-lbl" style="margin-top:0">📄 RAG — Upload PDFs</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload TIA Portal documentation, manuals, or function block references",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="PDFs will be indexed and the most relevant sections will be injected into the generation prompt automatically."
    )
    ocr_dpi = st.select_slider(
        "OCR Quality (for scanned PDFs)",
        options=[100, 150, 200],
        value=150,
        help="150 DPI = fast (~2s/page). 200 DPI = better accuracy (~5s/page). Only applies to scanned/image PDFs.",
        label_visibility="visible"
    )

    if uploaded_files:
        new_names = [f.name for f in uploaded_files]
        # Only re-process if files changed
        if new_names != st.session_state.pdf_names:
            all_page_chunks = []
            ocr_files = []
            for uf in uploaded_files:
                raw_bytes = uf.read()
                st.markdown(f'<span class="tag-rag">⏳ Processing {uf.name}…</span>', unsafe_allow_html=True)
                progress_bar = st.progress(0, text=f"Extracting {uf.name}…")

                # Quick pre-check: try pypdf to detect if OCR needed
                try:
                    from pypdf import PdfReader
                    import io as _io
                    _r = PdfReader(_io.BytesIO(raw_bytes))
                    _pages = len(_r.pages)
                    _sample = sum(1 for p in _r.pages[:5] if (p.extract_text() or "").strip())
                    needs_ocr = (_sample == 0)
                except Exception:
                    needs_ocr = True
                    _pages = "?"

                if needs_ocr:
                    progress_bar.progress(0, text=f"🔍 Scanned PDF detected — running OCR on {uf.name} ({_pages} pages)…")
                    ocr_files.append(uf.name)

                page_chunks = extract_pdf_text(raw_bytes, uf.name, progress_bar=progress_bar, ocr_dpi=ocr_dpi)
                all_page_chunks.extend(page_chunks)
                progress_bar.progress(1.0, text=f"✅ Done: {uf.name}")

            st.session_state.rag_chunks = build_rag_index(all_page_chunks)
            st.session_state.pdf_names = new_names

        total_chunks = len(st.session_state.rag_chunks)
        total_pages  = len(set((c["filename"], c["page"]) for c in st.session_state.rag_chunks))
        st.markdown(
            f'<div class="rag-active">🔮 RAG ACTIVE<br>'
            f'<span style="font-size:12px;font-weight:400;">'
            f'{len(new_names)} file{"s" if len(new_names)>1 else ""} · '
            f'{total_pages} pages · {total_chunks} chunks indexed</span></div>',
            unsafe_allow_html=True
        )
        for name in new_names:
            n_chunks = sum(1 for c in st.session_state.rag_chunks if c["filename"] == name)
            st.markdown(f'<span class="tag-rag" style="font-size:11px;">📄 {name} ({n_chunks} chunks)</span>', unsafe_allow_html=True)

        if st.button("🗑️ Clear PDFs", use_container_width=True):
            st.session_state.rag_chunks = []
            st.session_state.pdf_names = []
            st.rerun()
    else:
        if st.session_state.rag_chunks:
            # Files were previously loaded but uploader was cleared
            st.session_state.rag_chunks = []
            st.session_state.pdf_names = []
        st.markdown('<div class="rag-inactive">📭 No PDFs uploaded.<br><span style="font-size:12px;">Upload manuals to enable RAG-enhanced generation.</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    page = st.radio("Module", ["🔧 Generator", "📚 RAG Inspector", "📜 History", "📖 SCL Reference"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div class="section-lbl">Session Stats</div>', unsafe_allow_html=True)
    total_gen  = len(st.session_state.history)
    passed_all = sum(1 for h in st.session_state.history if h.get("score") == len(AUDIT_CHECKS))
    rag_used   = sum(1 for h in st.session_state.history if h.get("rag_used"))
    st.markdown(f"""
    <div class="metric-box"><div class="metric-val">{total_gen}</div><div class="metric-lbl">Blocks Generated</div></div>
    <div class="metric-box"><div class="metric-val" style="color:var(--success)">{passed_all}</div><div class="metric-lbl">Full Audits Passed</div></div>
    <div class="metric-box"><div class="metric-val" style="color:var(--rag)">{rag_used}</div><div class="metric-lbl">RAG-Enhanced</div></div>
    """, unsafe_allow_html=True)


# Guard: no API key
if not _api_key:
    st.markdown("# ⚙️ SIEMENS SCL FUNCTION BLOCK AGENT")
    st.info("Enter your Gemini API Key in the sidebar to get started.")
    st.stop()

genai.configure(api_key=_api_key)
model = genai.GenerativeModel("gemini-2.5-flash")


# ══════════════════════════════════════════════════════════
# PAGE: GENERATOR
# ══════════════════════════════════════════════════════════
if "Generator" in page:
    st.markdown("# ⚙️ SIEMENS SCL FUNCTION BLOCK AGENT")

    rag_active = bool(st.session_state.rag_chunks)
    tag_rag = '<span class="tag-rag">🔮 RAG ON</span>' if rag_active else '<span class="tag-warn">📭 RAG OFF</span>'
    st.markdown(
        f'<span class="tag">TIA Portal V16–V21</span>'
        f'<span class="tag">S7-1500 / S7-1200</span>'
        f'<span class="tag">IEC 61131-3</span>'
        f'<span class="tag">SCL</span>'
        f'  {tag_rag}',
        unsafe_allow_html=True
    )

    col_form, col_opts = st.columns([3, 2])

    with col_form:
        st.markdown('<div class="section-lbl">Quick Templates</div>', unsafe_allow_html=True)
        tpl_cols = st.columns(3)
        for idx, tname in enumerate(FB_TEMPLATES):
            with tpl_cols[idx % 3]:
                if st.button(tname, key=f"tpl_{idx}", use_container_width=True):
                    st.session_state.active_template = FB_TEMPLATES[tname]
                    st.rerun()

        st.markdown('<div class="section-lbl">Function Block Requirement</div>', unsafe_allow_html=True)
        requirement = st.text_area(
            "Requirement",
            value=st.session_state.active_template or "",
            height=130,
            placeholder="e.g. Lead/Lag pump control with pressure safety interlock, flow monitoring, and HMI status feedback…",
            label_visibility="collapsed"
        )
        fb_name = st.text_input(
            "Function Block Name",
            value="FB_Generated_Logic",
            help='Appears as FUNCTION_BLOCK "FB_Generated_Logic"'
        )

        # Show RAG preview if active
        if rag_active and requirement.strip():
            preview_chunks = retrieve_relevant_chunks(requirement, st.session_state.rag_chunks, top_k=3)
            if preview_chunks:
                st.markdown('<div class="section-lbl">🔮 RAG Preview — Top Matching Chunks</div>', unsafe_allow_html=True)
                for pc in preview_chunks:
                    st.markdown(
                        f'<div class="chunk-card">'
                        f'<div class="chunk-meta">📄 {pc["filename"]} · Page {pc["page"]}</div>'
                        f'{pc["text"][:300]}{"…" if len(pc["text"])>300 else ""}'
                        f'</div>',
                        unsafe_allow_html=True
                    )

    with col_opts:
        st.markdown('<div class="section-lbl">Generation Options</div>', unsafe_allow_html=True)
        plc_model   = st.selectbox("Target PLC", ["S7-1500", "S7-1200", "S7-300 (Legacy)"])
        tia_version = st.selectbox("TIA Portal Version", TIA_VERSIONS)
        strictness  = st.radio("Code Standard", ["production", "prototype"], horizontal=True)
        include_comments = st.toggle("Inline Comments", value=True)
        include_alarms   = st.toggle("Alarm Status Word", value=True)
        add_review       = st.toggle("AI Code Review", value=True)
        rag_top_k        = st.slider("RAG chunks to inject", 2, 10, 6, disabled=not rag_active,
                                     help="How many PDF chunks to retrieve and inject into the prompt")

        # Version notes preview
        ver_note = TIA_VERSION_NOTES.get(tia_version, "")
        if ver_note:
            st.markdown('<div class="section-lbl">Version Notes</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:12px;color:var(--muted);font-family:JetBrains Mono,monospace;line-height:1.5">{ver_note}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-lbl">Audit Checks</div>', unsafe_allow_html=True)
        for check in AUDIT_CHECKS:
            st.markdown(f'<span class="tag" style="font-size:11px;margin:2px;">{check}</span>', unsafe_allow_html=True)

    st.markdown("")
    gen_col, _ = st.columns([2, 3])
    with gen_col:
        generate = st.button("⚡ GENERATE FUNCTION BLOCK", use_container_width=True)

    if generate:
        if not requirement.strip():
            st.warning("⚠️ Enter a requirement or select a template.")
        else:
            # RAG retrieval
            rag_context = ""
            retrieved_chunks = []
            if rag_active:
                retrieved_chunks = retrieve_relevant_chunks(
                    requirement, st.session_state.rag_chunks, top_k=rag_top_k
                )
                rag_context = format_rag_context(retrieved_chunks)

            opts = {
                "plc_model": plc_model, "tia_version": tia_version,
                "strictness": strictness, "comments": include_comments,
                "alarms": include_alarms,
            }
            prompt = build_prompt(requirement, fb_name, opts, rag_context)

            with st.spinner(f"Generating SCL for TIA Portal {tia_version}{' with RAG' if rag_active else ''}…"):
                response = model.generate_content(prompt)
                scl_code = response.text.strip()
                for fence in ["```scl", "```pascal", "```", "~~~"]:
                    scl_code = scl_code.replace(fence, "")
                st.session_state.scl_code = scl_code.strip()
                st.session_state.review_text = None

            if add_review:
                with st.spinner("Running AI code review…"):
                    review_prompt = f"""You are a senior Siemens TIA Portal {tia_version} engineer doing a code review.
Analyse this SCL Function Block and provide a structured review:

**1. Correctness** – syntax issues, undeclared variables, logic errors
**2. Safety Gaps** – missing interlocks, unguarded outputs, missing RETURN paths
**3. TIA Portal {tia_version} Compatibility** – version-specific issues
**4. Optimisation Tips** – redundant code, better patterns, performance
**5. RAG Utilisation** – {"did the code correctly use the documentation context?" if rag_active else "N/A (no PDFs uploaded)"}
**6. Overall Rating** – score /10 with one-line verdict

Be concise, technical, and specific. Use bullet points.

SCL Code:
{st.session_state.scl_code}"""
                    st.session_state.review_text = model.generate_content(review_prompt).text

            # Save to history
            audit_results = run_audit(st.session_state.scl_code)
            st.session_state.history.insert(0, {
                "timestamp":  datetime.now().strftime("%H:%M:%S"),
                "requirement": requirement[:60] + ("…" if len(requirement) > 60 else ""),
                "fb_name":    fb_name,
                "plc":        plc_model,
                "tia":        tia_version,
                "code":       st.session_state.scl_code,
                "score":      audit_score(audit_results),
                "lines":      count_lines(st.session_state.scl_code),
                "rag_used":   rag_active,
                "rag_sources": list({c["filename"] for c in retrieved_chunks}),
            })

    # ── Results ──
    if st.session_state.scl_code:
        scl_code = st.session_state.scl_code
        audit_results = run_audit(scl_code)
        score = audit_score(audit_results)
        total_checks = len(AUDIT_CHECKS)

        st.markdown("---")

        # RAG sources used banner
        if st.session_state.history and st.session_state.history[0].get("rag_used"):
            sources = st.session_state.history[0].get("rag_sources", [])
            if sources:
                src_tags = " ".join(f'<span class="tag-rag">📄 {s}</span>' for s in sources)
                st.markdown(
                    f'<div class="rag-active">🔮 RAG-enhanced — Generated using your uploaded documentation: {src_tags}</div>',
                    unsafe_allow_html=True
                )

        st.markdown('<div class="section-lbl">Generated Output</div>', unsafe_allow_html=True)

        mc1, mc2, mc3, mc4 = st.columns(4)
        sc_color = "var(--success)" if score == total_checks else "var(--warn)" if score >= int(total_checks * 0.7) else "var(--danger)"
        mc1.markdown(f'<div class="metric-box"><div class="metric-val">{count_lines(scl_code)}</div><div class="metric-lbl">Lines of Code</div></div>', unsafe_allow_html=True)
        mc2.markdown(f'<div class="metric-box"><div class="metric-val">{count_vars(scl_code)}</div><div class="metric-lbl">Variables Declared</div></div>', unsafe_allow_html=True)
        mc3.markdown(f'<div class="metric-box"><div class="metric-val" style="color:{sc_color}">{score}/{total_checks}</div><div class="metric-lbl">Audit Score</div></div>', unsafe_allow_html=True)
        mc4.markdown(f'<div class="metric-box"><div class="metric-val" style="color:var(--accent)">{int(score/total_checks*100)}%</div><div class="metric-lbl">Compliance</div></div>', unsafe_allow_html=True)

        code_col, audit_col = st.columns([3, 2])

        with code_col:
            st.markdown('<div class="section-lbl">SCL Source Code</div>', unsafe_allow_html=True)
            st.code(scl_code, language="pascal")
            dl1, dl2 = st.columns(2)
            with dl1:
                st.download_button("💾 Download .SCL", data=scl_code, file_name=f"{fb_name}.scl",
                                   mime="text/plain", use_container_width=True)
            with dl2:
                st.download_button("📄 Download .TXT", data=scl_code, file_name=f"{fb_name}.txt",
                                   mime="text/plain", use_container_width=True)

        with audit_col:
            st.markdown('<div class="section-lbl">Security & Compliance Audit</div>', unsafe_allow_html=True)
            for check, passed in audit_results.items():
                css  = "audit-pass" if passed else "audit-fail"
                icon = "✅" if passed else "❌"
                st.markdown(f'<div class="{css}">{icon} {check}</div>', unsafe_allow_html=True)

            st.markdown("")
            if score == total_checks:
                st.markdown('<div class="status-ok">✅ VALIDATED — READY FOR TIA PORTAL</div>', unsafe_allow_html=True)
            elif score >= int(total_checks * 0.7):
                st.markdown('<div class="status-warn">⚠️ PARTIAL PASS — MANUAL REVIEW REQUIRED</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-fail">❌ AUDIT FAILED — DO NOT DEPLOY</div>', unsafe_allow_html=True)

            failed = [k for k, v in audit_results.items() if not v]
            if failed:
                st.markdown('<div class="section-lbl">Remediation Needed</div>', unsafe_allow_html=True)
                for f in failed:
                    st.markdown(f'<span class="tag-danger">{f}</span>', unsafe_allow_html=True)

        if st.session_state.review_text:
            st.markdown("---")
            with st.expander("🤖 AI Code Review Report", expanded=True):
                st.markdown(st.session_state.review_text)


# ══════════════════════════════════════════════════════════
# PAGE: RAG INSPECTOR
# ══════════════════════════════════════════════════════════
elif "RAG" in page:
    st.markdown("# 📚 RAG KNOWLEDGE BASE INSPECTOR")
    st.caption("Browse the indexed PDF chunks and test retrieval")

    if not st.session_state.rag_chunks:
        st.info("No PDFs indexed yet. Upload TIA Portal documentation in the sidebar.")
        st.stop()

    chunks = st.session_state.rag_chunks
    filenames = sorted(set(c["filename"] for c in chunks))

    # Stats
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="metric-box"><div class="metric-val">{len(filenames)}</div><div class="metric-lbl">PDFs Indexed</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-box"><div class="metric-val">{len(set((c["filename"],c["page"]) for c in chunks))}</div><div class="metric-lbl">Pages Processed</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-box"><div class="metric-val" style="color:var(--rag)">{len(chunks)}</div><div class="metric-lbl">Chunks in Index</div></div>', unsafe_allow_html=True)

    # Retrieval test
    st.markdown("---")
    st.markdown('<div class="section-lbl">🔍 Test Retrieval</div>', unsafe_allow_html=True)
    test_query = st.text_input("Enter a query to see which chunks would be retrieved", placeholder="e.g. TON timer usage in SCL function block")
    top_k_test = st.slider("Number of chunks to retrieve", 1, 15, 6)

    if test_query:
        hits = retrieve_relevant_chunks(test_query, chunks, top_k=top_k_test)
        if hits:
            st.markdown(f"**Found {len(hits)} relevant chunks:**")
            for i, h in enumerate(hits, 1):
                st.markdown(
                    f'<div class="chunk-card">'
                    f'<div class="chunk-meta">#{i} · 📄 {h["filename"]} · Page {h["page"]} · Chunk {h["chunk_idx"]}</div>'
                    f'{h["text"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.warning("No relevant chunks found for this query. Try different keywords.")

    # Browse by file
    st.markdown("---")
    st.markdown('<div class="section-lbl">📂 Browse by File</div>', unsafe_allow_html=True)
    sel_file = st.selectbox("Select PDF", filenames)
    if sel_file:
        file_chunks = [c for c in chunks if c["filename"] == sel_file]
        pages = sorted(set(c["page"] for c in file_chunks))
        sel_page = st.selectbox(f"Page ({len(pages)} pages)", pages)
        page_chunks = [c for c in file_chunks if c["page"] == sel_page]
        for pc in page_chunks:
            st.markdown(
                f'<div class="chunk-card">'
                f'<div class="chunk-meta">Chunk {pc["chunk_idx"]+1} of {len(page_chunks)} on this page</div>'
                f'{pc["text"]}'
                f'</div>',
                unsafe_allow_html=True
            )


# ══════════════════════════════════════════════════════════
# PAGE: HISTORY
# ══════════════════════════════════════════════════════════
elif "History" in page:
    st.markdown("# 📜 GENERATION HISTORY")
    st.caption("All Function Blocks generated this session")

    history = st.session_state.history
    if not history:
        st.info("No blocks generated yet.")
    else:
        for i, item in enumerate(history):
            score = item.get("score", 0)
            total = len(AUDIT_CHECKS)
            sc = "var(--success)" if score == total else "var(--warn)" if score >= int(total * 0.7) else "var(--danger)"
            rag_badge = ' <span class="tag-rag">🔮 RAG</span>' if item.get("rag_used") else ""
            with st.expander(
                f"⚙️ {item['fb_name']}  |  {item['timestamp']}  |  {item['plc']}  |  TIA {item.get('tia','?')}  |  Score {score}/{total}",
                expanded=False
            ):
                st.markdown(f"**Requirement:** {item['requirement']}")
                src_tags = " ".join(f'<span class="tag-rag">{s}</span>' for s in item.get("rag_sources", []))
                st.markdown(
                    f'<span class="tag">{item["plc"]}</span>'
                    f'<span class="tag">TIA {item.get("tia","?")}</span>'
                    f'<span class="tag">{item["lines"]} lines</span>'
                    f'<span class="tag" style="color:{sc}">Audit {score}/{total}</span>'
                    f'{rag_badge} {src_tags}',
                    unsafe_allow_html=True
                )
                st.code(item["code"], language="pascal")
                st.download_button(
                    f"💾 Download {item['fb_name']}.scl",
                    data=item["code"], file_name=f"{item['fb_name']}.scl",
                    mime="text/plain", key=f"dl_hist_{i}"
                )

        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()


# ══════════════════════════════════════════════════════════
# PAGE: SCL REFERENCE
# ══════════════════════════════════════════════════════════
elif "Reference" in page:
    st.markdown("# 📖 SCL QUICK REFERENCE")
    st.caption("Common patterns for Siemens TIA Portal SCL development")

    r1, r2 = st.columns(2)
    with r1:
        st.markdown("### Block Structure")
        st.code("""FUNCTION_BLOCK "FB_Name"
VAR_INPUT
    i_Enable   : Bool;
    i_Setpoint : Real;
END_VAR
VAR_OUTPUT
    q_Active   : Bool;
    q_Fault    : Bool;
END_VAR
VAR
    s_State    : Int;
    s_Timer    : TON;
END_VAR
VAR_TEMP
    t_Calc     : Real;
END_VAR

BEGIN
    IF NOT "Global_Safety_DB".All_Systems_OK THEN
        q_Fault := TRUE;
        RETURN;
    END_IF;

END_FUNCTION_BLOCK""", language="pascal")

        st.markdown("### LIMIT Function")
        st.code("""scaled := LIMIT(MN := 0.0,
                IN := raw_analog,
                MX := 100.0);""", language="pascal")

        st.markdown("### TON Timer")
        st.code("""s_Timer(IN := i_StartCondition,
        PT := T#5S,
        Q  => s_Done,
        ET => s_Elapsed);""", language="pascal")

    with r2:
        st.markdown("### 3-Way Handshake")
        st.code("""IF i_AI_Req AND i_HMI_Confirm AND i_System_Ready THEN
    q_Execute := TRUE;
ELSE
    q_Execute := FALSE;
END_IF;""", language="pascal")

        st.markdown("### State Machine")
        st.code("""CASE s_State OF
    0: (* IDLE *)
        IF i_Start THEN s_State := 1; END_IF;
    1: (* RUNNING *)
        q_Running := TRUE;
        IF i_Stop OR q_Fault THEN
            s_State := 0;
        END_IF;
    ELSE
        s_State := 0;
END_CASE;""", language="pascal")

        st.markdown("### Alarm Status Word")
        st.code("""q_Status.%X0 := b_OverTemp;
q_Status.%X1 := b_UnderPressure;
q_Status.%X2 := b_MotorFault;
q_Status.%X3 := b_CommTimeout;""", language="pascal")

        st.markdown("### Safety DB Check")
        st.code("""IF NOT "Global_Safety_DB".All_Systems_OK THEN
    q_Execute := FALSE;
    q_Fault   := TRUE;
    s_State   := 0;
    RETURN;
END_IF;""", language="pascal")

    st.markdown("---")
    st.markdown("### TIA Portal Version Compatibility")
    for ver in TIA_VERSIONS:
        note = TIA_VERSION_NOTES.get(ver, "")
        with st.expander(f"TIA Portal {ver}", expanded=(ver in ["V21", "V20"])):
            st.markdown(f'<div style="font-size:13px;font-family:JetBrains Mono,monospace;color:var(--text);line-height:1.6">{note}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### IEC 61131-3 Data Types")
    types = [
        ("Bool","1-bit boolean","TRUE / FALSE"),
        ("Int","16-bit signed","−32768..32767"),
        ("DInt","32-bit signed","−2147483648..2147483647"),
        ("Real","32-bit float","±3.4×10³⁸"),
        ("Word","16-bit unsigned","0..65535"),
        ("Time","Duration","T#1D2H3M4S5MS"),
        ("String","Characters","String[254]"),
        ("TON","On-delay timer","IN, PT → Q, ET"),
    ]
    tc1, tc2 = st.columns(2)
    for i, (dtype, desc, rng) in enumerate(types):
        col = tc1 if i % 2 == 0 else tc2
        col.markdown(
            f'<span class="tag">{dtype}</span> '
            f'<span style="color:var(--muted);font-size:13px;">{desc} — {rng}</span>',
            unsafe_allow_html=True
        )
