import streamlit as st
import fitz  # PyMuPDF
import requests
import json
import time

# --- CONFIGURATION ---
# Using the Hugging Face Inference API (Serverless/Free)
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/phi-4"

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
    try:
        HF_TOKEN = st.secrets["HF_TOKEN"]
    except KeyError:
        st.error("HF_TOKEN not found in Secrets. Please add it to Streamlit Cloud settings.")
        st.stop()

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
                    '''
                    ### **instructions.txt**

                    **### ROLE**
                    You are a **Surgical XML Editor** for IEEE JATS DTD v2.0. Your sole mission is to take a **[Raw Input XML]** and update specific data points using a **[Source PDF]** as the reference.

                    **### 1. PROTECTED ZONE (DO NOT MODIFY)**

                    * Everything from the first line of the file (`<?xml...?>`) down to the opening `<conf-front>` tag is a **PROTECTED ZONE**.
                    * Do not add, delete, or change a single character, space, or attribute in this zone.
                    * Inside `<conf-front>`, **strictly** do not change any tags or content until the `<title-group>` tag is reached.

                    HEX ENTITY LOCK & LITERAL PRESERVATION: * Do not convert existing literal characters (e.g., @, &, ") into hexadecimal entities if they appear as literals in the [Raw Input XML].Only use hexadecimal entities (e.g., &#x0026; for &) if they are already present in the original XML or if a new special character is being introduced that requires encoding.Strict Rule: If the input XML uses @, keep it as @. Do not "clean" or "standardize" entities unless they are broken.

                    **### 2. ABSOLUTE CONSTRAINTS (DO NOT VIOLATE)**

                    * **ZERO TAG ALTERATION:** Do not rename, delete, or re-order any existing XML tags unless specifically instructed below.
                    * **STRICT INDENTATION:** Maintain the exact whitespace and indentation of the original file. New blocks must align with their parent tag's indentation.
                    * **HEX ENTITY LOCK:** Do not convert hexadecimal entities (e.g., `&#x0026;`, `&#x201C;`) into literal characters. Use Hexadecimal values for any new special characters.
                    * **NO SPELL-CHECK:** Do not fix spelling, grammar, or capitalization. Copy names and titles exactly as they appear in the source.

                    **### 3. SPECIFIC REMEDIATION TASKS**

                    CONTRIB-GROUP STRUCTURE:

                    Maintain the <contrib-group> and <contrib> structure exactly as provided in the expected output.

                    Use <name-alternatives> containing two <string-name> tags: one with specific-use="display" and one with specific-use="index".

                    Inside <string-name>, use <given-names> followed by <surname>.

                    Example:
                    <contrib contrib-type="author" id="contrib1">
                    <name-alternatives>
                    <string-name specific-use="display"><given-names>Nicole</given-names> <surname>Fronda</surname></string-name>
                    <string-name specific-use="index"><given-names>Nicole</given-names> <surname>Fronda</surname></string-name>
                    </name-alternatives>
                    <xref ref-type="aff" rid="aff1"/>
                    </contrib>

                    * **CONTRIB-GROUP REARRANGEMENT:**
                    * If multiple author names exist without labels and share a single affiliation, and their emails are listed outside the `<contrib-group>` (e.g., inside `<aff>`):
                    * Rearrange the emails from the `<aff>` tag to their respective author.
                    * Place the `<email>` tag **inside** the `<contrib>` block, specifically under the `</name-alternatives>` tag for that author.

                    ### 3. ADVANCED AFFILIATION & FUNDING RULES

                    * **GRANULAR AFFILIATIONS:** * Wrap affiliation details in <institution-wrap>.
                        * Distinguish between <institution content-type="department"> (e.g., Department of...) and <institution content-type="institution"> (e.g., University of Arizona).
                        * Place City, State, and Country in their own tags: <city>, <state>, <country>.
                        * Maintain specific label markers (e.g., <sup>&#x2020;</sup>) inside the <aff> tag if present in the source.

                    * **ENTITY CODING FOR MARKERS:**
                        * Use &#x2020; for the Dagger (†).
                        * Use &#x2021; for the Double Dagger (‡).
                        * Use &#x00B6; for the Pilcrow (¶).
                        * Use &#x2016; for the Double Vertical Line (‖).

                    * **FUNDING & ACKNOWLEDGMENTS:**
                        * If the Source PDF contains an "Acknowledgment" or "Funding" section, you must construct a <funding-group> block.
                        * Use <award-group> for specific grants/programs.
                        * The full text of the acknowledgment must be placed inside <funding-statement>.

                    PAGINATION (<fpage> / <lpage>):

                    * **Detection Rule:** Scan the top or bottom corners of EVERY page in the PDF to find the highest printed number. 
                    * **Physical Count vs. Printed Number:** * If the PDF has 6 physical pages, but the last printed number you see is 2678, then <lpage> is 2678[cite: 659].
                        * If a page (like a References or Appendix page) does not have a printed number, increment the last known number by 1 for each subsequent page.
                    * **Verification:** Count the total number of physical pages in the PDF file (e.g., in Chrome or Acrobat). 
                        * Set <page-count count="X"/> where X is the total physical page count[cite: 660].
                        * Example: If the PDF starts at 2673 and has 6 physical pages, the math must be: <fpage>2673</fpage>, <lpage>2678</lpage>, and <page-count count="6"/>.


                    * **PAGE COUNT:** * Update `<page-count count="0"/>` by replacing `0` with the total number of pages in the source PDF.


                    COPYRIGHT & LICENSE (STRICT LITERAL COPY):

                    Search Area: Scan the bottom of Page 1 or Page 2 for a string containing a year, "IEEE", or a price.

                    Capture Rule: Copy the ENTIRE footer block exactly as it appears.

                    Example: If the PDF says 2375-9259/25/$31.00 ©2025 IEEE, you must copy that entire string into <copyright-statement>. Do not start at the © symbol; start from the very first character of that line.

                    License Price: If the string contains $31.00, you MUST insert this exact block inside <ali:license_ref>:
                    <license-p><price currency="USD">31.00</price></license-p>

                    * **STRICT LIMIT:** Do not change any other tags other than those explicitly listed here.

                    **### 4. OUTPUT FORMAT**

                    * Return the **ENTIRE** updated XML file in one single code block.
                    * Do not include any introductory or concluding remarks.
                    '''
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