import streamlit as st

st.set_page_config(page_title="App Universe", page_icon="🌌", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background: radial-gradient(circle at 20% 10%, #2b1a5e 0%, #0b0d2a 55%, #05060f 100%); color: #e9e9ff; }
    .card { background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.15);
            backdrop-filter: blur(12px); border-radius: 18px; padding: 18px 20px; margin-bottom: 6px; min-height: 130px; }
    .card h3 { margin: 0 0 6px 0; color: #fff; }
    .card p { margin: 0; color: #c9c9ee; font-size: .95rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Each app: name, emoji, blurb, and the URL (or local address) where it runs.
# Merge the OrbitMind entry below into your existing APPS list.
APPS = [
    # ... your existing apps go here ...
    {
        "name": "OrbitMind",
        "emoji": "🔮",
        "blurb": "Number tricks, a binary card trick, a pattern predictor, and a randomness test.",
        "url": "http://localhost:8501",  # replace with the deployed OrbitMind URL
    },
]

st.title("🌌 App Universe")
st.caption("Pick an app to launch.")

cols = st.columns(3)
for i, app in enumerate(APPS):
    with cols[i % 3]:
        st.markdown(
            f'<div class="card"><h3>{app["emoji"]} {app["name"]}</h3><p>{app["blurb"]}</p></div>',
            unsafe_allow_html=True,
        )
        st.link_button("Launch", app["url"], use_container_width=True)
