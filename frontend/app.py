import streamlit as st
from api_client import API_BASE_URL, ask_question, check_health

st.set_page_config(page_title="Electronics RAG Assistant", page_icon="🔌")
st.title("🔌 Electronics RAG Assistant")
st.caption("Backend: " + API_BASE_URL)

if not check_health():
    st.error("Can't reach the backend API. Make sure it's running.")

if "history" not in st.session_state:
    st.session_state.history = []

uploaded_image = st.file_uploader(
    "Optional: upload a photo of an electronic component",
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
            if turn["result"].get("sources"):
                st.caption("Sources: " + ", ".join(turn["result"]["sources"]))
            if turn["result"].get("detected_components"):
                st.caption("Detected in image: " + ", ".join(turn["result"]["detected_components"]))