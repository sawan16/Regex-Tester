"""
Regex Tester — a live, local regex playground built with Streamlit.

Run with:
    streamlit run app.py
"""

import html
import json
import re

import streamlit as st

st.set_page_config(page_title="Regex Tester", page_icon="🔍", layout="wide")

# --------------------------------------------------------------------------
# Data: common patterns + flags
# --------------------------------------------------------------------------

COMMON_PATTERNS = {
    "Email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "URL": r"https?://[^\s/$.?#].[^\s]*",
    "IPv4 address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "Phone (US-style)": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    "Date (YYYY-MM-DD)": r"\d{4}-\d{2}-\d{2}",
    "Hex color": r"#(?:[0-9a-fA-F]{3}){1,2}\b",
    "Hashtag": r"#\w+",
    "HTML tag": r"</?[a-zA-Z][^>]*>",
}

FLAG_OPTIONS = {
    "IGNORECASE (i)": re.IGNORECASE,
    "MULTILINE (m)": re.MULTILINE,
    "DOTALL (s)": re.DOTALL,
    "VERBOSE (x)": re.VERBOSE,
}

HIGHLIGHT_COLORS = ["#ffe08a", "#a8e6a1", "#a3d8f4", "#f4a3d8", "#d8a3f4", "#f4c9a3"]

DEFAULT_PRESETS = {name: pattern for name, pattern in COMMON_PATTERNS.items()}


# --------------------------------------------------------------------------
# Session state init
# --------------------------------------------------------------------------

if "pattern" not in st.session_state:
    st.session_state.pattern = r"\b\w+@\w+\.\w+\b"
if "test_string" not in st.session_state:
    st.session_state.test_string = (
        "Contact us at hello@example.com or support@example.org.\n"
        "Visit https://example.com/docs for more info.\n"
        "Call (555) 123-4567 between 2024-01-01 and 2024-12-31."
    )
if "saved_presets" not in st.session_state:
    st.session_state.saved_presets = {}


def load_pattern(p):
    st.session_state.pattern = p


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

st.sidebar.title("🔍 Regex Tester")
st.sidebar.caption("Runs 100% locally — nothing you type leaves your machine.")

st.sidebar.subheader("Common patterns")
for name, pattern in COMMON_PATTERNS.items():
    st.sidebar.button(name, on_click=load_pattern, args=(pattern,), use_container_width=True)

st.sidebar.divider()
st.sidebar.subheader("Your saved patterns")
if st.session_state.saved_presets:
    for name, pattern in list(st.session_state.saved_presets.items()):
        c1, c2 = st.sidebar.columns([4, 1])
        c1.button(name, on_click=load_pattern, args=(pattern,), use_container_width=True, key=f"load_{name}")
        if c2.button("🗑️", key=f"del_{name}"):
            del st.session_state.saved_presets[name]
            st.rerun()
else:
    st.sidebar.caption("No saved patterns yet.")

new_name = st.sidebar.text_input("Save current pattern as…", placeholder="e.g. My email regex")
if st.sidebar.button("💾 Save pattern", use_container_width=True) and new_name:
    st.session_state.saved_presets[new_name] = st.session_state.pattern
    st.rerun()

if st.session_state.saved_presets:
    export = json.dumps(st.session_state.saved_presets, indent=2)
    st.sidebar.download_button("⬇️ Export presets (.json)", export, "regex_presets.json", "application/json", use_container_width=True)

uploaded_presets = st.sidebar.file_uploader("⬆️ Import presets (.json)", type="json")
if uploaded_presets is not None:
    try:
        imported = json.load(uploaded_presets)
        st.session_state.saved_presets.update(imported)
        st.sidebar.success(f"Imported {len(imported)} pattern(s).")
    except Exception as e:
        st.sidebar.error(f"Couldn't read that file: {e}")


# --------------------------------------------------------------------------
# Main layout
# --------------------------------------------------------------------------

st.title("Regex Tester")

col1, col2 = st.columns([3, 2])

with col1:
    pattern_str = st.text_input("Pattern", key="pattern", label_visibility="visible")

with col2:
    flag_labels = st.multiselect("Flags", list(FLAG_OPTIONS.keys()))

flags = 0
for label in flag_labels:
    flags |= FLAG_OPTIONS[label]

test_string = st.text_area("Test string", key="test_string", height=180)

# --------------------------------------------------------------------------
# Compile + match
# --------------------------------------------------------------------------

compiled = None
error_msg = None
matches = []

if pattern_str:
    try:
        compiled = re.compile(pattern_str, flags)
        matches = list(compiled.finditer(test_string))
    except re.error as e:
        error_msg = str(e)

if error_msg:
    st.error(f"Invalid regex: {error_msg}")
elif not pattern_str:
    st.info("Enter a pattern above to see matches.")
else:
    st.success(f"{len(matches)} match{'es' if len(matches) != 1 else ''} found.")

    # ---- Highlighted preview ----
    st.subheader("Highlighted matches")
    if matches:
        pieces = []
        last_end = 0
        for i, m in enumerate(matches):
            start, end = m.span()
            pieces.append(html.escape(test_string[last_end:start]))
            color = HIGHLIGHT_COLORS[i % len(HIGHLIGHT_COLORS)]
            matched_text = html.escape(test_string[start:end]) or "&nbsp;"
            pieces.append(
                f'<span style="background-color:{color}; border-radius:3px; padding:1px 2px;" '
                f'title="Match {i + 1}">{matched_text}</span>'
            )
            last_end = end
        pieces.append(html.escape(test_string[last_end:]))
        highlighted_html = "".join(pieces).replace("\n", "<br>")
        st.markdown(
            f'<div style="white-space:pre-wrap; font-family:monospace; line-height:1.6; '
            f'border:1px solid #444; border-radius:6px; padding:12px;">{highlighted_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="white-space:pre-wrap; font-family:monospace; '
            f'border:1px solid #444; border-radius:6px; padding:12px;">{html.escape(test_string)}</div>',
            unsafe_allow_html=True,
        )

    # ---- Match details table ----
    if matches:
        st.subheader("Match details")
        rows = []
        for i, m in enumerate(matches):
            rows.append({
                "#": i + 1,
                "Match": m.group(0),
                "Start": m.start(),
                "End": m.end(),
                "Groups": str(m.groups()) if m.groups() else "—",
                "Named groups": str(m.groupdict()) if m.groupdict() else "—",
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)

    # ---- Substitution ----
    st.subheader("Replace")
    repl = st.text_input("Replacement (use \\1, \\2 … for groups, or \\g<name>)", key="replacement")
    if compiled and matches:
        try:
            result = compiled.sub(repl, test_string)
            st.text_area("Result after replacement", value=result, height=140)
        except re.error as e:
            st.error(f"Invalid replacement: {e}")

    # ---- Explanation ----
    with st.expander("💡 Quick regex cheatsheet"):
        st.markdown(
            """
| Token | Meaning |
|---|---|
| `.` | Any character except newline |
| `\\d` `\\w` `\\s` | Digit, word char, whitespace |
| `\\D` `\\W` `\\S` | Negations of the above |
| `*` `+` `?` | 0+, 1+, 0-or-1 repetitions |
| `{n,m}` | Between n and m repetitions |
| `^` `$` | Start / end of string (or line, with MULTILINE) |
| `(...)` | Capturing group |
| `(?:...)` | Non-capturing group |
| `(?P<name>...)` | Named group |
| `\\|` | Alternation (OR) |
| `[abc]` | Character class |
| `(?=...)` `(?!...)` | Lookahead / negative lookahead |
"""
        )

st.sidebar.divider()
st.sidebar.caption("Built with Streamlit + Python's built-in `re` module.")
