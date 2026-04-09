import os
import textwrap
import streamlit as st
import google.generativeai as genai
from PIL import Image

# ---------- Quadrant theme colors ----------
COLORS = {
    "A": {"bg": "#2E6DA4", "fg": "white", "label": "Analytic"},
    "B": {"bg": "#F1C232", "fg": "#1a1a1a", "label": "Practical"},
    "C": {"bg": "#2AA876", "fg": "white", "label": "Relational"},
    "D": {"bg": "#E74C3C", "fg": "white", "label": "Creative"},
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

def build_prompt(user_text: str):
    return f"""
You are an HBDI coach creating a 1-minute “4-Quadrant Reset”.
Input from the user (may be messy or incomplete):
\"\"\"{user_text}\"\"\"

Task:
Return EXACTLY 4 short, warm, friendly coaching questions—one for each quadrant:
- A (Analytic): facts/what’s true/observable clarity; avoid repeating the whole input verbatim
- B (Practical): next adjustment/what to do now; make it actionable
- C (Relational): impacted people / who is missing / what needs trust/understanding
- D (Creative): new angle/options/reframes/possibility thinking

Hard rules:
- Output format must be JSON with keys: "A","B","C","D"
- Each question must be 12–22 words max (one sentence)
- Do NOT include any code blocks, bullet lists, or explanations
- Do NOT paste the full user text into each question
- Keep language supportive and non-judgmental

Now produce the JSON.
""".strip()

def call_gemini(user_text: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY environment variable.")

    model_id = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # you can override

    genai.configure(api_key=api_key)

    prompt = build_prompt(user_text)

    model = genai.GenerativeModel(model_id)
    resp = model.generate_content(prompt)
    text = resp.text.strip()

    # Expect JSON
    import json, re
    try:
        data = json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise RuntimeError("Model did not return JSON.")
        data = json.loads(m.group(0))

    if not all(k in data for k in ["A", "B", "C", "D"]):
        raise RuntimeError("JSON missing required quadrant keys.")

    return {k: str(data[k]).strip() for k in ["A", "B", "C", "D"]}


def main():
    st.set_page_config(page_title="HBDI 4-Quadrant Reset", layout="wide")

    # Logo top-left
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=160)
    except Exception:
        st.warning("logo.png not found. Add it next to streamlit_app.py.")

    st.title("HBDI 4-Quadrant Reset (1-minute prompt)")
    st.caption("Enter a sentence/feeling. Gemini generates one short question per quadrant—tailored to you.")

    thought = st.text_input(
        "Your sentence or feeling",
        placeholder='e.g., "I feel uncertain about working with a colleague on a deadline"'
    )

    if st.button("Generate 4 questions", type="primary"):
        with st.spinner("Thinking (Gemini)…"):
            qs = call_gemini(thought)

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
