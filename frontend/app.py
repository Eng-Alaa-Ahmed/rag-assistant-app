import streamlit as st
from api_client import API_BASE_URL, ask_question, check_health

st.set_page_config(page_title="Electronics RAG Assistant", page_icon="🔌", layout="centered")

st.markdown("""
<style>
    h1 { color: #2B6CB0; }
    .stCaption, .stCaption p { color: #718096 !important; }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        margin: 2px 4px 2px 0;
        font-weight: 500;
    }
    .source-badge { background-color: #EBF8FF; color: #2B6CB0; border: 1px solid #BEE3F8; }
    .component-badge { background-color: #E6FFFA; color: #285E61; border: 1px solid #B2F5EA; }
</style>
""", unsafe_allow_html=True)

st.title("🔌 Electronics RAG Assistant")
st.caption("Ask about resistors, capacitors, transistors, ICs & more — grounded in the textbook.")
st.caption(f"Backend: {API_BASE_URL}")

if not check_health():
    st.error("Can't reach the backend API. Make sure it's running.")

if "history" not in st.session_state:
    st.session_state.history = []

uploaded_image = st.file_uploader(
    "📷 Optional: upload a photo of an electronic component",
    type=["jpg", "jpeg", "png"],
)

question = st.chat_input("Ask a question about basic electronics...")

if question:
    with st.spinner("Thinking..."):
        try:
            image_bytes = uploaded_image.getvalue() if uploaded_image else None
            image_name = uploaded_image.name if uploaded_image else None
            result = ask_question(question, image_bytes=image_bytes, image_name=image_name)
            st.session_state.history.append({"question": question, "result": result})
        except Exception as e:
            st.session_state.history.append({"question": question, "error": str(e)})

for turn in reversed(st.session_state.history):
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        if "error" in turn:
            st.error("Something went wrong: " + turn["error"])
        else:
            st.write(turn["result"]["answer"])

            sources = turn["result"].get("sources")
            if sources:
                badges = "".join(f'<span class="badge source-badge">📄 {s}</span>' for s in sources)
                st.markdown("**Sources:** " + badges, unsafe_allow_html=True)

            components = turn["result"].get("detected_components")
            if components:
                badges = "".join(f'<span class="badge component-badge">🔧 {c}</span>' for c in components)
                st.markdown("**Detected in image:** " + badges, unsafe_allow_html=True)