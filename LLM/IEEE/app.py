import streamlit as st
import fitz  # PyMuPDF
from huggingface_hub import InferenceClient

# --- PAGE SETUP ---
st.set_page_config(page_title="Surgical XML Editor", layout="wide")

# --- INITIALIZE SESSION STATE ---
if 'xml_output' not in st.session_state:
    st.session_state['xml_output'] = ""

st.title("✂️ Surgical XML Editor (Phi-4)")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    # Change to "microsoft/phi-4" or "microsoft/Phi-4-mini-instruct"
# This tells the router to find ANY provider currently hosting the model
    model_id = "microsoft/phi-4:fastest"
    temp = st.slider("Temperature", 0.0, 1.0, 0.01)
    
    if st.button("🗑️ Reset"):
        st.session_state['xml_output'] = ""
        st.rerun()

# --- MAIN UI ---
col_pdf, col_xml = st.columns(2)
with col_pdf:
    st.subheader("1. Source PDF")
    pdf_file = st.file_uploader("Upload PDF", type="pdf")

with col_xml:
    st.subheader("2. XML Query")
    xml_query = st.text_area("Paste XML here", height=250)

# --- EXECUTION ---
if st.button("🚀 Run Remediation"):
    if not pdf_file or not xml_query:
        st.error("Please provide both inputs.")
    else:
        try:
            # 1. Fetch Token from Secrets
            hf_token = st.secrets["HF_TOKEN"]
            
            # 2. Extract PDF Text
            with st.spinner("Extracting PDF..."):
                doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
                pdf_text = "\n".join([page.get_text() for page in doc])
            
            # 3. Use the Official Client (Fixes 404/410 errors)
            client = InferenceClient(api_key=hf_token)
            
            with st.spinner("Consulting Phi-4..."):
                response = client.chat_completion(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": "You are a Surgical XML Editor. Return ONLY valid XML code."},
                        {"role": "user", "content": f"CONTEXT PDF:\n{pdf_text}\n\nTARGET XML:\n{xml_query}"}
                    ],
                    max_tokens=2048,
                    temperature=temp
                )
                
                st.session_state['xml_output'] = response.choices[0].message.content
                st.success("Done!")

        except Exception as e:
            st.error(f"Error: {e}")

# --- RESULTS ---
if st.session_state['xml_output']:
    st.divider()
    st.code(st.session_state['xml_output'], language='xml')
    st.download_button("📥 Download", st.session_state['xml_output'], "output.xml")