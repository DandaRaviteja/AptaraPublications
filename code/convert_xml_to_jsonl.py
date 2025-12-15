#!/usr/bin/env python3
"""
Convert XML input-output pairs to JSONL format for Google Vertex AI fine-tuning

Usage:
    python convert_xml_to_jsonl.py

Requirements:
    - Put all input XMLs in folder: ./xml-input/
    - Put all output XMLs in folder: ./xml-output/
    - Files can have patterns like: 
      * Input: 11273196_ft_Input.xml → Output: 11273196_ft_output.xml
      * Input: file_001.xml → Output: file_001.xml (matching names)

Output:
    - Creates: training_data.jsonl (80% - training)
    - Creates: validation_data.jsonl (20% - validation)
"""

import json
import os
from pathlib import Path
import re
import sys
import random

def extract_file_id(filename):
    """Extract ID from filename for matching input/output pairs"""
    # Try to extract numeric ID or base name
    # Pattern 1: 11273196_ft_Input.xml -> extract 11273196
    match = re.match(r'(\d+)_ft_', filename)
    if match:
        return match.group(1)
    
    # Pattern 2: file_001.xml -> extract 001
    match = re.match(r'file_(\d+)', filename)
    if match:
        return match.group(1)
    
    # Pattern 3: sample_001.xml -> extract 001
    match = re.match(r'\w+_(\d+)', filename)
    if match:
        return match.group(1)
    
    # If no pattern, return filename without extension
    return os.path.splitext(filename)[0]

def find_matching_output(input_filename, output_dir):
    """Find matching output file for given input file"""
    input_id = extract_file_id(input_filename)
    
    output_files = [f for f in os.listdir(output_dir) if f.endswith('.xml')]
    
    # First try exact match
    if input_filename in output_files:
        return input_filename
    
    # Try to find matching output by ID
    for output_file in output_files:
        output_id = extract_file_id(output_file)
        if output_id == input_id:
            return output_file
    
    return None

def create_jsonl_from_xml_pairs(input_dir="xml-input", output_dir="xml-output", 
                               training_file="training_data.jsonl", 
                               validation_file="validation_data.jsonl",
                               validation_split=0.2):
    """
    Convert XML input-output pairs to JSONL format for Vertex AI fine-tuning
    Automatically splits into training (80%) and validation (20%) sets
    
    Args:
        input_dir: Directory containing input XML files
        output_dir: Directory containing output XML files
        training_file: Output JSONL filename for training
        validation_file: Output JSONL filename for validation
        validation_split: Percentage for validation (default 0.2 = 20%)
    """
    
    # Check if directories exist
    if not os.path.exists(input_dir):
        print(f"❌ Error: Input directory '{input_dir}' not found!")
        print(f"   Create folder: {os.path.abspath(input_dir)}")
        return False
    
    if not os.path.exists(output_dir):
        print(f"❌ Error: Output directory '{output_dir}' not found!")
        print(f"   Create folder: {os.path.abspath(output_dir)}")
        return False
    
    # Get input XML files
    input_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.xml')])
    
    if not input_files:
        print(f"❌ Error: No XML files found in '{input_dir}'")
        return False
    
    print(f"📂 Found {len(input_files)} input XML files")
    
    all_examples = []
    skipped = 0
    
    for idx, filename in enumerate(input_files, 1):
        input_path = os.path.join(input_dir, filename)
        
        # Find matching output file (handles different naming patterns)
        output_filename = find_matching_output(filename, output_dir)
        
        if not output_filename:
            print(f"⚠️  Skipping {filename} - no matching output file found")
            skipped += 1
            continue
        
        output_path = os.path.join(output_dir, output_filename)
        
        # Read input XML
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                input_xml = f.read().strip()
        except Exception as e:
            print(f"⚠️  Error reading {input_path}: {e}")
            skipped += 1
            continue
        
        # Read output XML
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                output_xml = f.read().strip()
        except Exception as e:
            print(f"⚠️  Error reading {output_path}: {e}")
            skipped += 1
            continue
        
        # Create JSONL example for Vertex AI
        # Format: {"prompt": "user instruction", "completion": "model response"}
        example = {
            "prompt": f"Transform and tag this XML document with proper references and table names:\n\n{input_xml}",
            "completion": f"\n{output_xml}"
        }
        
        all_examples.append(example)
        
        # Print progress
        input_size = len(input_xml) / 1024
        output_size = len(output_xml) / 1024
        print(f"✓ {idx}. {filename} → {output_filename} ({input_size:.1f}KB → {output_size:.1f}KB)")
    
    if not all_examples:
        print("❌ Error: No training examples created!")
        return False
    
    # Split into training and validation sets
    random.seed(42)  # For reproducibility
    random.shuffle(all_examples)
    
    split_index = int(len(all_examples) * (1 - validation_split))
    training_examples = all_examples[:split_index]
    validation_examples = all_examples[split_index:]
    
    # Write training JSONL file
    try:
        with open(training_file, 'w', encoding='utf-8') as f:
            for example in training_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"\n✅ SUCCESS: Created {training_file}")
        print(f"📊 Training Statistics:")
        print(f"   - Total examples: {len(training_examples)}")
        print(f"   - File size: {os.path.getsize(training_file) / (1024*1024):.2f} MB")
        
    except Exception as e:
        print(f"❌ Error writing training JSONL file: {e}")
        return False
    
    # Write validation JSONL file
    try:
        with open(validation_file, 'w', encoding='utf-8') as f:
            for example in validation_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"\n✅ SUCCESS: Created {validation_file}")
        print(f"📊 Validation Statistics:")
        print(f"   - Total examples: {len(validation_examples)}")
        print(f"   - File size: {os.path.getsize(validation_file) / (1024*1024):.2f} MB")
        
    except Exception as e:
        print(f"❌ Error writing validation JSONL file: {e}")
        return False
    
    # Print summary
    print(f"\n" + "="*60)
    print(f"📊 DATASET SPLIT SUMMARY:")
    print(f"="*60)
    print(f"Total examples:      {len(all_examples)}")
    print(f"Training examples:   {len(training_examples)} ({(len(training_examples)/len(all_examples)*100):.1f}%)")
    print(f"Validation examples: {len(validation_examples)} ({(len(validation_examples)/len(all_examples)*100):.1f}%)")
    print(f"Skipped:             {skipped}")
    
    # Show first example
    print(f"\n📝 First example in training set:")
    first_example = training_examples[0]
    print(f"   Prompt length: {len(first_example['prompt'])} chars")
    print(f"   Completion length: {len(first_example['completion'])} chars")
    
    return True

def verify_jsonl_file(jsonl_file="training_data.jsonl"):
    """Verify JSONL file format"""
    
    if not os.path.exists(jsonl_file):
        print(f"❌ File not found: {jsonl_file}")
        return False
    
    print(f"\n🔍 Verifying {jsonl_file}...")
    
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"   ✓ Total lines: {len(lines)}")
        
        # Check each line is valid JSON
        valid_count = 0
        for i, line in enumerate(lines, 1):
            try:
                example = json.loads(line)
                if "prompt" in example and "completion" in example:
                    valid_count += 1
                else:
                    print(f"   ⚠️  Line {i}: Missing 'prompt' or 'completion' field")
            except json.JSONDecodeError as e:
                print(f"   ⚠️  Line {i}: Invalid JSON - {e}")
        
        print(f"   ✓ Valid examples: {valid_count}/{len(lines)}")
        
        if valid_count == len(lines):
            print(f"✅ {jsonl_file} is valid!")
            return True
        else:
            print(f"⚠️  Some examples are invalid")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying file: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("XML to JSONL Converter with Validation Split")
    print("Google Vertex AI Fine-tuning")
    print("=" * 60)
    
    # Create directories if they don't exist
    os.makedirs("xml-input", exist_ok=True)
    os.makedirs("xml-output", exist_ok=True)
    
    print("\n📋 Instructions:")
    print("   1. Place all INPUT XMLs in: ./xml-input/")
    print("   2. Place all OUTPUT XMLs in: ./xml-output/")
    print("   3. Naming patterns supported:")
    print("      - 11273196_ft_Input.xml ↔ 11273196_ft_output.xml")
    print("      - file_001.xml ↔ file_001.xml (same name)")
    print("   4. Run this script\n")
    
    # Convert XMLs to JSONL with automatic validation split
    success = create_jsonl_from_xml_pairs(
        input_dir="xml-input",
        output_dir="xml-output",
        training_file="training_data.jsonl",
        validation_file="validation_data.jsonl",
        validation_split=0.2  # 20% for validation, 80% for training
    )
    
    if success:
        # Verify both JSONL files
        verify_jsonl_file("training_data.jsonl")
        verify_jsonl_file("validation_data.jsonl")
        
        print("\n" + "=" * 60)
        print("📤 NEXT STEPS (Google Vertex AI):")
        print("=" * 60)
        print("1. Go to: https://console.cloud.google.com/vertex-ai")
        print("2. Click: Generative AI Studio")
        print("3. Click: Create tuned model")
        print("4. Select: Gemini 2.0 Flash")
        print("5. Upload TRAINING file: training_data.jsonl")
        print("6. OPTIONAL - Upload VALIDATION file: validation_data.jsonl")
        print("   (Click: Enable model validation → Browse → validation_data.jsonl)")
        print("7. Set epochs to: 3")
        print("8. Click: Start Tuning")
        print("=" * 60 + "\n")
    else:
        print("\n❌ Failed to create JSONL. Check the errors above.")
        sys.exit(1)