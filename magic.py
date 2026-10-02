import json
import math
import random
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="OrbitMind", page_icon="🔮", layout="centered")

DATA_FILE = Path("orbitmind_data.json")

MODES = {
    "coin": {
        "label": "Coin flip",
        "symbols": ["H", "T"],
        "names": {"H": "🟡 Heads", "T": "⚫ Tails"},
    },
    "rps": {
        "label": "Rock-Paper-Scissors",
        "symbols": ["R", "P", "S"],
        "names": {"R": "🪨 Rock", "P": "📄 Paper", "S": "✂️ Scissors"},
    },
}
BEATS = {"R": "P", "P": "S", "S": "R"}  # key -> the move that beats it

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
    .big { font-size: 3.4rem; font-weight: 700; text-align:center; animation: pop .6s ease-out;
           background: linear-gradient(90deg,#a78bfa,#38bdf8); -webkit-background-clip:text; color:transparent; }
    @keyframes pop { 0% { transform: scale(.4); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
    .win { color:#4ade80; font-weight:600; } .lose { color:#f87171; font-weight:600; }
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
            d = json.loads(DATA_FILE.read_text())
            if "modes" in d:
                return d
        except Exception:
            pass
    return {"modes": {}}


def save(d):
    try:
        DATA_FILE.write_text(json.dumps(d))
    except Exception:
        pass


# ---------- Predictor: longest matching pattern wins ----------
def predict(history, symbols, max_order=4):
    for order in range(min(max_order, len(history)), 0, -1):
        ctx = history[-order:]
        counts = {s: 0 for s in symbols}
        for i in range(len(history) - order):
            if history[i : i + order] == ctx:
                counts[history[i + order]] += 1
        top = max(counts.values())
        if top > 0:
            best = [s for s, c in counts.items() if c == top]
            if len(best) == 1:
                return best[0]
    if history:
        counts = {s: history.count(s) for s in symbols}
        top = max(counts.values())
        return random.choice([s for s, c in counts.items() if c == top])
    return random.choice(symbols)


if "data" not in st.session_state:
    st.session_state.data = load()
    st.session_state.pending = {}


def mdata(mode):
    return st.session_state.data["modes"].setdefault(mode, {"history": [], "hits": [], "last": None})


def get_pending(mode):
    if mode not in st.session_state.pending:
        st.session_state.pending[mode] = predict(mdata(mode)["history"], MODES[mode]["symbols"])
    return st.session_state.pending[mode]


def play(mode, choice):
    m = mdata(mode)
    pred = get_pending(mode)
    m["history"].append(choice)
    m["hits"].append(int(pred == choice))
    m["last"] = {"pred": pred, "choice": choice}
    save(st.session_state.data)
    st.session_state.pending[mode] = predict(m["history"], MODES[mode]["symbols"])


def reset(mode):
    st.session_state.data["modes"][mode] = {"history": [], "hits": [], "last": None}
    st.session_state.pending.pop(mode, None)
    save(st.session_state.data)


# ---------- UI ----------
st.title("🔮 OrbitMind")
st.caption("Mind-reading tricks and tests. Spoiler: it's math and pattern-spotting, not psychic powers.")

tab1, tab2, tab3, tab4 = st.tabs(["🧮 Number Tricks", "🃏 Six Cards", "🧠 Predict Me", "🎲 Randomness Test"])

# --- Tab 1: number tricks ---
with tab1:
    trick = st.radio("Choose a trick", ["Always 5", "The 1089 Trick"], horizontal=True)

    if trick == "Always 5":
        st.markdown(
            '<div class="glass">Pick any whole number, then:<br>'
            "1. Double it &nbsp; 2. Add 10 &nbsp; 3. Halve it &nbsp; 4. Subtract your original number</div>",
            unsafe_allow_html=True,
        )
        n = st.number_input("Your secret number", min_value=1, max_value=9999, value=7, step=1)
        if st.button("Reveal my prediction", key="reveal5"):
            a, b = n * 2, n * 2 + 10
            c = b // 2
            st.markdown(f'<div class="glass">{n} → ×2 = {a} → +10 = {b} → ÷2 = {c} → −{n} = <b>{c - n}</b></div>', unsafe_allow_html=True)
            st.markdown('<div class="big">5</div>', unsafe_allow_html=True)
            st.caption("Why it works: (2n + 10) / 2 − n = 5. Your number cancels out.")
    else:
        st.markdown(
            '<div class="glass">Pick a 3-digit number whose first and last digits differ by at least 2.<br>'
            "1. Reverse it &nbsp; 2. Subtract the smaller from the larger &nbsp; "
            "3. Reverse the result (keep a leading zero if needed) &nbsp; 4. Add the two results</div>",
            unsafe_allow_html=True,
        )
        n = st.number_input("Your 3-digit number", min_value=100, max_value=999, value=532, step=1)
        if abs(n // 100 - n % 10) < 2:
            st.warning("The first and last digits must differ by at least 2.")
        elif st.button("Reveal my prediction", key="reveal1089"):
            r = int(str(n)[::-1])
            d = abs(n - r)
            dr = int(str(d).zfill(3)[::-1])
            st.markdown(
                f'<div class="glass">{n} and {r:03d} → difference <b>{d:03d}</b> → reversed <b>{dr}</b> → {d} + {dr} = <b>{d + dr}</b></div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="big">1089</div>', unsafe_allow_html=True)
            st.caption("Why it works: the difference is always 99 × (a − c), so it is one of 198, 297, 396, 495, 594, 693, 792 or 891. Each one plus its reversal equals 1089.")

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
        if not picked:
            st.warning("Tick at least one card. Every number from 1 to 63 appears on one or more.")
        else:
            st.balloons()
            st.markdown(f'<div class="big">{sum(picked)}</div>', unsafe_allow_html=True)
            st.caption("Why it works: each card holds the numbers with one binary digit switched on. The first numbers are 1, 2, 4, 8, 16, 32, and adding them rebuilds your number.")

# --- Tab 3: predictor ---
with tab3:
    mode = st.radio("Game", list(MODES), format_func=lambda k: MODES[k]["label"], horizontal=True)
    cfg = MODES[mode]
    m = mdata(mode)
    chance = 100 / len(cfg["symbols"])

    st.markdown(
        f'<div class="glass">My guess is already locked in. Choose however you like. '
        f"Random guessing scores about {chance:.0f}%. People are rarely as random as they think.</div>",
        unsafe_allow_html=True,
    )
    get_pending(mode)
    bcols = st.columns(len(cfg["symbols"]))
    for col, s in zip(bcols, cfg["symbols"]):
        col.button(cfg["names"][s], key=f"{mode}_{s}", on_click=play, args=(mode, s), use_container_width=True)

    last = m["last"]
    if last:
        hit = last["pred"] == last["choice"]
        line = f'I guessed <b>{cfg["names"][last["pred"]]}</b>, you chose <b>{cfg["names"][last["choice"]]}</b> '
        line += '<span class="win">✅ Read you.</span>' if hit else '<span class="lose">❌ You fooled me.</span>'
        if mode == "rps":
            app_move = BEATS[last["pred"]]
            if app_move == last["choice"]:
                outcome = "Tie."
            elif BEATS[last["choice"]] == app_move:
                outcome = "I win the round."
            else:
                outcome = "You win the round."
            line += f'<br>I played {cfg["names"][app_move]}. {outcome}'
        st.markdown(f'<div class="glass">{line}</div>', unsafe_allow_html=True)

    rounds = len(m["hits"])
    if rounds:
        rate = sum(m["hits"]) / rounds * 100
        c1, c2, c3 = st.columns(3)
        c1.metric("Rounds", rounds)
        c2.metric("My hits", sum(m["hits"]))
        c3.metric("Accuracy", f"{rate:.0f}%", f"{rate - chance:+.0f} vs chance")
        if rounds >= 10:
            h = m["hits"]
            roll = [sum(h[max(0, i - 9) : i + 1]) / len(h[max(0, i - 9) : i + 1]) * 100 for i in range(len(h))]
            st.caption("Rolling accuracy (last 10 rounds)")
            st.line_chart(roll)
        if rounds >= 20:
            if rate > chance + 7:
                st.info("You have a detectable pattern. I'm reading you.")
            else:
                st.info("You're close to chance. Impressively random.")
        st.button("Reset this game", key=f"reset_{mode}", on_click=reset, args=(mode,))

# --- Tab 4: randomness test ---
with tab4:
    st.markdown("### How random are you really?")
    st.markdown(
        '<div class="glass">Type 30 or more coin flips from your head, as randomly as you can. '
        "Use H and T (or 1 and 0). Don't peek at a real coin.</div>",
        unsafe_allow_html=True,
    )
    raw = st.text_area("Your sequence", placeholder="HTTHTHHTHT...", height=100)
    seq = ["H" if ch in "H1" else "T" for ch in raw.upper() if ch in "HT01"]
    n = len(seq)
    if 0 < n < 30:
        st.caption(f"{n} flips so far. Keep going to at least 30.")
    elif n >= 30:
        switches = sum(1 for a, b in zip(seq, seq[1:]) if a != b)
        alt = switches / (n - 1)
        longest = cur = 1
        for a, b in zip(seq, seq[1:]):
            cur = cur + 1 if a == b else 1
            longest = max(longest, cur)
        expected_run = math.log2(n) - 0.67
        heads = seq.count("H") / n * 100
        hits = sum(1 for i in range(1, n) if predict(seq[:i], ["H", "T"]) == seq[i])
        acc = hits / (n - 1) * 100

        c1, c2 = st.columns(2)
        c1.metric("Heads share", f"{heads:.0f}%", "random ≈ 50%", delta_color="off")
        c2.metric("Switch rate", f"{alt * 100:.0f}%", "random ≈ 50%", delta_color="off")
        c3, c4 = st.columns(2)
        c3.metric("Longest streak", longest, f"random ≈ {expected_run:.0f}", delta_color="off")
        c4.metric("My prediction accuracy", f"{acc:.0f}%", "random ≈ 50%", delta_color="off")

        flags = []
        if alt > 0.6:
            flags.append("You switch between H and T too often. Real randomness has more repeats than people expect.")
        if longest < expected_run - 1.5:
            flags.append("Your longest streak is shorter than chance predicts. Humans avoid long runs.")
        if abs(heads - 50) > 15:
            flags.append("Your sequence leans heavily to one side.")
        if acc > 60:
            flags.append("My predictor beat chance on your sequence, so there is a pattern in it.")
        if flags:
            st.markdown('<div class="glass">' + "<br>".join("• " + f for f in flags) + "</div>", unsafe_allow_html=True)
        else:
            st.success("This looks genuinely random. Either you're very good or you cheated with a coin.")
