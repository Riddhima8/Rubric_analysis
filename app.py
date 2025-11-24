import re
import json
from typing import Optional

import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import language_tool_python
import plotly.graph_objects as go

# =========================
#  PAGE CONFIG
# =========================

st.set_page_config(
    page_title="AI Self-Introduction Scorer",
    page_icon="🎤",
    layout="centered"
)

# =========================
#  CACHED TOOLS
# =========================

@st.cache_resource
def load_sentiment_analyzer():
    return SentimentIntensityAnalyzer()

@st.cache_resource
def load_grammar_tool():
    # English grammar checker
    return language_tool_python.LanguageTool('en-US')

sentiment_analyzer = load_sentiment_analyzer()
grammar_tool = load_grammar_tool()

# =========================
#  RUBRIC CONSTANTS (HARDCODED)
# =========================

FILLER_WORDS = {
    "um", "uh", "like", "you know", "so", "actually", "basically",
    "right", "i mean", "well", "kinda", "sort of", "okay", "ok",
    "hmm", "ah"
}

# Must-have items (each 4 points, total 20 max)
MUST_HAVE_PATTERNS = {
    "name": [r"\bmy name is\b", r"\bi am\b", r"\bthis is\b"],
    "age": [r"\byears old\b", r"\byear old\b", r"\bage\b"],
    "school_class": [r"\bschool\b", r"\bclass\b", r"\bgrade\b", r"\bcollege\b", r"\buniversity\b"],
    "family": [r"\bfamily\b", r"\bmother\b", r"\bfather\b", r"\bparents\b", r"\bsister\b", r"\bbrother\b"],
    "hobbies": [r"\bhobby\b", r"\bhobbies\b", r"\bi like to\b", r"\bi love to\b", r"\bin my free time\b"]
}
MUST_HAVE_POINTS = 4

# Good-to-have items (each 2 points, total 10 max)
GOOD_TO_HAVE_PATTERNS = {
    "about_family": [r"\bfamily\b", r"\bmother\b", r"\bfather\b", r"\bparents\b"],
    "origin_location": [r"\bi am from\b", r"\bi'm from\b", r"\bwe live in\b", r"\bfrom\b"],
    "ambition_goal": [r"\bwant to\b", r"\bmy goal\b", r"\bmy dream\b", r"\baspire\b", r"\bambition\b"],
    "interesting_fact": [r"\bfun fact\b", r"\binteresting\b", r"\bunique\b"],
    "strengths_achievements": [r"\bstrength\b", r"\bstrong in\b", r"\bachievement\b", r"\bwon\b", r"\baward\b"]
}
GOOD_TO_HAVE_POINTS = 2

# Salutation levels
NORMAL_SALUTATIONS = ["hi", "hello"]
GOOD_SALUTATIONS = [
    "good morning", "good afternoon", "good evening",
    "good day", "hello everyone", "hi everyone"
]
EXCELLENT_PHRASES = [
    "i am excited to introduce", "feeling great",
    "i'm excited to introduce", "i am excited to be here"
]

# Max points per rubric area (for display)
MAX_POINTS = {
    "content_structure": 40,  # 5 (salutation) + 30 (keyword presence) + 5 (flow)
    "speech_rate": 10,
    "language_grammar": 20,   # 10 grammar + 10 vocab
    "clarity": 15,
    "engagement": 15
}

# =========================
#  TEXT UTILITIES
# =========================

def tokenize_words(text: str):
    text_lower = text.lower()
    tokens = re.findall(r"\b\w+\b", text_lower)
    return tokens

def compute_word_count(text: str) -> int:
    return len(tokenize_words(text))

def find_any_pattern(text_lower: str, patterns):
    for pat in patterns:
        if re.search(pat, text_lower):
            return True
    return False

# =========================
#  SALUTATION SCORE (0–5)
# =========================

def get_salutation_score(text: str):
    tl = text.lower()
    reason = "No salutation detected."

    # Excellent
    if any(phrase in tl for phrase in EXCELLENT_PHRASES):
        return 5, "Excellent salutation (excited/feeling great) detected."

    # Good
    if any(phrase in tl for phrase in GOOD_SALUTATIONS):
        return 4, "Good salutation (Good morning/afternoon/evening etc.) detected."

    # Normal
    if any(re.search(r"\b" + re.escape(s) + r"\b", tl) for s in NORMAL_SALUTATIONS):
        return 2, "Normal salutation (Hi/Hello) detected."

    return 0, reason

# =========================
#  KEYWORD PRESENCE (0–30)
# =========================

def get_keyword_presence_score(text: str):
    tl = text.lower()
    must_have_present = {}
    good_to_have_present = {}

    # Must-have
    for key, patterns in MUST_HAVE_PATTERNS.items():
        present = find_any_pattern(tl, patterns)
        must_have_present[key] = present

    # Good-to-have
    for key, patterns in GOOD_TO_HAVE_PATTERNS.items():
        present = find_any_pattern(tl, patterns)
        good_to_have_present[key] = present

    must_score = sum(1 for v in must_have_present.values() if v) * MUST_HAVE_POINTS
    good_score = sum(1 for v in good_to_have_present.values() if v) * GOOD_TO_HAVE_POINTS

    # Cap scores exactly as rubric (20 for must, 10 for good)
    must_score = min(must_score, 20)
    good_score = min(good_score, 10)

    total_score = must_score + good_score  # max 30

    return total_score, must_have_present, good_to_have_present

# =========================
#  FLOW SCORE (0 or 5)
# =========================

def get_flow_score(text: str):
    tl = text.lower()

    # Approximate positions
    def first_index_of_any(phrases):
        idxs = []
        for p in phrases:
            pos = tl.find(p)
            if pos != -1:
                idxs.append(pos)
        return min(idxs) if idxs else None

    sal_index = first_index_of_any(NORMAL_SALUTATIONS + GOOD_SALUTATIONS)
    basic_index = first_index_of_any(["my name is", "i am", "i'm", "years old", "school", "class", "grade"])
    additional_index = first_index_of_any(["hobby", "hobbies", "fun fact", "goal", "dream", "family"])
    closing_index = first_index_of_any(["thank you", "thanks for listening", "that's all", "that is all"])

    if None in (sal_index, basic_index, additional_index, closing_index):
        return 0, "Order not clearly followed (some sections missing)."

    if sal_index <= basic_index <= additional_index <= closing_index:
        return 5, "Order followed: Salutation → Basic Details → Additional Details → Closing."
    else:
        return 0, "Order not followed as expected."

# =========================
#  SPEECH RATE (0–10)
# =========================

def get_speech_rate_score(word_count: int, duration_seconds: Optional[float]):
    if not duration_seconds or duration_seconds <= 0:
        # If duration not provided, rubric cannot be applied
        return None, None, "Duration not provided – speech rate not scored."

    wpm = word_count / (duration_seconds / 60.0)

    if wpm > 161:
        return 2, wpm, "Too fast (>161 WPM)."
    elif 141 <= wpm <= 160:
        return 6, wpm, "Fast (141–160 WPM)."
    elif 111 <= wpm <= 140:
        return 10, wpm, "Ideal (111–140 WPM)."
    elif 81 <= wpm <= 110:
        return 6, wpm, "Slow (81–110 WPM)."
    else:  # <80
        return 2, wpm, "Too slow (<80 WPM)."

# =========================
#  GRAMMAR SCORE (0–10)
# =========================

def get_grammar_score(text: str, word_count: int):
    if word_count == 0:
        return 0, 0.0, 0.0, "Empty text."

    matches = grammar_tool.check(text)
    error_count = len(matches)
    errors_per_100 = (error_count / word_count) * 100

    # Grammar quality:
    # Grammar Score = 1 − min(errors_per_100_words / 10, 1)
    grammar_quality = 1 - min(errors_per_100 / 10.0, 1.0)

    if grammar_quality > 0.9:
        score = 10
    elif 0.7 <= grammar_quality <= 0.89:
        score = 8
    elif 0.5 <= grammar_quality <= 0.69:
        score = 6
    elif 0.3 <= grammar_quality <= 0.49:
        score = 4
    else:
        score = 2

    feedback = f"Grammar quality: {grammar_quality:.2f} with {error_count} errors (~{errors_per_100:.2f} errors per 100 words)."
    return score, error_count, errors_per_100, feedback

# =========================
#  VOCABULARY RICHNESS (0–10) using TTR
# =========================

def get_vocabulary_score(text: str):
    tokens = tokenize_words(text)
    word_count = len(tokens)
    if word_count == 0:
        return 0, 0.0, "Empty text."

    distinct_count = len(set(tokens))
    ttr = distinct_count / word_count

    if 0.9 <= ttr <= 1.0:
        score = 10
    elif 0.7 <= ttr <= 0.89:
        score = 8
    elif 0.5 <= ttr <= 0.69:
        score = 6
    elif 0.3 <= ttr <= 0.49:
        score = 4
    else:
        score = 2

    feedback = f"TTR (type-token ratio) = {ttr:.2f} ({distinct_count} distinct words out of {word_count})."
    return score, ttr, feedback

# =========================
#  CLARITY / FILLER WORDS (0–15)
# =========================

def get_clarity_score(text: str):
    tokens = tokenize_words(text)
    word_count = len(tokens)
    if word_count == 0:
        return 0, 0, 0.0, "Empty text."

    filler_count = 0
    for t in tokens:
        if t in FILLER_WORDS:
            filler_count += 1

    filler_rate = (filler_count / word_count) * 100  # percentage

    if 0 <= filler_rate <= 3:
        score = 15
    elif 4 <= filler_rate <= 6:
        score = 12
    elif 7 <= filler_rate <= 9:
        score = 9
    elif 10 <= filler_rate <= 12:
        score = 6
    else:  # 13 and above
        score = 3

    feedback = f"{filler_count} filler words (~{filler_rate:.2f}% of all words)."
    return score, filler_count, filler_rate, feedback

# =========================
#  ENGAGEMENT / SENTIMENT (0–15)
# =========================

def get_engagement_score(text: str):
    scores = sentiment_analyzer.polarity_scores(text)
    pos_prob = scores["pos"]  # 0–1

    if pos_prob >= 0.9:
        score = 15
    elif 0.7 <= pos_prob <= 0.89:
        score = 12
    elif 0.5 <= pos_prob <= 0.69:
        score = 9
    elif 0.3 <= pos_prob <= 0.49:
        score = 6
    else:
        score = 3

    feedback = f"Positive sentiment probability (VADER) = {pos_prob:.2f}."
    return score, pos_prob, feedback

# =========================
#  OVERALL SCORING PIPELINE (STRICT RUBRIC)
# =========================

def score_transcript(text: str, duration_seconds: Optional[float] = None):
    word_count = compute_word_count(text)

    # ---- Content & Structure (40) ----
    sal_score, sal_reason = get_salutation_score(text)
    kw_score, must_have_present, good_to_have_present = get_keyword_presence_score(text)
    flow_score, flow_reason = get_flow_score(text)
    cs_total = sal_score + kw_score + flow_score  # max 40

    # ---- Speech Rate (10) ----
    sr_score, wpm, sr_feedback = get_speech_rate_score(word_count, duration_seconds)
    # If duration missing, treat speech rate as 0 in overall strict rubric
    sr_total_for_overall = sr_score if sr_score is not None else 0

    # ---- Language & Grammar (20) ----
    grammar_score, err_count, err_per_100, grammar_fb = get_grammar_score(text, word_count)
    vocab_score, ttr, vocab_fb = get_vocabulary_score(text)
    lg_total = grammar_score + vocab_score  # max 20

    # ---- Clarity (15) ----
    clarity_score, filler_count, filler_rate, clarity_fb = get_clarity_score(text)

    # ---- Engagement (15) ----
    engagement_score_val, pos_prob, eng_fb = get_engagement_score(text)

    # Overall as simple sum (strict rubric)
    overall = cs_total + sr_total_for_overall + lg_total + clarity_score + engagement_score_val
    overall = max(0.0, min(100.0, overall))  # clamp to [0,100]

    # Build detailed result
    result = {
        "overall_score": round(overall, 2),
        "word_count": word_count,
        "criteria": [
            {
                "name": "Content & Structure",
                "final_score": cs_total,
                "max_score": MAX_POINTS["content_structure"],
                "subcomponents": {
                    "salutation": {
                        "score": sal_score,
                        "max_score": 5,
                        "feedback": sal_reason
                    },
                    "keyword_presence": {
                        "score": kw_score,
                        "max_score": 30,
                        "must_have_present": must_have_present,
                        "good_to_have_present": good_to_have_present
                    },
                    "flow": {
                        "score": flow_score,
                        "max_score": 5,
                        "feedback": flow_reason
                    }
                }
            },
            {
                "name": "Speech Rate",
                "final_score": sr_score if sr_score is not None else 0,
                "max_score": MAX_POINTS["speech_rate"],
                "wpm": round(wpm, 2) if wpm is not None else None,
                "feedback": sr_feedback
            },
            {
                "name": "Language & Grammar",
                "final_score": lg_total,
                "max_score": MAX_POINTS["language_grammar"],
                "subcomponents": {
                    "grammar": {
                        "score": grammar_score,
                        "max_score": 10,
                        "error_count": err_count,
                        "errors_per_100_words": round(err_per_100, 2),
                        "feedback": grammar_fb
                    },
                    "vocabulary": {
                        "score": vocab_score,
                        "max_score": 10,
                        "ttr": round(ttr, 3) if word_count > 0 else 0,
                        "feedback": vocab_fb
                    }
                }
            },
            {
                "name": "Clarity",
                "final_score": clarity_score,
                "max_score": MAX_POINTS["clarity"],
                "subcomponents": {
                    "filler_words": {
                        "score": clarity_score,
                        "max_score": 15,
                        "filler_count": filler_count,
                        "filler_rate_percent": round(filler_rate, 2),
                        "feedback": clarity_fb
                    }
                }
            },
            {
                "name": "Engagement",
                "final_score": engagement_score_val,
                "max_score": MAX_POINTS["engagement"],
                "subcomponents": {
                    "sentiment": {
                        "score": engagement_score_val,
                        "max_score": 15,
                        "positive_probability": round(pos_prob, 3),
                        "feedback": eng_fb
                    }
                }
            }
        ]
    }

    return result

# =========================
#  HELPER: GAUGE FIGURE
# =========================

def make_gauge(score: float):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": " / 100"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"thickness": 0.3},
                "steps": [
                    {"range": [0, 40], "color": "#ffcccc"},
                    {"range": [40, 70], "color": "#ffe8b3"},
                    {"range": [70, 85], "color": "#e0f7c2"},
                    {"range": [85, 100], "color": "#c5f1ff"},
                ],
                "threshold": {
                    "line": {"width": 4},
                    "thickness": 0.75,
                    "value": score,
                },
            },
            domain={"x": [0, 1], "y": [0, 1]}
        )
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=260
    )
    return fig

# =========================
#  STREAMLIT UI (PREMIUM)
# =========================

st.markdown("""
<div style="text-align:center; margin-bottom: 10px;">
    <h1>🎤 AI Self-Introduction Scoring</h1>
    <p style="font-size:18px;">Strict Excel-based rubric • Real-time feedback</p>
</div>
""", unsafe_allow_html=True)

with st.container():
    transcript = st.text_area(
        "📝 Paste your self-introduction transcript:",
        height=220,
        placeholder="Example: Good morning everyone, my name is..."
    )

col1, col2 = st.columns([1, 1])
with col1:
    duration_input = st.text_input(
        "⏱️ Speaking duration (seconds, optional):",
        placeholder="e.g., 30"
    )
with col2:
    st.write("")  # spacing
    score_button = st.button("✅ Score My Introduction", use_container_width=True)

st.markdown("---")

if score_button:
    if not transcript.strip():
        st.error("❌ Please paste a transcript before scoring.")
    else:
        duration_seconds: Optional[float] = None
        if duration_input.strip():
            try:
                duration_seconds = float(duration_input)
            except ValueError:
                st.warning("Duration must be a number (in seconds). Speech rate will not be scored.")
                duration_seconds = None

        with st.spinner("🔍 Analyzing based on rubric..."):
            result = score_transcript(transcript, duration_seconds)

        overall = result["overall_score"]

        # Confetti / celebration
        if overall >= 85:
            st.balloons()

        # Top summary section
        st.subheader("🏆 Overall Result")

        gauge_col, info_col = st.columns([1.2, 1])

        with gauge_col:
            fig = make_gauge(overall)
            st.plotly_chart(fig, use_container_width=True)

        with info_col:
            st.markdown(f"""
            <div style="padding: 12px; border-radius: 12px; background-color:#f7f7f7; border:1px solid #eee;">
                <h3 style="margin-top:0;">Score: {overall} / 100</h3>
                <p><b>Word count:</b> {result['word_count']}</p>
                <p style="font-size:14px; color:#555;">This score is calculated strictly using your rubric:
                Content & Structure (40) + Speech Rate (10) + Language & Grammar (20) + Clarity (15) + Engagement (15).</p>
            </div>
            """, unsafe_allow_html=True)

        # Category cards
        st.markdown("### 📌 Category Snapshot")

        c1, c2, c3 = st.columns(3)
        crit_map = {c["name"]: c for c in result["criteria"]}

        def card_html(title, crit_key, bg_color):
            crit = crit_map[crit_key]
            return f"""
            <div style="background:{bg_color}; padding:12px; border-radius:14px; border:1px solid #ddd; height:100%;">
                <h4 style="margin-top:0; margin-bottom:6px;">{title}</h4>
                <p style="margin:0; font-size:24px;"><b>{crit['final_score']} / {crit['max_score']}</b></p>
            </div>
            """

        with c1:
            st.markdown(card_html("Content & Structure", "Content & Structure", "#f4f8ff"), unsafe_allow_html=True)
        with c2:
            st.markdown(card_html("Language & Grammar", "Language & Grammar", "#f6fff4"), unsafe_allow_html=True)
        with c3:
            st.markdown(card_html("Engagement", "Engagement", "#fff7ec"), unsafe_allow_html=True)

        st.markdown("---")

        # TABS
        tabs = st.tabs(["📊 Detailed Scoring", "📄 Criterion Feedback", "📦 JSON Output"])

        # TAB 1: Detailed numeric scoring + progress bars
        with tabs[0]:
            st.subheader("📊 Detailed Scores")
            for crit in result["criteria"]:
                st.markdown(f"#### {crit['name']}")
                st.progress(crit["final_score"] / crit["max_score"] if crit["max_score"] > 0 else 0)
                st.write(f"**Score:** {crit['final_score']} / {crit['max_score']}")
                st.write("---")

        # TAB 2: Feedback per criterion
        with tabs[1]:
            st.subheader("📄 Rubric-Level Feedback")

            # Content & Structure
            cs = crit_map["Content & Structure"]["subcomponents"]
            with st.expander("🧩 Content & Structure"):
                st.write(f"**Salutation:** {cs['salutation']['score']} / 5")
                st.write(cs["salutation"]["feedback"])
                st.write("")
                st.write(f"**Keyword Presence:** {cs['keyword_presence']['score']} / 30")
                st.write("• Must-have present:", cs["keyword_presence"]["must_have_present"])
                st.write("• Good-to-have present:", cs["keyword_presence"]["good_to_have_present"])
                st.write("")
                st.write(f"**Flow:** {cs['flow']['score']} / 5")
                st.write(cs["flow"]["feedback"])

            # Speech Rate
            sr = crit_map["Speech Rate"]
            with st.expander("⏱️ Speech Rate"):
                st.write(f"**Score:** {sr['final_score']} / {sr['max_score']}")
                if sr["wpm"] is not None:
                    st.write(f"Estimated WPM: {sr['wpm']}")
                st.write(sr["feedback"])

            # Language & Grammar
            lg = crit_map["Language & Grammar"]["subcomponents"]
            with st.expander("📚 Language & Grammar"):
                st.write(f"**Grammar:** {lg['grammar']['score']} / 10")
                st.write(
                    f"Errors: {lg['grammar']['error_count']} "
                    f"({lg['grammar']['errors_per_100_words']} per 100 words)"
                )
                st.write(lg["grammar"]["feedback"])
                st.write("")
                st.write(f"**Vocabulary:** {lg['vocabulary']['score']} / 10")
                st.write(f"TTR: {lg['vocabulary']['ttr']}")
                st.write(lg["vocabulary"]["feedback"])

            # Clarity
            cl = crit_map["Clarity"]["subcomponents"]["filler_words"]
            with st.expander("🔊 Clarity & Filler Words"):
                st.write(f"**Score:** {cl['score']} / 15")
                st.write(
                    f"Filler count: {cl['filler_count']} "
                    f"({cl['filler_rate_percent']}% of words)"
                )
                st.write(cl["feedback"])

            # Engagement
            en = crit_map["Engagement"]["subcomponents"]["sentiment"]
            with st.expander("✨ Engagement & Sentiment"):
                st.write(f"**Score:** {en['score']} / 15")
                st.write(f"Positive probability: {en['positive_probability']}")
                st.write(en["feedback"])

        # TAB 3: JSON
        with tabs[2]:
            st.subheader("📦 Raw JSON Result")
            st.json(result)

            st.download_button(
                "💾 Download JSON",
                data=json.dumps(result, indent=2),
                file_name="score_result.json",
                mime="application/json"
            )
