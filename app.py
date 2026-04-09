import streamlit as st
import textwrap

# --- Quadrant theme colors (edit to match your exact slide) ---
COLORS = {
    "A": {"bg": "#2E6DA4", "fg": "white", "label": "Analytic"},
    "B": {"bg": "#F1C232", "fg": "#1a1a1a", "label": "Practical"},
    "C": {"bg": "#2AA876", "fg": "white", "label": "Relational"},
    "D": {"bg": "#E74C3C", "fg": "white", "label": "Creative"},
}

def generate_questions(thought: str):
    thought = thought.strip() or "I feel stuck"
    return {
        "A": f'What do I know for sure (observable facts) rather than assumptions about: "{thought}"?',
        "B": f'What is one practical adjustment I can make right now to reduce the stuck feeling about: "{thought}"?',
        "C": f'Who is impacted or missing from this situation that I should consider about: "{thought}" (and what might they be experiencing)?',
        "D": f'What else is possible here if I approached it with a new frame, perspective, or creative constraint set about: "{thought}"?'
    }

def card_html(q_key: str, prompt: str, title: str):
    c = COLORS[q_key]
    wrapped = textwrap.fill(prompt, width=78)

    # Note: We use unsafe_allow_html=True when rendering this card.
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
        {q_key} — {c['label']}
      </div>
      <div style="font-size: 15px; line-height: 1.35; white-space: pre-wrap;">
        <span style="font-weight: 600;">{title}</span>
        {"\\n"}
        {wrapped}
      </div>
    </div>
    """

def main():
    st.set_page_config(page_title="HBDI 4-Quadrant Reset", layout="wide")

    # --- Logo (top-left) ---
    # Assumes logo.png is located alongside this Streamlit file in your GitHub repo.
    st.markdown(
        """
        <div style="text-align:left; margin-bottom: 6px;">
          <img src="logo.png" width="160" />
        </div>
        """,
        unsafe_allow_html=True
    )

    st.title("HBDI 4-Quadrant Reset (1-minute prompt)")
    st.caption("Enter what’s on your mind (e.g., “I feel stuck…”). We’ll generate one question per quadrant.")

    thought = st.text_input(
        "Your sentence or feeling",
        placeholder='e.g., "I feel stuck choosing between two options"'
    )

    if st.button("Generate 4 questions", type="primary"):
        qs = generate_questions(thought)

        # 2x2 grid arrangement: A (top-left), B (top-right), C (bottom-left), D (bottom-right)
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            st.markdown(card_html("A", qs["A"], "Analytic question"), unsafe_allow_html=True)
        with col2:
            st.markdown(card_html("B", qs["B"], "Practical question"), unsafe_allow_html=True)

        col3, col4 = st.columns(2, gap="medium")
        with col3:
            st.markdown(card_html("C", qs["C"], "Relational question"), unsafe_allow_html=True)
        with col4:
            st.markdown(card_html("D", qs["D"], "Creative question"), unsafe_allow_html=True)

        st.divider()
        st.success("Reset questions generated. Take 30–60 seconds to scan, then choose one to explore.")

if __name__ == "__main__":
    main()
