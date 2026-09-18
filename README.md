# Regex Tester

A live, local regex playground built with Streamlit. Type a pattern, see
matches highlighted in real time, inspect groups, test replacements, and
save your favorite patterns for later — all running on your own machine.

## Features

- **Live highlighting** — matches are highlighted inline as you type, each
  match colored distinctly
- **Match details table** — start/end index, captured groups, named groups
- **Flags** — toggle IGNORECASE, MULTILINE, DOTALL, VERBOSE
- **Replace mode** — test substitutions with backreferences (`\1`, `\g<name>`)
- **Common pattern library** — one-click load for email, URL, IPv4, phone,
  date, hex color, hashtag, HTML tag
- **Save/load your own presets** — stored in-session, with JSON export/import
  so you can carry your pattern library between sessions
- **Built-in cheatsheet** — quick reference for regex syntax

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Your browser opens automatically at `http://localhost:8501`.

## Notes

- Uses Python's built-in `re` module — no external regex engine dependency.
- Saved presets live in Streamlit's session state (cleared on restart) unless
  you export them to JSON and re-import next time.

## Extending it

The whole app is one file (`app.py`). Easy additions:
- Support the third-party `regex` module for features `re` lacks
  (e.g. recursive patterns, fuzzy matching)
- Add a "regex golf" mode with sample challenges
- Syntax-highlight the pattern itself, not just the matches
