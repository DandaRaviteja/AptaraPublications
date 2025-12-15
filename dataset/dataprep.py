import os
import glob
import re
from lxml import etree as ET_LXML
from lxml.etree import XMLSyntaxError
import json

# --- Configuration ---
ROOT_DIR = 'C:/Users/raviteja/OneDrive/Desktop/IEEE_Articles'
INPUT_DIR = os.path.join(ROOT_DIR, 'xml-input')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'xml-output')
OUTPUT_JSONL_FILE = 'paired_sft_dataset.jsonl'
ENCODING = 'utf-8'

# Set the maximum content size (in characters) for a single training example
# LLMs typically handle up to ~4096 tokens, which is roughly 16000 characters, 
# but 4096 is a safer, conservative limit to prevent chunking large elements later.
MAX_CHUNK_SIZE = 4096 

# 🛑 CRITICAL: Define the semantic JATS tags to chunk by.
# These XPaths were confirmed from your provided XML sample.
TAGS_TO_PAIR_BY = [
    '//conf-article/conf-front/conf-article-meta/abstract',  # The abstract block (usually unique)
    '//conf-article/body/sec',                              # Each main section (often too large)
    '//conf-article/body/sec//p',                           # Individual paragraphs
    '//conf-article/body/sec//table-wrap',                  # Tables with wrappers
    '//conf-article/body/sec//fig',                         # Figures with wrappers
    '//conf-article/back/ref-list',                         # Reference list (often too large)
]

# --- XML Recovery and Cleaning ---

# Create an XMLParser instance with the crucial 'recover=True' flag
RECOVERY_PARSER = ET_LXML.XMLParser(recover=True, encoding=ENCODING)

# Regular expression to catch and remove illegal XML 1.0 control characters
ILLEGAL_CHAR_RE = re.compile(
    '[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]' 
)

def clean_and_read_xml(file_path):
    """Reads a file, cleans illegal characters, and attempts to parse it with recovery."""
    file_name = os.path.basename(file_path)
    try:
        with open(file_path, 'r', encoding=ENCODING, errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"   ❌ Error reading file {file_name}: {e}")
        return None
    
    # 1. Clean up illegal control characters
    cleaned_content = ILLEGAL_CHAR_RE.sub('', content)
    
    # 2. Parse with recovery mode
    try:
        root = ET_LXML.fromstring(cleaned_content.encode(ENCODING), parser=RECOVERY_PARSER)
        return ET_LXML.ElementTree(root)
    except XMLSyntaxError as e:
        print(f"   ❌ Recovery Mode Failed for {file_name}: {e}")
        return None
    except Exception as e:
        print(f"   ❌ Final Parsing Failure for {file_name}: {e}")
        return None

def extract_xml_chunk(element):
    """Extracts the XML snippet string for the element."""
    xml_string = ET_LXML.tostring(element, encoding='unicode', pretty_print=False)
    return xml_string.strip()

def create_sft_example(input_chunk, output_chunk, chunk_type):
    """Generates a structured SFT example (prompt-completion pair) for fine-tuning."""
    
    prompt = (
        f"Normalize the structure and content of the following XML chunk, identified as a '{chunk_type}', "
        f"into the target XML format.\n\n"
        f"### INPUT_XML_CHUNK ###\n{input_chunk}"
    )
    
    completion = f"### TARGET_XML_CHUNK ###\n{output_chunk}"
    
    return {
        "prompt": prompt,
        "completion": completion,
        "chunk_type": chunk_type
    }

def split_large_chunk(xml_chunk, max_size=MAX_CHUNK_SIZE):
    """
    Splits a large XML chunk's text content into smaller segments 
    and re-wraps them in a generic tag.
    """
    # 1. Strip the surrounding XML tags to get the pure text content
    text_content = re.sub(r'<[^>]*>', '', xml_chunk)
    
    # 2. Split the text into sentence-level chunks
    sentences = re.split(r'(?<=[.?!])\s+', text_content)
    
    current_chunk = ""
    sub_chunks = []
    
    # 3. Aggregate sentences into chunks no larger than max_size
    for sentence in sentences:
        # Check if adding the next sentence plus a space exceeds the limit
        if len(current_chunk) + len(sentence) + 1 > max_size:
            sub_chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
        else:
            current_chunk += sentence + " "
    
    if current_chunk:
        sub_chunks.append(current_chunk.strip())
        
    # Re-wrap the final text chunks with a generic tag (useful for context)
    return [f"<text_segment>{c}</text_segment>" for c in sub_chunks]

# --- Main Processing Logic ---

def generate_paired_chunks(input_dir, output_dir, tags_to_pair):
    """
    Reads pairs of XML files, extracts content based on tags, and creates
    paired training chunks in JSONL format.
    """
    sft_examples = []
    
    input_files = glob.glob(os.path.join(input_dir, '*.xml'))
    
    print(f"Found {len(input_files)} XML files in the input directory.")

    for input_file_path in input_files:
        file_name = os.path.basename(input_file_path)
        output_file_path = os.path.join(output_dir, file_name)

        if not os.path.exists(output_file_path):
            print(f"⚠️ Warning: Missing output file for {file_name}. Skipping.")
            continue
            
        print(f"Processing pair: {file_name}")

        # --- Step 1: Parse Files with Recovery and Error Check ---
        input_tree = clean_and_read_xml(input_file_path)
        output_tree = clean_and_read_xml(output_file_path)
        
        # Check for successful parsing and the presence of a root element (Fixes 'NoneType' error)
        if input_tree is None or output_tree is None or \
           input_tree.getroot() is None or output_tree.getroot() is None:
            print(f"   Skipping pair due to unrecoverable errors (No Root Element Found).")
            continue
            
        input_root = input_tree.getroot()
        output_root = output_tree.getroot()


        # --- Step 2: Extract and Pair Chunks ---
        for xpath in tags_to_pair:
            try:
                input_elements = input_root.xpath(xpath)
                output_elements = output_root.xpath(xpath)
                
                # Check 1: Mismatched count (The main source of lost data)
                if len(input_elements) != len(output_elements):
                    # Only report mismatch if at least one side has elements
                    if len(input_elements) > 0 or len(output_elements) > 0:
                         print(f"   Mismatch: {len(input_elements)} in input vs {len(output_elements)} in output for XPath: {xpath}. Skipping pairing for this tag in this file.")
                    continue
                
                # Check 2: Process the paired elements
                for input_elem, output_elem in zip(input_elements, output_elements):
                    
                    input_chunk = extract_xml_chunk(input_elem)
                    output_chunk = extract_xml_chunk(output_elem)
                    
                    chunk_type = input_elem.tag.split('}')[-1]
                        
                    # ⚠️ Token Limit Check (Handles 'Chunk is too large' errors)
                    if len(input_chunk) > MAX_CHUNK_SIZE or len(output_chunk) > MAX_CHUNK_SIZE:
                        
                        # Only apply sub-chunking to the large, textual blocks (sec, ref-list)
                        if chunk_type in ['sec', 'ref-list']:
                            input_sub_chunks = split_large_chunk(input_chunk)
                            output_sub_chunks = split_large_chunk(output_chunk)
                            
                            # We only pair if the number of textual segments are roughly equal
                            if len(input_sub_chunks) == len(output_sub_chunks):
                                for i_sub, o_sub in zip(input_sub_chunks, output_sub_chunks):
                                    example = create_sft_example(i_sub, o_sub, chunk_type + "_segment")
                                    sft_examples.append(example)
                                print(f"   Splitting large '{chunk_type}' in {file_name} into {len(input_sub_chunks)} segments.")
                            else:
                                print(f"   Could not reliably sub-chunk and pair large '{chunk_type}' (segment count mismatch). Skipping.")
                                continue
                        else:
                            # Skip large, non-splitable chunks (like huge tables or figures)
                            print(f"   Chunk for '{chunk_type}' in {file_name} is too large (>4096 chars). Skipping.")
                        continue
                        
                    # Original logic for small/medium chunks
                    example = create_sft_example(input_chunk, output_chunk, chunk_type)
                    sft_examples.append(example)

            except Exception as e:
                # Catch any runtime error during extraction
                print(f"   ❌ Runtime Error during chunk extraction for {xpath} in {file_name}: {e}")

    # --- Step 3: Write Dataset ---
    with open(OUTPUT_JSONL_FILE, 'w', encoding=ENCODING) as f:
        for example in sft_examples:
            f.write(json.dumps(example) + '\n')
            
    print(f"\n🎉 Paired chunk generation complete!")
    print(f"Total structured SFT examples created: **{len(sft_examples)}**")
    print(f"Dataset saved to: **{OUTPUT_JSONL_FILE}**")


# --- Execution ---
if __name__ == "__main__":
    generate_paired_chunks(INPUT_DIR, OUTPUT_DIR, TAGS_TO_PAIR_BY)