import re

INPUT_FILE = "input.tex"
OUTPUT_FILE = "output.xml"


def count_equations(block):
    # number of equations inside equation environment
    return block.count('\\\\') + 1


def process_latex(tex):
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


if __name__ == "__main__":
    with open(INPUT_FILE, "r", encoding="utf8") as f:
        tex = f.read()

    result = process_latex(tex)

    with open(OUTPUT_FILE, "w", encoding="utf8") as f:
        f.write(result)

    print("✔ LaTeX converted directly to disp-formula XML")
