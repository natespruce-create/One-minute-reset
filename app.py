import streamlit as st
import textwrap
from PIL import Image

# --- Quadrant theme colors (kept as-is) ---
COLORS = {
    "A": {"bg": "#2E6DA4", "fg": "white", "label": "Analytic"},
    "B": {"bg": "#F1C232", "fg": "#1a1a1a", "label": "Practical"},
    "C": {"bg": "#2AA876", "fg": "white", "label": "Relational"},
    "D": {"bg": "#E74C3C", "fg": "white", "label": "Creative"},
}

# Display phrases you requested (replace the old title/label duplicates)
QUADRANT_PHRASES = {
    "A": "Gentle Clarity",
    "B": "Next Steps",
    "C": "Who’s Involved",
    "D": "New Possibilities",
}

def generate_questions(thought: str):
    thought = thought.strip() or "I feel stuck"

    return {
        "A": f'Let’s get clear and gentle: what do you know for sure (observable facts) rather than assumptions about “{thought}”?',
        "B": f'What’s one kind, practical next adjustment you can make right now to ease the stuck feeling about “{thought}”?',
        "C": f'Who might be affected by “{thought}”, or who could be missing from the picture (and what might they be feeling)?',
        "D": f'If you could take a fresh, creative step—what else might be possible with “{thought}” (another angle, option, or constraint)?'
    }

def card_html(q_key: str, prompt: str):
    c = COLORS[q_key]
    wrapped = textwrap.fill(prompt, width=88)

    header = f"{q_key} — {QUADRANT_PHRASES[q_key]}"

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

        col1, col2 = st.columns(2, gap="medium")
        with col1:
            st.markdown(card_html("A", qs["A"]), unsafe_allow_html=True)
        with col2:
            st.markdown(card_html("B", qs["B"]), unsafe_allow_html=True)

        col3, col4 = st.columns(2, gap="medium")
        with col3:
            st.markdown(card_html("C", qs["C"]), unsafe_allow_html=True)
        with col4:
            st.markdown(card_html("D", qs["D"]), unsafe_allow_html=True)

        st.divider()
        st.success("Take 30–60 seconds. Scan each question, then choose just one to explore first.")

if __name__ == "__main__":
    main()
