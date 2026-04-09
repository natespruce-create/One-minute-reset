import streamlit as st
import textwrap
import re
from PIL import Image

# Colors by position requirement:
# Top-left (blue) = Analytical
# Bottom-left (green) = Practical
# Top-right (yellow) = Creative
# Bottom-right (red) = Relational

COLORS = {
    "A": {"bg": "#2E6DA4", "fg": "white", "label": "Analytical"},   # Blue
    "B": {"bg": "#2AA876", "fg": "white", "label": "Practical"},    # Green
    "C": {"bg": "#F1C232", "fg": "#1a1a1a", "label": "Creative"},   # Yellow
    "D": {"bg": "#E74C3C", "fg": "white", "label": "Relational"},  # Red
}

QUADRANT_PHRASES = {
    "A": "Gentle Clarity",
    "B": "Next Steps",
    "C": "New Possibilities",
    "D": "Who’s Involved",
}

STOPWORDS = {
    "i","im","i'm","feel","feels","feeling","about","the","a","an","and","or","to","of","in","on","with","for","from",
    "this","that","it","is","are","was","were","be","being","as","my","our","your","their","they","he","she",
    "me","we","you","at","but","so","very","really","just","up","right","now"
}

EMOTION = ["stuck", "uncertain", "overwhelmed", "anxious", "worried", "panicked", "frustrated", "angry", "lost", "torn"]
DECISION = ["choose", "decision", "decide", "between", "options", "option", "tradeoff", "which", "whether", "decision-making"]
PRESSURE = ["deadline", "pressure", "limited", "time", "money", "constraints", "risk", "cant", "can't", "cannot"]
PEOPLE = ["colleague", "team", "manager", "client", "customer", "partner", "people", "trust", "conflict"]

def pick_entities(text: str):
    t = text.lower()

    # Collect keyword matches (max 3)
    keywords = []
    def add_if_present(key_list):
        for k in key_list:
            if k in t and k not in keywords:
                keywords.append(k)
    add_if_present(EMOTION)
    add_if_present(DECISION)
    add_if_present(PRESSURE)
    add_if_present(PEOPLE)

    # If nothing matched, fall back to a couple of meaningful nouns-ish tokens
    if not keywords:
        tokens = re.findall(r"[a-zA-Z']+", t)
        tokens = [x for x in tokens if x not in STOPWORDS and len(x) >= 4]
        # keep unique, first few
        for x in tokens:
            if x not in keywords:
                keywords.append(x)
            if len(keywords) >= 2:
                break

    # Keep at most 3
    return keywords[:3]

import re

EMOTION = {"stuck","uncertain","overwhelmed","anxious","worried","panicked","frustrated","angry","lost","torn","depressed","sad","down"}
DECISION = {"choose","decision","decide","between","options","option","tradeoff","which","whether","decision-making"}
PRESSURE = {"deadline","pressure","limited","time","money","constraints","risk","can't","cant","cannot"}
PEOPLE = {"colleague","team","manager","client","customer","partner","people","trust","conflict"}

def pick_keywords(text: str):
    t = text.lower()

    keywords = []
    # Prefer the “useful” categories first
    for group in (["emotion", EMOTION], ["decision", DECISION], ["pressure", PRESSURE], ["people", PEOPLE]):
        _, vocab = group
        for k in vocab:
            if k in t and k not in keywords:
                keywords.append(k)
            if len(keywords) >= 3:
                break
        if len(keywords) >= 3:
            break

    # fallback: pick a couple meaningful tokens
    if not keywords:
        tokens = re.findall(r"[a-zA-Z']+", t)
        tokens = [x for x in tokens if len(x) >= 4]
        for x in tokens:
            if x not in keywords:
                keywords.append(x)
            if len(keywords) >= 2:
                break

    return keywords[:3]

def reference_phrase(keywords):
    """
    Turn extracted keywords into a short, grammatical reference phrase
    (without forcing "this depressed" style output).
    """
    if not keywords:
        return "this situation"

    # If the first keyword is an emotion-feeling, avoid awkward "this depressed"
    if keywords[0] in EMOTION:
        # If we also have a workplace cue, blend it
        if len(keywords) > 1 and keywords[1] in PEOPLE:
            return f"this feeling and workplace dynamic"
        if len(keywords) > 1 and keywords[1] in PRESSURE:
            return f"this feeling under pressure"
        return "this feeling"

    # If we have a people cue
    if any(k in PEOPLE for k in keywords):
        return "this working dynamic"

    # If we have a pressure cue
    if any(k in PRESSURE for k in keywords):
        return "this pressured situation"

    # If we have decision cue
    if any(k in DECISION for k in keywords):
        return "this decision"

    return "this situation"

def generate_questions(thought: str):
    thought = (thought or "").strip() or "I feel stuck"
    keywords = pick_keywords(thought)
    ref = reference_phrase(keywords)

    return {
        "A": f"Let’s get clear: what observable facts do I have about {ref} (vs what I’m assuming)?",
        "B": f"What’s one practical next adjustment I can make about {ref} in the next 10 minutes?",
        "C": f"What’s a creative reframe or new option for {ref} that could open momentum?",
        "D": f"Who is impacted by {ref}—and who might be missing from the picture right now?"
    }




def card_html(q_key: str, prompt: str):
    c = COLORS[q_key]
    wrapped = textwrap.fill(prompt, width=88)
    header = f"{c['label']} — {QUADRANT_PHRASES[q_key]}"

    return f"""
    <div style="
        background-color: {c['bg']};
        color: {c['fg']};
        border-radius: 14px;
        padding: 16px 18px;
        min-height: 155px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.12);
        border: 1px solid rgba(255,255,255,0.12);
    ">
      <div style="font-weight: 800; font-size: 14px; margin-bottom: 8px; opacity: 0.95;">
        {header}
      </div>
      <div style="font-size: 15px; line-height: 1.45; white-space: normal;">
        {wrapped}
      </div>
    </div>
    """

def main():
    st.set_page_config(page_title="HBDI 4-Quadrant Reset", layout="wide")

    # Logo top-left
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=160)
    except Exception:
        st.warning("logo.png not found. Add it next to streamlit_app.py.")

    st.title("HBDI 4-Quadrant Reset (1-minute prompt)")
    st.caption("Enter what’s on your mind. You’ll get 4 gentle questions to help you shift out of the stuck feeling.")

    thought = st.text_input(
        "Your sentence or feeling",
        placeholder='e.g., "I feel stuck choosing between two options"'
    )

    if st.button("Generate 4 questions", type="primary"):
        qs = generate_questions(thought)

        # Build 2 rows so we can control top-left/top-right vs bottom-left/bottom-right.
        top_left, top_right = st.columns(2, gap="medium")
        bottom_left, bottom_right = st.columns(2, gap="medium")

        # Top row: Blue (Analytical) on left, Yellow (Creative) on right
        with top_left:
            st.markdown(card_html("A", qs["A"]), unsafe_allow_html=True)  # Top-left Blue = Analytical
        with top_right:
            st.markdown(card_html("C", qs["C"]), unsafe_allow_html=True)  # Top-right Yellow = Creative

        st.write("")  # spacing between rows

        # Bottom row: Green (Practical) on left, Red (Relational) on right
        with bottom_left:
            st.markdown(card_html("B", qs["B"]), unsafe_allow_html=True)  # Bottom-left Green = Practical
        with bottom_right:
            st.markdown(card_html("D", qs["D"]), unsafe_allow_html=True)  # Bottom-right Red = Relational

        st.divider()
        st.success("Take 30–60 seconds. Scan A → C → B → D (by position), then choose one to explore first.")

if __name__ == "__main__":
    main()
