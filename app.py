import streamlit as st
from PIL import Image
from io import BytesIO
import base64
from biased_words import highlight_text
import docx

header_image = Image.open("ggg.png")
buffered = BytesIO()
header_image.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()

st.set_page_config(
    page_title="WordBalance",
    layout="wide",
    page_icon=header_image
)

st.markdown("""
<style>
.block-container { padding-top: 2rem; }
.centered-title {
    text-align: center;
    font-size: 2.2em;
    font-weight: bold;
    margin-bottom: 0.2em;
    display: flex;
    align-items: center;
    justify-content: center;
}
.centered-title img { margin-right: 10px; }
.centered-subtitle {
    text-align: center;
    font-size: 1.1em;
    color: gray;
    margin-bottom: 2em;
}
.stTextArea textarea {
    border: 2px solid #4CAF50;
    border-radius: 12px;
    padding: 12px;
    font-size: 16px;
}
.highlight-box {
    background-color: #fff9c4;
    padding: 10px;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    f'<h1 class="centered-title"><img src="data:image/png;base64,{img_str}" width="50"> WordBalance</h1>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="centered-subtitle"><b>Gender-Fair Language Detection Tool</b></p>',
    unsafe_allow_html=True
)

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "pending_file_text" not in st.session_state:
    st.session_state.pending_file_text = None

if "scanned_text" not in st.session_state:
    st.session_state.scanned_text = ""

if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

if "char_count" not in st.session_state:
    st.session_state.char_count = 0

# Key controller for text_area reset
if "text_area_key" not in st.session_state:
    st.session_state.text_area_key = 0


def process_text(text):
    st.session_state.input_text = text
    st.session_state.char_count = len(text)

    if text.strip():
        highlighted, suggestions = highlight_text(text)
        st.session_state.scanned_text = highlighted
        st.session_state.suggestions = suggestions
    else:
        st.session_state.scanned_text = ""
        st.session_state.suggestions = []


def clear_text():
    st.session_state.input_text = ""
    st.session_state.pending_file_text = None
    st.session_state.scanned_text = ""
    st.session_state.suggestions = []
    st.session_state.char_count = 0
    st.session_state.text_area_key += 1



col1, col2 = st.columns(2)

with col1:
    st.subheader("✍️ Paste your text")

    if st.session_state.pending_file_text is not None:
        default_value = st.session_state.pending_file_text
        st.session_state.pending_file_text = None
    else:
        default_value = st.session_state.input_text

    user_text = st.text_area(
        "Enter your text here:",
        height=300,
        value=default_value,
        key=f"input_text_widget_{st.session_state.text_area_key}",
        placeholder="Type or paste your text..."
    )

    if user_text != st.session_state.input_text:
        process_text(user_text)

    b1, b2, b3 = st.columns([4, 1, 1])
    with b1:
        st.caption(f"📊 Characters: {st.session_state.char_count}")
    with b2:
        st.button("🗑️ Clear", on_click=clear_text)
    with b3:
        st.button(
            "🔎 Scan",
            on_click=lambda: process_text(
                st.session_state.get(
                    f"input_text_widget_{st.session_state.text_area_key}", ""
                )
            )
        )

    uploaded_file = st.file_uploader("📄 Upload Word Document (.docx)", type=["docx"])
    if uploaded_file:
        with st.spinner("Scanning the document..."):
            try:
                doc = docx.Document(uploaded_file)
                file_text = "\n".join(
                    [p.text for p in doc.paragraphs if p.text.strip()]
                )

                st.session_state.pending_file_text = file_text
                process_text(file_text)

                st.success("✅ Scan complete!")
            except Exception as e:
                st.error(f"Error reading file: {e}")

with col2:
    st.subheader("🔍 Highlighted Text")

    if st.session_state.scanned_text:
        st.markdown(
            f'<div class="highlight-box">{st.session_state.scanned_text}</div>',
            unsafe_allow_html=True
        )

        if st.session_state.suggestions:
            st.subheader("💡 Suggestions")
            for word, replacement in sorted(st.session_state.suggestions):
                st.markdown(f"- **{word}** → {', '.join(replacement)}")
        else:
            st.success("✅ No biased words detected!")
    else:
        st.info("👈 Paste text on the left or upload a Word file to see highlights here.")
