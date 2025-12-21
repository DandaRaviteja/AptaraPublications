import re
import sys

def count_equations(block: str) -> int:
    # number of equations inside equation environment (split by \\)
    return block.count('\\\\') + 1

def process_latex_to_disp_formulas(tex: str) -> list[str]:
    """
    Use your current logic:
    - find \\begin{equation} ... \\end{equation}
    - handle single / grouped
    - return list of <disp-formula>...</disp-formula> strings IN ORDER
    """
    eq_pattern = re.compile(
        r'\\begin\{equation\}(.*?)\\end\{equation\}',
        re.S
    )

    eq_counter = 1
    disp_formulas: list[str] = []

    for block in eq_pattern.findall(tex):
        # remove \label{...}
        block = re.sub(r'\\label\{[^}]+\}', '', block).strip()

        eq_count = count_equations(block)

        # ID generation (you can keep deqnX style)
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

        disp_formulas.append(
            f"""<disp-formula id="{disp_id}"><tex-math notation="LaTeX">
{math}
</tex-math></disp-formula>"""
        )

        eq_counter += eq_count

    return disp_formulas

def replace_disp_formulas_in_xml(xml_text: str, new_disp_list: list[str]) -> str:
    """
    Replace existing <disp-formula ...>...</disp-formula> blocks
    with new ones, position by position.
    """
    pattern = re.compile(r'<disp-formula[^>]*>.*?</disp-formula>', re.DOTALL)

    matches = list(pattern.finditer(xml_text))
    if not matches:
        print("No <disp-formula> found in XML.")
        return xml_text

    print(f"Found {len(matches)} disp-formula blocks in XML.")
    print(f"{len(new_disp_list)} new disp-formulas from LaTeX.")

    # Replace from last to first so indices stay valid
    result = xml_text
    for i in range(len(matches) - 1, -1, -1):
        if i < len(new_disp_list):
            m = matches[i]
            old_block = m.group(0)
            new_block = new_disp_list[i]
            result = result[:m.start()] + new_block + result[m.end():]
            print(f"Replaced equation #{i+1}")
        else:
            print(f"Warning: XML has more equations ({len(matches)}) than LaTeX output ({len(new_disp_list)}).")
            break

    return result

def main():
    if len(sys.argv) != 4:
        print("Usage: python fix_equations.py source.tex bad.xml fixed.xml")
        sys.exit(1)

    tex_file = sys.argv[1]
    in_xml_file = sys.argv[2]
    out_xml_file = sys.argv[3]

    # 1) Read LaTeX
    with open(tex_file, encoding="utf-8") as f:
        tex = f.read()

    # 2) Generate correct disp-formula blocks
    disp_list = process_latex_to_disp_formulas(tex)
    print(f"Generated {len(disp_list)} disp-formula blocks from LaTeX.")

    # 3) Read existing XML
    with open(in_xml_file, encoding="utf-8") as f:
        xml_text = f.read()

    # 4) Replace disp-formula blocks by position
    fixed_xml = replace_disp_formulas_in_xml(xml_text, disp_list)

    # 5) Write final XML
    with open(out_xml_file, "w", encoding="utf-8") as f:
        f.write(fixed_xml)

    print(f"Done. Written fixed XML to: {out_xml_file}")

if __name__ == "__main__":
    main()
