import streamlit as st
import textwrap
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

def generate_questions(thought: str):
    # Do NOT paste the user’s sentence back verbatim into the questions.
    # We’ll keep it warm, short, and interpretive.
    return {
        "A": "Let’s get clear and gentle: what do you know for sure (observable facts) right now, rather than assumptions?",
        "B": "What’s one kind, practical next adjustment you can make right now to ease the stuck feeling?",
        "C": "If you could take a fresh, creative step—what else might be possible right now (another angle, option, or constraint)?",
        "D": "Who might be affected by this—who could be missing from the picture (and what might they be feeling)?",
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
