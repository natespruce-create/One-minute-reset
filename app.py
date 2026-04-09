import os
import json
import re
import textwrap
import streamlit as st
from PIL import Image
import google.generativeai as genai


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


def get_model_id_candidates():
    return ["gemini-3.1-flash-lite-preview"]



def build_prompt(user_text: str) -> str:
    return f"""
You are an HBDI coach creating a 1-minute “4-Quadrant Reset”.

User input (may be messy):
{user_text}

Generate EXACTLY 4 short, warm, human coaching questions (one per quadrant), tailored to the specific meaning of the user input.
Do NOT copy the user input verbatim. Do NOT use the same wording across quadrants.

Quadrant meanings:
A (Analytical / Gentle Clarity): observable facts vs assumptions
B (Practical / Next Steps): smallest practical next step
C (Creative / New Possibilities): new angle/options/reframes that open possibility
D (Relational / Who’s Involved): who is impacted/missing and what they may need

Hard constraints:
- Output MUST be valid JSON only (no markdown, no commentary).
- JSON keys must be: "A","B","C","D"
- Each value must be 12–22 words, exactly one question (end with ?)
- Make each question distinct (no repeated sentence starters).

Return JSON:
{{
  "A": "...?",
  "B": "...?",
  "C": "...?",
  "D": "...?"
}}
""".strip()


@st.cache_data(show_spinner=False)
def call_gemini_cached(user_text: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY environment variable.")

    genai.configure(api_key=api_key)

    prompt = build_prompt(user_text)
    candidates = [x for x in get_model_id_candidates() if x]
    last_err = None

    for mid in candidates:
        try:
            model = genai.GenerativeModel(mid)
            resp = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.95,
                    max_output_tokens=450,
                ),
            )

            text = (resp.text or "").strip()

            # Parse JSON strictly
            data = json.loads(text)

            # Validate keys and format
            for k in ["A", "B", "C", "D"]:
                if k not in data:
                    raise RuntimeError(f"Gemini JSON missing key: {k}")
                if not isinstance(data[k], str):
                    raise RuntimeError(f"Gemini value for {k} must be a string")
                q = data[k].strip()
                if not q.endswith("?"):
                    q = q + "?"
                data[k] = q

                # Word count sanity (optional)
                wc = len(re.findall(r"\b[\w']+\b", data[k]))
                if wc < 12 or wc > 22:
                    raise RuntimeError(f"Question for {k} not within 12–22 words.")

            return {k: data[k].strip() for k in ["A", "B", "C", "D"]}

        except Exception as e:
            last_err = e
            continue

    raise RuntimeError(f"All model attempts failed. Last error: {last_err}")


def card_html(q_key: str, prompt: str):
    c = COLORS[q_key]
    wrapped = textwrap.fill(prompt, width=92)
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
    st.caption("Enter what’s on your mind. Gemini generates one tailored question per quadrant.")

    thought = st.text_input(
        "Your sentence or feeling",
        placeholder='e.g., "I feel stuck choosing between two options"'
    )

    if st.button("Generate 4 questions", type="primary"):
        if not thought.strip():
            st.error("Please enter a sentence or feeling first.")
            return

        with st.spinner("Thinking with Gemini..."):
            qs = call_gemini_cached(thought.strip())

        # 2 rows layout
        top_left, top_right = st.columns(2, gap="medium")
        bottom_left, bottom_right = st.columns(2, gap="medium")

        # Top row: A blue (Analytical) left, C yellow (Creative) right
        with top_left:
            st.markdown(card_html("A", qs["A"]), unsafe_allow_html=True)
        with top_right:
            st.markdown(card_html("C", qs["C"]), unsafe_allow_html=True)

        st.write("")

        # Bottom row: B green (Practical) left, D red (Relational) right
        with bottom_left:
            st.markdown(card_html("B", qs["B"]), unsafe_allow_html=True)
        with bottom_right:
            st.markdown(card_html("D", qs["D"]), unsafe_allow_html=True)

        st.divider()
        st.success("Scan A → C → B → D (by position), then pick one to explore first.")


if __name__ == "__main__":
    main()
