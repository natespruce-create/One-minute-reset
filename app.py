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
RELATION_WORDS = ["team", "colleague", "manager", "client", "customer", "partner", "people", "relationship", "trust", "conflict", "impacted", "affected", "colleague"]

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
    thought = sanitize(thought) or ""
    flags = detect_intents(thought)
    domain = domain_from_flags(flags)

    # Short, high-utility questions that do NOT paste the whole sentence back.
    # We may reference "the situation" rather than echo the user input.
    if domain == "relationship":
        return {
            "A": "What observable facts do I have (not assumptions) about the working dynamic?",
            "B": "What’s one practical next step to clarify expectations or reduce uncertainty?",
            "C": "What needs to be understood or agreed with the other person/team for trust to work?",
            "D": "What alternate way of working (or framing) could make this easier?"
        }

    if domain == "decision_under_constraints":
        return {
            "A": "What are the true constraints and the key facts I’m using to decide?",
            "B": "What’s the next realistic action that reduces uncertainty about the decision?",
            "C": "Who is impacted if I choose one option over another?",
            "D": "What creative option appears if we treat constraints as design inputs?"
        }

    if domain == "decision":
        return {
            "A": "What facts vs beliefs am I relying on for this choice?",
            "B": "What’s one practical step that helps me test the options quickly?",
            "C": "Whose needs matter in this decision—and have I heard them?",
            "D": "What else is possible beyond the two options I’m comparing?"
        }

    if domain == "constraint_pressure":
        return {
            "A": "What’s truly true right now (observable) versus what I’m worried about?",
            "B": "What can I adjust immediately to reduce pressure and create momentum?",
            "C": "Who’s affected by the pressure—and what do they need from me?",
            "D": "What reframe makes the problem feel more solvable?"
        }

    if domain == "emotion":
        return {
            "A": "What facts are underneath this feeling?",
            "B": "What’s one practical adjustment that would help me move 5% today?",
            "C": "Who might be affected by how I respond right now?",
            "D": "What’s a kinder reframe that opens a new option?"
        }

    # general fallback
    return {
        "A": "What do I know for sure (observable facts), and what am I assuming?",
        "B": "What’s one practical next step to reduce the stuck feeling?",
        "C": "Who is impacted—or missing—from this picture?",
        "D": "What’s another angle that makes progress possible?"
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
    st.caption("One short question per quadrant. The questions interpret your input—without repeating it verbatim.")

    thought = st.text_input(
        "Your sentence or feeling",
        placeholder='e.g., "I feel uncertain about working with a colleague"'
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
