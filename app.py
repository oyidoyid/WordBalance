from auth import google_login
import streamlit as st
from PIL import Image
from io import BytesIO
import base64
from biased_words import highlight_text, calculate_bias_percentage
import docx

user = google_login()
if user:
    st.success(f"Welcome {user['name']}!")
    # Load the WordBalance dashboard here
else:
    st.info("Please login with Google to continue.")

header_image = Image.open("ggg.png")
buffered = BytesIO()
header_image.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()

st.set_page_config(
    page_title="WordBalance",
    layout="wide",
    page_icon=header_image
)


st.markdown(
    f'<h1 style="text-align:center;"><img src="data:image/png;base64,{img_str}" width="50"> WordBalance</h1>',
    unsafe_allow_html=True
)
st.markdown(
    '<p style="text-align:center; color:gray;">Gender-Fair Language Detection Tool</p>',
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
if "bias_percentage" not in st.session_state:
    st.session_state.bias_percentage = 0.0
if "biased_count" not in st.session_state:
    st.session_state.biased_count = 0
if "total_words" not in st.session_state:
    st.session_state.total_words = 0
if "text_area_key" not in st.session_state:
    st.session_state.text_area_key = 0


def process_text(text):
    st.session_state.input_text = text
    st.session_state.char_count = len(text)
    if text.strip():
        highlighted, suggestions = highlight_text(text)
        bias_pct, biased_count, total_words = calculate_bias_percentage(text)

        st.session_state.scanned_text = highlighted
        st.session_state.suggestions = suggestions
        st.session_state.bias_percentage = bias_pct
        st.session_state.biased_count = biased_count
        st.session_state.total_words = total_words
    else:
        st.session_state.scanned_text = ""
        st.session_state.suggestions = []
        st.session_state.bias_percentage = 0.0
        st.session_state.biased_count = 0
        st.session_state.total_words = 0

def display_colored_progress(percentage):
    if percentage < 5:
        color = "#4CAF50"
    elif percentage < 15:
        color = "#FFEB3B"
    else:
        color = "#F44336"

    bar_html = f"""
    <div style='background-color: #e0e0e0; border-radius: 8px; height: 24px; width: 100%;'>
        <div style='background-color: {color}; width: {percentage}%; height: 100%; border-radius: 8px; text-align: center; color: black; font-weight:bold; line-height: 24px;'>{percentage}%</div>
    </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)

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

    default_value = st.session_state.pending_file_text if st.session_state.pending_file_text else st.session_state.input_text

    user_text = st.text_area(
        "Enter your text here:",
        height=300,
        value=default_value,
        key=f"input_text_widget_{st.session_state.text_area_key}",
        placeholder="Type or paste your text..."
    )

    if user_text != st.session_state.input_text:
        process_text(user_text)

    b1, b2, b3 = st.columns([4,1,1])
    with b1:
        st.caption(f"📊 Characters: {st.session_state.char_count}")
    with b2:
        st.button("🗑️ Clear", on_click=clear_text)
    with b3:
        st.button("🔎 Scan", on_click=lambda: process_text(
            st.session_state.get(f"input_text_widget_{st.session_state.text_area_key}", "")
        ))

    uploaded_file = st.file_uploader("📄 Upload Word Document (.docx)", type=["docx"])
    if uploaded_file:
        with st.spinner("Scanning the document..."):
            try:
                doc = docx.Document(uploaded_file)
                file_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                st.session_state.pending_file_text = file_text
                process_text(file_text)
                st.success("✅ Scan complete!")
            except Exception as e:
                st.error(f"Error reading file: {e}")

   
    if st.session_state.input_text.strip():
        st.subheader("📊 Bias Analysis")
        st.metric("Bias Percentage", f"{st.session_state.bias_percentage}%", help="Proportion of biased words in the text")
        display_colored_progress(st.session_state.bias_percentage)
        st.markdown(f"**Total words:** {st.session_state.total_words}  |  **Biased words:** {st.session_state.biased_count}")

with col2:
    st.subheader("🔍 Highlighted Text")
    if st.session_state.scanned_text:
        st.markdown(f'<div style="background-color:#fff9c4; padding:10px; border-radius:8px;">{st.session_state.scanned_text}</div>', unsafe_allow_html=True)
        if st.session_state.suggestions:
            st.subheader("💡 Suggestions")
            for word, replacement in sorted(st.session_state.suggestions):
                st.markdown(f"- **{word}** → {', '.join(replacement)}")
        else:
            st.success("✅ No biased words detected!")
    else:
        st.info("👈 Paste text on the left or upload a Word file to see highlights here.")
