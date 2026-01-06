import os, time, requests, streamlit as st
import base64
from pathlib import Path

# --- Page config (do this once) ---
st.set_page_config(page_title="IntelliDoc — IIT Patna", page_icon="🎓", layout="wide")

def center_image_local(filename: str, width: int = 200):
    """Load an image that lives in the same folder as this file and center it."""
    here = Path(__file__).parent
    img_path = here / filename  # resolves to /app/images.png inside the container
    if not img_path.exists():
        st.warning(f"Logo not found at {img_path}.")
        return
    encoded = base64.b64encode(img_path.read_bytes()).decode()
    st.markdown(
        f"""
        <div style='display:flex; justify-content:center; margin-top:12px;'>
            <img src='data:image/png;base64,{encoded}' width='{width}'>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Centered IIT Patna logo
center_image_local("images.png", width=200)

st.markdown(
    """
    <h1 style='text-align:center; color:#004aad; margin:10px 0 4px 0;'>
        <b>IntelliDoc — IIT Patna</b>
    </h1>
    <hr style='border:1px solid #0b61e1; margin:12px 0 24px 0;'>
    """,
    unsafe_allow_html=True,
)



API_URL = os.getenv("API_URL","http://api:8000")

tabs = st.tabs(["Assistant","Debug"])

with tabs[0]:
    q = st.text_input("Ask about TNF docs, SOPs, KPIs, etc.")
    if st.button("Go") and q:
        t0 = time.time()
        r = requests.post(f"{API_URL}/ask", json={"query": q})
        dt = time.time()-t0
        if r.ok:
            data = r.json()
            st.markdown("### Answer")
            st.write(data["answer"])
            st.markdown("### Sources")
            for s in data.get("sources", []):
                st.write(f"- **{s.get('file','?')}** page {s.get('page','?')}")
            st.caption(f"Latency: {dt:.2f}s")
        else:
            st.error(f"Error: {r.status_code} {r.text}")

with tabs[1]:
    st.subheader("Debug")
    try:
        hr = requests.get(f"{API_URL}/health", timeout=5).json()
        st.write("API health:", hr)
    except Exception as e:
        st.error(f"API not reachable: {e}")
    st.write("Models:", os.getenv("CHAT_MODEL","llama3.1:8b"),
             "| Embeddings:", os.getenv("EMBED_MODEL","nomic-embed-text"))
with st.sidebar:
    st.subheader("⚙️ Runtime")
    st.write("API:", os.getenv("API_URL","http://api:8000"))
    st.write("Chat model:", os.getenv("CHAT_MODEL","llama3.1:8b"))
    st.write("Embed model:", os.getenv("EMBED_MODEL","nomic-embed-text"))

st.markdown(
    """
    <hr style='margin-top:40px;'>
    <p style='text-align:center; font-size:13px; color:#888;'>
        © 2025 IIT Patna | Local RAG Demo | Built by Abhishek Raj Permani
    </p>
    """,
    unsafe_allow_html=True,
)
