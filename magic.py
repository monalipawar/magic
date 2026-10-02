import json
import random
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="OrbitMind", page_icon="🔮", layout="centered")

DATA_FILE = Path("orbitmind_data.json")

# ---------- Styling (cosmic glassmorphism, Outfit) ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background: radial-gradient(circle at 20% 10%, #2b1a5e 0%, #0b0d2a 55%, #05060f 100%); color: #e9e9ff; }
    h1, h2, h3 { color: #fff; letter-spacing: .5px; }
    .glass { background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.15);
             backdrop-filter: blur(12px); border-radius: 18px; padding: 18px 20px; margin: 10px 0; }
    .num-grid { display:grid; grid-template-columns: repeat(8, 1fr); gap:6px; text-align:center; font-weight:600; }
    .big { font-size: 3rem; font-weight: 700; text-align:center;
           background: linear-gradient(90deg,#a78bfa,#38bdf8); -webkit-background-clip:text; color:transparent; }
    .stButton>button { border-radius: 12px; border: 1px solid rgba(255,255,255,.25);
                       background: rgba(255,255,255,.1); color: #fff; font-weight: 600; }
    .stButton>button:hover { border-color: #a78bfa; color: #a78bfa; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Persistence ----------
def load():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"history": [], "rounds": 0, "hits": 0, "last": None}


def save(d):
    try:
        DATA_FILE.write_text(json.dumps(d))
    except Exception:
        pass


# ---------- Predictor (pattern matching on your past choices) ----------
def predict(history, max_order=3):
    for order in range(min(max_order, len(history)), 0, -1):
        ctx = history[-order:]
        counts = {"H": 0, "T": 0}
        for i in range(len(history) - order):
            if history[i : i + order] == ctx:
                counts[history[i + order]] += 1
        if counts["H"] != counts["T"]:
            return "H" if counts["H"] > counts["T"] else "T"
    return random.choice("HT")


if "data" not in st.session_state:
    st.session_state.data = load()
    st.session_state.pending = predict(st.session_state.data["history"])


def play(choice):
    d = st.session_state.data
    pred = st.session_state.pending
    d["history"].append(choice)
    d["rounds"] += 1
    d["hits"] += int(pred == choice)
    d["last"] = {"pred": pred, "choice": choice}
    save(d)
    st.session_state.pending = predict(d["history"])


# ---------- UI ----------
st.title("🔮 OrbitMind")
st.caption("Three ways to feel like you're reading minds (spoiler: it's math and pattern-spotting).")

tab1, tab2, tab3 = st.tabs(["🧮 Number Trick", "🃏 Six Cards", "🧠 Can I Predict You?"])

# --- Tab 1: always-5 trick ---
with tab1:
    st.markdown("### I already know your final answer")
    st.markdown(
        '<div class="glass">Pick any whole number, then follow along:<br>'
        "1. Double it &nbsp; 2. Add 10 &nbsp; 3. Halve it &nbsp; 4. Subtract your original number</div>",
        unsafe_allow_html=True,
    )
    n = st.number_input("Your secret number", min_value=1, max_value=9999, value=7, step=1)
    if st.button("Reveal my prediction", key="reveal5"):
        a = n * 2
        b = a + 10
        c = b // 2
        d = c - n
        st.markdown(f'<div class="glass">{n} → ×2 = {a} → +10 = {b} → ÷2 = {c} → −{n} = <b>{d}</b></div>', unsafe_allow_html=True)
        st.markdown('<div class="big">5</div>', unsafe_allow_html=True)
        st.caption("Why it works: (2n + 10) / 2 − n = n + 5 − n = 5. Your number cancels out.")

# --- Tab 2: binary cards ---
with tab2:
    st.markdown("### Think of a number from 1 to 63")
    st.markdown('<div class="glass">Tick every card that contains your number. I\'ll name it.</div>', unsafe_allow_html=True)
    picked = []
    cols = st.columns(2)
    for bit in range(6):
        nums = [x for x in range(1, 64) if x & (1 << bit)]
        with cols[bit % 2]:
            grid = "".join(f"<div>{x}</div>" for x in nums)
            st.markdown(f'<div class="glass"><b>Card {bit + 1}</b><div class="num-grid">{grid}</div></div>', unsafe_allow_html=True)
            if st.checkbox("My number is on this card", key=f"card{bit}"):
                picked.append(1 << bit)
    if st.button("Read my mind", key="readmind"):
        st.markdown(f'<div class="big">{sum(picked)}</div>', unsafe_allow_html=True)
        st.caption("Why it works: each card holds the numbers whose binary digit is 1 in one position. The first number on each card is 1, 2, 4, 8, 16, 32, so adding them up rebuilds your number in binary.")

# --- Tab 3: predictor test ---
with tab3:
    d = st.session_state.data
    st.markdown("### Can I predict your next move?")
    st.markdown(
        '<div class="glass">My guess is already locked in. Pick Heads or Tails however you like. '
        "Random guessing would score about 50%; people are rarely as random as they think.</div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    c1.button("🟡 Heads", on_click=play, args=("H",), use_container_width=True)
    c2.button("⚫ Tails", on_click=play, args=("T",), use_container_width=True)

    if d["last"]:
        ok = d["last"]["pred"] == d["last"]["choice"]
        st.markdown(
            f'<div class="glass">Last round: I guessed <b>{d["last"]["pred"]}</b>, you picked <b>{d["last"]["choice"]}</b> '
            f'{"✅ Read you." if ok else "❌ You fooled me."}</div>',
            unsafe_allow_html=True,
        )
    if d["rounds"]:
        rate = d["hits"] / d["rounds"] * 100
        m1, m2, m3 = st.columns(3)
        m1.metric("Rounds", d["rounds"])
        m2.metric("My hits", d["hits"])
        m3.metric("Accuracy", f"{rate:.0f}%")
        if d["rounds"] >= 20:
            st.info("Above ~55% over 20+ rounds means you have a detectable pattern." if rate > 55 else "You're hovering near chance. Nicely random.")
    if st.button("Reset stats"):
        st.session_state.data = {"history": [], "rounds": 0, "hits": 0, "last": None}
        save(st.session_state.data)
        st.session_state.pending = predict([])
        st.rerun()
