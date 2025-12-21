import re
import sys


def count_equations(block):
    """Number of equations inside equation environment"""
    return block.count('\\\\') + 1


def process_latex(tex):
    """Convert LaTeX equations to JATS disp-formula XML"""
    eq_pattern = re.compile(
        r'\\begin\{equation\}(.*?)\\end\{equation\}',
        re.S
    )

    eq_counter = 1
    output = []

    for block in eq_pattern.findall(tex):
        # remove label
        block = re.sub(r'\\label\{[^}]+\}', '', block).strip()

        eq_count = count_equations(block)

        # ID generation
        if eq_count == 1:
            disp_id = f"deqn{eq_counter}"
        else:
            disp_id = f"deqn{eq_counter}-deqn{eq_counter + eq_count - 1}"

        # SINGLE equation
        if eq_count == 1:
            math = f"""\\begin{{equation*}}
{block}
\\tag{{{eq_counter}}}
\\end{{equation*}}"""

        # GROUPED equations
        else:
            lines = block.split('\\\\')
            tagged_lines = []

            for i, line in enumerate(lines):
                tag_num = eq_counter + i
                line = line.rstrip().rstrip(',').rstrip('.')
                tagged_lines.append(f"{line} \\tag{{{tag_num}}}")

            inner = " \\\\\n".join(tagged_lines)

            math = f"""\\begin{{equation*}}
\\begin{{gathered}}
{inner}
\\end{{gathered}}
\\end{{equation*}}"""

        output.append(
f"""<disp-formula id="{disp_id}"><tex-math notation="LaTeX">
{math}
</tex-math></disp-formula>"""
        )

        eq_counter += eq_count

    return "\n\n".join(output)


def main():
    """Main function with command-line argument handling"""
    
    # Check if arguments provided
    if len(sys.argv) < 3:
        print("Usage: python script.py <input_file.tex> <output_file.xml>")
        print("\nExample:")
        print("  python script.py input.tex output.xml")
        print("  python script.py 11297693.tex equations.xml")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        # Read input TeX file
        print(f"Reading: {input_file}")
        with open(input_file, "r", encoding="utf8") as f:
            tex = f.read()
        
        # Process LaTeX
        print("Processing equations...")
        result = process_latex(tex)
        
        # Write output XML file
        print(f"Writing: {output_file}")
        with open(output_file, "w", encoding="utf8") as f:
            f.write(result)
        
        # Count equations
        eq_count = result.count('<disp-formula')
        print(f"✔ Success! Converted {eq_count} equation blocks")
        print(f"✔ LaTeX converted directly to disp-formula XML")
        
    except FileNotFoundError as e:
        print(f"✗ Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
