import streamlit as st
import textwrap
import re
from PIL import Image

COLORS = {
    "A": {"bg": "#2E6DA4", "fg": "white", "label": "Analytic"},
    "B": {"bg": "#F1C232", "fg": "#1a1a1a", "label": "Practical"},
    "C": {"bg": "#2AA876", "fg": "white", "label": "Relational"},
    "D": {"bg": "#E74C3C", "fg": "white", "label": "Creative"},
}

EMOTION_WORDS = ["stuck", "overwhelmed", "anxious", "worried", "panicked", "frustrated", "angry", "uncertain", "lost", "torn"]
DECISION_WORDS = ["choose", "decision", "decide", "between", "option", "options", "tradeoff", "which", "whether"]
CONSTRAINT_WORDS = ["deadline", "pressure", "limited", "time", "money", "resource", "constraints", "risk", "can’t", "can't", "cannot"]
RELATION_WORDS = ["team", "colleague", "manager", "client", "customer", "partner", "people", "relationship", "trust", "conflict", "impacted", "affected"]

def sanitize(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text

def detect_intents(text: str):
    t = text.lower()
    return {
        "emotion": any(w in t for w in EMOTION_WORDS),
        "decision": any(w in t for w in DECISION_WORDS),
        "constraint": any(w in t for w in CONSTRAINT_WORDS),
        "relationship": any(w in t for w in RELATION_WORDS),
    }

def domain_from_flags(flags):
    if flags["decision"] and flags["constraint"]:
        return "decision_under_constraints"
    if flags["decision"]:
        return "decision"
    if flags["relationship"]:
        return "relationship"
    if flags["constraint"]:
        return "constraint_pressure"
    if flags["emotion"]:
        return "emotion"
    return "general"

def short_questions(thought: str):
    thought = sanitize(thought) or "I feel stuck"
    flags = detect_intents(thought)
    domain = domain_from_flags(flags)
    q = f"“{thought}”"

    # Keep them short (1 line-ish)
    if domain == "decision_under_constraints":
        return {
            "A": f"What do I know for sure about {q}?",
            "B": f"What is the next realistic adjustment for {q}?",
            "C": f"Who is impacted by my decision in {q}?",
            "D": f"What’s a creative option that fits the constraints for {q}?"
        }
    if domain == "decision":
        return {
            "A": f"What are the facts behind my choice in {q}?",
            "B": f"What’s one practical step that clarifies my decision in {q}?",
            "C": f"Who’s affected by the choice in {q}?",
            "D": f"What else could I choose or frame in {q}?"
        }
    if domain == "relationship":
        return {
            "A": f"What do I know for sure about what’s happening in {q}?",
            "B": f"What’s one practical move to improve this in {q}?",
            "C": f"Who needs a voice/understanding in {q}?",
            "D": f"What new way of working could help in {q}?"
        }
    if domain == "constraint_pressure":
        return {
            "A": f"What’s true right now about {q} (not just worry)?",
            "B": f"What can I adjust immediately to reduce pressure in {q}?",
            "C": f"Who is affected by the pressure in {q}?",
            "D": f"What else is possible without fighting the constraint in {q}?"
        }
    if domain == "emotion":
        return {
            "A": f"What facts explain what I’m feeling in {q}?",
            "B": f"What’s one practical adjustment that helps in {q}?",
            "C": f"Who might be impacted by my feeling in {q}?",
            "D": f"What reframe makes space for possibility in {q}?"
        }

    # general fallback
    return {
        "A": f"What do I know for sure about {q}?",
        "B": f"What’s the next practical step for easing {q}?",
        "C": f"Who is impacted or missing in {q}?",
        "D": f"What else is possible if I shift perspective on {q}?"
    }

def card_block(q_key: str, prompt: str):
    c = COLORS[q_key]
    wrapped = textwrap.fill(prompt, width=46)

    st.markdown(
        f"""
        <div style="
            background-color: {c['bg']};
            color: {c['fg']};
            border-radius: 14px;
            padding: 14px 16px;
            min-height: 130px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.12);
            border: 1px solid rgba(255,255,255,0.12);
        ">
          <div style="font-weight: 800; font-size: 14px; margin-bottom: 10px; opacity: 0.95;">
            {q_key} — {c['label']}
          </div>
          <div style="font-size: 15px; line-height: 1.4;">
            {wrapped}
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    st.set_page_config(page_title="HBDI 4-Quadrant Reset", layout="wide")

    # Logo top-left
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=160)
    except Exception as e:
        st.warning(f"Logo not found. Ensure logo.png is next to the app file. ({e})")

    st.title("HBDI 4-Quadrant Reset (1-minute prompt)")
    st.caption("One short question per quadrant. Prompts adapt to what you type—still HBDI-aligned.")

    thought = st.text_input(
        "Your sentence or feeling",
        placeholder='e.g., "I feel stuck choosing between two options under a deadline"'
    )

    if st.button("Generate 4 questions", type="primary"):
        qs = short_questions(thought)

        col1, col2 = st.columns(2, gap="medium")
        with col1:
            card_block("A", qs["A"])
        with col2:
            card_block("B", qs["B"])

        col3, col4 = st.columns(2, gap="medium")
        with col3:
            card_block("C", qs["C"])
        with col4:
            card_block("D", qs["D"])

        st.divider()
        st.success("Take 30–60 seconds. Scan A → B → C → D, then pick ONE to explore first.")

if __name__ == "__main__":
    main()
