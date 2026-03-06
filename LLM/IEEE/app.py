import streamlit as st
import fitz  # PyMuPDF
import requests
import json
import time

# --- CONFIGURATION ---
# Using the Hugging Face Inference API (Serverless/Free)
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/phi-4"
HF_TOKEN = "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"

st.set_page_config(page_title="Surgical XML Editor", layout="wide")

# --- 1. INITIALIZE SESSION STATE ---
if 'pdf_text' not in st.session_state:
    st.session_state['pdf_text'] = ""
if 'xml_output' not in st.session_state:
    st.session_state['xml_output'] = ""

st.title("✂️ Surgical XML Editor (Hugging Face Phi-4)")

# --- 2. SIDEBAR: SETTINGS ---
with st.sidebar:
    st.header("Model Settings")
    model_id = st.text_input("Hugging Face Model Path", value="microsoft/phi-4")
    temp = st.slider("Temperature (0.0 = Surgical)", 0.0, 1.0, 0.0)
    
    st.info("Using Hardcoded HF Token for Free Tier Access.")
    
    if st.button("🗑️ Reset Application"):
        st.session_state['pdf_text'] = ""
        st.session_state['xml_output'] = ""
        st.rerun()

# --- 3. MAIN UI ---
col_pdf, col_xml = st.columns(2)

with col_pdf:
    st.subheader("1. Source PDF")
    pdf_file = st.file_uploader("Upload PDF", type="pdf")

with col_xml:
    st.subheader("2. XML Query/Snippet")
    xml_query = st.text_area("Paste XML here", height=250, placeholder="<contrib-group>...</contrib-group>")

# --- 4. EXECUTION LOGIC ---
if st.button("🚀 Run Surgical Remediation"):
    if not pdf_file or not xml_query:
        st.error("Please provide both a PDF file and the XML input.")
    else:
        with st.spinner("Processing..."):
            try:
                # Step 1: Extract PDF Text
                doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
                st.session_state['pdf_text'] = "\n".join([page.get_text() for page in doc])
                
                # Step 2: Prepare Prompt for Phi-4
                system_prompt = (
                    "You are a Surgical XML Editor for IEEE JATS DTD v2.0. "
                    "Rules: Preserve PROTECTED ZONE. Use <name-alternatives>. "
                    "Move emails to <contrib>. Use hex entities (&#x2020;). "
                    "Return ONLY valid XML code."
                )
                
                # Hugging Face Inference API uses a specific "inputs" format
                prompt = f"<|system|>\n{system_prompt}\n<|user|>\nPDF DATA:\n{st.session_state['pdf_text']}\n\nXML TO EDIT:\n{xml_query}\n<|assistant|>\n"

                # Step 3: API Call with Retry Logic (for Model Loading)
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 2048,
                        "temperature": temp + 0.01, # Avoid exact 0 for some HF engines
                        "return_full_text": False
                    }
                }

                def query_hf(url, headers, payload):
                    response = requests.post(url, headers=headers, json=payload)
                    return response

                response = query_hf(HF_API_URL, headers, payload)
                
                # Handle "Model is loading" (Common on Free Tier)
                if response.status_code == 503:
                    estimated_time = response.json().get('estimated_time', 20)
                    with st.warning(f"Model is waking up... waiting {int(estimated_time)}s"):
                        time.sleep(estimated_time)
                        response = query_hf(HF_API_URL, headers, payload)

                if response.status_code == 200:
                    # Hugging Face returns a list: [{'generated_text': '...'}]
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        st.session_state['xml_output'] = result[0]['generated_text']
                        st.success("✅ Remediation Complete!")
                    else:
                        st.error("Unexpected response format from Hugging Face.")
                else:
                    st.error(f"HF API Error ({response.status_code}): {response.text}")

            except Exception as e:
                st.error(f"System Error: {str(e)}")

# --- 5. RESULTS & PREVIEW ---
if st.session_state['xml_output']:
    st.divider()
    st.subheader("Resulting XML Output")
    st.code(st.session_state['xml_output'], language='xml')
    st.download_button("📥 Download Result", st.session_state['xml_output'], "remediated.xml", "text/xml")

if st.session_state['pdf_text']:
    with st.expander("🔍 View Extracted PDF Text"):
        st.text(st.session_state['pdf_text'])