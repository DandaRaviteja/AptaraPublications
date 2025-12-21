import re
import xml.etree.ElementTree as ET
from pathlib import Path

"""
EQUATION REPLACER FOR XML PUBLISHING
=====================================
Purpose: Extract equations from Python processor output and replace them in overall XML file

Workflow:
1. Run your existing Python code (improved-equation-processor.py)
   Input:  paper.tex
   Output: equations.xml (contains only <disp-formula> blocks)

2. Use this script to integrate those equations into the full XML
   Input:  original_full_article.xml + equations.xml
   Output: final_article.xml (with corrected equations)

This keeps your working equation processor untouched!
"""

class EquationReplacer:
    def __init__(self, full_xml_file, equations_xml_file):
        """Initialize with paths to full XML and extracted equations XML"""
        self.full_xml_file = full_xml_file
        self.equations_xml_file = equations_xml_file
        self.full_tree = None
        self.equations = {}
        
    def load_equations(self):
        """Parse equations XML and store by ID"""
        try:
            tree = ET.parse(self.equations_xml_file)
            root = tree.getroot()
            
            # Handle case where root is disp-formula itself
            if root.tag == 'disp-formula':
                eq_id = root.get('id')
                self.equations[eq_id] = root
            else:
                # Parse multiple disp-formula elements
                for elem in root.findall('.//disp-formula'):
                    eq_id = elem.get('id')
                    if eq_id:
                        self.equations[eq_id] = elem
            
            print(f"✓ Loaded {len(self.equations)} equations")
            print(f"  Equation IDs: {list(self.equations.keys())}")
            return True
            
        except ET.ParseError as e:
            print(f"✗ Error parsing equations XML: {e}")
            return False
    
    def load_full_xml(self):
        """Load the full article XML"""
        try:
            self.full_tree = ET.parse(self.full_xml_file)
            print(f"✓ Loaded full XML article")
            return True
        except ET.ParseError as e:
            print(f"✗ Error parsing full XML: {e}")
            return False
    
    def replace_equations(self):
        """Replace equation blocks in full XML with correct ones"""
        if not self.full_tree:
            print("✗ Full XML not loaded")
            return False
        
        root = self.full_tree.getroot()
        replacements = 0
        
        # Find all disp-formula elements in the full XML
        for old_disp_formula in root.findall('.//disp-formula'):
            eq_id = old_disp_formula.get('id')
            
            if eq_id in self.equations:
                new_disp_formula = self.equations[eq_id]
                
                # Replace the old element with new one
                parent = root.find('.//' + old_disp_formula.tag + '/..')
                if parent is None:
                    # Try different approach - find parent by iterating
                    for parent_candidate in root.iter():
                        if old_disp_formula in list(parent_candidate):
                            parent = parent_candidate
                            break
                
                if parent is not None:
                    index = list(parent).index(old_disp_formula)
                    parent.remove(old_disp_formula)
                    # Deep copy the new equation
                    new_copy = self._element_to_string(new_disp_formula)
                    new_elem = ET.fromstring(new_copy)
                    parent.insert(index, new_elem)
                    replacements += 1
                    print(f"  ✓ Replaced: {eq_id}")
        
        print(f"\n✓ Total replacements: {replacements} equations")
        return replacements > 0
    
    def _element_to_string(self, element):
        """Convert XML element to string for re-parsing"""
        return ET.tostring(element, encoding='unicode')
    
    def save_output(self, output_file):
        """Save the modified XML to output file"""
        if not self.full_tree:
            print("✗ No XML tree to save")
            return False
        
        try:
            self.full_tree.write(
                output_file,
                encoding='utf-8',
                xml_declaration=True
            )
            print(f"✓ Saved to: {output_file}")
            return True
        except Exception as e:
            print(f"✗ Error saving output: {e}")
            return False
    
    def process(self, output_file):
        """Main processing workflow"""
        print("="*70)
        print("EQUATION REPLACER - Integration Tool")
        print("="*70)
        
        # Step 1: Load equations from Python processor output
        print("\nStep 1: Loading equations from Python processor...")
        if not self.load_equations():
            return False
        
        # Step 2: Load full XML article
        print("\nStep 2: Loading full article XML...")
        if not self.load_full_xml():
            return False
        
        # Step 3: Replace equations in full XML
        print("\nStep 3: Replacing equations in full XML...")
        if not self.replace_equations():
            print("⚠ No equations were replaced")
        
        # Step 4: Save output
        print("\nStep 4: Saving updated XML...")
        self.save_output(output_file)
        
        print("\n" + "="*70)
        print("✓ Process complete!")
        print("="*70)


def extract_equations_from_xml(full_xml_file, equations_output_file):
    """
    Extract all <disp-formula> elements from full XML
    (for checking what equations currently exist)
    """
    try:
        tree = ET.parse(full_xml_file)
        root = tree.getroot()
        
        # Create wrapper element for equations
        equations_root = ET.Element('equations')
        
        # Extract all disp-formula
        count = 0
        for disp_formula in root.findall('.//disp-formula'):
            equations_root.append(disp_formula)
            count += 1
        
        # Save extracted equations
        tree = ET.ElementTree(equations_root)
        tree.write(equations_output_file, encoding='utf-8', xml_declaration=True)
        
        print(f"✓ Extracted {count} equations to: {equations_output_file}")
        return count
        
    except Exception as e:
        print(f"✗ Error extracting equations: {e}")
        return 0


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    """
    WORKFLOW:
    
    1. Run your Python equation processor:
       python improved-equation-processor.py
       Input:  11297693.tex
       Output: equations.xml
    
    2. Run this script to integrate equations into full XML:
       python equation_replacer.py
    """
    
    # Configuration
    FULL_XML_FILE = "11297693_ft.xml"  # Your manually-corrected XML
    EQUATIONS_XML_FILE = "equations.xml"  # Output from your Python processor
    OUTPUT_XML_FILE = "11297693_ft_updated.xml"  # Final result
    
    # Step A: Extract current equations from full XML (for reference)
    print("STEP A: Extracting current equations from full XML...")
    current_eqs = extract_equations_from_xml(FULL_XML_FILE, "current_equations.xml")
    print()
    
    # Step B: Use replacer to integrate corrected equations
    print("STEP B: Integrating corrected equations...")
    replacer = EquationReplacer(FULL_XML_FILE, EQUATIONS_XML_FILE)
    replacer.process(OUTPUT_XML_FILE)
    
    print("\n" + "="*70)
    print("RESULT: Updated XML file ready!")
    print("="*70)
    print(f"File: {OUTPUT_XML_FILE}")
    print("\nNow send this file to your publisher or Epsilon for final processing.")
